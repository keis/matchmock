import pytest
from mock import Mock
from hamcrest import assert_that, instance_of, equal_to, starts_with
from hamcrest.core.string_description import StringDescription
from matchmock import (
    called, not_called, called_once, called_with, called_n_times)


@pytest.fixture
def desc():
    return StringDescription()


def test_called_ok() -> None:
    matcher = called()
    mock = Mock()
    mock()

    ok = matcher.matches(mock)
    assert_that(ok, equal_to(True))


def test_called_member_ok() -> None:
    matcher = called()
    mock = Mock()
    mock.fun()

    ok = matcher.matches(mock.fun)
    assert_that(ok, equal_to(True))


def test_called_ok_twice() -> None:
    matcher = called()
    mock = Mock()
    mock()
    mock()

    ok = matcher.matches(mock)
    assert_that(ok, equal_to(True))


def test_called_ok_explicitly_twice() -> None:
    matcher = called_n_times(2)
    mock = Mock()
    mock()
    mock()

    ok = matcher.matches(mock)
    assert_that(ok, equal_to(True))


def test_called_ok_explicitly_twice_fail(desc) -> None:
    expected = 'was called 3 times'
    matcher = called_n_times(2)
    mock = Mock()
    mock()
    mock()
    mock()

    ok = matcher.matches(mock, desc)
    assert_that(ok, equal_to(False))
    assert_that(str(desc), starts_with(expected))


def test_called_description(desc) -> None:
    expected = 'Mock called a value greater than <0> times with ANYTHING'
    matcher = called()
    matcher.describe_to(desc)
    assert_that(str(desc), equal_to(expected))


def test_called_fail(desc) -> None:
    expected = 'was called 0 times'
    matcher = called()
    mock = Mock()

    ok = matcher.matches(mock, desc)
    assert_that(ok, equal_to(False))
    assert_that(str(desc), equal_to(expected))


def test_not_called_ok() -> None:
    matcher = not_called()
    mock = Mock()

    ok = matcher.matches(mock)
    assert_that(ok, equal_to(True))


def test_not_called_description(desc) -> None:
    matcher = not_called()
    expected = 'Mock called <0> times with ANYTHING'
    matcher.describe_to(desc)
    assert_that(str(desc), equal_to(expected))


def test_not_called_fail(desc) -> None:
    matcher = not_called()
    expected = "was called 1 times with ('foo', )"

    mock = Mock()
    mock('foo')

    ok = matcher.matches(mock, desc)

    assert_that(ok, equal_to(False))
    assert_that(str(desc), equal_to(expected))


def test_called_once_ok() -> None:
    matcher = called_once()
    mock = Mock()
    mock('foo')

    ok = matcher.matches(mock)

    assert_that(ok, equal_to(True))


def test_called_once_description(desc) -> None:
    expected = 'Mock called <1> times with ANYTHING'
    matcher = called_once()
    matcher.describe_to(desc)
    assert_that(str(desc), equal_to(expected))


def test_called_once_fail_not_called(desc) -> None:
    expected = 'was called 0 times'
    matcher = called_once()
    mock = Mock()

    ok = matcher.matches(mock, desc)

    assert_that(ok, equal_to(False))
    assert_that(str(desc), equal_to(expected))


def test_called_once_fail_called_twice(desc) -> None:
    expected = "was called 2 times with ('foo', ) and ('bar', )"
    matcher = called_once()
    mock = Mock()
    mock('foo')
    mock('bar')

    ok = matcher.matches(mock, desc)

    assert_that(ok, equal_to(False))
    assert_that(str(desc), equal_to(expected))


def test_called_with_ok() -> None:
    matcher = called_with('foo', instance_of(int))
    mock = Mock()
    mock('foo', 5)

    ok = matcher.matches(mock)
    assert_that(ok, equal_to(True))


def test_called_with_ok_kwargs() -> None:
    matcher = called_with(x='foo', y=instance_of(int))
    mock = Mock()
    mock(x='foo', y=5)

    ok = matcher.matches(mock)
    assert_that(ok, equal_to(True))


def test_called_with_ok_multi() -> None:
    matcher = called_with('foo', instance_of(int))
    mock = Mock()
    mock('baz')
    mock('foo', 5)
    mock('bar', 5)

    ok = matcher.matches(mock)
    assert_that(ok, equal_to(True))


def test_called_with_description(desc) -> None:
    expected = ("Mock called a value greater than <0> times with " +
                "('foo', an instance of int, )")
    matcher = called_with('foo', instance_of(int))

    matcher.describe_to(desc)
    assert_that(str(desc), equal_to(expected))


def test_called_with_failed(desc) -> None:
    expected = "argument 1: was 'bar'"
    matcher = called_with('foo', instance_of(int))
    mock = Mock()
    mock('foo', 'bar')

    ok = matcher.matches(mock, desc)
    assert_that(ok, equal_to(False))
    assert_that(str(desc), equal_to(expected))


def test_called_with_failed_multi(desc) -> None:
    expected = "in call 0: argument 1: was 'bar', in call 1: 1 extra arguments"
    matcher = called_with('foo', instance_of(int))
    mock = Mock()
    mock('foo', 'bar')
    mock('foo', 'bar', 'baz')

    ok = matcher.matches(mock, desc)
    assert_that(ok, equal_to(False))
    assert_that(str(desc), equal_to(expected))


def test_called_with_kwarg_failed(desc) -> None:
    expected = "value for 'foo' was 'baz'"
    matcher = called_with(foo='bar')
    mock = Mock()
    mock(foo='baz')

    ok = matcher.matches(mock, desc)
    assert_that(ok, equal_to(False))
    assert_that(str(desc), equal_to(expected))


def test_called_with_extra_arg(desc) -> None:
    expected = "1 extra arguments"
    matcher = called_with('spam')
    mock = Mock()
    mock('spam', 'bar')

    ok = matcher.matches(mock, desc)
    assert_that(ok, equal_to(False))
    assert_that(str(desc), equal_to(expected))


def test_called_with_extra_kwarg(desc) -> None:
    expected = "extra keyword argument(s) 'foo' given"
    matcher = called_with('spam')
    mock = Mock()
    mock('spam', foo='bar')

    ok = matcher.matches(mock, desc)
    assert_that(ok, equal_to(False))
    assert_that(str(desc), equal_to(expected))
