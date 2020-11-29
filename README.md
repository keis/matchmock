# matchmock

[![PyPI Version][pypi-image]](https://pypi.python.org/pypi?name=matchmock&:action=display)
[![Build Status][travis-image]](https://travis-ci.org/keis/matchmock)
[![Coverage Status][coveralls-image]](https://coveralls.io/r/keis/matchmock?branch=master)

[Hamcrest][hamcrest] matchers for [mock][mock] objects.

Starting from version 2.0.0 **python2 is no longer supported** the 1.x series
will remain supported but no new features will be added.

## Example

```
    f = Mock()
    f.method('foo', 'bar')

    assert_that(f.method, called_once_with(anything(), 'bar')
```

## Matchers

* `called` - match mock that was called one or more times
* `not_called` - match mock that was never called
* `called_once` - match mock that was called once regardless of arguments
* `called_with` - match mock has at least one call with the specified arguments
* `called_once_with` - match mock that was called once and with the specified arguments
* `called_n_times` - match mock that was called number of times.

[hamcrest]: http://hamcrest.org/
[mock]: https://docs.python.org/3/library/unittest.mock.html
[pypi-image]: https://img.shields.io/pypi/v/matchmock.svg?style=flat
[travis-image]: https://img.shields.io/travis/keis/matchmock.svg?style=flat
[coveralls-image]: https://img.shields.io/coveralls/keis/matchmock.svg?style=flat
