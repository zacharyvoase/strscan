strscan
=======

``strscan.Scanner`` is a near-direct port of Ruby's ``StringScanner``.

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

Its mechanism of operation is similar to ``StringIO``, only instead of reading
by passing a number of bytes, you read by passing a regex. A scan pointer
tracks the current position through the string, and all scanning or searching
happens on the rest of the string after this pointer.  ``scan`` is the simple
case of reading some text and advancing the scan pointer, but there are several
other related methods which fulfil different requirements.

All the methods on ``Scanner`` which take regexes will accept either regex
strings or compiled pattern objects (as would be returned from
``re.compile()``).

(Un)license
===========

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
software, either in source code form or as a compiled binary, for any purpose,
commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this
software dedicate any and all copyright interest in the software to the public
domain. We make this dedication for the benefit of the public at large and to
the detriment of our heirs and successors. We intend this dedication to be an
overt act of relinquishment in perpetuity of all present and future rights to
this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
