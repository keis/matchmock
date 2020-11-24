from hamcrest import assert_that, equal_to, has_entries
from hamcrest.core.string_description import StringDescription
from matchmock import IsCall, match_args, match_kwargs
from unittest.mock import call


def test_matching_call():
    m = IsCall(match_args(('foo',)), match_kwargs({}))
    value = call('foo')
    print(value)
    assert_that(m.matches(value), equal_to(True))


def test_mismatching_call():
    m = IsCall(match_args(('foo',)), match_kwargs({}))
    value = call('bar')
    assert_that(m.matches(value), equal_to(False))


def test_describe_self():
    m = IsCall(match_args(('foo',)), match_kwargs({}))
    s = StringDescription()
    m.describe_to(s)
    assert_that(str(s), equal_to("('foo', )"))


def test_describe_mismatch():
    m = IsCall(match_args(('foo',)), match_kwargs({}))
    value = call('bar')
    s = StringDescription()
    m.describe_mismatch(value, s)
    assert_that(str(s), equal_to("argument 0: was 'bar'"))


def test_args_mismatch_complex():
    m = IsCall(match_args([has_entries(name='foo')]), match_kwargs({}))
    value = call({'name': 'baz'})
    s = StringDescription()
    m.matches(value, s)
    assert_that(str(s), equal_to("argument 0: value for 'name' was 'baz'"))
