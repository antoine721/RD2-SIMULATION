# Prompts pour étendre le catalogue avec une IA

Le catalogue n'est jamais « fini ». Ces deux prompts servent à le faire grandir
avec une IA (Claude ou autre) sans casser la grammaire. Copie-les tels quels et
remplace les parties entre `<…>`.

---

## 1. Brainstorming exhaustif d'une catégorie

À utiliser pour remplir le catalogue au départ, catégorie par catégorie.

```text
Tu aides à construire une simulation de l'Ouest américain en 1899, inspirée de
Red Dead Redemption 2, mais SANS se limiter à ce que le jeu permet.

Catégorie : <Survie>

Liste de façon exhaustive tout ce qu'un être humain de 1899 pourrait
physiquement faire dans cette catégorie, y compris ce que le jeu ne permet pas.
Pense en verbes à l'infinitif. Pour chaque verbe, indique :
- s'il a une cible (et quelle propriété elle doit avoir : comestible, vivant...)
- s'il nécessite un outil (et quelle propriété il doit avoir : arme_blanche...)
- les conditions sur le joueur (à cheval, a de l'argent, recherché...)

Voici les tags qui existent déjà, réutilise-les en priorité :
<coller la liste des tags, voir README>

Réponds uniquement en JSON, au format suivant :
{
  "id_du_verbe": {
    "categorie": "<Survie>",
    "phrase": "dépecer {cible} avec {outil}",
    "cible": ["depouille"],
    "outil": ["arme_blanche"],
    "conditions": ["!a_cheval"]
  }
}
```

## 2. Interpréter une action libre du joueur

À utiliser en jeu : le joueur tape ce qu'il veut, l'IA le traduit en action de la
grammaire, ou propose un nouveau verbe si rien ne correspond.

```text
Voici les verbes connus de la simulation (JSON) :
<contenu de data/verbes.json>

Voici la situation actuelle (JSON) :
<contenu du fichier de situation>

Le joueur écrit : "<je grimpe sur le toit de la diligence et je saute sur le shérif>"

1. Décompose cette phrase en une suite d'actions élémentaires.
2. Pour chaque action, si un verbe connu correspond, renvoie
   {"verbe": "...", "cible": "...", "outil": "..."} avec les identifiants exacts.
3. Si aucun verbe ne correspond, renvoie {"nouveau_verbe": {...}} au format de
   data/verbes.json, en réutilisant les tags existants autant que possible.

Réponds uniquement en JSON : une liste d'actions dans l'ordre.
```

Chaque `nouveau_verbe` proposé est relu, ajouté à `data/verbes.json`, puis
`python3 -m unittest` vérifie qu'il est cohérent. Il devient alors disponible
pour **toutes** les entités qui ont les bons tags, pas seulement dans la phrase
qui l'a fait naître.
