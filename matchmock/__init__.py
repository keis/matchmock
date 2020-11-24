'''Hamcrest matchers for mock objects'''

from typing import Any, Collection, Mapping, Sequence, Tuple

from unittest.mock import Mock, _Call
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest.core.matcher import Matcher
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest import (
    equal_to, anything, has_entries, has_item, greater_than)

__all__ = ['called', 'not_called', 'called_once',
           'called_with', 'called_once_with', 'called_n_times']

_Args = Tuple
_Kwargs = Mapping[str, Any]


def describe_call(args: _Args, kwargs: _Kwargs, desc: Description) -> None:
    desc.append_text('(')
    desc.append_list('', ', ', '', args)
    desc.append_text(', ')
    first = True
    for key, value in sorted(kwargs.items()):
        if not first:
            desc.append_text(', ')
        desc.append_text(key)   \
            .append_text('=')  \
            .append_description_of(value)
        first = False
    desc.append_text(')')


class IsCall(BaseMatcher[_Call]):
    '''A matcher that describes a call.

    The positional arguments and keyword arguments are represented with
    individual submatchers.
    '''
    args: Matcher[_Args]
    kwargs: Matcher[_Kwargs]

    def __init__(self, args: Matcher[_Args], kwargs: Matcher[_Kwargs]) -> None:
        self.args = args
        self.kwargs = kwargs

    def _matches(self, item: _Call) -> bool:
        # in python >= 3.8 this can be item.args, item.kwargs
        if len(item) == 3:
            _name, args, kwargs = item
        else:
            args, kwargs = item
        return self.args.matches(args) and self.kwargs.matches(kwargs)

    def describe_mismatch(self, item: _Call, mismatch_description: Description) -> None:
        # in python >= 3.8 this can be item.args, item.kwargs
        if len(item) == 3:
            _name, args, kwargs = item
        else:
            args, kwargs = item
        if self.args.matches(args, mismatch_description):
            self.kwargs.matches(kwargs, mismatch_description)

    def describe_to(self, desc: Description) -> None:
        desc.append_text('(')
        desc.append_description_of(self.args)
        desc.append_text(', ')
        desc.append_description_of(self.kwargs)
        desc.append_text(')')


class IsArgs(BaseMatcher[_Args]):
    matchers: Sequence[Matcher]

    def __init__(self, matchers: Sequence[Matcher]) -> None:
        self.matchers = matchers

    def matches(self, obj: _Args, mismatch_description: Description = None) -> bool:
        md = mismatch_description
        if len(obj) < len(self.matchers):
            if md:
                d = len(self.matchers) - len(obj)
                md.append_text('missing %s arguments' % d)
            return False
        if len(obj) > len(self.matchers):
            if md:
                d = len(obj) - len(self.matchers)
                md.append_text('%s extra arguments' % d)
            return False
        for i, (o, m) in enumerate(zip(obj, self.matchers)):
            if not m.matches(o):
                if md:
                    md.append_text('argument ' + str(i) + ': ')
                    m.describe_mismatch(o, md)
                return False
        return True

    def describe_to(self, desc: Description) -> None:
        desc.append_list('', ', ', '', self.matchers)


class IsKwargs(BaseMatcher[_Kwargs]):
    _value_matchers: Collection[Tuple[str, Matcher]]
    _matcher: Matcher[_Kwargs]

    def __init__(self, value_matchers: Mapping[str, Matcher]) -> None:
        self._value_matchers = value_matchers.items()
        self._matcher = has_entries(value_matchers)

    def matches(self, obj: _Kwargs, mismatch_description: Description = None) -> bool:
        md = mismatch_description
        ok = self._matcher.matches(obj, md)
        if not ok:
            return False

        expected_keys = set(k for k, _ in self._value_matchers)
        actual_keys = set(obj.keys())
        extra_keys = actual_keys - expected_keys
        if len(extra_keys) > 0:
            if md:
                md.append_text('extra keyword argument(s) ') \
                               .append_list('', ', ', '', extra_keys) \
                               .append_text(' given')
            return False

        return True

    def describe_to(self, desc: Description) -> None:
        first = True
        for key, value in self._value_matchers:
            if not first:
                desc.append_text(', ')
            desc.append_text(key)   \
                .append_text('=')  \
                .append_description_of(value)
            first = False


def match_args(args: Sequence[Any]) -> Matcher[_Args]:
    '''Create a matcher for positional arguments'''

    return IsArgs(tuple(wrap_matcher(m) for m in args))


def match_kwargs(kwargs: Mapping[str, Any]) -> Matcher[_Kwargs]:
    '''Create a matcher for keyword arguments'''

    return IsKwargs({k: wrap_matcher(v) for k, v in kwargs.items()})


class IsCalled(BaseMatcher[Mock]):
    '''Matches a mock and asserts the number of calls and parameters'''

    call: Matcher[_Call]
    count: Matcher[int]
    has_call: Matcher[Sequence[_Call]]

    def __init__(self, call: Matcher[_Call], count: Matcher[int]) -> None:
        self.call = call
        self.count = count
        self.has_call = has_item(self.call)

    def _matches(self, item: Mock) -> bool:
        if not self.count.matches(item.call_count):
            return False

        if len(item.call_args_list) == 0:
            return True

        return self.has_call.matches(item.call_args_list)

    def describe_mismatch(self, item: Mock, mismatch_description: Description) -> None:
        if not self.count.matches(item.call_count):
            mismatch_description.append_text(
                'was called %s times' % item.call_count)
            if item.call_count > 0:
                mismatch_description.append_text(' with ')

                for i, call in enumerate(item.call_args_list):
                    if i != 0:
                        mismatch_description.append_text(' and ')
                    describe_call(call[0], call[1], mismatch_description)
            return

        if item.call_count > 0:
            for i, call in enumerate(item.call_args_list):
                if item.call_count > 1:
                    mismatch_description.append_text('in call %s: ' % i)
                self.call.describe_mismatch(call, mismatch_description)
                if i != item.call_count - 1:
                    mismatch_description.append_text(', ')

    def describe_to(self, desc: Description) -> None:
        desc.append_text('Mock called ')
        self.count.describe_to(desc)
        desc.append_text(' times with ')
        self.call.describe_to(desc)


def called() -> Matcher[Mock]:
    '''Match mock that was called one or more times'''

    return IsCalled(anything(), count=greater_than(0))


def called_n_times(n) -> Matcher[Mock]:
    '''Match mock that was called exactly a given number of times'''

    return IsCalled(anything(), count=equal_to(n))


def not_called() -> Matcher[Mock]:
    '''Match mock that was never called'''

    return IsCalled(anything(), count=equal_to(0))


def called_once() -> Matcher[Mock]:
    '''Match mock that was called once regardless of arguments'''

    return IsCalled(anything(), count=equal_to(1))


def called_with(*args, **kwargs) -> Matcher[Mock]:
    '''Match mock has at least one call with the specified arguments'''

    return IsCalled(IsCall(match_args(args), match_kwargs(kwargs)),
                    count=greater_than(0))


def called_once_with(*args, **kwargs) -> Matcher[Mock]:
    '''Match mock that was called once and with the specified arguments'''

    return IsCalled(IsCall(match_args(args), match_kwargs(kwargs)),
                    count=equal_to(1))
