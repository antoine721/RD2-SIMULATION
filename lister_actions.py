#!/usr/bin/env python3
"""Liste toutes les actions possibles dans la simulation.

Exemples :
    python3 lister_actions.py                                # catalogue complet
    python3 lister_actions.py --resume                       # nombre d'actions par catégorie
    python3 lister_actions.py --entite ton_cheval            # tout ce qu'on peut faire avec une entité
    python3 lister_actions.py --situation situations/camp.json   # ce qui est possible maintenant
    python3 lister_actions.py --sortie catalogue_actions.md  # écrire dans un fichier
"""

import argparse
import sys
from pathlib import Path

from simulation.catalogue import charger, charger_situation, en_markdown, generer, resume, verifier


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Liste toutes les actions possibles.")
    parser.add_argument("--situation", type=Path, help="fichier JSON décrivant l'état du monde")
    parser.add_argument("--entite", help="ne garder que les actions impliquant cette entité")
    parser.add_argument("--resume", action="store_true", help="afficher seulement les totaux")
    parser.add_argument("--sortie", type=Path, help="écrire le résultat dans ce fichier")
    args = parser.parse_args(argv)

    verbes, entites = charger()
    problemes = verifier(verbes, entites)
    for probleme in problemes:
        print(f"⚠ {probleme}", file=sys.stderr)
    if problemes:
        return 1

    situation = None
    titre = "Catalogue complet des actions possibles"
    if args.situation:
        try:
            situation = charger_situation(args.situation, entites)
        except ValueError as erreur:
            parser.error(str(erreur))
        titre = f"Actions possibles — {situation.get('nom', args.situation.stem)}"
    if args.entite and args.entite not in entites:
        parser.error(f"entité inconnue : {args.entite}")

    actions = generer(verbes, entites, situation)
    if args.entite:
        actions = [a for a in actions if args.entite in (a.cible, a.outil)]
        titre += f" impliquant {entites[args.entite]['nom']}"

    if args.resume:
        texte = resume(actions)
    else:
        sous_titre = (
            "> Généré automatiquement par `lister_actions.py` — ne pas modifier à la main.\n\n"
            f"**{len(actions)} actions**, calculées à partir de "
            f"{len(verbes)} verbes et {len(entites)} entités."
        )
        texte = en_markdown(actions, titre, sous_titre)

    if args.sortie:
        args.sortie.write_text(texte, encoding="utf-8")
        print(f"{len(actions)} actions écrites dans {args.sortie}")
    else:
        print(texte)
    return 0


if __name__ == "__main__":
    sys.exit(main())
