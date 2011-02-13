import copy
import re


__all__ = ['Scanner', 'text_coords']


class Scanner(object):

    """
    :class:`Scanner` is a near-direct port of Ruby's ``StringScanner``.

    The aim is to provide for lexical scanning operations on strings::

        >>> from strscan import Scanner
        >>> s = Scanner("This is an example string")
        >>> s.eos()
        False
        >>> s.scan(r'\w+')
        'This'
        >>> s.scan(r'\w+')
        >>> s.scan(r'\s+')
        ' '
        >>> s.scan(r'\s+')
        >>> s.scan(r'\w+')
        'is'
        >>> s.eos()
        False

        >>> s.scan(r'\s+')
        ' '
        >>> s.scan(r'\w+')
        'an'
        >>> s.scan(r'\s+')
        ' '
        >>> s.scan(r'\w+')
        'example'
        >>> s.scan(r'\s+')
        ' '
        >>> s.scan(r'\w+')
        'string'
        >>> s.eos()
        True

        >>> s.scan(r'\s+')
        >>> s.scan(r'\w+')

    Its mechanism of operation is similar to :class:`StringIO`, only instead of
    reading by passing a number of bytes, you read by passing a regex. A scan
    pointer tracks the current position through the string, and all scanning or
    searching happens on the rest of the string after this pointer.
    :meth:`scan` is the simple case of reading some text and advancing the scan
    pointer, but there are several other related methods which fulfil different
    requirements.

    All the methods on :class:`Scanner` which take regexes will accept either
    regex strings or compiled pattern objects (as would be returned from
    ``re.compile()``).
    """

    def __init__(self, string):
        self.string = string
        self.pos_history, self._pos = [0], 0
        self.match_history, self._match = [None], None

    def __getitem__(self, index):
        """Proxy for ``self.match.group(index)``."""

        if self.match:
            return self.match.group(index)
        raise IndexError("No match on this scanner")

    def _get_pos(self):
        return self._pos
    def _set_pos(self, pos):
        self._pos = pos
        self.pos_history.append(pos)
    pos = property(_get_pos, _set_pos,
            doc="The current position of the scan pointer.")
    prev = property(lambda self: self.pos_history[-2],
            doc="The last position of the scan pointer.")

    def coords(self):
        r"""
        Return the current scanner position as `(lineno, columnno, line)`.

        This method is useful for displaying the scanner position in a human-
        readable way. For example, you could use it to provide friendlier
        debugging information when writing parsers.

            >>> s = Scanner("abcdef\nghijkl\nmnopqr\nstuvwx\nyz")
            >>> s.coords()
            (0, 0, 'abcdef')
            >>> s.pos += 4
            >>> s.coords()
            (0, 4, 'abcdef')
            >>> s.pos += 2
            >>> s.coords()
            (0, 6, 'abcdef')
            >>> s.pos += 1
            >>> s.coords()
            (1, 0, 'ghijkl')
            >>> s.pos += 4
            >>> s.coords()
            (1, 4, 'ghijkl')
            >>> s.pos += 4
            >>> s.coords()
            (2, 1, 'mnopqr')
        """
        return text_coords(self.string, self.pos)

    def _get_match(self):
        return self._match
    def _set_match(self, match):
        self._match = match
        self.match_history.append(match)
    match = property(_get_match, _set_match,
            doc="The latest scan match.")

    def beginning_of_line(self):
        r"""
        Return true if the scan pointer is at the beginning of a line.

            >>> s = Scanner("test\ntest\n")
            >>> s.beginning_of_line()
            True
            >>> s.skip(r'te')
            2
            >>> s.beginning_of_line()
            False
            >>> s.skip(r'st\n')
            3
            >>> s.beginning_of_line()
            True
            >>> s.terminate()
            >>> s.beginning_of_line()
            True
        """
        if self.pos > len(self.string):
            return None
        elif self.pos == 0:
            return True
        return self.string[self.pos - 1] == '\n'

    def terminate(self):
        """Set the scan pointer to the end of the string; clear match data."""
        self.pos = len(self.string)
        self.match = None

    def eos(self):
        """
        Return true if the scan pointer is at the end of the string.

            >>> s = Scanner("abc")
            >>> s.eos()
            False
            >>> s.terminate()
            >>> s.eos()
            True
        """
        return len(self.string) == self.pos

    def getch(self):
        """
        Get a single character and advance the scan pointer.

            >>> s = Scanner("abc")
            >>> s.getch()
            'a'
            >>> s.getch()
            'b'
            >>> s.getch()
            'c'
            >>> s.pos
            3
        """
        self.pos += 1
        return self.string[self.pos - 1:self.pos]

    def peek(self, length):
        """
        Get a number of characters without advancing the scan pointer.

            >>> s = Scanner("test string")
            >>> s.peek(7)
            'test st'
            >>> s.peek(7)
            'test st'
        """
        return self.string[self.pos:self.pos + length]

    def rest(self):
        """
        Get the rest of the string that hasn't been scanned yet.

            >>> s = Scanner("test string")
            >>> s.scan(r'test')
            'test'
            >>> s.rest
            ' string'
        """
        return self.string[self.pos:]
    rest = property(rest)

    def matched(self):
        """
        Get the whole of the current match.

        This method returns whatever would have been returned by the latest
        :meth:`scan()` call.

            >>> s = Scanner("test string")
            >>> s.scan(r'test')
            'test'
            >>> s.matched()
            'test'
        """
        return self.match.group(0)

    def pre_match(self):
        r"""
        Get whatever comes before the current match.

            >>> s = Scanner('test string')
            >>> s.skip(r'test')
            4
            >>> s.scan(r'\s')
            ' '
            >>> s.pre_match()
            'test'
        """
        return self.string[:self.match.start()]

    def post_match(self):
        r"""
        Get whatever comes after the current match.

            >>> s = Scanner('test string')
            >>> s.skip(r'test')
            4
            >>> s.scan(r'\s')
            ' '
            >>> s.post_match()
            'string'
        """
        return self.string[self.match.end():]

    def unscan(self):
        """
        Undo the last scan, resetting the position and match registers.

            >>> s = Scanner('test string')
            >>> s.pos
            0
            >>> s.skip(r'te')
            2
            >>> s.rest
            'st string'
            >>> s.unscan()
            >>> s.pos
            0
            >>> s.rest
            'test string'
        """
        self.pos_history.pop()
        self._pos = self.pos_history[-1]
        self.match_history.pop()
        self._match = self.match_history[-1]

    def scan_full(self, regex, return_string=True, advance_pointer=True):
        """
        Match from the current position.

        If `return_string` is false and a match is found, returns the number of
        characters matched.

            >>> s = Scanner("test string")
            >>> s.scan_full(r' ')
            >>> s.scan_full(r'test ')
            'test '
            >>> s.pos
            5
            >>> s.scan_full(r'stri', advance_pointer=False)
            'stri'
            >>> s.pos
            5
            >>> s.scan_full(r'stri', return_string=False, advance_pointer=False)
            4
            >>> s.pos
            5
        """
        regex = get_regex(regex)
        self.match = regex.match(self.string, self.pos)
        if not self.match:
            return
        if advance_pointer:
            self.pos = self.match.end()
        if return_string:
            return self.match.group(0)
        return len(self.match.group(0))

    def search_full(self, regex, return_string=True, advance_pointer=True):
        """
        Search from the current position.

        If `return_string` is false and a match is found, returns the number of
        characters matched (from the current position *up to* the end of the
        match).

            >>> s = Scanner("test string")
            >>> s.search_full(r' ')
            'test '
            >>> s.pos
            5
            >>> s.search_full(r'i', advance_pointer=False)
            'stri'
            >>> s.pos
            5
            >>> s.search_full(r'i', return_string=False, advance_pointer=False)
            4
            >>> s.pos
            5
        """
        regex = get_regex(regex)
        self.match = regex.search(self.string, self.pos)
        if not self.match:
            return
        start_pos = self.pos
        if advance_pointer:
            self.pos = self.match.end()
        if return_string:
            return self.string[start_pos:self.match.end()]
        return (self.match.end() - start_pos)

    def scan(self, regex):
        """
        Match a pattern from the current position.

        If a match is found, advances the scan pointer and returns the matched
        string. Otherwise returns ``None``.

            >>> s = Scanner("test string")
            >>> s.pos
            0
            >>> s.scan(r'foo')
            >>> s.scan(r'bar')
            >>> s.pos
            0
            >>> s.scan(r'test ')
            'test '
            >>> s.pos
            5
        """
        return self.scan_full(regex, return_string=True, advance_pointer=True)

    def scan_until(self, regex):
        """
        Search for a pattern from the current position.

        If a match is found, advances the scan pointer and returns the matched
        string, from the current position *up to* the end of the match.
        Otherwise returns ``None``.

            >>> s = Scanner("test string")
            >>> s.pos
            0
            >>> s.scan_until(r'foo')
            >>> s.scan_until(r'bar')
            >>> s.pos
            0
            >>> s.scan_until(r' ')
            'test '
            >>> s.pos
            5
        """
        return self.search_full(regex, return_string=True, advance_pointer=True)

    def scan_upto(self, regex):
        """
        Scan up to, but not including, the given regex.

            >>> s = Scanner("test string")
            >>> s.scan('t')
            't'
            >>> s.scan_upto(r' ')
            'est'
            >>> s.pos
            4
            >>> s.pos_history
            [0, 1, 4]
        """
        pos = self.pos
        if self.scan_until(regex) is not None:
            self.pos -= len(self.matched())
            # Remove the intermediate position history entry.
            self.pos_history.pop(-2)
            return self.pre_match()[pos:]

    def skip(self, regex):
        """
        Like :meth:`scan`, but return the number of characters matched.

            >>> s = Scanner("test string")
            >>> s.skip('test ')
            5
        """
        return self.scan_full(regex, return_string=False, advance_pointer=True)

    def skip_until(self, regex):
        """
        Like :meth:`scan_until`, but return the number of characters matched.

            >>> s = Scanner("test string")
            >>> s.skip_until(' ')
            5
        """
        return self.search_full(regex, return_string=False, advance_pointer=True)

    def check(self, regex):
        """
        See what :meth:`scan` would return without advancing the pointer.

            >>> s = Scanner("test string")
            >>> s.check('test ')
            'test '
            >>> s.pos
            0
        """
        return self.scan_full(regex, return_string=True, advance_pointer=False)

    def check_until(self, regex):
        """
        See what :meth:`scan_until` would return without advancing the pointer.

            >>> s = Scanner("test string")
            >>> s.check_until(' ')
            'test '
            >>> s.pos
            0
        """
        return self.search_full(regex, return_string=True, advance_pointer=False)

    def exists(self, regex):
        """
        See what :meth:`skip_until` would return without advancing the pointer.

            >>> s = Scanner("test string")
            >>> s.exists(' ')
            5
            >>> s.pos
            0

        Returns the number of characters matched if it does exist, or ``None``
        otherwise.
        """
        return self.search_full(regex, return_string=False, advance_pointer=False)


def text_coords(string, position):
    r"""
    Transform a simple index into a human-readable position in a string.

    This function accepts a string and an index, and will return a triple of
    `(lineno, columnno, line)` representing the position through the text. It's
    useful for displaying a string index in a human-readable way::

        >>> s = "abcdef\nghijkl\nmnopqr\nstuvwx\nyz"
        >>> text_coords(s, 0)
        (0, 0, 'abcdef')
        >>> text_coords(s, 4)
        (0, 4, 'abcdef')
        >>> text_coords(s, 6)
        (0, 6, 'abcdef')
        >>> text_coords(s, 7)
        (1, 0, 'ghijkl')
        >>> text_coords(s, 11)
        (1, 4, 'ghijkl')
        >>> text_coords(s, 15)
        (2, 1, 'mnopqr')
    """
    line_start = string.rfind('\n', 0, position) + 1
    line_end = string.find('\n', position)
    lineno = string.count('\n', 0, position)
    columnno = position - line_start
    line = string[line_start:line_end]
    return (lineno, columnno, line)


def get_regex(regex):
    """
    Ensure we have a compiled regular expression object.

        >>> import re
        >>> get_regex('string') # doctest: +ELLIPSIS
        <_sre.SRE_Pattern object at 0x...>
        >>> pattern = re.compile(r'string')
        >>> get_regex(pattern) is pattern
        True
        >>> get_regex(3) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        TypeError: Invalid regex type: 3
    """
    if isinstance(regex, basestring):
        return re.compile(regex)
    elif not isinstance(regex, re._pattern_type):
        raise TypeError("Invalid regex type: %r" % (regex,))
    return regex


def _get_tests():
    """Enables ``python setup.py test``."""
    import doctest
    return doctest.DocTestSuite()
