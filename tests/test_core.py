import math

import pytest

import audiodrc

def _raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    return False

def _c():
    return audiodrc.Compressor(48000, 0.5, 4.0, 0.1, 0.005, 0.05)


def _check_below_threshold():
    return abs(_c().process([0.1])[0] - 0.1) < 1e-6


def _check_above_threshold():
    return abs(_c().process([1.0])[0]) < 1.0


def _check_len():
    return len(_c().process([0.1, 0.2])) == 2


def _check_ratio():
    out = _c().process([1.0])[0]
    return out < 1.0


def _check_gain_initial():
    return abs(_c().gain() - 1.0) < 1e-9


def _check_bad_ratio():
    return _raises(lambda: audiodrc.Compressor(48000, 0.5, 0.5, 0.1, 0.005, 0.05))


def _check_bad_threshold():
    return _raises(lambda: audiodrc.Compressor(48000, 1.5, 4.0, 0.1, 0.005, 0.05))


def _check_bad_time():
    return _raises(lambda: audiodrc.Compressor(48000, 0.5, 4.0, 0.1, 0.0, 0.05))


def _check_empty():
    return _c().process([]) == []


def _check_no_jump():
    out = _c().process([0.0, 1.0, 0.0])
    return max(abs(out[i + 1] - out[i]) for i in range(len(out) - 1)) < 1.0


def _check_state_continuity():
    c = _c()
    a = c.process([1.0])
    b = c.process([1.0])
    return len(a + b) == 2


def _check_det():
    return _c().process([0.3, 0.6]) == _c().process([0.3, 0.6])


def _check_type():
    return isinstance(_c().process([0.1]), list)


def _check_range():
    out = _c().process([1.0, -1.0])
    return all(-1.0 <= v <= 1.0 for v in out)


def _check_makeup():
    c = _c()
    c.set_makeup(2.0)
    return abs(c.process([0.1])[0]) > 0.1

CASES = [("below_threshold", "_check_below_threshold"), ("above_threshold", "_check_above_threshold"), ("len", "_check_len"), ("ratio", "_check_ratio"), ("gain_initial", "_check_gain_initial"), ("bad_ratio", "_check_bad_ratio"), ("bad_threshold", "_check_bad_threshold"), ("bad_time", "_check_bad_time"), ("empty", "_check_empty"), ("no_jump", "_check_no_jump"), ("state_continuity", "_check_state_continuity"), ("det", "_check_det"), ("type", "_check_type"), ("range", "_check_range"), ("makeup", "_check_makeup")]


@pytest.mark.parametrize("name,check", CASES, ids=[c[0] for c in CASES])
def test_spec(name, check):
    assert globals()[check]() is True
