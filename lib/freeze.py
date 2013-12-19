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
import pprint
import sys
import json
import gzip
import difflib

# These imports are need for doc tests.
nothing = json.__file__
nothing = gzip.__file__
del nothing

__all__ = [
    "freeze",
    "dump",
    "tree_diff_assert",
    "stable_hash",
    "recursive_hash",
    "tree_diff",
    "vformat",
    "transparent_repr",
    "traverse_frozen_data",
    "TraversalBasedReprCompare",
]


try:
    _ignore_types = (six.string_types, tuple, bytes)
except:  # pragma: no cover
    _ignore_types = (six.string_types, tuple)

try:
    _string_types = (six.string_types,  bytes)
except:  # pragma: no cover
    _string_types = (six.string_types)

_primitive_types = (int, float, bool)

_builtin_function_or_method_type = type(dict().get)


def freeze(data_structure):
    """Freeze tries to convert any datastructure in a hierarchy of tuples.
    Tuples are comparable/sortable/hashable, you can use this with
    with recursive sort and or dump. freeze has no recursion detection.

    :param   data_structure: The structure to convert.

    Typical usage for unittesting: # TODO: recsort(freeze(dump(x)))

    """
    def freeze_helper(data_structure):
        # Dictize if possible (support objects)
        try:
            data_structure = dict(data_structure)
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
            # If item has a length we freeze it
            try:
                tlen = len(data_structure)
            except:
                pass
            if tlen != -1:
                # Well there are classes out in the wild that answer to len
                # but have no indexer.
                try:
                    return tuple([
                        freeze_helper(x) for x in data_structure
                    ])
                except:  # pragma: no cover
                    pass
        return data_structure
    return freeze_helper(data_structure)


class IDD(int):
    __slots__ = ()
    pass


class Meta(list):
    __slots__ = ()
    pass


def dump(data_structure):
    """Dump will create a human readable version of your datastructure.
    It will try to dump almost anything, it has recursion detection and
    will try to display the recursion in a meaningful way.

    :param   data_structure: The structure to convert.

    Typical usage for unittesting: # TODO: recsort(freeze(dump(x)))

    >>> dump([1, {'a' : 'b'}])
    [<class 'list'>, ('1', [<class 'dict'>, {'a': 'b'}])]
    """

    identity_set = set()
    dup_set      = set()

    def dump_helper(data_structure):
        if isinstance(data_structure, _primitive_types):
            return str(data_structure)
        # Cycle detection
        idd = id(data_structure)
        if idd in identity_set:
            dup_set.add(idd)
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
                    # I can't test this on python3. I would need a type that is
                    # not handled above. Namespaces are the only thing I know
                    # and python3 doesn't freeze namespaces :(
                    return "%s at 0x%d" % (
                        type(data_structure), idd
                    )  # pragma: no cover
        else:
            identity_set.add(idd)
        ret = Meta()
        ret.append(type(data_structure))
        ret.append(IDD(idd))
        # Dictize if possible (support objects)
        try:
            data_structure = dict(data_structure)
        except:
            pass
        # Itemize if possible
        try:
            data_structure = data_structure.items()
            ret.append(dict([
                (dump_helper(x[0]), dump_helper(x[1]))
                for x in data_structure
            ]))
            return ret
        except:
            pass
        # We don't freeze strings
        if not isinstance(data_structure, _string_types):
            tlen = -1
            # If item has a length we freeze it
            try:
                tlen = len(data_structure)
            except:
                pass
            if tlen != -1:
                # Well there are classes out in the wild that answer to len
                # but have no indexer.
                try:
                    ret.append(tuple([dump_helper(x) for x in data_structure]))
                    return ret
                except:  # pragma: no cover
                    pass
        return data_structure

    def clean_up(data_structure):
        if isinstance(data_structure, Meta):
            idd_temp = data_structure[1]
            if isinstance(idd_temp, IDD):
                if idd_temp not in dup_set:
                    del data_structure[1]
        # We don't clean strings
        if not isinstance(data_structure, _string_types):
            tlen = -1
            # If item has a length we clean it
            try:
                tlen = len(data_structure)
            except:
                pass
            if tlen != -1:
                for x in data_structure:
                    clean_up(x)
        return data_structure
    return clean_up(dump_helper(data_structure))


def recursive_sort(data_structure):
    """Sort a recursive data_structure.

    :param   data_structure: The structure to convert.

    data_structure must be already sortable or you must use freeze() or dump().
    The function will work is many kinds of input.

    >>> recursive_sort(dump([3, 1, {'c' : 'c', 'a' : 'b'}]))
    [<class 'list'>, ('1', '3', [<class 'dict'>, [['a', 'b'], ['c', 'c']]])]
    """
    # We don't sort strings
    if not isinstance(data_structure, _string_types):
        is_meta = isinstance(data_structure, Meta)
        was_dict = False
        # Dictize if possible (support objects)
        try:
            data_structure = dict(data_structure)
            was_dict = True
        except:
            pass
        # Itemize if possible
        try:
            data_structure = data_structure.items()
        except:
            pass
        tlen = -1
        # If item has a length we sort it
        try:
            tlen = len(data_structure)
        except:
            pass
        if tlen != -1:
            # Well there are classes out in the wild that answer to len
            # but have no indexer.
            try:
                if was_dict:
                    return sorted(
                        [
                            (
                                recursive_sort(x[0]),
                                recursive_sort(x[1]),
                            )
                            for x in data_structure
                        ],
                        key=TraversalBasedReprCompare
                    )
                elif is_meta:
                    return [
                        recursive_sort(
                            x,
                        ) for x in data_structure
                    ]
                else:
                    return tuple(sorted(
                        [recursive_sort(
                            x,
                        ) for x in data_structure],
                        key=TraversalBasedReprCompare,
                    ))
            except:  # pragma: no cover
                pass
    return data_structure

#........................................................


def stable_hash(data_structure):
    """Recursive hash of data-structure and objects. No cycle detection.
    Creates always the same hash independant of the order inside
    iterable parts of the data-structure.

    Note: hash(freeze.freeze_fast(x)) is faster than freeze.recursive_hash(x)
    BUT freeze.stable_hash(x) is much faster than hash(freeze.stable_freeze(x)

    :param   data_structure: The structure to hash

    >>> class A(object):
    ...     def __init__(self):
    ...         self.huhu = 53
    >>> a = A()
    >>> stable_hash([a, 4]) == stable_hash([4, a])
    True
    """
    # Dictize if possible (support objects)
    try:
        data_structure = dict(data_structure)
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
        # If item has a length we freeze it
        try:
            tlen = len(data_structure)
        except:
            pass
        if tlen != -1:
            # Well there are classes out in the wild that answer to len
            # but have no indexer.
            try:
                hashs = sorted([stable_hash(item) for item in data_structure])
                return hash(tuple(hashs))
            except:  # pragma: no cover
                pass
    return hash(data_structure)


def recursive_hash(data_structure):
    """Recursive hash of data-structure and objects. No cycle detection.

    :param   data_structure: The structure to hash

    The hash is seeded different everytime python is started. So there is no
    meaningful test yet.

    >>> class A(object):
    ...     def __init__(self):
    ...         self.huhu = 53
    >>> a = A()
    >>> b = [a, 4]
    >>> bool(recursive_hash(b))
    True

    """
    # Dictize if possible (support objects)
    try:
        data_structure = dict(data_structure)
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
        # If item has a length we freeze it
        try:
            tlen = len(data_structure)
        except:
            pass
        if tlen != -1:
            # Well there are classes out in the wild that answer to len
            # but have no indexer.
            try:
                hashs = tuple(recursive_hash(item) for item in data_structure)
                return hash(tuple(hashs))
            except:  # pragma: no cover
                pass
    return hash(data_structure)


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

    We need freeze stable to test this across python versions. It doesn't make
    too much sense, but at least there are some tests.

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


class TransparentRepr(str):
    """That doctest calls __repr__ is very annoying, you can't follow PEP8
    on large objects. TransparentRepr makes string represent itself
    including all non-printable characters."""

    def __repr__(self):
        return self


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


def traverse_frozen_data(data_structure):
    """Yields the leaves of the frozen data-structure pre-order.

    It will produce the same order as one would write data-structure."""
    parent_stack = [data_structure]
    while parent_stack:
        node = parent_stack.pop(0)
        # We don't iterate strings
        tlen = -1
        if not isinstance(node, _string_types):
            # If item has a length we freeze it
            try:
                tlen = len(node)
            except:
                pass
        if tlen == -1:
            yield node
        else:
            parent_stack = list(node) + parent_stack


class TraversalBasedReprCompare(object):
    """Implements the comparison method for frozen data-structures based on
    traverse_frozen_data.

    >>> cm = TraversalBasedReprCompare
    >>> cm(3) < cm(4)
    True
    >>> cm(4) > cm(3)
    True
    >>> cm(3) > cm(4)
    False
    >>> cm(3) == cm(3)
    True
    >>> cm(3) == cm(4)
    False
    >>> cm((3, 3)) > cm((3,))
    True
    >>> cm((3, 3)) == cm((3, 3))
    True
    >>> cm((3,)) > cm((3, 3))
    False
    >>> cm((3,)) == cm((3, 3))
    False
    """

    def __init__(self, payload):
        """Initialize a payload (usually a key) for comparison"""
        self.payload   = payload

    def _cmp(self, other):
        """Generic cmp method to support python 2/3"""
        #import pdb; pdb.set_trace()
        self_gen  = traverse_frozen_data(self.payload)
        other_gen = traverse_frozen_data(other.payload)
        while True:
            try:
                self_node  = repr(next(self_gen))
            except StopIteration:
                self_node  = None
            try:
                other_node = repr(next(other_gen))
            except StopIteration:
                other_node = None
            if self_node is None or other_node is None:
                # We iterated to the end
                if self_node is not None:
                    return 1
                if other_node is not None:
                    return -1
                return 0
            if self_node != other_node:
                return (
                    self_node > other_node
                ) - (
                    self_node < other_node
                )

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __cmp__(self, other):  # pragma: no cover
        return self._cmp(other)


if __name__ == "__main__":  # pragma: no cover
    import doctest
    result = doctest.testmod()
    sys.exit(result.failed)
# lint_ignore=W0702,R0912,R0911
