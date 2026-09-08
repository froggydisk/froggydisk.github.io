"""교재에서 설명한 확률의 성질과 잘못된 입력의 처리를 검증한다."""

import math
import unittest

from sampling import probabilities


class SamplingTests(unittest.TestCase):
    def test_probability_distribution(self):
        values = probabilities([2.0, 1.0, 0.0], 1.0)
        self.assertAlmostEqual(sum(values), 1.0)
        self.assertTrue(all(0 <= p <= 1 for p in values))
        self.assertGreater(values[0], values[1])
        self.assertGreater(values[1], values[2])

    def test_shift_invariance(self):
        base = probabilities([2.0, 1.0, 0.0], 1.0)
        shifted = probabilities([102.0, 101.0, 100.0], 1.0)
        for left, right in zip(base, shifted):
            self.assertAlmostEqual(left, right)

    def test_uniform_logits(self):
        for temperature in (0.5, 1.0, 2.0):
            for value in probabilities([5.0, 5.0, 5.0], temperature):
                self.assertAlmostEqual(value, 1 / 3)

    def test_lower_temperature_concentrates_mass(self):
        low = probabilities([2.0, 1.0, 0.0], 0.5)
        high = probabilities([2.0, 1.0, 0.0], 2.0)
        self.assertGreater(low[0], high[0])

    def test_rejects_invalid_input(self):
        for logits, temperature in (
            ([], 1), ([0], 0), ([0], -1), ([math.inf], 1),
            ([math.nan], 1), ([0], math.inf), ([0], math.nan),
        ):
            with self.subTest(logits=logits, temperature=temperature):
                with self.assertRaises(ValueError):
                    probabilities(logits, temperature)


if __name__ == "__main__":
    unittest.main()
