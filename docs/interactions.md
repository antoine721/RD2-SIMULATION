# Tout ce qui peut se passer à Valentine

Une ville vivante ne se résume pas à « le joueur fait quelque chose à quelqu'un ».
Voici les seize familles d'interactions que la simulation couvre, et où chacune
est décrite dans les données.

## A. Ce que tu fais

| # | Interaction | Exemple | Données |
|---|-------------|---------|---------|
| 1 | Agir **sur** quelqu'un ou quelque chose | « provoquer le shérif », « caresser le chien » | `data/reactions/<id>.json` → `reactions.<verbe>` |
| 2 | Passer **par** quelqu'un ou quelque chose | « acheter un fusil à l'armurier », « atteler ton cheval à la diligence » | `reactions.<verbe>@outil` |
| 3 | Utiliser les **métiers et services** de chacun | « se faire soigner par le docteur », « envoyer un télégramme » | verbes inventés par entité |
| 4 | Agir **seul** ou avec ton inventaire | « chanter », « prier », « tirer en l'air », « fumer une cigarette » | `data/joueur.json` |
| 5 | Les gestes **universels** | « serrer la main », « gifler », « offrir à boire », « demander son chemin » | `data/verbes_proposes.json` puis `data/verbes.json` |

## B. Ce que la ville fait sans toi

| # | Interaction | Exemple | Données |
|---|-------------|---------|---------|
| 6 | **Routines** : chacun vit sa journée | le barman dort à l'étage, ouvre à 8 h, ferme à 2 h | `routine` de chaque habitant |
| 7 | **Scènes entre habitants** | le shérif ramasse l'ivrogne, le chat chasse le rat | `data/evenements/*.json` |
| 8 | **Vie collective** | messe du dimanche, arrivée du train, vente de bétail, enterrement | `data/evenements/*.json` |
| 9 | **Météo et accidents** | orage, crue du ruisseau, incendie de l'écurie, taureau échappé | `meteo` + événements |

## C. Ce que la ville fait à cause de toi

| # | Interaction | Exemple | Données |
|---|-------------|---------|---------|
| 10 | **Témoins** : ceux qui sont là réagissent | l'épicier hurle quand tu dégaines dans sa boutique | `data/temoins/*.json` |
| 11 | **Réputation** : l'honneur change les réponses | le pasteur te bénit ou te ferme sa porte | conditions `honneur_haut` / `honneur_bas` |
| 12 | **Loi** : la prime attire shérif et chasseurs | le chasseur de primes t'attend devant le saloon | `est_recherche` + événements |
| 13 | **Conséquences durables** | un mort reste mort, sa boutique reste fermée, la veuve s'en souvient | états `mort`, `detruit`, relation |
| 14 | **Réactions en chaîne** juste après un acte | après un braquage, l'adjoint forme une milice | événements `apres` |

## D. Ce que la ville te demande

| # | Interaction | Exemple | Données |
|---|-------------|---------|---------|
| 15 | **On vient vers toi** | le gamin propose une info, la veuve demande vengeance, défi au bras de fer, offre de travail | événements avec `choix` |

## E. Les histoires

| # | Interaction | Exemple | Données |
|---|-------------|---------|---------|
| 16 | **Arcs en plusieurs étapes** reliés par des drapeaux | repérage → dynamite → évasion de jeudi → poursuite | `drapeaux` des événements |

## Le monde autour

- **Temps** : heure (0–23 h) et jour de la semaine. Le dimanche, la messe ;
  le jeudi, le train du juge.
- **Météo** : beau, chaleur, pluie, orage, brouillard.
- **Toi** : honneur, argent, prime, santé, à pied ou à cheval, et le lieu où tu es.
- **Mémoire** : la relation de chaque habitant avec toi, et l'état de chacun
  (mort, blessé, hostile, en fuite, ligoté, détruit).

## Les conditions disponibles

Elles permettent à une même action de produire des résultats différents.

| Condition | Vraie quand |
|-----------|-------------|
| `honneur_haut` / `honneur_bas` | honneur ≥ 3 / ≤ -3 |
| `est_recherche` | ta prime est supérieure à 0 |
| `nuit` / `jour` | entre 21 h et 6 h / le reste du temps |
| `dedans` / `dehors` | tu es dans un bâtiment / dans la rue |
| `a_cheval` | tu es en selle |
| `pluie`, `orage`, `brouillard`, `chaleur` | météo du moment (`pluie` vaut aussi pendant l'orage) |
| `dimanche` | jour de repos |
| `ami` / `hostile` | relation de l'entité avec toi (réactions seulement) |
| `ami:id`, `hostile:id`, `mort:id`, `vivant:id` | état d'une entité précise (événements) |
| `present:lieu` | tu te trouves dans ce lieu (événements) |
