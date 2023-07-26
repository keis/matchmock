from hamcrest import assert_that, equal_to, has_entries
from hamcrest.core.string_description import StringDescription
from matchmock import IsCall, match_args, match_kwargs
from unittest.mock import call


def test_matching_call() -> None:
    m = IsCall(match_args(('foo',)), match_kwargs({}))
    value = call('foo')
    assert_that(m.matches(value), equal_to(True))


def test_mismatching_call() -> None:
    m = IsCall(match_args(('foo',)), match_kwargs({}))
    value = call('bar')
    assert_that(m.matches(value), equal_to(False))


def test_describe_self() -> None:
    m = IsCall(match_args(('foo',)), match_kwargs({}))
    s = StringDescription()
    m.describe_to(s)
    assert_that(str(s), equal_to("('foo', )"))


def test_describe_self_with_kwargs() -> None:
    m = IsCall(match_args(('foo',)), match_kwargs({'key': 'value'}))
    s = StringDescription()
    m.describe_to(s)
    assert_that(str(s), equal_to("('foo', key='value')"))


def test_describe_mismatch() -> None:
    m = IsCall(match_args(('foo',)), match_kwargs({}))
    value = call('bar')
    s = StringDescription()
    m.describe_mismatch(value, s)
    assert_that(str(s), equal_to("argument 0: was 'bar'"))


def test_describe_mismatch_kwargs() -> None:
    m = IsCall(match_args(('foo',)), match_kwargs({'key': 'value'}))
    value = call('foo', key='VALUE')
    s = StringDescription()
    m.describe_mismatch(value, s)
    assert_that(str(s), equal_to("value for 'key' was 'VALUE'"))


def test_args_mismatch_complex() -> None:
    m = IsCall(match_args([has_entries(name='foo')]), match_kwargs({}))
    value = call({'name': 'baz'})
    s = StringDescription()
    m.matches(value, s)
    assert_that(str(s), equal_to("argument 0: value for 'name' was 'baz'"))
