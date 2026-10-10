import tempfile
import unittest
from pathlib import Path

from simulation.catalogue import _accorder, charger, charger_situation, generer, verifier

RACINE = Path(__file__).resolve().parent.parent


class TestCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verbes, cls.entites = charger()

    def situation(self, nom):
        return charger_situation(RACINE / "situations" / f"{nom}.json", self.entites)

    def textes(self, situation=None):
        return {a.texte for a in generer(self.verbes, self.entites, situation)}

    def test_donnees_coherentes(self):
        self.assertEqual(verifier(self.verbes, self.entites), [])

    def test_chaque_verbe_produit_au_moins_une_action(self):
        verbes_utilises = {a.verbe for a in generer(self.verbes, self.entites)}
        self.assertEqual(set(self.verbes) - verbes_utilises, set())

    def test_une_entite_ne_sert_pas_d_outil_sur_elle_meme(self):
        for action in generer(self.verbes, self.entites):
            if action.cible is not None:
                self.assertNotEqual(action.cible, action.outil)

    def test_accords(self):
        self.assertEqual(_accorder("parler à le shérif"), "parler au shérif")
        self.assertEqual(_accorder("jouer de le piano"), "jouer du piano")
        self.assertEqual(_accorder("la piste de un cerf"), "la piste d'un cerf")
        self.assertEqual(_accorder("boire l'eau de la rivière"), "boire l'eau de la rivière")

    def test_situation_a_pied(self):
        actions = self.textes(self.situation("camp"))
        self.assertIn("monter sur ton cheval", actions)
        self.assertIn("cuisiner de la viande crue sur le feu de camp", actions)
        self.assertNotIn("galoper", actions)
        # Le shérif n'est pas au camp.
        self.assertNotIn("parler au shérif", actions)

    def test_situation_a_cheval(self):
        actions = self.textes(self.situation("a_cheval"))
        self.assertIn("galoper", actions)
        self.assertNotIn("monter sur ton cheval", actions)
        # Pas d'argent : impossible d'acheter ou de soudoyer.
        self.assertFalse(any(a.startswith(("acheter", "soudoyer")) for a in actions))

    def test_situation_recherche(self):
        actions = self.textes(self.situation("saloon"))
        self.assertIn("payer sa prime", actions)
        self.assertIn("crocheter le coffre-fort avec un crochet de serrurier", actions)
        self.assertIn("faire sauter la porte avec un bâton de dynamite", actions)

    def test_situation_avec_entite_inconnue(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "situation.json"
            chemin.write_text('{"inventaire": ["sabre_laser"]}', encoding="utf-8")
            with self.assertRaises(ValueError):
                charger_situation(chemin, self.entites)


if __name__ == "__main__":
    unittest.main()
