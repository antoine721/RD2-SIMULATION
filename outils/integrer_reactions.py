#!/usr/bin/env python3
"""Intègre au catalogue les verbes et tags inventés dans les fichiers de réactions.

Les « nouveaux_verbes » passent dans data/verbes.json et les « nouveaux_tags »
dans data/villes/valentine.json. Ils sont ensuite retirés des fichiers de
réactions : chaque verbe n'est défini qu'à un seul endroit.

    python3 outils/integrer_reactions.py            # intègre tout
    python3 outils/integrer_reactions.py --essai    # affiche ce qui serait fait
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulation.catalogue import DOSSIER_DATA  # noqa: E402
from simulation.ville import DOSSIER_REACTIONS, VILLE_PAR_DEFAUT  # noqa: E402

FICHIER_VERBES = DOSSIER_DATA / "verbes.json"


def _objet(groupes: list[list[tuple[str, object]]], retrait: str) -> str:
    """Objet JSON compact : une entrée par ligne, une ligne vide entre les groupes."""
    cles = [cle for groupe in groupes for cle, _ in groupe]
    largeur = max(len(json.dumps(cle, ensure_ascii=False)) for cle in cles) + 1
    lignes, n = [], 0
    for i, groupe in enumerate(groupes):
        if i:
            lignes.append("")
        for cle, valeur in groupe:
            n += 1
            debut = (json.dumps(cle, ensure_ascii=False) + ":").ljust(largeur)
            fin = "," if n < len(cles) else ""
            lignes.append(f"{retrait}{debut} {json.dumps(valeur, ensure_ascii=False)}{fin}")
    return "{\n" + "\n".join(lignes) + "\n" + retrait[:-2] + "}"


def _par_categorie(entrees: dict, champ: str) -> list[list[tuple[str, object]]]:
    groupes: dict[str, list] = {}
    for cle, valeur in entrees.items():
        if not cle.startswith("_"):
            groupes.setdefault(valeur[champ], []).append((cle, valeur))
    return list(groupes.values())


def ecrire_verbes(verbes: dict, chemin: Path = FICHIER_VERBES) -> None:
    groupes = _par_categorie(verbes, "categorie")
    if "_doc" in verbes:
        groupes.insert(0, [("_doc", verbes["_doc"])])
    chemin.write_text(_objet(groupes, "  ") + "\n", encoding="utf-8")


def ecrire_ville(ville: dict, chemin: Path = VILLE_PAR_DEFAUT) -> None:
    entete = ",\n".join(
        f"  {json.dumps(cle, ensure_ascii=False)}: {json.dumps(valeur, ensure_ascii=False)}"
        for cle, valeur in ville.items()
        if cle not in ("lieux", "entites")
    )
    lieux = '  "lieux": ' + _objet([list(ville["lieux"].items())], "    ")
    entites = '  "entites": ' + _objet(_par_categorie(ville["entites"], "categorie"), "    ")
    chemin.write_text("{\n" + ",\n\n".join([entete, lieux, entites]) + "\n}\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--essai", action="store_true", help="ne rien écrire")
    args = parser.parse_args(argv)

    verbes = json.loads(FICHIER_VERBES.read_text(encoding="utf-8"))
    ville = json.loads(VILLE_PAR_DEFAUT.read_text(encoding="utf-8"))
    fichiers = sorted(DOSSIER_REACTIONS.glob("*.json"))

    conflits, ajouts_verbes, ajouts_tags, modifies = [], [], [], []
    for chemin in fichiers:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
        eid = chemin.stem
        for vid, verbe in donnees.get("nouveaux_verbes", {}).items():
            if vid in verbes and verbes[vid] != verbe:
                conflits.append(f"{eid} : le verbe « {vid} » existe déjà avec une autre définition")
            elif vid not in verbes:
                verbes[vid] = verbe
                ajouts_verbes.append(f"{vid} ({eid})")
        tags = ville["entites"][eid]["tags"]
        for tag in donnees.get("nouveaux_tags", []):
            if tag not in tags:
                tags.append(tag)
                ajouts_tags.append(f"{eid} +{tag}")
        if "nouveaux_verbes" in donnees or "nouveaux_tags" in donnees:
            modifies.append((chemin, donnees))

    if conflits:
        print("Conflits à résoudre à la main (renomme l'un des verbes) :")
        for conflit in conflits:
            print(f"  - {conflit}")
        return 1

    print(f"{len(ajouts_verbes)} verbes ajoutés, {len(ajouts_tags)} tags ajoutés, {len(modifies)} fichiers allégés.")
    if args.essai:
        return 0
    ecrire_verbes(verbes)
    ecrire_ville(ville)
    for chemin, donnees in modifies:
        donnees.pop("nouveaux_verbes", None)
        donnees.pop("nouveaux_tags", None)
        chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
