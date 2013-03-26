#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python

"""
Freeze the state of data-structures and objects for data-analysis or testing
(diffing data-structures). Frozen data-structures consist of only tuples
and these are comparable/sortable/hashable. The freeze method can be used
for many purposes for example implement __hash__ for your complex object
very fast. freeze_stable and flatten are usable for testing and analysis.

Authors: Jean-Louis Fuchs <ganwell@fangorn.ch> https://github.com/ganwell

Run doctests by with "python lib/freeze.py"
"""

# Copyright (c) 2012, Adfinis SyGroup AG
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Adfinis SyGroup AG nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS";
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Adfinis SyGroup AG BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import six
import pickle
import pprint
import sys
import difflib

__all__ = [
    "freeze",
    "freeze_fast",
    "freeze_stable",
    "tree_diff_assert",
    "stable_hash",
    "recursive_hash",
    "tree_diff",
    "flatten",
    "frozen_equal_assert",
    "pickle_protocol",
    "vformat",
    "transparent_repr"
]


# Setting the pickle protocol python2/3 compat
try:
    pickle_protocol = pickle.DEFAULT_PROTOCOL
except:
    pickle_protocol = pickle.HIGHEST_PROTOCOL

try:
    _ignore_types = (six.string_types, tuple, bytes)
except:
    _ignore_types = (six.string_types, tuple)

try:
    _string_types = (six.string_types,  bytes)
except:
    _string_types = (six.string_types)

_builtin_function_or_method_type = type(dict().get)


# At the moment the freeze variants don't share code. My merged version of
# freeze was quite slow. Unit I come up with a better solution all freeze
# variants have to be maintained.
def freeze(data_structure, stringify=False):
    """Freezing a data-structure makes all items tuples and therefore
    all levels are comparable/hashable/sortable. It has cycle detection
    and will freeze any kind of python object.

    :param   data_structure: The structure to convert
    :param        stringify: Stringify all leaves
    :type         stringify: bool

    >>> freeze([
    ...     'a',
    ...     [3, 4],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ...     []
    ... ])
    ('a', (3, 4), (('a', (3, (('w', ((2, 3, 5), '3', 4)),))),), ())

    >>> freeze([
    ...     [],
    ...     'a',
    ...     [3, 4],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ... ])
    ((), 'a', (3, 4), (('a', (3, (('w', ((2, 3, 5), '3', 4)),))),))

    >>> b"sdf" == freeze({3: b"sdf", 4: 245234534})[0][1]
    True

    >>> testdata = json.loads(
    ...     gzip.open("testdata.json.gz", "r").read().decode()
    ... )

    >>> freeze(testdata) == freeze_fast(testdata)
    True

    Hash anything!

    >>> a = freeze(sys)
    >>> len(a) > 0
    True
    >>> hash(a) != None
    True
    """

    identity_set = set()

    def freeze_helper(data_structure):
        # Cycle detection
        idd = id(data_structure)
        if idd in identity_set:
            # We do not recurse into dictizable objects
            if hasattr(data_structure, "__dict__"):
                return "%s at 0x%d" % (type(data_structure), idd)
            # We do not recurse into containers
            tlen = -1
            try:
                tlen = len(data_structure)
            except:
                pass
            if tlen != -1:
                # Except string and tuples
                if not isinstance(data_structure, _ignore_types):
                    return "%s at 0x%d" % (type(data_structure), idd)
        else:
            identity_set.add(idd)
        # Dictize if possible (support objects)
        try:
            data_structure = data_structure.__dict__
        except:
            pass
        # Itemize if needed
        try:
            data_structure = data_structure.items()
        except:
            pass
        # We don't freeze strings
        if not isinstance(data_structure, _string_types):
            tlen = -1
            # If item has a length we frezze it
            try:
                tlen = len(data_structure)
            except:
                pass
            if tlen != -1:
                return tuple([freeze_helper(x) for x in data_structure])
        # To guarantee that the result is hashable we do not return
        # builtin_function_or_method
        if stringify or isinstance(
            data_structure,
            _builtin_function_or_method_type
        ):
            return str(data_structure)
        return data_structure
    return freeze_helper(data_structure)


def freeze_fast(data_structure):
    """Like freeze but has no cycle detection and it doesn't
    guarantee that the result is hashable.

    :param   data_structure: The structure to convert

    >>> freeze_fast([
    ...     'a',
    ...     [3, 4],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ...     []
    ... ])
    ('a', (3, 4), (('a', (3, (('w', ((2, 3, 5), '3', 4)),))),), ())

    >>> freeze_fast([
    ...     [],
    ...     'a',
    ...     [3, 4],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ... ])
    ((), 'a', (3, 4), (('a', (3, (('w', ((2, 3, 5), '3', 4)),))),))

    >>> b"sdf" == freeze_fast({3: b"sdf", 4: 245234534})[0][1]
    True
    """
    def freeze_fast_helper(data_structure):
        # Dictize if possible (support objects)
        try:
            data_structure = data_structure.__dict__
        except:
            pass
        # Itemize if needed
        try:
            data_structure = data_structure.items()
        except:
            pass
        # We don't freeze strings
        if not isinstance(data_structure, _string_types):
            tlen = -1
            # If item has a length we frezze it
            try:
                tlen = len(data_structure)
            except:
                pass
            if tlen != -1:
                return tuple([freeze_fast_helper(x) for x in data_structure])
        return data_structure
    return freeze_fast_helper(data_structure)


def _recursive_sort(data_structure, assume_key=False):
    # We don't sort strings
    if not isinstance(data_structure, _string_types):
        tlen = -1
        # If item has a length we frezze it
        try:
            tlen = len(data_structure)
        except:
            pass
        if tlen != -1:
            if assume_key and tlen == 2:
                return tuple([
                    _recursive_sort(
                        x,
                        assume_key=assume_key
                    ) for x in data_structure
                ])
            else:
                return tuple(sorted(
                    [_recursive_sort(
                        x,
                        assume_key=assume_key
                    ) for x in data_structure],
                    key=lambda x: pickle.dumps(
                        x,
                        protocol=pickle_protocol
                    )
                ))
    return data_structure


def freeze_stable(data_structure, assume_key=False, stringify=False):
    """Like freeze but results are stable regarding sorting.

    The stable functionality changes the datestructure (sorting)!
    For deterministic results don't use stable. If a two structures
    differ only in order / sorting of items freeze_stable will have
    the same result for both.

    With assume_key freeze uses the assumtion that all tuples (lenght 2) are
    key-value pairs and doesn't sort them. This approximation usually
    creates smaller structures for flatten and a smaller
    difference when comparing two flattened structures.

    stringify allow to freeze_stable anything.

    :param   data_structure: The structure to convert
    :param       assume_key: Assume that substructures of len() == 2
                             are key-value pairs -> don't sort
    :type        assume_key: bool
    :param        stringify: Stringify all leaves
    :type         stringify: bool


    >>> a = freeze_stable([
    ...     'a',
    ...     [3, 4],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ...     []
    ... ])
    >>> a
    ((), (((((((2, 3, 5), 4, '3'), 'w'),), 3), 'a'),), (3, 4), 'a')

    >>> b = freeze_stable([
    ...     [],
    ...     'a',
    ...     [4, 3],
    ...     {'a': [{'w' : set([4, '3', frozenset([3,5,2])])}, 3]},
    ... ])
    >>> b
    ((), (((((((2, 3, 5), 4, '3'), 'w'),), 3), 'a'),), (3, 4), 'a')

    a is the same as b!!

    >>> a == b
    True

    >>> b"sdf" == freeze_stable({3: b"sdf", 4: 245234534})[1][1]
    True

    >>> a = freeze_stable([
    ...     'a',
    ...     [3, 4],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ...     []
    ... ], stringify = True)
    >>> a
    ((), ((((((('2', '3', '5'), '3', '4'), 'w'),), '3'), 'a'),), ('3', '4'), 'a')
    >>> a = freeze_stable([
    ...     'a',
    ...     [5, 4],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ...     []
    ... ], stringify = True, assume_key=True)
    >>> a
    ((), ('5', '4'), 'a', (('a', ('3', (('w', (('2', '3', '5'), '3', '4')),))),))
    """

    if not stringify:
        identity_set = set()

    def freeze_stable_helper(data_structure):
        # Cycle detection
        idd = id(data_structure)
        if idd in identity_set:
            # We do not recurse into dictizable objects
            if hasattr(data_structure, "__dict__"):
                return "%s at 0x%d" % (type(data_structure), idd)
            # We do not recurse into containers
            tlen = -1
            try:
                tlen = len(data_structure)
            except:
                pass
            if tlen != -1:
                # Except string and tuples
                if not isinstance(data_structure, _ignore_types):
                    return "%s at 0x%d" % (type(data_structure), idd)
        else:
            identity_set.add(idd)
        # Dictize if possible (support objects)
        try:
            data_structure = data_structure.__dict__
        except:
            pass
        # Itemize if needed
        try:
            data_structure = data_structure.items()
        except:
            pass
        # We don't freeze strings
        if not isinstance(data_structure, _string_types):
            tlen = -1
            # If item has a length we frezze it
            try:
                tlen = len(data_structure)
            except:
                pass
            if tlen != -1:
                if assume_key and tlen == 2:
                    return tuple([
                        freeze_stable_helper(x) for x in data_structure
                    ])
                else:
                    return tuple(sorted(
                        [freeze_stable_helper(x) for x in data_structure],
                        key=lambda x: pickle.dumps(
                            x,
                            protocol=pickle_protocol
                        )
                    ))
        # To guarantee that the result is hashable we do not return
        # builtin_function_or_method
        if isinstance(data_structure, _builtin_function_or_method_type):
            return str(data_structure)
        return data_structure
    if stringify:
        return _recursive_sort(
            freeze(
                data_structure,
                stringify=True
            ),
            assume_key=assume_key
        )
    else:
        return freeze_stable_helper(data_structure)


def stable_hash(data_structure):
    """Recursive hash of data-structure and objects. No cycle detection.
    Creates always the same hash independant of the order inside
    iterable parts of the data-structure.

    Note: hash(freeze.freeze_fast(x)) is faster than freeze.recursive_hash(x)
    BUT freeze.stable_hash(x) is much faster than hash(freeze.stable_freeze(x)

    :param   data_structure: The structure to hash"""
    # Dictize if possible (support objects)
    try:
        data_structure = data_structure.__dict__
    except:
        pass
    # Itemize if needed
    try:
        data_structure = data_structure.items()
    except:
        pass
    # We don't iterate strings
    if not isinstance(data_structure, _string_types):
        tlen = -1
        # If item has a length we frezze it
        try:
            tlen = len(data_structure)
        except:
            pass
        if tlen != -1:
            hashs = sorted([stable_hash(item) for item in data_structure])
            return hash(tuple(hashs))
    return hash(data_structure)


def recursive_hash(data_structure):
    """Recursive hash of data-structure and objects. No cycle detection.

    :param   data_structure: The structure to hash"""
    # Dictize if possible (support objects)
    try:
        data_structure = data_structure.__dict__
    except:
        pass
    # Itemize if needed
    try:
        data_structure = data_structure.items()
    except:
        pass
    # We don't iterate strings
    if not isinstance(data_structure, _string_types):
        tlen = -1
        # If item has a length we frezze it
        try:
            tlen = len(data_structure)
        except:
            pass
        if tlen != -1:
            hashs = tuple(recursive_hash(item) for item in data_structure)
            return hash(tuple(hashs))
    return hash(data_structure)


def _flatten_helper(iterable, pathlist, path, parent_index=False):
    # Do not iterate over strings
    if isinstance(iterable, _string_types):
        path.append(iterable)
        pathlist.append("/".join(path))
    else:
        tlen = -1
        # If the item has a length we flatten it
        try:
            tlen = len(iterable)
        except:
            pass
        if tlen == -1:
            # We are done
            path.append(str(iterable))
            pathlist.append("/".join(path))
            return
        if tlen == 0:
            # A empty tuple marks a empty iterable
            path.append("()")
            pathlist.append("/".join(path))
            return
        # If we have a tuple (length 2) we try to use
        # the first item as key
        if tlen == 2:
            sublen = -1
            try:
                sublen = len(iterable[0])
            except:
                pass
            if sublen == -1 or isinstance(iterable[0], _string_types):
                # If the parent is an index, we don't need it since we
                # have a key.
                if parent_index:
                    del path[-1]
                _flatten_helper(
                    iterable[1],
                    pathlist,
                    path + [str(iterable[0])]
                )
                return
        # We have a list
        index = 0
        for item in iterable:
            sublen = -1
            try:
                sublen = len(item)
            except:
                pass
            _flatten_helper(
                item,
                pathlist,
                path + [str(index)],
                parent_index=True
            )
            index += 1


def tree_diff(a, b, n=5, deterministic=True):
    """Freeze and stringify any data-structure or object, traverse
    it depth-first in-order and apply a unified diff.

    Depth-first in-order is just like structure would be printed.

    Annotation:

    "(           x"       Going down to level: x
    ")           x"       Going one level up from: x

    :param             a: data_structure a
    :param             b: data_structure b
    :param             n: lines of context
    :type              n: int


    >>> a = [
    ...     'a',
    ...     [3, 4],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ...     []
    ... ]
    >>> b = [
    ...     'a',
    ...     [4, 3],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([2,5,3])])}]},
    ...     []
    ... ]
    >>> transparent_repr("\\n".join(tree_diff(a, b).split("\\n")[2:]))
    @@ -1,8 +1,8 @@
     ('a',
    - ('3',
    -  '4'),
    + ('4',
    +  '3'),
      (('a',
        ('3',
         (('w',
           (('2',
             '3',

    >>> a = [
    ...     'a',
    ...     [3, 4],
    ...     {'a': [3, {'w' : set([4, 'tree', frozenset([3,5,2])])}]},
    ...     []
    ... ]
    >>> b = [
    ...     'a',
    ...     [4, 3],
    ...     {'a': [3, {'w' : set([4, '3', frozenset([2,5,3])])}]},
    ...     []
    ... ]
    >>> transparent_repr("\\n".join(tree_diff(a, b).split("\\n")[2:]))
    @@ -1,12 +1,12 @@
     ('a',
    - ('3',
    -  '4'),
    + ('4',
    +  '3'),
      (('a',
        ('3',
         (('w',
           (('2',
             '3',
             '5'),
    -       'tree',
    +       '3',
            '4')),))),),
      ())
    """
    a = freeze(a, stringify=True)
    b = freeze(b, stringify=True)
    if deterministic:
        a = vformat(a).split("\n")
        b = vformat(b).split("\n")
    else:
        a = vformat(_recursive_sort(a)).split("\n")
        b = vformat(_recursive_sort(b)).split("\n")
    return "\n".join(difflib.unified_diff(a, b, n=n, lineterm=""))


def tree_diff_assert(a, b, n=5, deterministic=True):
    """Assert if a equals b. Freeze and stringify any data-structure or object,
    traverse it depth-first and apply a unified diff, to display the result.

    :param             a: data_structure a
    :param             b: data_structure b
    :param             n: lines of context
    :type              n: int
    :param deterministic: Do not sort the tree
    """
    a = freeze(a, stringify=True)
    b = freeze(b, stringify=True)
    if deterministic:
        a = vformat(a).split("\n")
        b = vformat(b).split("\n")
    else:
        a = vformat(_recursive_sort(a)).split("\n")
        b = vformat(_recursive_sort(b)).split("\n")
    msg = "\n".join(difflib.unified_diff(a, b, n=n, lineterm=""))
    if len(msg) != 0:
        assert False, "difference: \n%s" % msg


def flatten(data_structure, assume_key=True):
    """Converts a data-structure to a flat set of paths.
    It makes it easier to comapre data-structures in unittests.

    Creating a set from a flattened structure can be lossy. This is the
    reason frozen_equal_assert will not use flatten for comparison by
    default. BUT flatten is very useful if you have data that changes
    order often, but order doesn't matter.

    :param   data_structure: The structure to convert
    :param   assume_key:     Assume that substructures of len() == 2
                             are key-value pairs -> don't sort
    :type    assume_key:     bool

    >>> test_one = [
    ...    'a',
    ...    [3, 4],
    ...    {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ...    []
    ... ]
    >>> flat_one = flatten(test_one)
    >>> vformat(flat_one)
    ['/0/()',
     '/3/4',
     '/2/a',
     '/3/a/3/w/0/0/2',
     '/3/a/3/w/0/1/3',
     '/3/a/3/w/0/2/5',
     '/3/a/3/w/1/4',
     '/3/a/3/w/2/3']

    >>> test_two = [
    ...    'a',
    ...    [3, 4],
    ...    {'a': [3, {'w' : set([4, '3', frozenset([3,5,2])])}]},
    ...    []
    ... ]
    >>> flat_two = flatten(test_two)
    >>> vformat(flat_two)
    ['/0/()',
     '/3/4',
     '/2/a',
     '/3/a/3/w/0/0/2',
     '/3/a/3/w/0/1/3',
     '/3/a/3/w/0/2/5',
     '/3/a/3/w/1/4',
     '/3/a/3/w/2/3']

     >>> len(set(flat_one) - set(flat_two))
     0
    """
    pathlist = []

    _flatten_helper(freeze_stable(
        data_structure,
        assume_key=assume_key
    ), pathlist, [''])
    return pathlist


def _flatten_for_assert(data_structure):
    pathlist = []
    _flatten_helper(data_structure, pathlist, [''])
    return pathlist


def frozen_equal_assert(a, b, deterministic=True):
    """Freeze the structures, compare and assert with diff.
    Because structures are frozen first: you can also pass
    objects to compare.

    :param             a: data_structure a
    :param             b: data_structure b
    :param deterministic: use flatten only for creating the diff
    """

    if not deterministic:
        freeze_func = lambda x: freeze_stable(x, assume_key=True)
    else:
        freeze_func = freeze
    a = freeze_func(a)
    b = freeze_func(b)
    # If a == b we are save anyway
    if a != b:
        flatten_a = set(_flatten_for_assert(a))
        flatten_b = set(_flatten_for_assert(b))
        diff_a = flatten_a - flatten_b
        diff_b = flatten_b - flatten_a
        if len(diff_a) != 0 or len(diff_b) != 0:
            assert False, "set diff not empty: \na=%s\nb=%s" % (
                vformat(diff_a),
                vformat(diff_b),
            )
        else:
            # If it is deterministic we have to tell user that flatten
            # did not find differences
            if deterministic:
                assert False, "data_structure not equal, but " \
                    "flatten did not find a diff: \na=%s\nb=%s" % (
                        vformat(a),
                        vformat(b),
                    )


class TransparentRepr(object):
    """That doctest calls __repr__ is very annoying, you can't follow PEP8
    on large objects. TransparentRepr makes string represent itself
    including all non-printable characters."""
    def __init__(self, repr_str):
        self.repr_str = repr_str

    def __repr__(self):
        if isinstance(self.repr_str, six.string_types):
            return self.repr_str
        else:
            return super(TransparentRepr, self).__repr__()

    def split(self, *args, **kwargs):
        return self.repr_str.split(*args, **kwargs)


def transparent_repr(string):
    """The result is __repr__ transparent. Non-printable
    characters won't be escaped"""
    return TransparentRepr(string)


def vformat(*args, **kwargs):
    """A pformat wrapper that produces narrow representations of
    data-structures. The result is __repr__ transparent. Non-printable
    characters won't be escaped"""
    return TransparentRepr(
        pprint.pformat(*args, width=1, **kwargs)
    )


if __name__ == "__main__":
    import doctest
    import json
    import gzip
    pickle_protocol = 2
    result = doctest.testmod()
    sys.exit(result.failed)
