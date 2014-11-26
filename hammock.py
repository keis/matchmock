from hamcrest.core.base_matcher import BaseMatcher
from hamcrest import contains, equal_to, all_of, anything, has_entry


def match_args(args):
    return contains(*args)


def match_kwargs(kwargs):
    return all_of(*[has_entry(k, v) for k, v in kwargs.items()])


class Called(BaseMatcher):
    def __init__(self, args, kwargs, count=None):
        self.args = args
        self.kwargs = kwargs
        self.count = count

    def _matches(self, item):
        if self.count is not None and item.call_count != self.count:
            return False

        if item.call_args is None:
            return True

        args, kwargs = item.call_args
        if not self.args.matches(args):
            return False

        return self.kwargs.matches(kwargs)

    def describe_call(self, args, kwargs, desc):
        desc.append_description_of(args)
        desc.append_text(', ')
        desc.append_description_of(kwargs)

    def describe_mismatch(self, item, mismatch_description):
        if self.count is not None and item.call_count != self.count:
            mismatch_description.append_text(
                'was called %s times' % item.call_count)
        else:
            mismatch_description.append_text('was called with ')
            self.describe_call(item.call_args[0],
                               item.call_args[1],
                               mismatch_description)

    def describe_to(self, desc):
        desc.append_text('Mock called with ')
        self.describe_call(self.args, self.kwargs, desc)
        desc.append_text(' %s times' % self.count)


def not_called():
    return Called(anything(), anything(), count=0)


def called_once():
    return Called(anything(), anything(), count=1)


def called_with(*args, **kwargs):
    return Called(match_args(args), match_kwargs(kwargs))


def called_once_with(*args, **kwargs):
    return Called(match_args(args), match_kwargs(kwargs), count=1)
