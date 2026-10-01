import unittest

from mtrack.validation import compare_candidate, residual_metrics


class ValidationTests(unittest.TestCase):
    def test_metrics(self):
        m = residual_metrics([1, 2, 3, 4])
        self.assertEqual(m.samples, 4)
        self.assertAlmostEqual(m.mean, 2.5)
        self.assertEqual(m.maximum, 4)

    def test_better_candidate_is_accepted(self):
        decision = compare_candidate(
            [10, 10, 10, 10, 10],
            [8, 8, 8, 8, 8],
            min_rms_improvement=0.10,
        )
        self.assertTrue(decision.accept)

    def test_average_improvement_cannot_hide_bad_tail(self):
        active = [10] * 20
        candidate = [5] * 19 + [20]
        decision = compare_candidate(
            active,
            candidate,
            min_rms_improvement=0.05,
            max_p95_regression=0.05,
            max_worst_regression=0.10,
        )
        self.assertFalse(decision.accept)
        self.assertIn("worst", decision.reason)


if __name__ == "__main__":
    unittest.main()
