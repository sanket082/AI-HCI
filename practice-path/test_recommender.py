import unittest
from recommender import PracticePath


class RankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = PracticePath()

    def test_named_goals(self):
        for goal, expected in [("SQL joins", "joins"), ("keyboard focus", "keyboard"),
                               ("payment mock", "mock"), ("zero baseline", "axis")]:
            with self.subTest(goal=goal):
                hits, _ = self.model.recommend(goal)
                self.assertEqual(hits[0][0]["id"], expected)

    def test_seed_only(self):
        hits, _ = self.model.recommend(liked="mock")
        self.assertTrue(hits)
        self.assertNotIn("mock", [item["id"] for item, _, _ in hits])

    def test_seed_word_collision(self):
        hits, _ = self.model.recommend(liked="mock")
        self.assertNotIn("keyboard", [item["id"] for item, _, _ in hits])

    def test_time_boundary(self):
        hits, _ = self.model.recommend("SQL joins", minutes=20)
        self.assertEqual([item["id"] for item, _, _ in hits], ["joins"])

    def test_no_time(self):
        hits, message = self.model.recommend("SQL", minutes=5)
        self.assertFalse(hits)
        self.assertIn("time", message)

    def test_unknown(self):
        hits, message = self.model.recommend("aquaponics")
        self.assertFalse(hits)
        self.assertIn("--like", message)

    def test_combined(self):
        hits, _ = self.model.recommend("keyboard", liked="labels", minutes=20)
        self.assertEqual(hits[0][0]["id"], "keyboard")
        self.assertIn("keyboard", hits[0][2])
        self.assertLessEqual(hits[0][1], 1.000001)


if __name__ == "__main__":
    unittest.main()
