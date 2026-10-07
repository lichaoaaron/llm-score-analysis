"""假设检验与统计分布测试。"""
from __future__ import annotations

import math
import unittest

from score_analysis.utils.distributions import (
    chi2_p_value,
    f_cdf,
    gamma,
    gamma_inc,
    normal_cdf,
    t_cdf,
)
from score_analysis.services.hypothesis_testing import HypothesisTestingService
from score_analysis.services.effect_size import EffectSizeService


class TestDistributions(unittest.TestCase):
    def test_gamma_integer(self) -> None:
        # Γ(5) = 4! = 24。
        self.assertAlmostEqual(gamma(5.0), 24.0, places=4)

    def test_gamma_half(self) -> None:
        # Γ(0.5) = √π。
        self.assertAlmostEqual(gamma(0.5), math.sqrt(math.pi), places=4)

    def test_normal_cdf_center(self) -> None:
        self.assertAlmostEqual(normal_cdf(0.0), 0.5, places=5)

    def test_normal_cdf_196(self) -> None:
        # Φ(1.96) ≈ 0.975。
        self.assertAlmostEqual(normal_cdf(1.96), 0.975, places=2)

    def test_t_cdf_zero(self) -> None:
        self.assertAlmostEqual(t_cdf(0.0, 10), 0.5, places=5)

    def test_chi2_cdf_nonnegative(self) -> None:
        # 卡方 CDF 值域 [0, 1]。
        for x in (0.0, 1.0, 5.0, 20.0):
            v = chi2_p_value(x, 3)
            self.assertTrue(0.0 <= v <= 1.0)

    def test_f_cdf_monotonic(self) -> None:
        self.assertGreater(f_cdf(5.0, 3, 20), f_cdf(1.0, 3, 20))


class TestHypothesisTesting(unittest.TestCase):
    def setUp(self) -> None:
        self.service = HypothesisTestingService()

    def test_t_test_significant(self) -> None:
        a = [80, 82, 85, 78, 81]
        b = [60, 62, 58, 61, 63]
        r = self.service.independent_t_test(a, b)
        self.assertTrue(r.significant)
        self.assertLess(r.p_value, 0.05)
        self.assertGreater(r.mean_diff, 0)

    def test_t_test_identical(self) -> None:
        a = [70, 72, 71, 70, 71]
        b = [70, 72, 71, 70, 71]
        r = self.service.independent_t_test(a, b)
        self.assertFalse(r.significant)
        self.assertAlmostEqual(r.mean_diff, 0.0)

    def test_anova_significant(self) -> None:
        g1 = [85, 88, 90, 87, 89]
        g2 = [70, 72, 71, 73, 70]
        g3 = [55, 58, 57, 56, 59]
        r = self.service.one_way_anova([g1, g2, g3])
        self.assertTrue(r.significant)
        self.assertLess(r.p_value, 0.05)

    def test_chi_square_independent(self) -> None:
        # 构造一个近似独立的 2x2 列联表。
        observed = [[50, 50], [50, 50]]
        r = self.service.chi_square_independence(observed)
        self.assertAlmostEqual(r.chi2, 0.0, places=6)
        self.assertFalse(r.significant)


class TestEffectSize(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EffectSizeService()

    def test_cohens_d_large(self) -> None:
        a = [80, 82, 85, 78, 81]
        b = [60, 62, 58, 61, 63]
        r = self.service.cohens_d(a, b)
        self.assertGreater(r.value, 0.8)
        self.assertIn("大", r.interpretation)

    def test_cohens_d_zero(self) -> None:
        a = [70, 71, 70, 72, 71]
        b = [70, 71, 70, 72, 71]
        r = self.service.cohens_d(a, b)
        self.assertEqual(r.value, 0.0)

    def test_eta_squared_range(self) -> None:
        r = self.service.eta_squared(50.0, 100.0)
        self.assertAlmostEqual(r.value, 0.5, places=4)


if __name__ == "__main__":
    unittest.main()
