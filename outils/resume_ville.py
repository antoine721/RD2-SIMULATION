#!/usr/bin/env python3
"""Résumé de tout ce qui a déjà été écrit sur la ville (pour rester cohérent).

    python3 outils/resume_ville.py              # toutes les entités
    python3 outils/resume_ville.py veuve gamin  # seulement celles-ci
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulation.ville import charger_reactions, charger_ville  # noqa: E402


def main() -> None:
    ville = charger_ville()
    reactions = charger_reactions()
    ids = sys.argv[1:] or list(ville["entites"])
    for eid in ids:
        entite = ville["entites"][eid]
        r = reactions.get(eid)
        entete = f"## {eid} — {entite['nom']}" + (f" ({entite['metier']})" if "metier" in entite else "")
        print(entete)
        if not r:
            print("   (pas encore écrit)\n")
            continue
        print(f"   {r.get('description', '')}")
        if r.get("personnalite"):
            print(f"   Caractère : {r['personnalite']}")
        if r.get("routine"):
            print("   Journée : " + " ; ".join(f"{c['de']}-{c['a']}h {c['lieu']} ({c['activite']})" for c in r["routine"]))
        if r.get("repliques"):
            print(f"   Dit : {r['repliques'][0]}")
        print()


if __name__ == "__main__":
    main()
