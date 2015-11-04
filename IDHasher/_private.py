#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    _private.py
'''

import warnings

from functools import wraps
from math import ceil

#: BEGIN OF THE SCRIPT

MIN_ALPHABET_LENGTH = 16
RATIO_SEPARATORS = 3.5
RATIO_GUARDS = 12

try:
    StrType = basestring
except NameError:
    StrType = str

#: Returns whether a value is a string.
is_string = lambda s: isinstance(s, StrType)

#: Returns whether a value is an unsigned integer.
is_uint = lambda n: n == int(n) and n >= 0


def isString(var):
    '''
    Returns whether a value is a string.
    '''

    return isinstance(var, StrType)


def isUint(number):
    '''
    Returns whether a value is an unsigned integer.
    '''

    try:
        return number == int(number) and number >= 0
    except ValueError:
        return False


def stringSplit(string, splitters):
    '''
    Splits a string into parts at multiple characters
    '''

    part = ''

    for char in string:
        if char in splitters:
            yield part
            part = ''
        else:
            part += char

    yield part


def hash(number, alphabet):
    '''
    Hashes `number` using the given `alphabet` sequence.
    '''

    hashed = ''

    alphabetLen = len(alphabet)

    while True:
        hashed = alphabet[number % alphabetLen] + hashed
        number //= alphabetLen
        if not number:
            return hashed


def unhash(hashed, alphabet):
    '''
    Restores a number tuple from hashed using the given `alphabet` index.
    '''

    number = 0

    hashLength = len(hashed)
    alphabetLen = len(alphabet)

    for x, char in enumerate(hashed):
        position = alphabet.index(char)
        number += position * alphabetLen ** (hashLength - x - 1)

    return number


def reorder(string, salt):
    '''
    Reorders `string` according to `salt`.
    '''

    saltLength = len(salt)

    if saltLength == 0:
        return string

    x, index, intSum = len(string) - 1, 0, 0

    while x > 0:
        index %= saltLength
        integer = ord(salt[index])
        intSum += integer

        n = (integer + index + intSum) % x

        temp = string[n]
        trailer = string[n + 1:] if n + 1 < len(string) else ''
        string = string[0:n] + string[x] + trailer
        string = string[0:x] + temp + string[x + 1:]

        x -= 1

        index += 1

    return string


def indexFromRatio(dividend, divisor):
    '''
    Returns the ceiled ratio of two numbers as int.
    '''

    return int(ceil(float(dividend) / divisor))


def ensureLength(encoded, minlen, alphabet, guards, valuesHash):
    '''
    Ensures the minimal hash length
    '''

    guardsLen = len(guards)
    guardIdx = (valuesHash + ord(encoded[0])) % guardsLen
    encoded = guards[guardIdx] + encoded

    if len(encoded) < minlen:
        guardIdx = (valuesHash + ord(encoded[2])) % guardsLen
        encoded += guards[guardIdx]

    splitAt = len(alphabet) // 2

    while len(encoded) < minlen:
        alphabet = reorder(alphabet, alphabet)
        encoded = alphabet[splitAt:] + encoded + alphabet[:splitAt]
        excess = len(encoded) - minlen

        if excess > 0:
            from_index = excess // 2
            encoded = encoded[from_index:from_index + minlen]

    return encoded


def encode(values, salt, minlen, alphabet, seps, guards):
    '''
    Helper function that does the hash building without argument checks.
    '''

    alphabetLen = len(alphabet)
    sepsLen = len(seps)
    valuesHash = sum(x % (x + 100) for x, x in enumerate(values))
    encoded = lottery = alphabet[valuesHash % len(alphabet)]

    last = None

    for x, value in enumerate(values):
        alphabetSalt = (lottery + salt + alphabet)[:alphabetLen]
        alphabet = reorder(alphabet, alphabetSalt)
        last = hash(value, alphabet)
        encoded += last
        value %= ord(last[0]) + x
        encoded += seps[value % sepsLen]

    #: Cutting off the last separator
    encoded = encoded[:-1]

    if len(encoded) >= minlen:
        return encoded
    else:
        return ensureLength(
            encoded, minlen, alphabet, guards, valuesHash)


def decode(hid, salt, alphabet, seps, guards):
    '''
    Helper method that restores the values encoded in a hashid without
    argument checks.
    '''

    parts = tuple(stringSplit(hid, guards))
    hid = parts[1] if 2 <= len(parts) <= 3 else parts[0]

    if not hid:
        return

    lotteryChar = hid[0]
    hid = hid[1:]

    hashParts = stringSplit(hid, seps)

    for part in hashParts:
        alphabetSalt = (lotteryChar + salt + alphabet)[:len(alphabet)]
        alphabet = reorder(alphabet, alphabetSalt)
        yield unhash(part, alphabet)


def deprecated(func):
    '''
    A decorator that warns about deprecation when the passed-in function is
    invoked.
    '''

    @wraps(func)
    def with_warning(*args, **kwargs):
        warnings.warn(
            (
                'The %s method is deprecated and will be removed in v2.*.*' %
                func.__name__
            ),

            DeprecationWarning
        )

        return func(*args, **kwargs)

    return with_warning


def numberToHex(val):
    _hash = ''
    charset = '0123456789abcdef'
    alphabetLen = len(charset)

    while True:
        _hash = charset[val % alphabetLen] + _hash
        val //= alphabetLen
        if not val:
            return _hash

#: END OF FILE: ./IDHasher/_private.py
