# RD2-SIMULATION

Simulation avancée inspirée de *Red Dead Redemption 2*, où le joueur n'est pas
limité aux choix prévus par le jeu : il doit pouvoir faire **tout ce qui est
physiquement possible** dans l'Ouest de 1899.

## Le problème : on ne peut pas tout lister à la main

Écrire à la main « caresser le cheval », « caresser le chien », « tirer sur le
shérif avec le revolver », « tirer sur la lanterne avec le fusil »... ne finit
jamais. Le nombre d'actions explose dès qu'on ajoute un objet ou un personnage.

## La technique : une grammaire d'actions

On ne liste pas les actions : on liste **leurs ingrédients**, et l'ordinateur
calcule toutes les combinaisons.

```
ACTION = VERBE + CIBLE (facultative) + OUTIL (facultatif)
```

1. **Les entités déclarent ce qu'elles permettent** (`data/entites.json`).
   On appelle ça des *affordances* (des tags) :
   ```json
   "ton_cheval": { "nom": "ton cheval", "tags": ["vivant", "monture", "caressable", "brossable"] }
   ```
2. **Les verbes déclarent ce qu'ils exigent** (`data/verbes.json`) :
   ```json
   "brosser": { "phrase": "brosser {cible} avec {outil}", "cible": ["brossable"], "outil": ["brosse"] }
   ```
3. **Le générateur croise les deux.** Chaque verbe est essayé avec chaque
   entité qui possède les bons tags. On obtient le catalogue complet.
4. **La situation filtre.** Un fichier de situation (`situations/*.json`) dit ce
   que le joueur a dans son inventaire, ce qui est à proximité et son état
   (à cheval, recherché, a de l'argent...). Le générateur ne garde alors que ce
   qui est possible **maintenant**.

Ajouter **un seul** verbe crée d'un coup des dizaines d'actions, et ajouter
**une seule** entité la rend compatible avec tous les verbes existants. Avec
84 verbes et 57 entités, le prototype génère déjà **1 403 actions**
(voir [`catalogue_actions.md`](catalogue_actions.md)).

## Utilisation

Python 3.10+ suffit, sans dépendance.

```bash
python3 lister_actions.py                                    # catalogue complet
python3 lister_actions.py --resume                           # totaux par catégorie
python3 lister_actions.py --entite ton_cheval                # tout ce qu'on peut faire avec le cheval
python3 lister_actions.py --situation situations/camp.json   # ce qui est possible au camp
python3 lister_actions.py --sortie catalogue_actions.md      # régénérer le catalogue
python3 -m unittest                                          # vérifier la cohérence des données
```

Exemple (`--situation situations/a_cheval.json`, extrait) :

```
## Cheval & animaux (9)
- descendre de cheval
- galoper
- faire cabrer son cheval
- caresser ton cheval
- nourrir ton cheval avec une pomme
- dresser un cheval sauvage
...
```

## Ne jamais être limité : la boucle d'extension

La grammaire couvre ce qu'on a pensé à y mettre. Pour aller au-delà :

1. **Remplir au départ**, catégorie par catégorie, en demandant à une IA de
   lister de façon exhaustive ce qu'un humain de 1899 peut faire, directement
   au format JSON du projet.
2. **En jeu, accepter du texte libre** : le joueur écrit ce qu'il veut,
   une IA le décompose en actions de la grammaire.
3. **Si rien ne correspond**, l'IA propose un nouveau verbe au bon format.
   Une fois validé et ajouté, il marche pour **toutes** les entités
   compatibles.

Les deux prompts prêts à copier sont dans [`docs/prompt_extension.md`](docs/prompt_extension.md).
`python3 -m unittest` détecte les fautes de frappe dans les tags et les verbes
qui ne produisent aucune action.

## Ajouter du contenu

**Une entité** : dans `data/entites.json`, donne-lui un `nom` (avec article :
« un tonneau », « la rivière ») et ses `tags`. Tags existants :

> achetable, aiguisable, allumable, animal, appareil_photo, apprivoisable, arme,
> arme_blanche, arme_de_tir, assise, attelable, braquable, brossable, brosse,
> buvable, cachette, canne_a_peche, caressable, carnet, chassable, comestible,
> conduisible, crochet, crochetable, cueillable, cuisinable, depouille,
> destructible, eau, equipable, escaladable, explosif, fouillable, fourrage,
> fumable, humain, inscriptible, instrument, jeu_de_table, lancable, lien, lieu,
> lisible, lit, marchand, monture, nettoyable, nourrissable, ouvrable, parlant,
> physique, portable, rasoir, recherche, soudoyable, source_chaleur,
> transportable, vehicule, vendable, vivant, volable

**Un verbe** : dans `data/verbes.json` :

| Champ        | Rôle                                                              |
|--------------|-------------------------------------------------------------------|
| `categorie`  | regroupement dans le catalogue                                    |
| `phrase`     | texte avec `{cible}` et/ou `{outil}`                              |
| `cible`      | tags exigés de la cible (absent = pas de cible)                   |
| `outil`      | tags exigés de l'outil (absent = pas d'outil)                     |
| `conditions` | drapeaux du joueur, `!` pour la négation (`"!a_cheval"`)          |
| `cible_ou`   | `inventaire` ou `proximite` (par défaut : l'un ou l'autre)        |
| `outil_ou`   | idem pour l'outil                                                 |

## Prochaines étapes

- **Effets** : donner à chaque verbe ses conséquences (honneur, prime,
  santé, inventaire, relation avec les PNJ) pour que l'action change le monde.
- **Boucle de jeu** : afficher la situation, laisser le joueur choisir ou taper
  une action, appliquer les effets, recommencer.
- **Monde persistant** : villes, PNJ avec mémoire, économie, météo, heure.
