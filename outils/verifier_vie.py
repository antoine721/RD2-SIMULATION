#!/usr/bin/env python3
"""Vérifie la « vie » de la ville : événements, témoins et actions du joueur seul.

    python3 outils/verifier_vie.py evenements [fichier ...]   # data/evenements/*.json
    python3 outils/verifier_vie.py temoins [fichier ...]      # data/temoins/*.json
    python3 outils/verifier_vie.py joueur                     # data/joueur.json
    python3 outils/verifier_vie.py joueur --a-faire           # clés à écrire pour le joueur
    python3 outils/verifier_vie.py drapeaux                   # drapeaux posés / attendus
    python3 outils/verifier_vie.py propositions               # data/verbes_proposes.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulation.catalogue import charger, verifier  # noqa: E402
from simulation.ville import (  # noqa: E402
    CATEGORIES_TEMOIN,
    CONDITIONS_MONDE,
    DOSSIER_EVENEMENTS,
    DOSSIER_REACTIONS,
    DOSSIER_TEMOINS,
    EFFETS_JOUEUR,
    ETATS_CHOSES,
    ETATS_VIVANTS,
    FICHIER_JOUEUR,
    JOURS,
    METEOS,
    actions_joueur,
    actions_ville,
    charger_dossier,
    charger_ville,
    entites_jouables,
)

FORMAT_ID = re.compile(r"^[a-z][a-z0-9_]*$")
PREFIXES_ENTITE = {"ami", "hostile", "mort", "vivant", "present"}
CLES_EVENEMENT = {
    "titre", "texte", "lieu", "acteurs", "heures", "jours", "meteo", "si", "drapeaux",
    "chance", "unique", "apres", "consequences", "choix",
}
MIN_LIGNES_TEMOIN = {"habitant": 3, "animal": 2}
CATEGORIE_METIERS = "Métiers & services"


def _lire(chemin: Path):
    try:
        return json.loads(chemin.read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError) as erreur:
        return None, f"{chemin.name} : illisible ({erreur})"


def tous_les_verbes(verbes: dict) -> dict:
    """Verbes de base + verbes inventés pas encore intégrés."""
    tous = dict(verbes)
    for donnees in charger_dossier(DOSSIER_REACTIONS).values():
        tous.update(donnees.get("nouveaux_verbes", {}))
    if FICHIER_JOUEUR.exists():
        donnees, _ = _lire(FICHIER_JOUEUR)
        tous.update((donnees or {}).get("nouveaux_verbes", {}))
    return tous


def verifier_condition(c, ville: dict, ou: str) -> list[str]:
    if not isinstance(c, str):
        return [f"{ou} : condition invalide {c!r}"]
    if ":" in c:
        prefixe, cible = c.split(":", 1)
        if prefixe not in PREFIXES_ENTITE:
            return [f"{ou} : préfixe « {prefixe} » inconnu (permis : {sorted(PREFIXES_ENTITE)})"]
        if prefixe == "present":
            return [] if cible in ville["lieux"] else [f"{ou} : lieu inconnu « {cible} »"]
        return [] if cible in ville["entites"] else [f"{ou} : entité inconnue « {cible} »"]
    if c not in CONDITIONS_MONDE:
        return [f"{ou} : condition « {c} » inconnue (permis : {sorted(CONDITIONS_MONDE)} ou préfixe:id)"]
    return []


def verifier_effets_joueur(effets, ou: str) -> list[str]:
    if not isinstance(effets, dict):
        return [f"{ou} : « effets » doit être un objet"]
    erreurs = []
    for nom, valeur in effets.items():
        if nom not in EFFETS_JOUEUR:
            erreurs.append(f"{ou} : effet « {nom} » inconnu (permis : {sorted(EFFETS_JOUEUR)})")
        elif not isinstance(valeur, int) or isinstance(valeur, bool):
            erreurs.append(f"{ou} : l'effet « {nom} » doit être un entier")
    return erreurs


def verifier_consequences(cons, ville: dict, ou: str) -> tuple[list[str], set[str]]:
    """Renvoie (erreurs, drapeaux posés)."""
    if not isinstance(cons, dict):
        return [f"{ou} : « consequences » doit être un objet"], set()
    erreurs, poses = [], set()
    inconnues = set(cons) - {"drapeaux", "entites", "joueur"}
    if inconnues:
        erreurs.append(f"{ou} : clés inconnues {sorted(inconnues)}")
    for d in cons.get("drapeaux", []):
        if not isinstance(d, str) or d[:1] not in "+-" or not FORMAT_ID.match(d[1:]):
            erreurs.append(f"{ou} : drapeau « {d} » doit s'écrire +nom ou -nom")
        elif d[0] == "+":
            poses.add(d[1:])
    for eid, changement in cons.get("entites", {}).items():
        if eid not in ville["entites"]:
            erreurs.append(f"{ou} : entité inconnue « {eid} »")
            continue
        vivant = "vivant" in ville["entites"][eid]["tags"]
        for cle, valeur in changement.items():
            if cle == "etat" and valeur not in (ETATS_VIVANTS if vivant else ETATS_CHOSES):
                erreurs.append(f"{ou} : état « {valeur} » impossible pour {eid}")
            elif cle == "relation" and not isinstance(valeur, int):
                erreurs.append(f"{ou} : relation de {eid} doit être un entier")
            elif cle == "lieu" and valeur is not None and valeur not in ville["lieux"]:
                erreurs.append(f"{ou} : lieu inconnu « {valeur} » pour {eid}")
            elif cle not in ("etat", "relation", "lieu"):
                erreurs.append(f"{ou} : changement « {cle} » inconnu pour {eid} (etat, relation, lieu)")
    erreurs += verifier_effets_joueur(cons.get("joueur", {}), ou + ".joueur")
    return erreurs, poses


def verifier_evenement(eid: str, ev, ville: dict, verbes: dict) -> tuple[list[str], set[str], set[str]]:
    """Renvoie (erreurs, drapeaux posés, drapeaux attendus)."""
    ou = f"evenements.{eid}"
    if not FORMAT_ID.match(eid):
        return [f"{ou} : identifiant invalide"], set(), set()
    if not isinstance(ev, dict):
        return [f"{ou} : doit être un objet"], set(), set()
    erreurs, poses, attendus = [], set(), set()
    inconnues = set(ev) - CLES_EVENEMENT
    if inconnues:
        erreurs.append(f"{ou} : clés inconnues {sorted(inconnues)}")
    if not isinstance(ev.get("titre"), str) or not 3 <= len(ev["titre"]) <= 70:
        erreurs.append(f"{ou} : « titre » de 3 à 70 caractères")
    if not isinstance(ev.get("texte"), str) or len(ev["texte"]) < 60:
        erreurs.append(f"{ou} : « texte » manquant ou trop court (60 caractères minimum)")
    if ev.get("lieu") not in ville["lieux"]:
        erreurs.append(f"{ou} : « lieu » inconnu")
    for a in ev.get("acteurs", []):
        if a not in ville["entites"]:
            erreurs.append(f"{ou} : acteur inconnu « {a} »")
    heures = ev.get("heures")
    if heures is not None and not (
        isinstance(heures, list) and len(heures) == 2 and all(isinstance(x, int) and 0 <= x <= 24 for x in heures)
        and heures[0] != heures[1]
    ):
        erreurs.append(f"{ou} : « heures » = [de, a] entre 0 et 24 (a < de traverse minuit)")
    for j in ev.get("jours", []):
        if j not in JOURS:
            erreurs.append(f"{ou} : jour inconnu « {j} »")
    for m in ev.get("meteo", []):
        if m not in METEOS:
            erreurs.append(f"{ou} : météo inconnue « {m} » (permis : {sorted(METEOS)})")
    for c in ev.get("si", []):
        erreurs += verifier_condition(c, ville, ou + ".si")
    for d in ev.get("drapeaux", []):
        nom = d.lstrip("!") if isinstance(d, str) else ""
        if not FORMAT_ID.match(nom):
            erreurs.append(f"{ou} : drapeau attendu « {d} » invalide")
        elif not d.startswith("!"):
            attendus.add(nom)
    chance = ev.get("chance")
    if not isinstance(chance, (int, float)) or not 0 < chance <= 1:
        erreurs.append(f"{ou} : « chance » doit être entre 0 (exclu) et 1")
    if "unique" in ev and not isinstance(ev["unique"], bool):
        erreurs.append(f"{ou} : « unique » doit être true ou false")
    apres = ev.get("apres")
    if apres is not None:
        if not isinstance(apres, dict) or not apres.get("verbes"):
            erreurs.append(f"{ou} : « apres » = {{\"verbes\": [...], \"cibles\": [...]}}")
        else:
            for v in apres["verbes"]:
                if v not in verbes:
                    erreurs.append(f"{ou} : « apres » cite un verbe inconnu « {v} »")
            for c in apres.get("cibles", []):
                if c not in ville["entites"]:
                    erreurs.append(f"{ou} : « apres » cite une cible inconnue « {c} »")
    if "consequences" in ev:
        e, p = verifier_consequences(ev["consequences"], ville, ou + ".consequences")
        erreurs += e
        poses |= p
    choix = ev.get("choix", [])
    if choix and len(choix) < 2:
        erreurs.append(f"{ou} : s'il y a des choix, il en faut au moins 2")
    for i, c in enumerate(choix):
        oc = f"{ou}.choix[{i}]"
        if not isinstance(c, dict):
            erreurs.append(f"{oc} : doit être un objet")
            continue
        inconnues = set(c) - {"texte", "resultat", "si", "effets", "consequences"}
        if inconnues:
            erreurs.append(f"{oc} : clés inconnues {sorted(inconnues)}")
        if not isinstance(c.get("texte"), str) or not 3 <= len(c["texte"]) <= 90:
            erreurs.append(f"{oc} : « texte » (le bouton) de 3 à 90 caractères")
        if not isinstance(c.get("resultat"), str) or len(c["resultat"]) < 30:
            erreurs.append(f"{oc} : « resultat » manquant ou trop court")
        for cond in c.get("si", []):
            erreurs += verifier_condition(cond, ville, oc + ".si")
        erreurs += verifier_effets_joueur(c.get("effets", {}), oc)
        if "consequences" in c:
            e, p = verifier_consequences(c["consequences"], ville, oc + ".consequences")
            erreurs += e
            poses |= p
    return erreurs, poses, attendus


def verifier_fichier_evenements(chemin: Path, ville: dict, verbes: dict, ids_vus: dict) -> list[str]:
    donnees, erreur = _lire(chemin)
    if erreur:
        return [erreur]
    if set(donnees) != {"theme", "evenements"} or not isinstance(donnees.get("evenements"), dict):
        return ["le fichier doit contenir exactement « theme » et « evenements »"]
    erreurs, poses, attendus = [], set(), set()
    for eid, ev in donnees["evenements"].items():
        if eid in ids_vus and ids_vus[eid] != chemin.name:
            erreurs.append(f"evenements.{eid} : identifiant déjà utilisé dans {ids_vus[eid]}")
        ids_vus[eid] = chemin.name
        e, p, a = verifier_evenement(eid, ev, ville, verbes)
        erreurs += e
        poses |= p
        attendus |= a
    for d in sorted(attendus - poses):
        erreurs.append(f"le drapeau « {d} » est attendu mais aucun événement de ce fichier ne le pose")
    return erreurs


def verifier_fichier_temoins(chemin: Path, ville: dict, deja: dict) -> list[str]:
    donnees, erreur = _lire(chemin)
    if erreur:
        return [erreur]
    erreurs = []
    for eid, lignes in donnees.items():
        entite = ville["entites"].get(eid)
        if not entite or entite["categorie"] not in MIN_LIGNES_TEMOIN:
            erreurs.append(f"{eid} : doit être un habitant ou un animal de la ville")
            continue
        if eid in deja and deja[eid] != chemin.name:
            erreurs.append(f"{eid} : déjà décrit dans {deja[eid]}")
        deja[eid] = chemin.name
        if not isinstance(lignes, dict) or set(lignes) != set(CATEGORIES_TEMOIN):
            erreurs.append(f"{eid} : il faut exactement les catégories {CATEGORIES_TEMOIN}")
            continue
        minimum = MIN_LIGNES_TEMOIN[entite["categorie"]]
        for cat, liste in lignes.items():
            if not isinstance(liste, list) or len(liste) < minimum:
                erreurs.append(f"{eid}.{cat} : au moins {minimum} répliques")
                continue
            for i, ligne in enumerate(liste):
                if not isinstance(ligne, str) or not 8 <= len(ligne) <= 160:
                    erreurs.append(f"{eid}.{cat}[{i}] : réplique de 8 à 160 caractères")
    return erreurs


def cles_joueur(ville: dict, verbes: dict, base: dict, donnees: dict | None) -> dict:
    verbes = dict(verbes)
    if donnees:
        verbes.update(donnees.get("nouveaux_verbes", {}))
    cles: dict[str, list] = {}
    for a in actions_joueur(ville, verbes, base):
        cles.setdefault(a.verbe, []).append(a)
    return cles


def verifier_joueur(ville: dict, verbes: dict, base: dict) -> list[str]:
    if not FICHIER_JOUEUR.exists():
        return [f"{FICHIER_JOUEUR} n'existe pas"]
    donnees, erreur = _lire(FICHIER_JOUEUR)
    if erreur:
        return [erreur]
    erreurs = []
    inconnues = set(donnees) - {"description", "reactions", "nouveaux_verbes"}
    if inconnues:
        erreurs.append(f"clés inconnues {sorted(inconnues)}")
    nouveaux = donnees.get("nouveaux_verbes", {})
    for vid in nouveaux:
        if not FORMAT_ID.match(vid) or vid in verbes:
            erreurs.append(f"nouveau verbe « {vid} » : identifiant invalide ou déjà pris")
    tous = {**verbes, **nouveaux}
    categories = {v["categorie"] for v in verbes.values()} | {CATEGORIE_METIERS}
    for vid, v in nouveaux.items():
        if v.get("categorie") not in categories:
            erreurs.append(f"nouveau verbe {vid} : catégorie parmi {sorted(categories)}")
    erreurs += [p for p in verifier(tous, {**base, **entites_jouables(ville, base)}) if any(f"verbe {v} " in p for v in nouveaux)]
    cles = cles_joueur(ville, verbes, base, donnees)
    for vid in nouveaux:
        if vid not in cles:
            erreurs.append(f"nouveau verbe {vid} : ne s'applique pas au joueur seul (pas de cible, ou une cible de l'inventaire)")
    reactions = donnees.get("reactions", {})
    for cle in sorted(set(cles) - set(reactions)):
        erreurs.append(f"réaction manquante pour « {cle} » (ex. « {cles[cle][0].texte} »)")
    for cle in sorted(set(reactions) - set(cles)):
        erreurs.append(f"réaction « {cle} » : ce verbe ne concerne pas le joueur seul")
    for cle, variantes in reactions.items():
        if not isinstance(variantes, list) or len(variantes) < 3:
            erreurs.append(f"reactions.{cle} : au moins 3 variantes")
            continue
        if all(v.get("si") for v in variantes if isinstance(v, dict)):
            erreurs.append(f"reactions.{cle} : au moins une variante sans « si »")
        emplacements = {"cible", "outil"} & set(tous.get(cle, {}))
        for i, v in enumerate(variantes):
            ou = f"reactions.{cle}[{i}]"
            if not isinstance(v, dict) or not isinstance(v.get("texte"), str) or len(v["texte"]) < 15:
                erreurs.append(f"{ou} : « texte » manquant ou trop court")
                continue
            if set(v) - {"texte", "si", "effets"}:
                erreurs.append(f"{ou} : clés inconnues")
            for nom in set(re.findall(r"\{(\w*)\}", v["texte"])) - emplacements:
                erreurs.append(f"{ou} : « {{{nom}}} » interdit ici")
            for c in v.get("si", []):
                if c not in CONDITIONS_MONDE:
                    erreurs.append(f"{ou} : condition « {c} » inconnue")
            erreurs += verifier_effets_joueur(v.get("effets", {}), ou)
    if len(nouveaux) < 15:
        erreurs.append(f"au moins 15 « nouveaux_verbes » pour le joueur (il y en a {len(nouveaux)})")
    return erreurs


FICHIER_PROPOSITIONS = FICHIER_JOUEUR.parent / "verbes_proposes.json"


def verifier_propositions(ville: dict, verbes: dict, base: dict) -> list[str]:
    """Verbes universels proposés : ils doivent valoir pour plusieurs entités de la ville."""
    donnees, erreur = _lire(FICHIER_PROPOSITIONS)
    if erreur:
        return [erreur]
    ville = json.loads(json.dumps(ville))
    for eid, reac in charger_dossier(DOSSIER_REACTIONS).items():
        if eid in ville["entites"]:
            ville["entites"][eid]["tags"] += reac.get("nouveaux_tags", [])
    existants = tous_les_verbes(verbes)
    categories = {v["categorie"] for v in verbes.values()} | {CATEGORIE_METIERS}
    erreurs = []
    for vid, v in donnees.items():
        if not FORMAT_ID.match(vid) or vid in existants:
            erreurs.append(f"{vid} : identifiant invalide ou déjà pris")
        if v.get("categorie") not in categories:
            erreurs.append(f"{vid} : catégorie parmi {sorted(categories)}")
    entites = {**base, **entites_jouables(ville, base)}
    erreurs += [p for p in verifier({**verbes, **donnees}, entites) if any(f"verbe {v} " in p for v in donnees)]
    actions = actions_ville(ville, {**verbes, **donnees}, base)
    portee = {}
    for a in actions:
        if a.verbe in donnees:
            portee.setdefault(a.verbe, set()).update(x for x in (a.cible, a.outil) if x in ville["entites"])
    for vid in donnees:
        if len(portee.get(vid, ())) < 2:
            erreurs.append(f"{vid} : doit s'appliquer à au moins 2 entités de la ville (ici {len(portee.get(vid, ()))})")
    return erreurs


def bilan_drapeaux() -> str:
    poses, attendus = {}, {}
    for nom, donnees in charger_dossier(DOSSIER_EVENEMENTS).items():
        for eid, ev in donnees.get("evenements", {}).items():
            for d in ev.get("drapeaux", []):
                attendus.setdefault(d.lstrip("!"), set()).add(f"{nom}/{eid}")
            sources = [ev.get("consequences", {})] + [c.get("consequences", {}) for c in ev.get("choix", [])]
            for cons in sources:
                for d in cons.get("drapeaux", []):
                    if d.startswith("+"):
                        poses.setdefault(d[1:], set()).add(f"{nom}/{eid}")
    lignes = []
    for d in sorted(set(poses) | set(attendus)):
        etat = "OK" if d in poses else "JAMAIS POSÉ"
        lignes.append(f"{d:<32} {etat:<12} posé par {len(poses.get(d, []))}, attendu par {len(attendus.get(d, []))}")
    return "\n".join(lignes) or "aucun drapeau"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("quoi", choices=["evenements", "temoins", "joueur", "drapeaux", "propositions"])
    parser.add_argument("fichiers", nargs="*", type=Path)
    parser.add_argument("--a-faire", action="store_true", help="(joueur) lister les clés à écrire")
    args = parser.parse_args(argv)

    verbes, base = charger()
    ville = charger_ville()

    if args.quoi == "drapeaux":
        print(bilan_drapeaux())
        return 0
    if args.quoi == "propositions":
        erreurs = verifier_propositions(ville, verbes, base)
        if not erreurs:
            print(f"✓ {len(_lire(FICHIER_PROPOSITIONS)[0])} verbes proposés")
        for e in erreurs:
            print(f"    - {e}")
        return 1 if erreurs else 0
    if args.quoi == "joueur":
        if args.a_faire:
            donnees = _lire(FICHIER_JOUEUR)[0] if FICHIER_JOUEUR.exists() else None
            for cle, actions in sorted(cles_joueur(ville, verbes, base, donnees).items()):
                print(f"  {cle:<24} ex. « {actions[0].texte} »")
            print(f"\nInventaire : {', '.join(ville['inventaire_depart'])}")
            print(f"Conditions « si » : {', '.join(sorted(CONDITIONS_MONDE))}")
            return 0
        erreurs = verifier_joueur(ville, verbes, base)
        print("✓ joueur" if not erreurs else "✗ joueur :\n" + "\n".join(f"    - {e}" for e in erreurs))
        return 1 if erreurs else 0

    dossier = DOSSIER_EVENEMENTS if args.quoi == "evenements" else DOSSIER_TEMOINS
    tous_fichiers = sorted(dossier.glob("*.json"))
    fichiers = args.fichiers or tous_fichiers
    verbes_connus = tous_les_verbes(verbes)
    vus: dict = {}
    # Les autres fichiers servent à détecter les doublons d'identifiants.
    for autre in tous_fichiers:
        if autre not in [Path(f).resolve() for f in fichiers]:
            donnees, _ = _lire(autre)
            cles = (donnees or {}).get("evenements", {}) if args.quoi == "evenements" else (donnees or {})
            for cle in cles:
                vus.setdefault(cle, autre.name)
    total = 0
    for chemin in fichiers:
        chemin = Path(chemin).resolve()
        if args.quoi == "evenements":
            erreurs = verifier_fichier_evenements(chemin, ville, verbes_connus, vus)
        else:
            erreurs = verifier_fichier_temoins(chemin, ville, vus)
        total += len(erreurs)
        if erreurs:
            print(f"✗ {chemin.name} : {len(erreurs)} erreur(s)")
            for e in erreurs:
                print(f"    - {e}")
        else:
            donnees, _ = _lire(chemin)
            n = len(donnees["evenements"]) if args.quoi == "evenements" else len(donnees)
            print(f"✓ {chemin.name} : {n} {'événements' if args.quoi == 'evenements' else 'entités'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
