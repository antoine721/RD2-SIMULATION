#!/usr/bin/env python3
"""Construit la carte interactive de la ville : un seul fichier HTML autonome.

    python3 generer_carte.py                         # écrit carte/valentine.html
    python3 generer_carte.py --fragment chemin.html  # sans <html>/<head>, pour une publication
"""

import argparse
import json
from pathlib import Path

from simulation.catalogue import charger
from simulation.ville import (
    DOSSIER_EVENEMENTS,
    DOSSIER_TEMOINS,
    FICHIER_JOUEUR,
    JOURS,
    actions_joueur,
    actions_ville,
    charger_dossier,
    charger_reactions,
    charger_ville,
    cles_reactions,
)

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


def _groupes(cles: dict, verbes: dict) -> list[dict]:
    groupes = []
    for cle, liste in cles.items():
        verbe = verbes[cle.removesuffix("@outil")]
        groupes.append({
            "cle": cle,
            "categorie": verbe["categorie"],
            "conditions": verbe.get("conditions", []),
            "options": [{"texte": a.texte, "cible": a.cible, "outil": a.outil} for a in liste],
        })
    groupes.sort(key=lambda g: (_rang(g["categorie"]), g["options"][0]["texte"]))
    return groupes


def _joueur(ville: dict, verbes: dict, base: dict) -> dict:
    donnees = json.loads(FICHIER_JOUEUR.read_text(encoding="utf-8")) if FICHIER_JOUEUR.exists() else {}
    verbes = {**verbes, **donnees.get("nouveaux_verbes", {})}
    cles: dict = {}
    for a in actions_joueur(ville, verbes, base):
        cles.setdefault(a.verbe, []).append(a)
    return {
        "description": donnees.get("description", "Un voyageur armé, de passage à Valentine."),
        "actions": _groupes(cles, verbes),
        "reactions": donnees.get("reactions", {}),
    }


def donnees_carte() -> dict:
    verbes, base = charger()
    ville = charger_ville()
    reactions = charger_reactions()
    actions = actions_ville(ville, verbes, base)

    entites = {}
    for eid, entite in ville["entites"].items():
        groupes = _groupes(cles_reactions(eid, actions), verbes)
        fiche = {"id": eid, **{k: entite[k] for k in CHAMPS_VILLE if k in entite}}
        fiche.update({k: reactions.get(eid, {}).get(k) for k in CHAMPS_REACTIONS})
        fiche["reactions"] = fiche["reactions"] or {}
        fiche["actions"] = groupes
        entites[eid] = fiche

    noms = {eid: e["nom"] for eid, e in base.items()}
    noms.update({eid: e["nom"] for eid, e in ville["entites"].items()})
    evenements = {}
    for theme in charger_dossier(DOSSIER_EVENEMENTS).values():
        for evid, ev in theme["evenements"].items():
            evenements[evid] = {"id": evid, "theme": theme["theme"], **ev}
    temoins = {}
    for groupe in charger_dossier(DOSSIER_TEMOINS).values():
        temoins.update(groupe)
    joueur = _joueur(ville, verbes, base)
    return {
        "ville": {k: ville[k] for k in ("nom", "annee", "taille")},
        "jours": JOURS,
        "lieux": ville["lieux"],
        "entites": entites,
        "noms": noms,
        "evenements": evenements,
        "temoins": temoins,
        "joueur": joueur,
        "stats": {
            "actions": sum(len(g["options"]) for e in entites.values() for g in e["actions"])
            + sum(len(g["options"]) for g in joueur["actions"]),
            "variantes": sum(len(v) for e in entites.values() for v in e["reactions"].values())
            + sum(len(v) for v in joueur["reactions"].values()),
            "evenements": len(evenements),
            "temoins": sum(len(l) for t in temoins.values() for l in t.values()),
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
