"""Une ville jouable : un plan, des entités placées dans des lieux, et leurs réactions.

Le joueur dispose d'un inventaire (entités génériques de data/entites.json) ;
toutes les entités de la ville sont considérées comme « à proximité ».
"""

from __future__ import annotations

import json
from pathlib import Path

from simulation.catalogue import DOSSIER_DATA, Action, generer

DOSSIER_REACTIONS = DOSSIER_DATA / "reactions"
VILLE_PAR_DEFAUT = DOSSIER_DATA / "villes" / "valentine.json"

# Vocabulaire commun aux fichiers de réactions et à la carte.
CONDITIONS_SI = {"honneur_haut", "honneur_bas", "est_recherche", "nuit", "jour", "hostile", "ami"}
EFFETS_NUMERIQUES = {"honneur", "argent", "prime", "sante", "relation"}
ETATS_VIVANTS = {"mort", "blesse", "hostile", "en_fuite", "ligote", "normal"}
ETATS_CHOSES = {"detruit", "normal"}


def charger_ville(chemin: Path = VILLE_PAR_DEFAUT) -> dict:
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def entites_jouables(ville: dict, base_entites: dict) -> dict:
    """Entités de la ville + objets de l'inventaire de départ."""
    entites = {eid: base_entites[eid] for eid in ville["inventaire_depart"]}
    entites.update(ville["entites"])
    return entites


def actions_ville(ville: dict, verbes: dict, base_entites: dict) -> list[Action]:
    situation = {
        "joueur": {},
        "inventaire": list(ville["inventaire_depart"]),
        "a_proximite": list(ville["entites"]),
    }
    return generer(verbes, entites_jouables(ville, base_entites), situation, verifier_conditions=False)


def cles_reactions(eid: str, actions: list[Action]) -> dict[str, list[Action]]:
    """Clés de réaction attendues pour une entité.

    « verbe » quand l'entité subit l'action, « verbe@outil » quand elle sert
    d'outil ou d'interlocuteur (ex. « acheter@outil » pour un marchand).
    """
    cles: dict[str, list[Action]] = {}
    for action in actions:
        if action.cible == eid:
            cles.setdefault(action.verbe, []).append(action)
        if action.outil == eid:
            cles.setdefault(action.verbe + "@outil", []).append(action)
    return cles


def charger_reactions(dossier: Path = DOSSIER_REACTIONS) -> dict[str, dict]:
    reactions = {}
    for chemin in sorted(dossier.glob("*.json")):
        with open(chemin, encoding="utf-8") as f:
            reactions[chemin.stem] = json.load(f)
    return reactions
