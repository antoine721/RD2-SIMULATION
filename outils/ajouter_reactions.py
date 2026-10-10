#!/usr/bin/env python3
"""Ajoute des réactions à des fichiers existants sans les réécrire à la main.

Le fichier d'ajouts a la forme { "<id>": { "<clé>": [variantes...] } }.

    python3 outils/ajouter_reactions.py ajouts.json              # ajoute les clés absentes
    python3 outils/ajouter_reactions.py ajouts.json --remplacer  # remplace aussi les clés existantes
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulation.ville import DOSSIER_REACTIONS  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ajouts", type=Path)
    parser.add_argument("--remplacer", action="store_true")
    args = parser.parse_args(argv)

    ajouts = json.loads(args.ajouts.read_text(encoding="utf-8"))
    for eid, reactions in ajouts.items():
        chemin = DOSSIER_REACTIONS / f"{eid}.json"
        if not chemin.exists():
            print(f"✗ {eid} : {chemin} n'existe pas")
            return 1
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
        existantes = donnees.setdefault("reactions", {})
        ajoutees, ignorees = 0, []
        for cle, variantes in reactions.items():
            if cle in existantes and not args.remplacer:
                ignorees.append(cle)
                continue
            existantes[cle] = variantes
            ajoutees += 1
        tmp = chemin.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, chemin)
        suite = f" ({len(ignorees)} déjà présentes, ignorées : {', '.join(ignorees)})" if ignorees else ""
        print(f"✓ {eid} : {ajoutees} clés ajoutées{suite}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
