"""统计工具单元测试。"""
from __future__ import annotations

import unittest

from score_analysis.utils.statistics import (
    cronbach_alpha,
    kurtosis,
    mean,
    median,
    percentile,
    quartiles,
    skewness,
    stddev,
    variance,
)


class TestBasic(unittest.TestCase):
    def test_mean(self) -> None:
        self.assertAlmostEqual(mean([1, 2, 3, 4, 5]), 3.0)

    def test_median_odd(self) -> None:
        self.assertEqual(median([3, 1, 2]), 2.0)

    def test_median_even(self) -> None:
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_variance_sample(self) -> None:
        # 数据 2,4,4,4,5,5,7,9 的样本方差为 32/7。
        self.assertAlmostEqual(variance([2, 4, 4, 4, 5, 5, 7, 9]), 32 / 7)

    def test_stddev(self) -> None:
        self.assertAlmostEqual(stddev([1, 1, 1]), 0.0)


class TestPercentile(unittest.TestCase):
    def test_quartiles(self) -> None:
        q1, q2, q3 = quartiles([1, 2, 3, 4, 5])
        self.assertEqual(q2, 3.0)
        self.assertLess(q1, q2)
        self.assertGreater(q3, q2)

    def test_percentile_extremes(self) -> None:
        self.assertEqual(percentile([1, 2, 3], 0), 1.0)
        self.assertEqual(percentile([1, 2, 3], 100), 3.0)


class TestShape(unittest.TestCase):
    def test_skewness_symmetric(self) -> None:
        # 对称分布偏度接近 0。
        self.assertAlmostEqual(skewness([1, 2, 3, 4, 5]), 0.0, places=6)

    def test_kurtosis_normalish(self) -> None:
        # [1,2,3,4,5] 均匀离散分布的超额峰度为 -1.2。
        self.assertAlmostEqual(kurtosis([1, 2, 3, 4, 5]), -1.2, places=1)


class TestReliability(unittest.TestCase):
    def test_cronbach_perfect_consistency(self) -> None:
        # 各题得分与总分完全线性相关时，信度接近 1。
        item_matrix = [[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12]]
        alpha = cronbach_alpha(item_matrix)
        self.assertGreater(alpha, 0.9)


if __name__ == "__main__":
    unittest.main()
