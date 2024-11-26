import pytest

def my_complex_func(x):
    return x + 1

@pytest.mark.parametrize("arg1", (1,2))
def test_my_complex_func(arg1):
    assert my_complex_func(arg1) == (arg1+1)