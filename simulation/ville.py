"""Une ville jouable : un plan, des entités placées dans des lieux, et leurs réactions.

Le joueur dispose d'un inventaire (entités génériques de data/entites.json) ;
toutes les entités de la ville sont considérées comme « à proximité ».
"""

from __future__ import annotations

import json
from pathlib import Path

from simulation.catalogue import DOSSIER_DATA, Action, generer

DOSSIER_REACTIONS = DOSSIER_DATA / "reactions"
DOSSIER_EVENEMENTS = DOSSIER_DATA / "evenements"
DOSSIER_TEMOINS = DOSSIER_DATA / "temoins"
FICHIER_JOUEUR = DOSSIER_DATA / "joueur.json"
VILLE_PAR_DEFAUT = DOSSIER_DATA / "villes" / "valentine.json"

# Vocabulaire commun aux fichiers de données et à la carte.
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
METEOS = {"beau", "chaleur", "pluie", "orage", "brouillard"}
CONDITIONS_MONDE = {
    "honneur_haut", "honneur_bas", "est_recherche", "nuit", "jour", "dedans", "dehors",
    "a_cheval", "pluie", "orage", "brouillard", "chaleur", "dimanche",
}
# Conditions sur l'entité qui réagit (réactions seulement).
CONDITIONS_ENTITE = {"hostile", "ami"}
CONDITIONS_SI = CONDITIONS_MONDE | CONDITIONS_ENTITE
EFFETS_NUMERIQUES = {"honneur", "argent", "prime", "sante", "relation"}
EFFETS_JOUEUR = {"honneur", "argent", "prime", "sante"}
ETATS_VIVANTS = {"mort", "blesse", "hostile", "en_fuite", "ligote", "normal"}
ETATS_CHOSES = {"detruit", "normal"}
CATEGORIES_TEMOIN = ["meurtre", "violence", "vol", "crime", "bonte", "insolite"]


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


def actions_joueur(ville: dict, verbes: dict, base_entites: dict) -> list[Action]:
    """Ce que le joueur peut faire seul ou avec son inventaire (sans personne autour)."""
    situation = {"joueur": {}, "inventaire": list(ville["inventaire_depart"]), "a_proximite": []}
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


def charger_dossier(dossier: Path) -> dict[str, dict]:
    contenu = {}
    for chemin in sorted(dossier.glob("*.json")):
        with open(chemin, encoding="utf-8") as f:
            contenu[chemin.stem] = json.load(f)
    return contenu


def charger_reactions(dossier: Path = DOSSIER_REACTIONS) -> dict[str, dict]:
    return charger_dossier(dossier)
