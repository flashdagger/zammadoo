from zammadoo.utils import YieldCounter


def test_yield_counter():
    rng = range(123)
    counter = YieldCounter()
    assert any((_n > 77 for _n in counter(rng))) is True
    assert counter.yielded == 79

    assert any((_n < 0 for _n in counter(rng))) is False
    assert counter.yielded == 123

    for _ in counter(()):
        pass
    assert counter.yielded == 0

    next(iter(counter([1, 2, 3])))
    assert counter.yielded == 1
