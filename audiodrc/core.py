"""audiodrc 核心 API：动态范围压缩器（软拐点 + attack/release 包络）。"""

import math

__all__ = ["Compressor"]


def _num(name, value):
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise ValueError("%s 必须是数值" % name) from None
    if not math.isfinite(v):
        raise ValueError("%s 必须是有限数值" % name)
    return v


class Compressor:
    def __init__(self, rate, threshold, ratio, knee, attack, release):
        rate = _num("rate", rate)
        threshold = _num("threshold", threshold)
        ratio = _num("ratio", ratio)
        knee = _num("knee", knee)
        attack = _num("attack", attack)
        release = _num("release", release)
        if rate <= 0.0:
            raise ValueError("rate 必须为正")
        if not 0.0 < threshold <= 1.0:
            raise ValueError("threshold 必须在 (0, 1] 内")
        if ratio < 1.0:
            raise ValueError("ratio 必须 >= 1")
        if knee < 0.0:
            raise ValueError("knee 必须 >= 0")
        if attack <= 0.0:
            raise ValueError("attack 必须为正")
        if release <= 0.0:
            raise ValueError("release 必须为正")

        self.rate = rate
        self.threshold = threshold
        self.ratio = ratio
        self.knee = knee
        self.attack = attack
        self.release = release

        # attack/release 一阶平滑系数（时间常数，单位秒）
        self._ca = math.exp(-1.0 / (attack * rate))
        self._cr = math.exp(-1.0 / (release * rate))
        self._gain = 1.0
        self._makeup = 1.0

        # 静态增益曲线（dB 域软拐点，拐点宽度 knee 单位为 dB）
        half = knee / 2.0
        self._lo = threshold * 10.0 ** (-half / 20.0)
        self._hi = threshold * 10.0 ** (half / 20.0)
        self._inv_t = 1.0 / threshold
        self._slope = 1.0 / ratio - 1.0
        self._tdb = 20.0 * math.log10(threshold)
        self._knee_c = self._slope / (2.0 * knee) if knee > 0.0 else 0.0
        self._half = half

    def process(self, samples):
        out = []
        append = out.append
        g = self._gain
        ca = self._ca
        cr = self._cr
        oca = 1.0 - ca
        ocr = 1.0 - cr
        makeup = self._makeup
        lo = self._lo
        hi = self._hi
        inv_t = self._inv_t
        slope = self._slope
        tdb = self._tdb
        kc = self._knee_c
        half = self._half
        log10 = math.log10
        isfinite = math.isfinite
        for x in samples:
            if not isfinite(x):
                raise ValueError("样本必须是有限数值")
            ax = x if x >= 0.0 else -x
            if ax <= lo:
                gt = 1.0
            elif ax >= hi:
                # 硬压缩区：gain = (ax / threshold) ** (1/ratio - 1)
                gt = (ax * inv_t) ** slope
            else:
                # 软拐点区（dB 域二次插值，边界处值与斜率均连续）
                xdb = 20.0 * log10(ax)
                gdb = kc * (xdb - tdb + half) ** 2
                gt = 10.0 ** (gdb * 0.05)
            # 增益减小时用 attack，增大时用 release，保证无爆音
            if gt < g:
                g = ca * g + oca * gt
            else:
                g = cr * g + ocr * gt
            append(x * g * makeup)
        self._gain = g
        return out

    def gain(self):
        """当前压缩增益（不含 makeup）。"""
        return self._gain

    def set_makeup(self, makeup):
        makeup = _num("makeup", makeup)
        if makeup < 0.0:
            raise ValueError("makeup 必须 >= 0")
        self._makeup = makeup
