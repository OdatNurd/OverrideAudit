# The code in this module was taken from Lib/base64.py from the CPython source
# code at https://github.com/python/cpython, specifically from commit ac0b3c2f.
#
# Contained here is just the definition of the b85 encoder/decoder, which is
# used in some patches in order to bundle binary files. The file name here
# mimics the source file it came from.
#
# This is for use in versions of Sublime that bundle versions of Python prior
# to version 3.4 where this functionality was added to the base64 library.

import struct

bytes_types = (bytes, bytearray)  # Types acceptable as binary data

def _bytes_from_decode_data(s):
    if isinstance(s, str):
        try:
            return s.encode('ascii')
        except UnicodeEncodeError:
            raise ValueError('string argument should contain only ASCII characters')
    if isinstance(s, bytes_types):
        return s
    try:
        return memoryview(s).tobytes()
    except TypeError:
        raise TypeError("argument should be a bytes-like object or ASCII "
                        "string, not %r" % s.__class__.__name__) from None

def _85encode(b, chars, chars2, pad=False, foldnuls=False, foldspaces=False):
    # Helper function for a85encode and b85encode
    if not isinstance(b, bytes_types):
        b = memoryview(b).tobytes()

    padding = (-len(b)) % 4
    if padding:
        b = b + b'\0' * padding
    words = struct.Struct('!%dI' % (len(b) // 4)).unpack(b)

    chunks = [b'z' if foldnuls and not word else
              b'y' if foldspaces and word == 0x20202020 else
              (chars2[word // 614125] +
               chars2[word // 85 % 7225] +
               chars[word % 85])
              for word in words]

    if padding and not pad:
        if chunks[-1] == b'z':
            chunks[-1] = chars[0] * 5
        chunks[-1] = chunks[-1][:-padding]

    return b''.join(chunks)

# The following code is originally taken (with permission) from Mercurial

_b85alphabet = (b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                b"abcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~")
_b85chars = None
_b85chars2 = None
_b85dec = None

def b85encode(b, pad=False):
    """Encode bytes-like object b in base85 format and return a bytes object.

    If pad is true, the input is padded with b'\\0' so its length is a multiple of
    4 bytes before encoding.
    """
    global _b85chars, _b85chars2
    # Delay the initialization of tables to not waste memory
    # if the function is never called
    if _b85chars is None:
        _b85chars = [bytes((i,)) for i in _b85alphabet]
        _b85chars2 = [(a + b) for a in _b85chars for b in _b85chars]
    return _85encode(b, _b85chars, _b85chars2, pad)

def b85decode(b):
    """Decode the base85-encoded bytes-like object or ASCII string b

    The result is returned as a bytes object.
    """
    global _b85dec
    # Delay the initialization of tables to not waste memory
    # if the function is never called
    if _b85dec is None:
        _b85dec = [None] * 256
        for i, c in enumerate(_b85alphabet):
            _b85dec[c] = i

    b = _bytes_from_decode_data(b)
    padding = (-len(b)) % 5
    b = b + b'~' * padding
    out = []
    packI = struct.Struct('!I').pack
    for i in range(0, len(b), 5):
        chunk = b[i:i + 5]
        acc = 0
        try:
            for c in chunk:
                acc = acc * 85 + _b85dec[c]
        except TypeError:
            for j, c in enumerate(chunk):
                if _b85dec[c] is None:
                    raise ValueError('bad base85 character at position %d'
                                    % (i + j)) from None
            raise
        try:
            out.append(packI(acc))
        except struct.error:
            raise ValueError('base85 overflow in hunk starting at byte %d'
                             % i) from None

    result = b''.join(out)
    if padding:
        result = result[:-padding]
    return result

