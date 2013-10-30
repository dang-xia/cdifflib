#! /usr/bin/python2.7

"""
Module cdifflib -- c implementation of difflib.

Class CSequenceMatcher:
    A faster version of difflib.SequenceMatcher.  Reimplements a single
    bottleneck function - find_longest_match - in native C.  The rest of the
    implementation is inherited.
"""

__all__ = ['CSequenceMatcher']

import difflib
import _cdifflib

class CSequenceMatcher(difflib.SequenceMatcher):
    def __init__(self, isjunk=None, a='', b='', autojunk=True):
        """Construct a CSequenceMatcher.

        Simply wraps the difflib.SequenceMatcher.
        """
        difflib.SequenceMatcher.__init__(self, isjunk, a, b, autojunk)

    def find_longest_match(self, alo, ahi, blo, bhi):
        """Find longest matching block in a[alo:ahi] and b[blo:bhi].

        Wrapper for the C implementation of this function.
        """
        besti, bestj, bestsize = _cdifflib.find_longest_match(self, alo, ahi, blo, bhi)
        return difflib.Match(besti, bestj, bestsize)

    def set_seq2(self, b):
        """Same as SequenceMatcher.set_seq2, but uses the c chainb
        implementation.  
        """
        if b is self.b and hasattr(self, 'isbjunk'):
            return
        self.b = b
        if not isinstance(self.a, list):
            self.a = list(self.a)
        if not isinstance(self.b, list):
            self.b = list(self.b)
        self.matching_blocks = self.opcodes = None
        self.fullbcount = None
        junk, popular = _cdifflib.chain_b(self)
        assert hasattr(junk, '__contains__')
        assert hasattr(popular, '__contains__')
        self.isbjunk = junk.__contains__
        self.isbpopular = popular.__contains__
        # We use this to speed up find_longest_match a smidge

    def get_matching_blocks(self):
        """Same as SequenceMatcher.get_matching_blocks, but calls through to a
        faster loop for find_longest_match.  The rest is the same.
        """
        if self.matching_blocks is not None:
            return self.matching_blocks

        matching_blocks = _cdifflib.matching_blocks(self)
        matching_blocks.append( (len(self.a), len(self.b), 0) )
        self.matching_blocks = matching_blocks 

        return map(difflib.Match._make, self.matching_blocks)
    
