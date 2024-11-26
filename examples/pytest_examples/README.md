# Tutorial on `pytest`

Main website: `pytest.org` or [docs.pytest.org](https://docs.pytest.org/en/7.4.x/)

## Installing

Follow guide on website.

It uses `pip`, but there is probably a conda version...

## Basic test file

Each file is a test. `test_***.py` or `***_test.py` are tests.

Inside each test, define `test_foo()` functions for each test.

The test functions should use `assert` statements.

Each test should be short and sweet. Remember, you can always make another test case!

> See `test_sample1.py`

## Running tests

After creating a test, run it from the command line:

`$ pytest`

By default, pytest will look in the current directory and sub directories for the test files, and run them all.

## Parametrize Tests

Use python decorators with pytest to run the same test case many times with different arguments.

> See `test_sample2.py`

Or, use `numpy` to generate large inputs for tests

> See `test_sample3.py`

## Mark Tests

Metadata for tests is denoted by `mark`ing them in the source file.

`@pytest.mark.foo`

This allows you to only run a subset of tests. These markings are totally customizable.

For example, we could mark:

- `jmag` for all tests using JMAG
- `fea` for FEA tests (JMAG, FEMM, etc)
- `slow` for slow tests (perhaps over 20 seconds expected time)

Must define project `mark`ings in the `pytest.ini` file.

> See `test_sample4.py` and `pytest.ini`

## Run Marked Tests

Run only the slow tests using 128 workers (run tests in parallel):

`$ pytest -k slow -n 128`

Run all not slow tests using 8 workers

`$ pytest -k "not slow" -n 8`

## Nice to Know

Run tests on multiple `N` workers (all completely independent from each other):

`$ python ... -n N`

Run tests matching certain keyword:

`$ python ... -k foo_bar`

Print out available markers:

`$ python --markers`
