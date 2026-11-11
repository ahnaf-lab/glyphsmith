import unittest

from glyphsmith.prng import make_rng


class MakeRngTests(unittest.TestCase):
    def test_same_seed_and_parts_are_deterministic(self):
        rng1 = make_rng("acme", "glyph", "A")
        rng2 = make_rng("acme", "glyph", "A")
        self.assertEqual(
            [rng1.random() for _ in range(10)],
            [rng2.random() for _ in range(10)],
        )

    def test_different_parts_diverge(self):
        rng_a = make_rng("acme", "glyph", "A")
        rng_b = make_rng("acme", "glyph", "B")
        self.assertNotEqual(rng_a.random(), rng_b.random())

    def test_different_seeds_diverge(self):
        rng_a = make_rng("acme", "glyph", "A")
        rng_b = make_rng("other-seed", "glyph", "A")
        self.assertNotEqual(rng_a.random(), rng_b.random())

    def test_returns_random_instance_with_working_api(self):
        rng = make_rng("acme")
        choice = rng.choice([1, 2, 3])
        self.assertIn(choice, (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
