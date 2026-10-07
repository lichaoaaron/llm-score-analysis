"""概率分布与累积分布函数模块。

为假设检验提供 Student-t 分布、F 分布、卡方分布的累积分布函数（CDF），
进而计算双侧/单侧 p 值。全部基于 Lanczos 伽马函数、连分数不完全 beta 函数
与不完全伽马函数手写实现，不依赖 scipy/statsmodels 等第三方统计包。

参考实现：Numerical Recipes (betacf/gammp) 与 Lanczos 伽马逼近。
"""
from __future__ import annotations

import math
from typing import List

# ---------------------------------------------------------------------------
# 伽马函数与对数伽马函数（Lanczos 逼近）
# ---------------------------------------------------------------------------
_LANCZOS_G = 7
_LANCZOS_C: List[float] = [
    0.99999999999980993,
    676.5203681218851,
    -1259.1392167224028,
    771.32342877765313,
    -176.61502916214059,
    12.507343278686905,
    -0.13857109526572012,
    9.9843695780195716e-6,
    1.5056327351493116e-7,
]


def gamma(x: float) -> float:
    """伽马函数 Γ(x)。对 x<0.5 用反射公式。"""
    if x < 0.5:
        return math.pi / (math.sin(math.pi * x) * gamma(1.0 - x))
    x -= 1.0
    a = _LANCZOS_C[0]
    t = x + _LANCZOS_G + 0.5
    for i in range(1, len(_LANCZOS_C)):
        a += _LANCZOS_C[i] / (x + i)
    return math.sqrt(2 * math.pi) * (t ** (x + 0.5)) * math.exp(-t) * a


_LOG_GAMMA_COEF: List[float] = [
    76.18009172947146,
    -86.50532032941677,
    24.01409824083091,
    -1.231739572450155,
    0.1208650973866179e-2,
    -0.5395239384953e-5,
]


def log_gamma(x: float) -> float:
    """自然对数伽马函数 lnΓ(x)，用于大参数时的稳定计算。"""
    y = x
    tmp = x + 5.5
    tmp -= (x + 0.5) * math.log(tmp)
    ser = 1.000000000190015
    for c in _LOG_GAMMA_COEF:
        y += 1.0
        ser += c / y
    return -tmp + math.log(2.5066282746310005 * ser / x)


# ---------------------------------------------------------------------------
# 不完全 beta 函数（连分数展开）
# ---------------------------------------------------------------------------
def _betacf(a: float, b: float, x: float) -> float:
    """连分数形式的 beta 函数展开（Numerical Recipes betacf）。"""
    max_iter = 200
    eps = 3.0e-14
    fp_min = 1.0e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fp_min:
        d = fp_min
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fp_min:
            d = fp_min
        c = 1.0 + aa / c
        if abs(c) < fp_min:
            c = fp_min
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fp_min:
            d = fp_min
        c = 1.0 + aa / c
        if abs(c) < fp_min:
            c = fp_min
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def beta_inc(x: float, a: float, b: float) -> float:
    """正则化不完全 beta 函数 I_x(a, b)，取值 [0, 1]。"""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    log_bt = (
        log_gamma(a + b) - log_gamma(a) - log_gamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    bt = math.exp(log_bt)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


# ---------------------------------------------------------------------------
# 不完全伽马函数（用于卡方分布 CDF）
# ---------------------------------------------------------------------------
def _gser(a: float, x: float) -> float:
    """不完全伽马函数的级数形式（适用于 x < a+1）。"""
    gln = log_gamma(a)
    ap = a
    s = 1.0 / a
    delta = s
    for _ in range(200):
        ap += 1.0
        delta *= x / ap
        s += delta
        if abs(delta) < abs(s) * 1.0e-14:
            break
    return s * math.exp(-x + a * math.log(x) - gln)


def _gcf(a: float, x: float) -> float:
    """不完全伽马函数的连分数形式（适用于 x >= a+1）。"""
    gln = log_gamma(a)
    b = x + 1.0 - a
    c = 1.0e300
    d = 1.0 / b
    h = d
    for i in range(1, 200):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1.0e-300:
            d = 1.0e-300
        c = b + an / c
        if abs(c) < 1.0e-300:
            c = 1.0e-300
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1.0e-14:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def gamma_inc(a: float, x: float) -> float:
    """正则化不完全伽马函数 P(a, x)，取值 [0, 1]。"""
    if x <= 0.0 or a <= 0.0:
        return 0.0
    if x < a + 1.0:
        return _gser(a, x)
    return 1.0 - _gcf(a, x)


# ---------------------------------------------------------------------------
# 累积分布函数与 p 值
# ---------------------------------------------------------------------------
def t_cdf(t: float, df: float) -> float:
    """Student-t 分布的累积分布函数 P(T <= t)。"""
    if df <= 0:
        return 0.0
    x = df / (df + t * t)
    ib = beta_inc(x, df / 2.0, 0.5)
    if t > 0:
        return 1.0 - 0.5 * ib
    return 0.5 * ib


def t_p_value(t: float, df: float, two_sided: bool = True) -> float:
    """由 t 统计量计算 p 值，默认双侧。"""
    p = 2.0 * (1.0 - t_cdf(abs(t), df)) if two_sided else 1.0 - t_cdf(t, df)
    return min(max(p, 0.0), 1.0)


def f_cdf(f: float, df1: float, df2: float) -> float:
    """F 分布的累积分布函数 P(F <= f)。"""
    if f <= 0 or df1 <= 0 or df2 <= 0:
        return 0.0
    x = df1 * f / (df1 * f + df2)
    return beta_inc(x, df1 / 2.0, df2 / 2.0)


def f_p_value(f: float, df1: float, df2: float) -> float:
    """由 F 统计量计算右尾 p 值。"""
    return min(max(1.0 - f_cdf(f, df1, df2), 0.0), 1.0)


def chi2_cdf(x: float, df: float) -> float:
    """卡方分布的累积分布函数 P(X² <= x)。"""
    if x < 0 or df <= 0:
        return 0.0
    return gamma_inc(df / 2.0, x / 2.0)


def chi2_p_value(x: float, df: float) -> float:
    """由卡方统计量计算右尾 p 值。"""
    return min(max(1.0 - chi2_cdf(x, df), 0.0), 1.0)


def normal_cdf(z: float) -> float:
    """标准正态分布的累积分布函数（Abramowitz-Stegun 近似）。"""
    if z < -8.0:
        return 0.0
    if z > 8.0:
        return 1.0
    # Hart 的 erf 近似。
    sign = 1.0 if z >= 0 else -1.0
    x = abs(z)
    t = 1.0 / (1.0 + 0.2316419 * x)
    poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    phi = 1.0 - 0.3989422804014327 * math.exp(-x * x / 2.0) * poly
    return phi if sign > 0 else 1.0 - phi
