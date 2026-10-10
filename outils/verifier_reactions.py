#!/usr/bin/env python3
"""Vérifie les fichiers de réactions d'une ville (data/reactions/<id>.json).

    python3 outils/verifier_reactions.py --a-faire sherif_malloy   # ce qu'il faut écrire pour cette entité
    python3 outils/verifier_reactions.py sherif_malloy adjoint      # vérifie ces fichiers
    python3 outils/verifier_reactions.py --creation sherif_malloy   # idem, en exigeant de nouveaux verbes
    python3 outils/verifier_reactions.py                            # vérifie tous les fichiers présents
    python3 outils/verifier_reactions.py --couverture               # entités sans fichier ou clés manquantes
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulation.catalogue import charger, verifier  # noqa: E402
from simulation.ville import (  # noqa: E402
    CONDITIONS_SI,
    DOSSIER_REACTIONS,
    EFFETS_NUMERIQUES,
    ETATS_CHOSES,
    ETATS_VIVANTS,
    actions_ville,
    charger_ville,
    cles_reactions,
    entites_jouables,
)

CLES_FICHIER = {
    "id", "description", "personnalite", "routine", "repliques",
    "reactions", "nouveaux_verbes", "nouveaux_tags",
}
MIN_VARIANTES = 2
MIN_NOUVEAUX_VERBES = {"habitant": 4, "animal": 2, "objet": 2, "batiment": 2}
MIN_REPLIQUES = {"habitant": 3, "animal": 2}
CATEGORIE_METIERS = "Métiers & services"
FORMAT_ID = re.compile(r"^[a-z][a-z0-9_]*$")


def contexte(eid: str, donnees: dict | None, ville: dict, verbes: dict, base: dict):
    """Ville et verbes vus par cette entité : données de base + ses propres ajouts."""
    ville = copy.deepcopy(ville)
    verbes = dict(verbes)
    if donnees:
        verbes.update(donnees.get("nouveaux_verbes", {}))
        tags = ville["entites"][eid]["tags"]
        tags += [t for t in donnees.get("nouveaux_tags", []) if t not in tags]
    cles = cles_reactions(eid, actions_ville(ville, verbes, base))
    return ville, verbes, cles


def verifier_variante(cle: str, i: int, variante, vivant: bool, emplacements: set[str]) -> list[str]:
    ou = f"reactions.{cle}[{i}]"
    if not isinstance(variante, dict):
        return [f"{ou} : doit être un objet"]
    erreurs = []
    inconnues = set(variante) - {"texte", "si", "effets"}
    if inconnues:
        erreurs.append(f"{ou} : clés inconnues {sorted(inconnues)}")
    texte = variante.get("texte")
    if not isinstance(texte, str) or len(texte.strip()) < 15:
        erreurs.append(f"{ou} : « texte » manquant ou trop court")
    else:
        for nom in set(re.findall(r"\{(\w*)\}", texte)) - emplacements:
            permis = ", ".join("{" + e + "}" for e in sorted(emplacements)) or "aucun"
            erreurs.append(f"{ou} : « {{{nom}}} » interdit ici (permis : {permis})")
    si = variante.get("si", [])
    if not isinstance(si, list) or not set(si) <= CONDITIONS_SI:
        erreurs.append(f"{ou} : « si » doit être une liste parmi {sorted(CONDITIONS_SI)}")
    effets = variante.get("effets", {})
    if not isinstance(effets, dict):
        return erreurs + [f"{ou} : « effets » doit être un objet"]
    for nom, valeur in effets.items():
        if nom == "etat":
            permis = ETATS_VIVANTS if vivant else ETATS_CHOSES
            if valeur not in permis:
                erreurs.append(f"{ou} : etat « {valeur} » impossible ici (permis : {sorted(permis)})")
        elif nom in EFFETS_NUMERIQUES:
            if not isinstance(valeur, int) or isinstance(valeur, bool):
                erreurs.append(f"{ou} : l'effet « {nom} » doit être un entier")
        else:
            erreurs.append(f"{ou} : effet inconnu « {nom} »")
    return erreurs


def verifier_routine(routine, lieux: dict) -> list[str]:
    if not isinstance(routine, list) or not routine:
        return ["« routine » doit être une liste non vide"]
    erreurs = []
    heure = 0
    for i, creneau in enumerate(routine):
        if not isinstance(creneau, dict) or set(creneau) != {"de", "a", "lieu", "activite"}:
            erreurs.append(f"routine[{i}] : il faut exactement de, a, lieu, activite")
            continue
        if creneau["de"] != heure:
            erreurs.append(f"routine[{i}] : commence à {creneau['de']}h au lieu de {heure}h")
        if not isinstance(creneau["a"], int) or not creneau["de"] < creneau["a"] <= 24:
            erreurs.append(f"routine[{i}] : « a » doit être un entier entre {creneau['de'] + 1} et 24")
        if creneau["lieu"] not in lieux:
            erreurs.append(f"routine[{i}] : lieu inconnu « {creneau['lieu']} »")
        heure = creneau["a"] if isinstance(creneau["a"], int) else heure
    if heure != 24:
        erreurs.append("routine : doit couvrir la journée de 0h à 24h sans trou")
    return erreurs


def verifier_fichier(eid: str, ville: dict, verbes: dict, base: dict, creation: bool = False) -> list[str]:
    chemin = DOSSIER_REACTIONS / f"{eid}.json"
    if eid not in ville["entites"]:
        return [f"« {eid} » n'est pas une entité de la ville"]
    if not chemin.exists():
        return [f"{chemin} n'existe pas"]
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erreur:
        return [f"JSON invalide : {erreur}"]

    entite = ville["entites"][eid]
    categorie = entite["categorie"]
    vivant = "vivant" in entite["tags"]
    erreurs = []

    inconnues = set(donnees) - CLES_FICHIER
    if inconnues:
        erreurs.append(f"clés inconnues {sorted(inconnues)}")
    if donnees.get("id") != eid:
        erreurs.append(f"« id » doit valoir « {eid} »")
    if not isinstance(donnees.get("description"), str) or len(donnees["description"]) < 40:
        erreurs.append("« description » manquante ou trop courte")
    if categorie in ("habitant", "animal") and not donnees.get("personnalite"):
        erreurs.append("« personnalite » manquante")
    if categorie in MIN_REPLIQUES:
        repliques = donnees.get("repliques", [])
        if not isinstance(repliques, list) or len(repliques) < MIN_REPLIQUES[categorie]:
            erreurs.append(f"il faut au moins {MIN_REPLIQUES[categorie]} « repliques »")
    if categorie == "habitant" or "routine" in donnees:
        erreurs += verifier_routine(donnees.get("routine"), ville["lieux"])

    nouveaux_tags = donnees.get("nouveaux_tags", [])
    for tag in nouveaux_tags:
        if not isinstance(tag, str) or not FORMAT_ID.match(tag):
            erreurs.append(f"nouveau tag invalide « {tag} » (minuscules, chiffres, _)")
    nouveaux_verbes = donnees.get("nouveaux_verbes", {})
    for vid in nouveaux_verbes:
        if not FORMAT_ID.match(vid):
            erreurs.append(f"identifiant de verbe invalide « {vid} »")
        elif vid in verbes:
            erreurs.append(f"le verbe « {vid} » existe déjà : choisis un autre identifiant")
    minimum = MIN_NOUVEAUX_VERBES[categorie]
    if creation and len(nouveaux_verbes) < minimum:
        erreurs.append(f"il faut au moins {minimum} « nouveaux_verbes » (il y en a {len(nouveaux_verbes)})")

    ville_e, verbes_e, cles = contexte(eid, donnees, ville, verbes, base)
    categories = {v["categorie"] for v in verbes.values()} | {CATEGORIE_METIERS}
    for vid, verbe in nouveaux_verbes.items():
        if verbe.get("categorie") not in categories:
            erreurs.append(f"nouveau verbe {vid} : catégorie parmi {sorted(categories)}")
        if vid not in cles and vid + "@outil" not in cles:
            erreurs.append(
                f"nouveau verbe {vid} : ne s'applique pas à {eid} "
                "(ajoute le tag exigé dans « nouveaux_tags », et vérifie que l'outil existe)"
            )
    problemes = verifier(verbes_e, entites_jouables(ville_e, base))
    erreurs += [p for p in problemes if any(f"verbe {vid} " in p for vid in nouveaux_verbes)]

    reactions = donnees.get("reactions", {})
    if not isinstance(reactions, dict):
        return erreurs + ["« reactions » doit être un objet"]
    for cle in sorted(set(reactions) - set(cles)):
        erreurs.append(f"réaction « {cle} » : ce verbe ne s'applique pas à {eid}")
    for cle in sorted(set(cles) - set(reactions)):
        erreurs.append(f"réaction manquante pour « {cle} » (ex. « {cles[cle][0].texte} »)")
    for cle, variantes in reactions.items():
        if not isinstance(variantes, list) or len(variantes) < MIN_VARIANTES:
            erreurs.append(f"reactions.{cle} : il faut au moins {MIN_VARIANTES} variantes")
            continue
        if all(v.get("si") for v in variantes if isinstance(v, dict)):
            erreurs.append(f"reactions.{cle} : il faut au moins une variante sans « si »")
        verbe = verbes_e.get(cle.removesuffix("@outil"), {})
        emplacements = {"cible", "outil"} & set(verbe)
        for i, variante in enumerate(variantes):
            erreurs += verifier_variante(cle, i, variante, vivant, emplacements)
    return erreurs


def a_faire(eid: str, ville: dict, verbes: dict, base: dict) -> str:
    entite = ville["entites"][eid]
    chemin = DOSSIER_REACTIONS / f"{eid}.json"
    donnees = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else None
    _, _, cles = contexte(eid, donnees, ville, verbes, base)
    lignes = [
        f"ENTITÉ  {eid} — {entite['nom']} ({entite['categorie']}"
        + (f", métier : {entite['metier']}" if "metier" in entite else "") + ")",
        f"LIEU    {entite['lieu']} ({ville['lieux'][entite['lieu']]['nom']})",
        f"TAGS    {', '.join(entite['tags'])}",
        f"FICHIER {chemin}",
        "",
        f"CLÉS DE « reactions » À ÉCRIRE ({len(cles)}) — au moins {MIN_VARIANTES} variantes chacune :",
    ]
    for cle in sorted(cles):
        exemples = cles[cle]
        suite = f"  (+{len(exemples) - 1} variante(s) d'outil/cible)" if len(exemples) > 1 else ""
        lignes.append(f"  {cle:<26} ex. « {exemples[0].texte} »{suite}")
    lignes += [
        "",
        f"NOUVEAUX VERBES : au moins {MIN_NOUVEAUX_VERBES[entite['categorie']]}",
        f"CONDITIONS « si » : {', '.join(sorted(CONDITIONS_SI))}",
        f"EFFETS numériques : {', '.join(sorted(EFFETS_NUMERIQUES))} ; "
        f"« etat » : {', '.join(sorted(ETATS_VIVANTS if 'vivant' in entite['tags'] else ETATS_CHOSES))}",
        f"LIEUX (routine) : {', '.join(ville['lieux'])}",
    ]
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ids", nargs="*", help="entités à vérifier (par défaut : tous les fichiers présents)")
    parser.add_argument("--a-faire", metavar="ID", help="afficher le travail attendu pour une entité")
    parser.add_argument("--couverture", action="store_true", help="lister les entités sans fichier")
    parser.add_argument("--creation", action="store_true", help="exiger le minimum de nouveaux verbes")
    args = parser.parse_args(argv)

    verbes, base = charger()
    ville = charger_ville()

    if args.a_faire:
        if args.a_faire not in ville["entites"]:
            parser.error(f"entité inconnue : {args.a_faire}")
        print(a_faire(args.a_faire, ville, verbes, base))
        return 0

    if args.couverture:
        manquants = [eid for eid in ville["entites"] if not (DOSSIER_REACTIONS / f"{eid}.json").exists()]
        print(f"{len(ville['entites']) - len(manquants)}/{len(ville['entites'])} entités ont un fichier.")
        for eid in manquants:
            print(f"  sans fichier : {eid}")
        return 1 if manquants else 0

    ids = args.ids or sorted(p.stem for p in DOSSIER_REACTIONS.glob("*.json"))
    total_erreurs = 0
    for eid in ids:
        erreurs = verifier_fichier(eid, ville, verbes, base, args.creation)
        if erreurs:
            total_erreurs += len(erreurs)
            print(f"✗ {eid} : {len(erreurs)} erreur(s)")
            for erreur in erreurs:
                print(f"    - {erreur}")
        else:
            donnees = json.loads((DOSSIER_REACTIONS / f"{eid}.json").read_text(encoding="utf-8"))
            nb = sum(len(v) for v in donnees["reactions"].values())
            print(f"✓ {eid} : {len(donnees['reactions'])} clés, {nb} variantes, "
                  f"{len(donnees.get('nouveaux_verbes', {}))} nouveaux verbes")
    return 1 if total_erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
