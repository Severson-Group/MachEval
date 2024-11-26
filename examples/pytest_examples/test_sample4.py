import pytest
import numpy as np
import time
import random

def my_complex_func(x):
    # Sleep for 0 to 1 seconds
    time.sleep(random.random())
    return x + 1

@pytest.mark.slow
@pytest.mark.parametrize("arg1", np.arange(0,10000,1))
def test_my_complex_func(arg1):
    assert my_complex_func(arg1) == (arg1+1)