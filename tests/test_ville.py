import unittest

from generer_carte import donnees_carte
from outils.verifier_reactions import verifier_fichier
from simulation.catalogue import charger, verifier
from simulation.ville import DOSSIER_REACTIONS, actions_ville, charger_ville, cles_reactions, entites_jouables

CATEGORIES = {"batiment", "habitant", "animal", "objet"}
FACTIONS = {"loi", "hors_la_loi", "commerce"}


class TestVille(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verbes, cls.base = charger()
        cls.ville = charger_ville()
        cls.actions = actions_ville(cls.ville, cls.verbes, cls.base)

    def test_donnees_coherentes(self):
        entites = {**self.base, **entites_jouables(self.ville, self.base)}
        self.assertEqual(verifier(self.verbes, entites), [])

    def test_plan(self):
        lieux = self.ville["lieux"]
        for eid, entite in self.ville["entites"].items():
            with self.subTest(eid=eid):
                self.assertIn(entite["categorie"], CATEGORIES)
                self.assertIn(entite["lieu"], lieux)
                self.assertIn(entite.get("faction", "loi"), FACTIONS)
                if entite["categorie"] == "habitant":
                    self.assertIn("metier", entite)
                if entite["categorie"] == "batiment":
                    self.assertEqual(lieux[eid]["type"], "batiment")

    def test_chaque_entite_a_des_actions(self):
        for eid in self.ville["entites"]:
            with self.subTest(eid=eid):
                self.assertTrue(cles_reactions(eid, self.actions))

    def test_chaque_entite_a_ses_reactions(self):
        for eid in self.ville["entites"]:
            with self.subTest(eid=eid):
                self.assertEqual(verifier_fichier(eid, self.ville, self.verbes, self.base), [])

    def test_pas_de_fichier_orphelin(self):
        orphelins = {p.stem for p in DOSSIER_REACTIONS.glob("*.json")} - set(self.ville["entites"])
        self.assertEqual(orphelins, set())

    def test_carte(self):
        donnees = donnees_carte()
        self.assertEqual(set(donnees["entites"]), set(self.ville["entites"]))
        self.assertGreater(donnees["stats"]["variantes"], 0)


if __name__ == "__main__":
    unittest.main()
