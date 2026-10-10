"""Génère la liste de toutes les actions possibles à partir d'une grammaire.

Une action = VERBE + CIBLE (facultative) + OUTIL (facultatif).

Les entités du monde déclarent des affordances (tags) : ce qu'elles permettent.
Les verbes déclarent les tags qu'ils exigent de leur cible et de leur outil.
Le catalogue n'est donc jamais écrit à la main : il est calculé en croisant
verbes et entités. Ajouter un verbe ou une entité enrichit automatiquement
toutes les combinaisons compatibles.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from itertools import product
from pathlib import Path

DOSSIER_DATA = Path(__file__).resolve().parent.parent / "data"
EMPLACEMENTS = {"inventaire", "proximite"}


@dataclass(frozen=True)
class Action:
    verbe: str
    categorie: str
    texte: str
    cible: str | None = None
    outil: str | None = None


def _lire_json(chemin: Path) -> dict:
    with open(chemin, encoding="utf-8") as f:
        donnees = json.load(f)
    # Les clés commençant par « _ » servent de commentaires.
    return {cle: val for cle, val in donnees.items() if not cle.startswith("_")}


def charger(dossier: Path = DOSSIER_DATA) -> tuple[dict, dict]:
    return _lire_json(dossier / "verbes.json"), _lire_json(dossier / "entites.json")


def charger_situation(chemin: Path, entites: dict) -> dict:
    situation = _lire_json(chemin)
    situation.setdefault("joueur", {})
    situation.setdefault("inventaire", [])
    situation.setdefault("a_proximite", [])
    inconnues = [
        eid
        for eid in situation["inventaire"] + situation["a_proximite"]
        if eid not in entites
    ]
    if inconnues:
        raise ValueError(f"Entités inconnues dans {chemin} : {', '.join(inconnues)}")
    return situation


def _accorder(texte: str) -> str:
    """Contractions et élisions françaises : « à le » → « au », « de un » → « d'un »..."""
    texte = re.sub(r"\bà le\b", "au", texte)
    texte = re.sub(r"\bà les\b", "aux", texte)
    texte = re.sub(r"\bde le\b", "du", texte)
    texte = re.sub(r"\bde les\b", "des", texte)
    texte = re.sub(r"\bde (?=[aeiouyéèêàâîôû])", "d'", texte)
    return texte


def _candidats(entites: dict, tags_requis: list[str]) -> list[str]:
    requis = set(tags_requis)
    return [eid for eid, e in entites.items() if requis <= set(e["tags"])]


def _presentes(ids: list[str], emplacement: str | None, situation: dict | None) -> list[str]:
    if situation is None:
        return ids
    if emplacement == "inventaire":
        autorisees = set(situation["inventaire"])
    elif emplacement == "proximite":
        autorisees = set(situation["a_proximite"])
    else:
        autorisees = set(situation["inventaire"]) | set(situation["a_proximite"])
    return [eid for eid in ids if eid in autorisees]


def _conditions_remplies(conditions: list[str], joueur: dict) -> bool:
    for condition in conditions:
        negation = condition.startswith("!")
        if bool(joueur.get(condition.lstrip("!"), False)) == negation:
            return False
    return True


def generer(
    verbes: dict,
    entites: dict,
    situation: dict | None = None,
    verifier_conditions: bool = True,
) -> list[Action]:
    """Toutes les actions possibles.

    Sans situation : le catalogue théorique complet (conditions ignorées).
    Avec situation : seulement ce que le joueur peut faire maintenant.
    """
    actions = []
    for vid, verbe in verbes.items():
        if situation is not None and verifier_conditions and not _conditions_remplies(
            verbe.get("conditions", []), situation["joueur"]
        ):
            continue
        cibles = [None]
        if "cible" in verbe:
            cibles = _presentes(_candidats(entites, verbe["cible"]), verbe.get("cible_ou"), situation)
        outils = [None]
        if "outil" in verbe:
            outils = _presentes(_candidats(entites, verbe["outil"]), verbe.get("outil_ou"), situation)
        for cible, outil in product(cibles, outils):
            if cible is not None and cible == outil:
                continue
            texte = verbe["phrase"].format(
                cible=entites[cible]["nom"] if cible else "",
                outil=entites[outil]["nom"] if outil else "",
            )
            actions.append(Action(vid, verbe["categorie"], _accorder(texte), cible, outil))
    return actions


def verifier(verbes: dict, entites: dict) -> list[str]:
    """Détecte les incohérences des données (fautes de frappe dans les tags, etc.)."""
    problemes = []
    tags_connus = {tag for e in entites.values() for tag in e["tags"]}
    for eid, entite in entites.items():
        if "nom" not in entite or "tags" not in entite:
            problemes.append(f"entité {eid} : il faut « nom » et « tags »")
    for vid, verbe in verbes.items():
        for champ in ("categorie", "phrase"):
            if champ not in verbe:
                problemes.append(f"verbe {vid} : champ « {champ} » manquant")
        phrase = verbe.get("phrase", "")
        for role in ("cible", "outil"):
            if ("{" + role + "}" in phrase) != (role in verbe):
                problemes.append(f"verbe {vid} : « {{{role}}} » dans la phrase ≠ champ « {role} »")
            for tag in verbe.get(role, []):
                if tag not in tags_connus:
                    problemes.append(f"verbe {vid} : le tag « {tag} » ({role}) n'est porté par aucune entité")
            emplacement = verbe.get(role + "_ou")
            if emplacement is not None and emplacement not in EMPLACEMENTS:
                problemes.append(f"verbe {vid} : « {role}_ou » doit valoir inventaire ou proximite")
    return problemes


def en_markdown(actions: list[Action], titre: str, sous_titre: str = "") -> str:
    par_categorie: dict[str, list[Action]] = {}
    for action in actions:
        par_categorie.setdefault(action.categorie, []).append(action)
    lignes = [f"# {titre}", ""]
    if sous_titre:
        lignes += [sous_titre, ""]
    for categorie, groupe in par_categorie.items():
        lignes += [f"## {categorie} ({len(groupe)})", ""]
        lignes += [f"- {a.texte}" for a in groupe]
        lignes.append("")
    return "\n".join(lignes)


def resume(actions: list[Action]) -> str:
    compte: dict[str, int] = {}
    for action in actions:
        compte[action.categorie] = compte.get(action.categorie, 0) + 1
    largeur = max((len(c) for c in compte), default=0)
    lignes = [f"{c.ljust(largeur)}  {n:>5}" for c, n in compte.items()]
    lignes.append(f"{'TOTAL'.ljust(largeur)}  {len(actions):>5}")
    return "\n".join(lignes)
