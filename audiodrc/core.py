"""audiodrc 核心 API（初始未实现）。"""


class Compressor:
    def __init__(self, rate, threshold, ratio, knee, attack, release):
        """构造"""
        raise NotImplementedError

    def process(self, samples):
        """处理"""
        raise NotImplementedError

    def gain(self):
        """当前增益"""
        raise NotImplementedError
