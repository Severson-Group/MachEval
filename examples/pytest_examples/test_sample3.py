import pytest
import numpy as np

def my_complex_func(x):
    return x + 1

@pytest.mark.parametrize("arg1", np.arange(0,10,1))
def test_my_complex_func(arg1):
    assert my_complex_func(arg1) == (arg1+1)