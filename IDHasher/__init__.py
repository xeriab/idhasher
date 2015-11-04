#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    __init__.py
'''

from __future__ import absolute_import
from __future__ import print_function

from ._private import *

__version__ = '0.1.0'
__author__ = ['Xeriab Nabil (aka KodeBurner) <kodeburner@gmail.com>']
__license__ = 'MIT License'

#: BEGIN OF THE SCRIPT


#: IDHasher CLASS
class IDHasher:
    '''
    Hashes and restores values using the "IDHasher" algorithm.
    '''

    VERSION = __version__

    SALT = ''
    MIN_LENGTH = 0
    CHARSET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def __init__(self, salt=SALT, minlen=MIN_LENGTH, alphabet=CHARSET):
        '''
        Initialises the IDHasher object with salt, minimum length, and alphabet

        :param salt: A string influencing the generated hash ids.
        :param minlen: The minimum length for generated hashes
        :param alphabet: The characters to use for the generated hash ids.
        '''

        self._salt = str(salt)
        self._minlen = max(int(minlen), 0)

        seps = ''.join(x for x in 'cfhistuCFHISTU' if x in alphabet)

        alphabet = ''.join(
            x for n, x in enumerate(alphabet)
            if alphabet.index(x) == n and x not in seps
        )

        alphabetLen, sepsLen = len(alphabet), len(seps)

        if alphabetLen + sepsLen < 16:
            raise ValueError(
                '`Alphabet` must contain at least'
                '16 unique characters.'
            )

        seps = reorder(seps, salt)

        minSeps = indexFromRatio(alphabetLen, RATIO_SEPARATORS)

        if not seps or sepsLen < minSeps:
            if minSeps == 1:
                minSeps = 2
            if minSeps > sepsLen:
                splitAt = minSeps - sepsLen
                seps += alphabet[:splitAt]
                alphabet = alphabet[splitAt:]
                alphabetLen = len(alphabet)

        alphabet = reorder(alphabet, salt)

        numGuards = indexFromRatio(alphabetLen, RATIO_GUARDS)

        if alphabetLen < 3:
            guards = seps[:numGuards]
            seps = seps[numGuards:]
        else:
            guards = alphabet[:numGuards]
            alphabet = alphabet[numGuards:]

        self._alphabet = str(alphabet)
        self._guards = guards
        self._separators = seps

        #: Support old API
        self.decrypt = deprecated(self.decode)
        self.encrypt = deprecated(self.encode)

        #: Support camel-cased method names
        self.encodeHex = self.encode_hex
        self.decodeHex = self.decode_hex

    def encode(self, *values):
        '''
        Builds a hash from the passed `values`.

        :param values The values to transform into a hashid

        >>> hashID = IDHasher('arbitrary salt', 16, 'abcdefghijkl0123456')
        >>> hashID.encode(1, 23, 456)
        '1d6216i30h53elk3'
        '''

        if not (values and all(isUint(x) for x in values)):
            return ''

        return encode(
            values, self._salt, self._minlen, self._alphabet,
            self._separators, self._guards)

    def decode(self, hid):
        '''
        Restore a tuple of numbers from the passed `hashid`.

        :param hid The hashid to decode

        >>> hashID = IDHasher('arbitrary salt', 16, 'abcdefghijkl0123456')
        >>> hashID.decode('1d6216i30h53elk3')
        (1, 23, 456)
        '''

        if not hid or not isString(hid):
            return ()
        try:
            numbers = tuple(
                decode(
                    hid, self._salt, self._alphabet,
                    self._separators, self._guards
                )
            )

            return numbers if hid == self.encode(*numbers) else ()
        except ValueError:
            return ()

    def encode_hex(self, hex):
        '''
        Converts a hexadecimal string (e.g. a MongoDB id) to a hashid.

        :param hex The hexadecimal string to encodes

        >>> IDHasher.encode_hex('507f1f77bcf86cd799439011')
        'y42LW46J9luq3Xq9XMly'
        '''

        numbers = (
            int('1' + hex[x:x + 12], 16)
            for x in range(0, len(hex), 12)
        )

        try:
            return self.encode(*numbers)
        except ValueError:
            return ''

    def decode_hex(self, hid):
        '''
        Restores a hexadecimal string (e.g. a MongoDB id) from a hashid.

        :param hid The hashid to decode

        >>> IDHasher.decode_hex('y42LW46J9luq3Xq9XMly')
        '507f1f77bcf86cd799439011'
        '''

        return ''.join(('%x' % x)[1:] for x in self.decode(hid))

#: END OF FILE: ./IDHasher/__init__.py
