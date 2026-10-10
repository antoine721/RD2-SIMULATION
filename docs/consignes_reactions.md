# Consignes pour écrire les réactions d'une ville

Ce document sert à toute personne (ou agent IA) qui écrit les fichiers
`data/reactions/<id>.json` : un fichier par entité de `data/villes/valentine.json`.

## 1. La bible de Valentine (1899)

Valentine est une petite ville d'éleveurs des Heartlands, dans l'État de New
Hanover. Rue principale boueuse, odeur de bétail, chemin de fer au nord,
ruisseau au sud. Pas d'électricité : lampes à pétrole, télégraphe, diligences.
Le gang O'Driscoll rôde dans la région et terrorise les fermes isolées.

Le joueur (« tu ») est un voyageur armé, de passage. Personne ne le connaît
encore. Selon ses actes, il devient un héros ou un bandit.

Personnages et liens (à réutiliser pour que la ville soit cohérente) :

- **Le shérif Malloy** : vieux, fatigué, honnête mais pragmatique. Il traque les
  O'Driscoll. **L'adjoint** est jeune, nerveux, rêve de gloire et dégaine trop vite.
- **Le prisonnier** est un O'Driscoll arrêté hier soir pour vol de chevaux.
  **Un autre O'Driscoll** boit au Smithfield's : il est venu préparer son
  évasion. Son visage est sur **le panneau des avis de recherche** (prime de 75 $).
- **Le chasseur de primes**, au Smithfield's, traque justement cet O'Driscoll.
- **Le saloon de Keane** est le saloon « respectable ». **Le barman de Keane**
  est bavard et connaît toutes les rumeurs. **Le pianiste** vient de
  La Nouvelle-Orléans et joue faux quand il a bu. **La danseuse** rêve de
  partir à Saint Denis. **Le joueur de poker** triche (cartes dans la manche).
  **Le chat du saloon**, un gros roux, chasse les rats.
- **Le Smithfield's** est mal famé, bagarres tous les soirs. **Son barman**
  est bourru et sert un whisky frelaté.
- **L'armurier** est un ancien soldat passionné d'armes. **L'épicier** est radin
  et ne fait jamais crédit.
- **Le directeur de la banque** est arrogant et prête à taux usuraire aux
  fermiers. **Le caissier**, timide, a peur d'un braquage depuis des semaines.
- **Le palefrenier** aime les chevaux plus que les gens. **Le cheval attaché**
  dans la rue appartient à l'O'Driscoll. **Le cheval à vendre** est un Morgan
  nerveux. **Ton cheval** est ton fidèle compagnon.
- **Le maréchal-ferrant** est un colosse taiseux. **Le docteur** boit et vend des
  toniques douteux.
- **Le croque-mort** est lugubre et drôle ; il mesure les gens du regard.
  **La veuve** a perdu son mari, tué par les O'Driscoll ; elle veut vengeance.
  **Une tombe** du cimetière est celle de son mari.
- **La gérante de l'hôtel** est stricte (bain : 50 cents). **Le boucher** est
  jovial, couvert de sang, il achète viande et peaux.
- **Le chef de gare** est obsédé par la ponctualité. **Le télégraphiste**, curieux,
  lit les messages des autres et sait tout des primes.
- **Le pasteur** prêche la tempérance ; c'est un ancien pistolero repenti.
  **Le gamin des rues** est orphelin, pickpocket et informateur.
- **L'éleveur** est riche et vend du bétail. **Le vacher** est jeune et rêve de
  devenir un cow-boy célèbre. **Le taureau**, surnommé Lucifer, est dangereux.
- **Le crieur de journaux** annonce les nouvelles de Saint Denis et les primes.
  **Le vétéran mendiant** a perdu une jambe pendant la guerre de Sécession.
  **Le chien errant** cherche un maître.
- **L'ivrogne** jure qu'il a vu de l'or dans les collines. **Le fermier de
  passage** est endetté auprès du banquier.

Tu peux inventer des prénoms, des souvenirs et des secrets, tant qu'ils ne
contredisent pas cette bible.

## 2. Méthode

1. Pour chaque entité, lance :
   `python3 outils/verifier_reactions.py --a-faire <id>`
   Cela affiche ses tags et **toutes les clés de réaction à écrire**.
2. Écris `data/reactions/<id>.json` (format ci-dessous).
3. Vérifie : `python3 outils/verifier_reactions.py --creation <id> [<id>...]`
   et corrige jusqu'à ce que tout soit ✓.
4. Ne modifie **aucun autre fichier** que ceux de tes entités.

## 3. Format d'un fichier

```json
{
  "id": "barman_keane",
  "description": "Un petit homme rond au tablier taché, moustache cirée, qui essuie sans fin le même verre.",
  "personnalite": "Bavard, curieux, peureux. Adore les ragots, déteste la casse.",
  "repliques": ["Whisky, bière, ou des nouvelles ?", "On dit que le shérif a coffré un O'Driscoll hier soir."],
  "routine": [
    { "de": 0, "a": 8,  "lieu": "saloon_keane", "activite": "dort à l'étage" },
    { "de": 8, "a": 24, "lieu": "saloon_keane", "activite": "sert au comptoir" }
  ],
  "nouveaux_tags": ["sert_a_boire"],
  "nouveaux_verbes": {
    "commander_whisky": { "categorie": "Métiers & services", "phrase": "commander un whisky à {cible}", "cible": ["sert_a_boire"], "conditions": ["a_de_l_argent"] }
  },
  "reactions": {
    "parler": [
      { "texte": "Il se penche par-dessus le comptoir : « Tu n'as pas entendu ? Malloy a coffré un O'Driscoll. »" },
      { "texte": "Il recule d'un pas : « Je ne veux pas d'ennuis, l'ami. »", "si": ["est_recherche"], "effets": { "relation": -1 } }
    ],
    "acheter@outil": [
      { "texte": "Il pose {cible} sur le comptoir et compte la monnaie deux fois.", "effets": { "argent": -2, "relation": 1 } }
    ]
  }
}
```

- **description** (obligatoire) : 1 à 3 phrases visuelles.
- **personnalite** : obligatoire pour les habitants et les animaux.
- **repliques** : ce que l'entité dit ou fait spontanément (bulles sur la carte).
  Au moins 5 pour un habitant, 3 pour un animal (`*hennit doucement*`), 0 à 3
  pour un objet ou un bâtiment (`Le piano grince.`).
- **routine** : obligatoire pour les habitants, facultative pour les animaux.
  De 0 h à 24 h sans trou, avec les lieux de `data/villes/valentine.json`.
  Une journée réaliste : dormir (pension, maisons, hôtel, à l'étage de sa
  boutique), travailler, manger, boire au saloon.
- **reactions** : une entrée par clé donnée par `--a-faire`.
  - `verbe` : l'entité subit l'action (« parler au barman »).
  - `verbe@outil` : l'entité sert d'outil ou d'interlocuteur (« acheter X au
    barman », « atteler ton cheval à la diligence »).
- **nouveaux_verbes / nouveaux_tags** : voir section 5.

## 4. Écrire une bonne réaction

- **Au moins 3 variantes par clé**, 4 ou plus pour les clés sociales d'un
  habitant (parler, saluer, provoquer, intimider, soudoyer, menacer) et pour
  ses nouveaux verbes. Au moins une variante sans `si`.
- **Utilise les conditions `si`** dès qu'elles changent la réaction, sur au
  moins un tiers des clés : `hostile`, `ami` (relation avec cette entité),
  `est_recherche` (le joueur a une prime), `honneur_haut`, `honneur_bas`,
  `nuit`, `jour`.
- **Style** : français, 1 à 3 phrases, deuxième personne (« tu »), présent.
  Concret, visuel, avec des dialogues entre « guillemets français ». Ton western
  de 1899, dramatique ou drôle. Pas deux variantes qui se ressemblent.
- **Emplacements** : `{cible}` et `{outil}` sont remplacés par le nom de l'objet
  (« le revolver »). Le vérificateur dit lesquels sont permis pour chaque clé.
  Ne commence pas une phrase par un emplacement.
- **Effets cohérents avec le texte** (entiers) :
  - `honneur` : de -5 (meurtre de sang-froid) à +3 (acte héroïque) ;
  - `argent` : en dollars (whisky -1, bain -1, pot-de-vin -20, butin +5 à +200) ;
  - `prime` : en dollars, ajoutée quand un témoin ou la loi voit un crime
    (bagarre 5, vol 10, meurtre 50 à 150) ;
  - `sante` : la santé du joueur, de -60 (balle) à +30 (soins) ;
  - `relation` : avec cette entité, de -5 à +3.
- **`etat`** change l'état de l'entité :
  `mort`, `blesse`, `hostile`, `en_fuite`, `ligote`, `normal` pour les êtres
  vivants ; `detruit`, `normal` pour les choses. Une balle ne tue pas toujours :
  mélange `mort`, `blesse`, `en_fuite`, et parfois une riposte (`sante` négative).

## 5. Inventer de nouveaux verbes

C'est ce qui rend la simulation illimitée. Pour chaque entité, ajoute ce qu'on
pourrait faire avec elle et que la liste ne prévoit pas encore :
au moins **4 par habitant**, **2 par animal, objet ou bâtiment**.

Exemples : « commander un whisky », « demander une chambre », « faire ferrer
son cheval », « envoyer un télégramme », « se confesser », « sonner la cloche »,
« traire la vache », « parier sur une partie », « adopter le chien ».

- Format identique à `data/verbes.json` (`categorie`, `phrase`, `cible`,
  `outil`, `conditions`). Catégorie au choix parmi celles existantes ou
  `Métiers & services`.
- Le verbe doit s'appliquer à l'entité : invente un **tag spécifique** dans
  `nouveaux_tags` (ex. `sert_a_boire`, `sonnable`, `trayable`) et exige-le dans
  `cible`. N'utilise pas un tag générique (`humain`, `vivant`...) : le verbe
  s'appliquerait à toute la ville.
- Si un nouveau verbe convient à plusieurs entités de ton groupe, définis-le
  **à l'identique** (même identifiant, même définition) dans chacun de leurs
  fichiers, avec le même tag.
- Un outil, s'il y en a un, doit exister dans l'inventaire du joueur
  (`inventaire_depart`) ou dans la ville.
- Écris ensuite les réactions de ces nouveaux verbes comme les autres.
