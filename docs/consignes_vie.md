# Consignes pour écrire la vie de la ville

Ces fichiers complètent les réactions (`data/reactions/`). Ils couvrent tout ce
qui peut se passer en dehors d'un clic du joueur sur une entité (voir
`docs/interactions.md`). Lis aussi la section 1 de `docs/consignes_reactions.md`
(la bible de Valentine).

## 0. Rester cohérent avec ce qui existe

Beaucoup de choses ont déjà été inventées. Avant d'écrire, lance :

    python3 outils/resume_ville.py                 # toutes les entités
    python3 outils/resume_ville.py veuve gamin     # seulement celles-ci

Faits déjà établis (à respecter) :

- Le prisonnier s'appelle **Finn Mulligan**, voleur de chevaux, il se dit cousin
  de l'O'Driscoll libre : **Ciaran Doyle, « le Balafré »** (foulard vert,
  Schofield, trèfle tatoué). Le Balafré prépare l'évasion à la dynamite.
- **Jeudi**, le train amène le juge et un marshal : Finn doit être transféré
  à Saint Denis. L'évasion doit avoir lieu avant.
- **Tommy Rourke, « Tommy le Rapide »**, le vacher, est payé 5 $ par le Balafré
  pour tenir les chevaux pendant l'évasion.
- Le shérif Malloy dort au bureau la nuit ; son adjoint s'appelle **Eli**. Il n'y a
  qu'une cellule, avec une paillasse.
- La veuve est **Ada Hartley** ; son mari **Elias Hartley**, éleveur de chevaux,
  a été tué il y a trois semaines, un dimanche, d'une balle dans le dos sur son
  perron, par trois O'Driscoll, le tireur étant **« Rory le Rouge »**. Il repose
  au cimetière (1861-1899). Le cheval attaché du Balafré porte des fers que
  Gunnar avait posés pour Elias. Le corbeau **Edgar** a volé le médaillon d'Ada.
- L'éleveur est **Silas Whitmore** (ranch du « W couronné »), proche du banquier
  **Horace**, il perd au poker contre le tricheur du Keane's. La vache s'appelle
  **Marguerite**, le taureau **Lucifer**.
- Le maréchal-ferrant est **Gunnar, « le Suédois »**, champion de bras de fer.
  Le docteur est **Thaddeus Barlow**.
- **Les Whitlock, famille fondatrice de Valentine** : **Horace P. Whitlock**, le
  directeur de la banque (il tient un « registre noir » de ses vrais taux et
  saisit les fermes) ; le **révérend Ezra Whitlock**, son frère, ancien pistolero
  « Whit le Pâle » de la bande de Tom Varney (Schofield caché sous l'autel) ;
  **Ambrose**, l'aîné, mort en 1894, mari de **Cornelia Whitlock**, la gérante de
  l'hôtel (ancienne institutrice de Boston, derringer nacré dans le tiroir).
  Les frères ne se parlent plus. Les Hartley ne sont **pas** des Whitlock.
- Le caissier est **Wendell Pruitt** (le crieur de journaux est de sa famille).
  La combinaison du coffre est **32-17-60-4**.
- Le chef de gare est **Silas Pettigrew**, le télégraphiste **Elmer Dobbs**.
  Trains : 7 h 12 pour Saint Denis, 11 h 40 pour Rhodes, 16 h 05 pour
  Strawberry. Le **wagon postal du samedi** apporte la paie des ranchs à la banque.
- Le boucher **Gus** courtise maladroitement Cornelia, qui passe à la boucherie
  de 17 h à 18 h. Un « M. Brown » à l'accent irlandais loge à l'hôtel, chambre 4.
- Le gamin s'appelle **Moineau** (Tobias) et dort dans le foin de l'écurie.
  Il ne meurt jamais : il s'enfuit ou il est blessé.
- Autres noms : le croque-mort **Mortimer Pembrook** ; la danseuse « Miss Rose »,
  de son vrai nom **Nell Harper** (38 $ économisés sur 60) ; le tricheur
  **Lucius Crane** ; le chat **Sultan** ; le barman du Smithfield's **Cyrus Hollis**
  et son fusil « Clementine » ; le chasseur de primes **Rook** ; le crieur
  **Billy Pruitt**, 15 ans ; le vétéran, **sergent Ezra Holloway** (jambe perdue à
  Franklin en 1864) ; le chien errant, « Scoop » ou « Caporal » ; le cocher de
  la diligence **Amos** et son garde **Wade** ; les mules du chariot **Prudence**
  et **Patience** ; la fille du fermier, **Ruth**.

## 1. Comment le moteur s'en sert

- **Temps** : l'heure avance (curseur, lecture, sommeil). À chaque heure qui
  passe, le moteur prend les événements possibles et en déclenche au plus deux
  (selon leur `chance`). Un jour de la semaine passe à minuit.
- **Événement possible** : l'heure est dans `heures`, le jour dans `jours`, la
  météo dans `meteo`, toutes les conditions `si` sont vraies, tous les
  `drapeaux` aussi, chaque acteur est vivant et présent (ni mort, ni en fuite,
  ni ligoté), et un événement `unique` n'a pas déjà eu lieu.
- **Réaction en chaîne** : un événement avec `apres` ne se déclenche pas à
  l'heure, mais **juste après** une action du joueur dont le verbe est dans
  `apres.verbes` (et la cible dans `apres.cibles`, si la liste est donnée).
- **Affichage** : le texte apparaît dans la gazette, les acteurs clignotent sur
  la carte, et les `choix` s'affichent sous forme de boutons. Ignorer
  l'événement est toujours possible (rien ne se passe).
- **Témoins** : après chaque action du joueur, les habitants et animaux présents
  dans le même lieu que la cible (sauf elle) peuvent réagir par une bulle, tirée
  de la catégorie correspondante : `meurtre`, `violence`, `vol`, `crime` (autre
  délit), `bonte` (acte qui rapporte de l'honneur) ou `insolite` (le reste).
- **Seul** : le joueur dispose d'un panneau « Toi » avec les actions sans cible
  ou sur son inventaire.

## 2. Événements : `data/evenements/<theme>.json`

```json
{
  "theme": "Le complot des O'Driscoll",
  "evenements": {
    "balafre_compte_les_fenetres": {
      "titre": "Le Balafré fait du repérage",
      "texte": "Ciaran Doyle fait les cent pas devant le bureau du shérif, le chapeau bas. Il compte les fenêtres, puis crache dans la boue.",
      "lieu": "rue_principale",
      "acteurs": ["odriscoll"],
      "heures": [10, 18],
      "jours": ["lundi", "mardi", "mercredi"],
      "chance": 0.35,
      "unique": true,
      "consequences": { "drapeaux": ["+evasion_reperee"] },
      "choix": [
        { "texte": "Prévenir le shérif Malloy", "resultat": "Malloy repose sa tasse. « Merci. Je doublerai la garde. »", "effets": { "honneur": 2 }, "consequences": { "drapeaux": ["+malloy_previent"], "entites": { "sherif_malloy": { "relation": 2 } } } },
        { "texte": "Lui proposer tes services", "resultat": "Il te jauge longuement. « Jeudi soir. Derrière la forge. Viens seul. »", "effets": { "honneur": -2 }, "consequences": { "drapeaux": ["+complice_du_balafre"], "entites": { "odriscoll": { "relation": 2 } } } },
        { "texte": "Passer ton chemin", "resultat": "Tu détournes les yeux. Ce n'est pas ton affaire, pas encore." }
      ]
    }
  }
}
```

| Champ | Obligatoire | Rôle |
|-------|-------------|------|
| `titre` | oui | 3 à 70 caractères |
| `texte` | oui | 1 à 4 phrases, au présent, vivantes (60 caractères minimum) |
| `lieu` | oui | où cela se passe (un lieu de la ville) |
| `acteurs` | non | entités impliquées, qui doivent être vivantes et présentes |
| `heures` | non | `[de, a]` ; `[22, 3]` traverse minuit |
| `jours` | non | `lundi` … `dimanche` |
| `meteo` | non | `beau`, `chaleur`, `pluie`, `orage`, `brouillard` |
| `si` | non | conditions (voir `docs/interactions.md`), y compris `mort:id`, `vivant:id`, `ami:id`, `hostile:id`, `present:lieu` |
| `drapeaux` | non | drapeaux exigés : `nom` (posé) ou `!nom` (pas posé) |
| `chance` | oui | probabilité par heure possible, entre 0 et 1 (rare : 0.05 ; fréquent : 0.5) |
| `unique` | non | `true` : une seule fois par partie (à mettre sur toutes les étapes d'une histoire) |
| `apres` | non | `{ "verbes": [...], "cibles": [...] }` : réaction immédiate à une action du joueur |
| `consequences` | non | appliquées dès que l'événement a lieu |
| `choix` | non | 2 à 4 options pour le joueur |

`consequences` (et celles d'un choix) :

- `drapeaux` : `["+nom", "-nom"]` pour poser ou retirer un drapeau. **Les
  drapeaux que tu exiges doivent être posés dans ton propre fichier.**
- `entites` : `{ "id": { "etat": "...", "relation": 1, "lieu": "bureau_sherif" } }`.
  `lieu` fige l'entité à cet endroit (ex. l'ivrogne mis en cellule) ; `null` la
  libère.
- `joueur` : `{ "honneur": 0, "argent": 0, "prime": 0, "sante": 0 }`.

Un choix : `texte` (le bouton, 90 caractères max), `resultat` (ce qui arrive),
`si` (conditions pour que le bouton soit proposé), `effets` (sur le joueur ;
un `argent` négatif est un coût), `consequences`.

**Ce qu'on attend d'un fichier de thème** : au moins **25 événements**, dont :

- au moins une **histoire** de 4 étapes ou plus, reliées par des drapeaux, avec
  des fins différentes selon les choix ;
- au moins 5 événements **avec choix** ;
- au moins 3 réactions en chaîne **`apres`** ;
- des événements **d'ambiance**, sans choix ni `unique`, qui donnent vie à la
  ville (fréquents mais variés) ;
- l'usage des heures, des jours, de la météo et de la réputation.

Vérifie : `python3 outils/verifier_vie.py evenements data/evenements/<theme>.json`.
Les identifiants d'événements doivent être uniques dans toute la ville.

## 3. Témoins : `data/temoins/<groupe>.json`

```json
{
  "epicier": {
    "meurtre":  ["« Seigneur ! Quelqu'un ! Allez chercher Malloy ! »", "*se jette derrière le comptoir en renversant les conserves*", "..."],
    "violence": ["« Pas dans ma boutique ! »", "...", "..."],
    "vol":      ["« Hé ! Ça se paie, ça ! »", "...", "..."],
    "crime":    ["...", "...", "..."],
    "bonte":    ["« Eh bien... Ça, ce n'est pas tous les jours. »", "...", "..."],
    "insolite": ["*fronce les sourcils* « Vous êtes sûr que ça va ? »", "...", "..."]
  }
}
```

Exactement ces six catégories, **au moins 3 répliques** pour un habitant (2 pour
un animal), 160 caractères maximum chacune (elles s'affichent dans une bulle).
Paroles entre « », gestes entre `*astérisques*`. Chaque personnage garde sa voix.

Vérifie : `python3 outils/verifier_vie.py temoins data/temoins/<groupe>.json`.

## 4. Le joueur seul : `data/joueur.json`

```json
{
  "description": "Un voyageur armé, poussiéreux, de passage à Valentine.",
  "nouveaux_verbes": {
    "prier": { "categorie": "Social", "phrase": "prier en silence" },
    "tirer_en_l_air": { "categorie": "Combat", "phrase": "tirer en l'air avec {outil}", "outil": ["arme_de_tir"], "outil_ou": "inventaire" }
  },
  "reactions": {
    "chanter": [
      { "texte": "Tu entonnes une vieille complainte de cow-boy. Un chien hurle quelque part." },
      { "texte": "Ta voix se perd sous la pluie. Personne ne t'écoute, et c'est très bien comme ça.", "si": ["pluie"] }
    ]
  }
}
```

Les clés à écrire : `python3 outils/verifier_vie.py joueur --a-faire`.
Au moins 3 variantes par clé, et au moins 15 nouveaux verbes sans cible (ou dont
la cible est un objet de l'inventaire). Les conditions possibles sont celles du
monde (pas `ami` ni `hostile`). Les effets ne portent que sur le joueur.

Vérifie : `python3 outils/verifier_vie.py joueur`.

## 5. Verbes universels : `data/verbes_proposes.json`

Des gestes qui valent pour beaucoup d'entités et manquent encore : même format
que `data/verbes.json`, avec des tags **existants et génériques**
(`humain`, `parlant`, `animal`, `lieu`, `vivant`...). Chacun doit s'appliquer à
au moins 2 entités de la ville.

Vérifie : `python3 outils/verifier_vie.py propositions`.

## 6. Style

Français, présent, deuxième personne pour le joueur. Ton western de 1899,
dramatique ou drôle, concret et visuel. Tout public : la violence peut être
dure mais jamais complaisante, et rien de sexuel.
