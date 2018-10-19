##     PyRT: Python Routeing Toolkit

##     mutils: various miscellaneous functions for dealing with IP
##     addresses, prefixes, etc.

##     Copyright (C) 2001 Richard Mortier <mort@sprintlabs.com>, Sprint ATL

##     This program is free software; you can redistribute it and/or
##     modify it under the terms of the GNU General Public License as
##     published by the Free Software Foundation; either version 2 of the
##     License, or (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##     General Public License for more details.

##     You should have received a copy of the GNU General Public License
##     along with this program; if not, write to the Free Software
##     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
##     02111-1307 USA

#
# $Id: mutils.py,v 1.11 2002/02/26 01:57:03 mort Exp $
#

import string, struct, sys

#-------------------------------------------------------------------------------

def error(message):

    sys.stderr.write(message)
    sys.stderr.flush()

################################################################################

def mask2plen(mask):

    rv = 32
    while mask % 2 == 0:
        rv = rv - 1
        mask = mask >> 1

    return rv

#-------------------------------------------------------------------------------

def plen2mask(plen):

    return pow(2L, 32) - pow(2L, 32-plen)

#-------------------------------------------------------------------------------

def pfx2id(pfx, plen=None):

    if plen == None:
        plen = pfx[1]
        pfx  = pfx[0]

    mask = plen2mask(plen)
    p    = 0
    for i in range(len(pfx)):
        p = p << 8
        p = p | ord(pfx[i])
    p = p << (8 * (4-len(pfx)))
    p = p & mask

    return p

#-------------------------------------------------------------------------------

def addrmask2str(addr, mask):

    plen = mask2plen(mask)
    id   = addr & mask

    return "%s/%d" % (id2str(id), plen)

#-------------------------------------------------------------------------------

def pfx2str(pfx, plen=None):

    if plen == None:
        plen = int(pfx[1])
        pfx  = pfx[0]

    mask = plen2mask(plen)
    p = 0
    for i in range(len(pfx)):
        p = p << 8
        p = p | ord(pfx[i])
    p = p << (8 * (4-len(pfx)))
    p = p & mask

    return "%s/%d" % (id2str(p), plen)

#-------------------------------------------------------------------------------

def rpfx2str(pfxtup):

    plen, pfx = pfxtup

    p = 0
    for i in range(len(pfx)):
        p = p << 8
        p = p | ord(pfx[i])
    p = p << (8 * (4-len(pfx)))

    return "%s/%d" % (id2str(p), plen)

#-------------------------------------------------------------------------------

def id2pfx(id):

    a = int( ((id & 0xff000000L) >> 24) & 0xff)
    b = int( ((id & 0x00ff0000)  >> 16) & 0xff)
    c = int( ((id & 0x0000ff00)  >>  8) & 0xff)
    d = int( ((id & 0x000000ff))        & 0xff)

    return struct.pack('4B', a, b, c, d)

#-------------------------------------------------------------------------------

def id2str(id):

    return "%d.%d.%d.%d" %\
           (int( ((id & 0xff000000L) >> 24) & 0xff),
            int( ((id & 0x00ff0000)  >> 16) & 0xff),
            int( ((id & 0x0000ff00)  >>  8) & 0xff),
            int( (id  & 0x000000ff)         & 0xff) )

#-------------------------------------------------------------------------------

def str2id(str):

    quads = string.split(str, '.')
    ret   = (string.atol(quads[0]) << 24) + (string.atol(quads[1]) << 16) + \
            (string.atol(quads[2]) <<  8) + (string.atol(quads[3]) <<  0)
    return ret

#-------------------------------------------------------------------------------

def str2pfx(strng):

    pfx, plen = string.split(strng, '/')
    plen = string.atoi(plen)

    pfx = string.split(pfx, '.')
    p   = ''
    for e in pfx:
        p = struct.pack('%dsB' % len(p), p, string.atoi(e))
    pfx = p

    return (pfx, plen)

#-------------------------------------------------------------------------------

def isid2id(str):

    str = string.join(string.split(str2hex(str), '.'), '')
    str = "%s.%s.%s.%s" % (str[0:3], str[3:6], str[6:9], str[9:12])

    return str2id(str)

def hex2isisd(str):
    str = string.join(string.split(str2hex(str), '.'), '')
    str = "%s.%s.%s.%s" % (str[0:3], str[3:6], str[6:9], str[9:12])
    return str

################################################################################

def str2hex(str):

    if str == None or str == "":
        return ""

    ret = map(lambda x: '%0.2x' % x, map(ord, str))
    ret = string.join(ret, '.')

    return ret

#-------------------------------------------------------------------------------

def str2dec(str):

    if str == None or str == "":
        return ""

    ret = map(lambda x: '%0.2x' % x, map(ord, str))
    ret = string.join(ret, '')
    ret = int(ret,16)

    return ret

#-------------------------------------------------------------------------------
def prthex(pfx, str):

    if str == None or str == "":
        return ""

    ret = ""
    for i in range(0, len(str), 16):
        ret = ret + '\n' + pfx + '0x' + str2hex(str[i:i+16])
    return ret

#-------------------------------------------------------------------------------

def str2mac(str):

    bytes = string.split(str, '.')
    if len(bytes) != 6:
        return

    bytes = map(lambda x: string.atoi(x, 16), bytes)
    return struct.pack("BBB BBB",
                       bytes[0], bytes[1], bytes[2],
                       bytes[3], bytes[4], bytes[5])

################################################################################

def str2bin(str):

    if str == None or str == "":
        return ""

    ret = ""
    for i in range(len(str)):
        s = ""
        n = ord(str[i])
        for j in range(7, -1, -1):
            b = n / (2**j)
            n = n % (2**j)
            s = s + `b`
        ret = ret + ("%s." % s)

    return ret

#-------------------------------------------------------------------------------

def prtbin(pfx, str):

    if str == None or str == "":
        return ""

    ret = ""
    for i in range(0, len(str), 8):
        ret = ret + '\n' + pfx + str2bin(str[i:i+8])
    return ret

################################################################################

def int2bin(int):

    # XXX this breaks for negative numbers since >> is arithmetic (?)
    # -- ie. -1 >> 1 == -1...

    if int == 0: return '00000000'

    ret = "" ; bit = 0
    while int != 0:
        if bit % 8 == 0: ret = '.' + ret
        ret = `int%2` + ret
        int = int >> 1
        bit += 1

    if bit % 8 != 0: ret = (8 - bit%8)*"0" + ret
    return ret[:-1]

#-------------------------------------------------------------------------------

def int2hex(i):

    if i == 0:
        return "00"
    else:
        ret = ""

    while i != 0:
        ret = "%0.2x." % (i&0xff) + ret
        i = i >> 8

    return ret[:-1]

################################################################################
################################################################################
