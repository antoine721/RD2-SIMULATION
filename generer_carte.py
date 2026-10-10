#!/usr/bin/env python3
"""Construit la carte interactive de la ville : un seul fichier HTML autonome.

    python3 generer_carte.py                         # écrit carte/valentine.html
    python3 generer_carte.py --fragment chemin.html  # sans <html>/<head>, pour une publication
"""

import argparse
import json
from pathlib import Path

from simulation.catalogue import charger
from simulation.ville import actions_ville, charger_reactions, charger_ville, cles_reactions

RACINE = Path(__file__).resolve().parent
MODELE = RACINE / "carte" / "modele.html"
SORTIE = RACINE / "carte" / "valentine.html"
ORDRE_CATEGORIES = [
    "Métiers & services", "Social", "Économie & crime", "Cheval & animaux", "Survie",
    "Combat", "Déplacement", "Entretien & inventaire", "Loisirs & culture",
]
CHAMPS_VILLE = ("nom", "categorie", "lieu", "metier", "etiquette", "faction", "pos")
CHAMPS_REACTIONS = ("description", "personnalite", "repliques", "routine", "reactions")


def _rang(categorie: str) -> int:
    return ORDRE_CATEGORIES.index(categorie) if categorie in ORDRE_CATEGORIES else len(ORDRE_CATEGORIES)


def donnees_carte() -> dict:
    verbes, base = charger()
    ville = charger_ville()
    reactions = charger_reactions()
    actions = actions_ville(ville, verbes, base)

    entites = {}
    for eid, entite in ville["entites"].items():
        groupes = []
        for cle, liste in cles_reactions(eid, actions).items():
            verbe = verbes[cle.removesuffix("@outil")]
            groupes.append({
                "cle": cle,
                "categorie": verbe["categorie"],
                "conditions": verbe.get("conditions", []),
                "options": [{"texte": a.texte, "cible": a.cible, "outil": a.outil} for a in liste],
            })
        groupes.sort(key=lambda g: (_rang(g["categorie"]), g["options"][0]["texte"]))
        fiche = {"id": eid, **{k: entite[k] for k in CHAMPS_VILLE if k in entite}}
        fiche.update({k: reactions.get(eid, {}).get(k) for k in CHAMPS_REACTIONS})
        fiche["reactions"] = fiche["reactions"] or {}
        fiche["actions"] = groupes
        entites[eid] = fiche

    noms = {eid: e["nom"] for eid, e in base.items()}
    noms.update({eid: e["nom"] for eid, e in ville["entites"].items()})
    return {
        "ville": {k: ville[k] for k in ("nom", "annee", "taille")},
        "lieux": ville["lieux"],
        "entites": entites,
        "noms": noms,
        "stats": {
            "actions": sum(len(g["options"]) for e in entites.values() for g in e["actions"]),
            "variantes": sum(len(v) for e in entites.values() for v in e["reactions"].values()),
        },
    }


def fragment() -> str:
    donnees = json.dumps(donnees_carte(), ensure_ascii=False, separators=(",", ":"))
    return MODELE.read_text(encoding="utf-8").replace("__DONNEES__", donnees.replace("</", "<\\/"))


def page_complete(contenu: str) -> str:
    return (
        '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        "</head>\n<body>\n" + contenu + "\n</body>\n</html>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fragment", type=Path, help="écrire la version sans <html>/<head> dans ce fichier")
    args = parser.parse_args()
    contenu = fragment()
    if args.fragment:
        args.fragment.write_text(contenu, encoding="utf-8")
        print(f"Fragment écrit dans {args.fragment}")
    SORTIE.write_text(page_complete(contenu), encoding="utf-8")
    print(f"Carte écrite dans {SORTIE.relative_to(RACINE)} ({SORTIE.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    main()
