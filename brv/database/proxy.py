#!/usr/bin/env python
#
# Copyright (c) 2015, 2017 Marek Chalupa
# E-mail: statica@fi.muni.cz, mchalupa@mail.muni.cz
#
# Permission to use, copy, modify, distribute, and sell this software and its
# documentation for any purpose is hereby granted without fee, provided that
# the above copyright notice appear in all copies and that both that copyright
# notice and this permission notice appear in supporting documentation, and
# that the name of the copyright holders not be used in advertising or
# publicity pertaining to distribution of the software without specific,
# written prior permission. The copyright holders make no representations
# about the suitability of this software for any purpose. It is provided "as
# is" without express or implied warranty.
#
# THE COPYRIGHT HOLDERS DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO
# EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.


from os.path import basename
from .. utils import err, dbg

from . connection import DatabaseConnection

def None2Zero(x):
    if x is None:
        return 0
    return x

def Empty2Null(x):
    if x == '':
        return 'NULL'

    return '\'{0}\''.format(x.strip())

class DatabaseProxy(object):
    def __init__(self, conffile = None):
        self._db = DatabaseConnection(conffile)

        # self check
        ver = self._db.query('SELECT VERSION()')[0][0]
        dbg('Connected to database: MySQL version {0}'.format(ver))

    ## Shortcuts for convenience
    def query_noresult(self, q):
        return self._db.query_noresult(q)

    def queryInt(self, q):
        return self._db.queryInt(q)

    def query(self, q):
        return self._db.query(q)

    def commit(self):
        self._db.commit()

    def getToolID(self, name, version):
        q = """
        SELECT id FROM tool
        WHERE name = '{0}' AND version = '{1}';
        """.format(name, version)

        return self.queryInt(q)