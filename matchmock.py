'''Hamcrest matchers for mock objects'''

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest import (equal_to, anything, has_entries,
                      has_item, greater_than)

__all__ = ['called', 'not_called', 'called_once',
           'called_with', 'called_once_with']


def describe_call(args, kwargs, desc):
    desc.append_text('(')
    if isinstance(args, BaseMatcher):
        desc.append_description_of(args)
    else:
        desc.append_list('', ', ', '', args)
    desc.append_text(', ')
    if isinstance(kwargs, BaseMatcher):
        desc.append_description_of(kwargs)
    else:
        first = True
        for key, value in sorted(kwargs.items()):
            if not first:
                desc.append_text(', ')
            desc.append_text(key)   \
                .append_text('=')  \
                .append_description_of(value)
            first = False
    desc.append_text(')')


class Call(BaseMatcher):
    '''A matcher that describes a call.

    The positional arguments and keyword arguments are represented with
    individual submatchers.
    '''

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def _matches(self, item):
        return self.args.matches(item[0]) and self.kwargs.matches(item[1])

    def describe_mismatch(self, item, mismatch_description):
        args, kwargs = item
        return (self.args.matches(args, mismatch_description) and
                self.kwargs.matches(kwargs, mismatch_description))

    def describe_to(self, desc):
        describe_call(self.args, self.kwargs, desc)


class IsArgs(BaseMatcher):
    def __init__(self, matchers):
        self.matchers = tuple(matchers)

    def matches(self, obj, mismatch_description=None):
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

    def describe_to(self, desc):
        desc.append_list('', ', ', '', self.matchers)


class IsKwargs(BaseMatcher):
    def __init__(self, matchers):
        self._matcher = has_entries(matchers)
        self._expected_keys = set(matchers.keys())

    def matches(self, obj, mismatch_description=None):
        md = mismatch_description
        ok = self._matcher.matches(obj, md)
        if not ok:
            return False

        actual_keys = set(obj.keys())
        extra_keys = actual_keys - self._expected_keys
        if len(extra_keys) > 0:
            if md:
                md.append_text('extra keyword argument(s) ') \
                               .append_list('', ', ', '', extra_keys) \
                               .append_text(' given')
            return False

        return True

    def describe_to(self, desc):
        first = True
        for key, value in self._matcher.value_matchers:
            if not first:
                desc.append_text(', ')
            desc.append_text(key)   \
                .append_text('=')  \
                .append_description_of(value)
            first = False


def match_args(args):
    '''Create a matcher for positional arguments'''

    return IsArgs(wrap_matcher(m) for m in args)


def match_kwargs(kwargs):
    '''Create a matcher for keyword arguments'''

    return IsKwargs({k: wrap_matcher(v) for k, v in kwargs.items()})


class Called(BaseMatcher):
    '''Matches a mock and asserts the number of calls and parameters'''

    def __init__(self, call, count=None):
        self.call = call
        self.count = count

    def _matches(self, item):
        if not self.count.matches(item.call_count):
            return False

        if len(item.call_args_list) == 0:
            return True

        return bool(has_item(self.call).matches(item.call_args_list))

    def describe_mismatch(self, item, mismatch_description):
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

    def describe_to(self, desc):
        desc.append_text('Mock called ')
        self.count.describe_to(desc)
        desc.append_text(' times with ')
        self.call.describe_to(desc)


def called():
    '''Match mock that was called one or more times'''

    return Called(anything(), count=greater_than(0))


def not_called():
    '''Match mock that was never called'''

    return Called(anything(), count=equal_to(0))


def called_once():
    '''Match mock that was called once regardless of arguments'''

    return Called(anything(), count=equal_to(1))


def called_with(*args, **kwargs):
    '''Match mock has at least one call with the specified arguments'''

    return Called(Call(match_args(args), match_kwargs(kwargs)),
                  count=greater_than(0))


def called_once_with(*args, **kwargs):
    '''Match mock that was called once and with the specified arguments'''

    return Called(Call(match_args(args), match_kwargs(kwargs)),
                  count=equal_to(1))
