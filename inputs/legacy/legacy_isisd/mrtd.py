#! /usr/bin/env python2.5

##     PyRT: Python Routeing Toolkit

##     MRTd module: provides MRT writing/reading using protocol
##     parsers from appropriate module.

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

import os, time, struct, getopt, sys, math, pprint, traceback

try:
    import bgp
except ImportError, ie:
    stk = traceback.extract_stack(limit=1)
    tb = stk[0]
    print "### File:", tb[0], "Line:", tb[1], ":", ie

try:
    import isis
except ImportError, ie:
    stk = traceback.extract_stack(limit=1)
    tb = stk[0]
    print "### File:", tb[0], "Line:", tb[1], ":", ie

try:
    import ospf
except ImportError, ie:
    stk = traceback.extract_stack(limit=1)
    tb = stk[0]
    print "### File:", tb[0], "Line:", tb[1], ":", ie

from mutils import *

#-------------------------------------------------------------------------------

DEFAULT_FILE = "mrtd.mrtd"
DEFAULT_SIZE = 50*1024*1024
MIN_FILE_SZ  = 50*1024

BUF_SZ       = 8192*8
INDENT       = "    "
VERSION      = "3.0"

COMMON_HDR_LEN         = 12

TABLE_DUMP_HDR_LEN     = 4

BGP_SUBTYPE_HDR_LEN    = 12
BGP4MP_SUBTYPE_HDR_LEN = 16
BGP4PY_SUBTYPE_HDR_LEN = 20

ISIS_SUBTYPE_HDR_LEN   = 0
ISIS2_SUBTYPE_HDR_LEN  = 4

OSPF2_SUBTYPE_HDR_LEN  = 4

################################################################################

DLIST = []

#
# MRTD values
#

MSG_TYPES = { 0L:  "NULL",
              1L:  "START",                # sender is starting up
              2L:  "DIE",                  # receiver should shutdown
              3L:  "I_AM_DEAD",            # sender is shutting down
              4L:  "PEER_DOWN",            # sender's peer is down
              5L:  "PROTOCOL_BGP",
              6L:  "PROTOCOL_RIP",
              7L:  "PROTOCOL_IDRP",
              8L:  "PROTOCOL_RIPNG",
              9L:  "PROTOCOL_BGP4PLUS",
              10L: "PROTOCOL_BGP4PLUS_01",
              11L: "PROTOCOL_OSPF2",
              12L: "TABLE_DUMP",           # routing table dump

              16L: "PROTOCOL_BGP4MP",      # Zebra BGP4

              17L: "PROTOCOL_BGP4PY",      # PyRT BGP4 (ext. time stamp)
              32L: "PROTOCOL_ISIS",        # ISIS
              33L: "PROTOCOL_ISIS2",       # ISIS + ext. time stamp

              64L: "PROTOCOL_OSPF2",       # OSPF v2
              }
DLIST = DLIST + [MSG_TYPES]

try:
    TABLE_DUMP_SUBTYPES = bgp.AFI_TYPES
    DLIST = DLIST + [TABLE_DUMP_SUBTYPES]

    BGP_SUBTYPES = { 0L: "NULL",
                     1L: "UPDATE",       # raw update
                     2L: "PREF_UPDATE",  # (T,L,V) prefs. followed by raw update
                     3L: "STATE_CHANGE", # state change
                     4L: "SYNC",

                     # XXX RMM XXX apparently bogo-extensions for some of RIS data?
                     # See, eg., updates.20000814.1631

                     5L: "BOGO_RIS_EXTN_1",
                     7L: "BOGO_RIS_EXTN_2",

                     # XXX RMM XXX extensions for other raw messages
                     129L: "OPEN",
                     131L: "NOTIFICATION",
                     132L: "KEEPALIVE",
                     133L: "ROUTE_REFRESH",
                     }
    DLIST = DLIST + [BGP_SUBTYPES]

    BGP4MP_SUBTYPES = { 0L: "STATE_CHANGE",
                        1L: "MESSAGE",
                        2L: "ENTRY",
                        3L: "SNAPSHOT"
                        }
    DLIST = DLIST + [BGP4MP_SUBTYPES]

    BGP4PY_SUBTYPES = { 0L: "STATE_CHANGE",
                        1L: "MESSAGE",
                        2L: "ENTRY",
                        3L: "SNAPSHOT"
                        }
    DLIST = DLIST + [BGP4PY_SUBTYPES]
except NameError, ne:
    stk = traceback.extract_stack(limit=1)
    tb = stk[0]
    print "### File:", tb[0], "Line:", tb[1], ":", ne

try:
    ISIS_SUBTYPES = isis.MSG_TYPES
    DLIST = DLIST + [ISIS_SUBTYPES]
except NameError, ne:
    stk = traceback.extract_stack(limit=1)
    tb = stk[0]
    print "### File:", tb[0], "Line:", tb[1], ":", ne

try:
    OSPF_SUBTYPES = ospf.MSG_TYPES
    DLIST += [OSPF_SUBTYPES]

except NameError, ne:
    stk = traceback.extract_stack(limit=1)
    tb = stk[0]
    print "### File:", tb[0], "Line:", tb[1], ":", ne

#
# GNU Zebra dump specific values
#

ZEBRA_STATES = { 1L: "IDLE",
                 2L: "CONNECT",
                 3L: "ACTIVE",
                 4L: "OPENSENT",
                 5L: "OPENCONFIRM",
                 6L: "ESTABLISHED"
                 }
DLIST = DLIST + [ZEBRA_STATES]

ZEBRA_EVENTS = { 1L:  "BGP_START",
                 2L:  "BGP_STOP",
                 3L:  "BGP_TRANS_CONN_OPEN",
                 4L:  "BGP_TRANS_CONN_CLOSED",
                 5L:  "BGP_TRANS_CONN_OPEN_FAILED",
                 6L:  "BGP_TRANS_FATAL_ERROR",
                 7L:  "CONNECTRETRY_TIMER_EXPIRED",
                 8L:  "HOLD_TIMER_EXPIRED",
                 9L:  "KEEPALIVE_TIMER_EXPIRED",
                 10L: "RCV_OPEN_MSG",
                 11L: "RCV_KEEPALIVE_MSG",
                 12L: "RCV_UPDATE_MSG",
                 13L: "RCV_NOTIFICATION_MSG"
                 }
DLIST = DLIST + [ZEBRA_EVENTS]

#-------------------------------------------------------------------------------

for d in DLIST:
    for k in d.keys():
        d[ d[k] ] = k

################################################################################

def parseBgp4mpMrtHdr(hdr, verbose=1, level=0):

    src_as, dst_as, ifc, afi, src_ip, dst_ip = struct.unpack(">HHHH LL", hdr)

    if verbose > 0:
        if afi == bgp.AFI_TYPES["IP"]:
            print level*INDENT + "AS(src): %d, AS(dst): %d" %\
                  (src_as, dst_as)
            print level*INDENT + "ifc idx: %d, AFI: %s" %\
                  (ifc, bgp.AFI_TYPES[afi])
            print level*INDENT + "IP(src): %s, IP(dst): %s" %\
                  (id2str(src_ip), id2str(dst_ip))
        else:
            print INDENT*level + "[ UNKNOWN ADDRESS FAMILY", `afi`, "]"

    return src_as, dst_as, ifc, afi, src_ip, dst_ip

#-------------------------------------------------------------------------------

def parseBgp4pyMrtHdr(hdr, verbose=1, level=0):

    src_as, dst_as, ifc, afi, src_ip, dst_ip, ts_frac =\
            struct.unpack(">HHHH LLL", hdr)

    if verbose > 0:
        if afi == bgp.AFI_TYPES["IP"]:
            print level*INDENT + "AS(src): %d, AS(dst): %d" %\
                  (src_as, dst_as)
            print level*INDENT + "ifc idx: %d, AFI: %s" %\
                  (ifc, bgp.AFI_TYPES[afi])
            print level*INDENT + "IP(src): %s, IP(dst): %s" %\
                  (id2str(src_ip), id2str(dst_ip))
        else:
            print INDENT*LEVEL + "[ UNKNOWN ADDRESS FAMILY", `afi`, "]"

    return src_as, dst_as, ifc, afi, src_ip, dst_ip, ts_frac

################################################################################

class EOFExc(Exception): pass
class ParseExc(Exception): pass

#-------------------------------------------------------------------------------

class Mrtd:

    _extn_fmt = ".%Y-%m-%d_%H.%M.%S"

    def __init__(self, file_pfx=DEFAULT_FILE, file_mode="w+b",
                 file_size=None, mrt_type=None, msg_src=None):

        self._mrt_type  = mrt_type
        self._msg_src   = msg_src # message source object, typed by mrt_type
        self._file_pfx  = file_pfx

        if not mrt_type:
            self._file_name = file_pfx
        else:
            self._file_name = file_pfx +\
                              time.strftime(Mrtd._extn_fmt, time.gmtime())

        self._file_size = file_size
        self._file_mode = file_mode

        self._of        = open(self._file_name, file_mode)
        self._read      = ""

    def __repr__(self):

        if self._msg_src:
            rs = """MRTD module:
            type: %s
            src:  %s
            pfx:  %s
            file: %s
            size: %s""" %\
            (MSG_TYPES[self._mrt_type],
             self._msg_src._sock, self._file_pfx, self._file_name, self._file_size)
        else:
            rs = """MRTD module:
            type: %s
            src:  %s
            pfx:  %s
            file: %s
            size: %s""" %\
            (MSG_TYPES[self._mrt_type],
             self._msg_src, self._file_pfx, self._file_name, self._file_size)

        return rs

    #---------------------------------------------------------------------------

    def close(self):
        # XXX RMM XXX this should possibly be __del__() method?
        try:
            self._of.flush()
            self._of.close()
        except IOError:
            pass

    def write(self, msg):

        if self._of.tell() + len(msg) > self._file_size:
            self._of.close()
            self._file_name = self._file_pfx +\
                              time.strftime(Mrtd._extn_fmt, time.gmtime())
            self._of = open(self._file_name, self._file_mode)

        self._of.write(msg)
        self._of.flush()

    def read(self):

        if len(self._read) < COMMON_HDR_LEN:
            self._read = self._read + self._of.read(BUF_SZ)
            if len(self._read) < COMMON_HDR_LEN:
                raise EOFExc

        ptime, ptype, psubtype, plen =\
               struct.unpack(">LHHL", self._read[:COMMON_HDR_LEN])
        plen = int(plen)

        phdr       = self._read[:COMMON_HDR_LEN]
        self._read = self._read[COMMON_HDR_LEN:]

        if len(self._read) < plen:
            self._read = self._read + self._of.read(BUF_SZ)
            if len(self._read) < plen:
                raise EOFExc

        pdata      = self._read[:plen]
        self._read = self._read[plen:]

        return (ptime, ptype, psubtype, plen, phdr, pdata)

    def parse(self, msg, verbose=1, level=0):

        (ptime, ptype, psubtype, plen, phdr, pdata) = msg

        if verbose > 1:
            print prtbin(level*INDENT, phdr)

        if verbose > 0:

            print level*INDENT + "[ " + time.ctime(ptime) + " ]"
            print level*INDENT + "MRT packet: len: %d, type: %s, subtype:" %\
                  (plen, MSG_TYPES.get(ptype, "UNKNOWN (%d)" % (ptype,))),

            try:
                if   ptype == MSG_TYPES["PROTOCOL_BGP4MP"]:
                    print BGP4MP_SUBTYPES[psubtype]

                elif ptype == MSG_TYPES["PROTOCOL_BGP4PY"]:
                    print BGP4MP_SUBTYPES[psubtype]

                elif ptype == MSG_TYPES["PROTOCOL_BGP"]:
                    print BGP_SUBTYPES[psubtype]

                elif ptype == MSG_TYPES["PROTOCOL_ISIS"]:
                    print ISIS_SUBTYPES[psubtype]

                elif ptype == MSG_TYPES["PROTOCOL_ISIS2"]:
                    print ISIS_SUBTYPES[psubtype]

                elif ptype == MSG_TYPES["PROTOCOL_OSPF2"]:
                    print OSPF_SUBTYPES[psubtype]

                elif ptype == MSG_TYPES["TABLE_DUMP"]:
                    print TABLE_DUMP_SUBTYPES[psubtype]

            except (KeyError):
                if verbose:
                    print level*INDENT +\
                          '[ *** Unsupported subtype: %d *** ]' % psubtype
                    return None

        if   ptype == MSG_TYPES["PROTOCOL_BGP"]:
            rv = self.parseBgpMsg(psubtype, plen, pdata, verbose, level+1)

        elif ptype == MSG_TYPES["PROTOCOL_BGP4MP"]:
            rv = self.parseBgp4mpMsg(psubtype, plen, pdata, verbose, level+1)

        elif ptype == MSG_TYPES["PROTOCOL_BGP4PY"]:
            rv = self.parseBgp4pyMsg(psubtype, plen, pdata, verbose, level+1)

        elif ptype == MSG_TYPES["PROTOCOL_ISIS"]:
            rv = self.parseIsisMsg(plen, pdata, verbose, level+1)

        elif ptype == MSG_TYPES["PROTOCOL_ISIS2"]:
            rv = self.parseIsis2Msg(plen, pdata, verbose, level+1)

        elif ptype == MSG_TYPES["PROTOCOL_OSPF2"]:
            rv = self.parseOspfMsg(plen, pdata, verbose, level+1)

        elif ptype == MSG_TYPES["TABLE_DUMP"]:
            rv = self.parseTableDump(psubtype, plen, pdata, verbose, level+1)

        else:
            rv = {"T": None, "L": 0, "V": None, "H": {"TIME":0L}}
            if verbose:
                print level*INDENT +\
                      "[ *** Unsupported message type [ '%s' ] *** ]" %\
                      self._file_name
                print (level+1)*INDENT + 'time:', time.ctime(ptime)
                print (level+1)*INDENT + 'header:', str2hex(phdr)
                print (level+1)*INDENT + 'data:', str2hex(pdata)

        rv["H"]["TIME"] =  rv["H"]["TIME"] + ptime
        if verbose:
            print (level+1)*INDENT +\
                  "extended timestamp: %f\n" % rv["H"]["TIME"]

        return rv

    def mkHdr(self, subtype, msg_len):

        ts = time.time()
        hdr = struct.pack(">LHHL", int(ts), self._mrt_type, subtype, msg_len)
        return (ts, hdr)

    #---------------------------------------------------------------------------

    def writeBgpMsg(self, msg_type, msg_len, msg):

        subtype = BGP_SUBTYPES[bgp.MSG_TYPES[msg_type]]
        (ts, hdr) = self.mkHdr(subtype, msg_len+BGP_SUBTYPE_HDR_LEN)

        src_as = self._msg_src._bgp_peer_as
        src_ip = self._msg_src._bgp_peer_id
        dst_as = self._msg_src._bgp_as
        dst_ip = self._msg_src._bgp_id

        msg = struct.pack(">%ds HLHL %ds" % (COMMON_HDR_LEN, msg_len),
                          hdr,
                          src_as, src_ip, dst_as, dst_ip,
                          msg)
        self.write(msg)

    def parseBgpMsg(self, psubtype, plen, pdata, verbose=1, level=0):

        rv = { "T":  MSG_TYPES["PROTOCOL_BGP"],
               "ST": psubtype,
               "L":  plen,
               "H":  { 'TIME': 0L },
               "V":  {}
               }

        if psubtype in (BGP_SUBTYPES['BOGO_RIS_EXTN_1'],
                        BGP_SUBTYPES['BOGO_RIS_EXTN_2']):
            print INDENT*level + '[ *** skipping *** ]'
            return rv

        if verbose > 1:
            print prtbin(level*INDENT, pdata[:BGP_SUBTYPE_HDR_LEN])

        try:
            src_as, src_ip, dst_as, dst_ip =\
                    struct.unpack(">HLHL", pdata[:BGP_SUBTYPE_HDR_LEN])
            rv["H"]["SRC_AS"] = src_as
            rv["H"]["SRC_IP"] = src_ip
            rv["H"]["DST_AS"] = dst_as
            rv["H"]["DST_IP"] = dst_ip

        except (struct.error):
            print INDENT*level + '[ *** struct error: bogus RIS data?! *** ]'
            if psubtype == BGP_SUBTYPES['STATE_CHANGE']:
                src, dst = struct.unpack(">HH", pdata[-4:])
                print INDENT*level +\
                      'state change: %s -> %s' %\
                      (ZEBRA_STATES[src], ZEBRA_STATES[dst])

            return rv

        if verbose > 0:
            print level*INDENT + "IP(src): %s, AS(src): %d" %\
                  (id2str(src_ip), src_as)
            print level*INDENT + "IP(dst): %s, AS(dst): %d" %\
                  (id2str(dst_ip), dst_as)

        pdata = pdata[BGP_SUBTYPE_HDR_LEN:]
        if pdata[0:len(bgp.BGP_MARKER)] != bgp.BGP_MARKER:
            raise ParseExc

        else:
            msg_len, msg_type =\
                     struct.unpack(">HB", pdata[len(bgp.BGP_MARKER):
                                                len(bgp.BGP_MARKER)+3])

        if verbose > 1:
            print prtbin(level*INDENT, pdata[:bgp.BGP_HDR_LEN])

        if verbose > 0:
            print level*INDENT + "BGP message type: %s len=%d" %\
                  (bgp.MSG_TYPES[msg_type], msg_len)

        rv["V"] = bgp.parseBgpPdu(msg_type, msg_len, pdata, verbose, level+1)

        return rv

    #---------------------------------------------------------------------------

    # NOTE: Bgp4mp is essentially GNU Zebra specific; as of version 0.89 and
    # 0.91a, Zebra's bgpd appears to have a couple of bugs wrt. dumping MRT
    # traces -- workarounds to patch things up before calling into the bgp
    # module are below.

    def writeBgp4mpMsg(self, ptype, plen, pkt):

        subtype = BGP4MP_SUBTYPES["MESSAGE"]
        (ts, hdr) = self.mkHdr(subtype, plen+BGP4MP_SUBTYPE_HDR_LEN)

        src_as = self._msg_src._bgp_peer_as
        dst_as = self._msg_src._bgp_as

        src_ip = self._msg_src._bgp_peer_id
        dst_ip = self._msg_src._bgp_id

        msg = struct.pack(">%ds HHHHLL %ds" % (COMMON_HDR_LEN, plen),
                          hdr,
                          src_as, dst_as, 0, bgp.AFI_TYPES["IP"], src_ip, dst_ip,
                          pkt)

        self.write(msg)

    def parseBgp4mpMsg(self, psubtype, plen, pdata, verbose=1, level=0):

        rv = { "T":  MSG_TYPES["PROTOCOL_BGP4MP"],
               "ST": psubtype,
               "L":  plen,
               "H":  { "TIME": 0L },
               "V":  {}
               }

        if psubtype == BGP4MP_SUBTYPES["STATE_CHANGE"]:
            if verbose > 1:
                print prtbin(level*INDENT, pdata)

            # XXX HACK get occasional 8 byte packets dumped, which I don't
            # _believe_ to be valid; seem to have a "valid" state changes in
            # though.  Bizarre.

            if plen == 8:

                if verbose > 0:
                    print level*INDENT +\
                          "[ *** BOGUS 8 byte PAYLOAD PACKET *** ]"
                pdata = pdata[4:]

            else:
                src_as, dst_as, ifc, afi, src_ip, dst_ip =\
                        parseBgp4mpMrtHdr(pdata[0:BGP4MP_SUBTYPE_HDR_LEN],
                                          verbose, level)

                rv["H"]["SRC_AS"] = src_as
                rv["H"]["DST_AS"] = dst_as
                rv["H"]["SRC_IP"] = src_ip
                rv["H"]["DST_IP"] = dst_ip
                rv["H"]["IFC"]    = ifc
                rv["H"]["AFI"]    = afi

                pdata = pdata[BGP4MP_SUBTYPE_HDR_LEN:]

            start_st, end_st = struct.unpack(">HH", pdata)
            rv["V"] = (start_st, end_st)
            if verbose > 0:
                print level*INDENT + "%s -> %s\n" %\
                      (ZEBRA_STATES[start_st], ZEBRA_STATES[end_st])

        elif psubtype == BGP4MP_SUBTYPES["MESSAGE"]:

            # XXX HACK similarly, get either (a) 4 null bytes instead of MRT
            # header, or (b) bogus MRT header for subtype MESSAGE.  Skip them.

            if pdata[0:4+bgp.BGP_MARKER_LEN] == ("\000\000\000\000" +
                                                 bgp.BGP_MARKER):
                if verbose > 1:
                    print prtbin(level*INDENT, pdata[:4])
                if verbose > 0:
                    print level*INDENT + "[ *** BOGUS NULL MRT HEADER *** ]"
                pdata = pdata[4:]
            else:
                if verbose > 1:
                    print prtbin(level*INDENT, pdata[:BGP4MP_SUBTYPE_HDR_LEN])
                src_as, dst_as, ifc, afi, src_ip, dst_ip =\
                        parseBgp4mpMrtHdr(pdata[0:BGP4MP_SUBTYPE_HDR_LEN],
                                          verbose, level)

                rv["H"]["SRC_AS"] = src_as
                rv["H"]["DST_AS"] = dst_as
                rv["H"]["SRC_IP"] = src_ip
                rv["H"]["DST_IP"] = dst_ip
                rv["H"]["IFC"]    = ifc
                rv["H"]["AFI"]    = afi

                pdata = pdata[BGP4MP_SUBTYPE_HDR_LEN:]

            msg_len, msg_type =\
                     struct.unpack(">HB",
                                   pdata[bgp.BGP_MARKER_LEN:bgp.BGP_HDR_LEN])
            rv["V"] = bgp.parseBgpPdu(msg_type, msg_len, pdata, verbose, level)

        else:
            print level*INDENT + "[ *** SUBTYPE: %d NOT PARSED *** ]" % psubtype

        return rv

    #---------------------------------------------------------------------------

    def writeBgp4pyMsg(self, ptype, plen, pkt):

        subtype = BGP4PY_SUBTYPES["MESSAGE"]
        (ts, hdr) = self.mkHdr(subtype, plen+BGP4PY_SUBTYPE_HDR_LEN)

        src_as = self._msg_src._bgp_peer_as
        dst_as = self._msg_src._bgp_as

        src_ip = self._msg_src._bgp_peer_id
        dst_ip = self._msg_src._bgp_id

        (ts_frac, ts_int) = math.modf(ts)
        msg = struct.pack(">%ds HH HH LLL %ds" % (COMMON_HDR_LEN, plen),
                          hdr,
                          src_as, dst_as, 0, bgp.AFI_TYPES["IP"],
                          src_ip, dst_ip, ts_frac*1000000,
                          pkt)
        self.write(msg)

    def parseBgp4pyMsg(self, psubtype, plen, pdata, verbose=1, level=0):

        rv = { "T":  MSG_TYPES["PROTOCOL_BGP4PY"],
               "ST": psubtype,
               "L":  plen,
               "H":  { "TIME": 0L },
               "V":  {}
               }

        if verbose > 1:
            print prtbin(level*INDENT, pdata[:BGP4PY_SUBTYPE_HDR_LEN])

        src_as, dst_as, ifc, afi, src_ip, dst_ip, ts_frac =\
                parseBgp4pyMrtHdr(pdata[0:BGP4PY_SUBTYPE_HDR_LEN], verbose, level)

        rv["H"]["SRC_AS"] = src_as
        rv["H"]["DST_AS"] = dst_as
        rv["H"]["SRC_IP"] = src_ip
        rv["H"]["DST_IP"] = dst_ip
        rv["H"]["IFC"]    = ifc
        rv["H"]["AFI"]    = afi
        rv["H"]["TIME"]   = ts_frac*0.000001

        pdata = pdata[BGP4PY_SUBTYPE_HDR_LEN:]

        if psubtype == BGP4PY_SUBTYPES["STATE_CHANGE"]:

            start_st, end_st = struct.unpack(">HH", pdata)
            rv["V"] = (start_st, end_st)
            if verbose > 0:
                print level*INDENT + "%s -> %s\n" %\
                      (ZEBRA_STATES[start_st], ZEBRA_STATES[end_st])

        elif psubtype == BGP4PY_SUBTYPES["MESSAGE"]:

            msg_len, msg_type =\
                     struct.unpack(">HB",
                                   pdata[bgp.BGP_MARKER_LEN:bgp.BGP_HDR_LEN])
            rv["V"] = bgp.parseBgpPdu(msg_type, msg_len, pdata, verbose, level)

        else:
            print level*INDENT + "[ *** SUBTYPE: %d NOT PARSED *** ]" % psubtype

        return rv

    #---------------------------------------------------------------------------

    def writeIsisMsg(self, ptype, plen, pkt):

        (ts, hdr) = self.mkHdr(ptype, plen+ISIS_SUBTYPE_HDR_LEN)
        msg = struct.pack(">%ds %ds" % (len(hdr), len(pkt)), hdr, pkt)
        self.write(msg)

    def parseIsisMsg(self, plen, pdata, verbose=1, level=0):

        rv = { "T":  MSG_TYPES["PROTOCOL_ISIS"],
               "ST": 0L,
               "L":  plen,
               "H":  { "TIME": 0L },
               "V":  {}
               }

        rv["V"].update(isis.parseIsisMsg(plen, pdata, verbose, level))
        return rv

    #---------------------------------------------------------------------------

    def writeIsis2Msg(self, ptype, plen, pkt):

        (ts, hdr) = self.mkHdr(ptype, plen+ISIS2_SUBTYPE_HDR_LEN)
        (ts_frac, ts_int) = math.modf(ts)
        msg = struct.pack(">%ds L %ds" % (COMMON_HDR_LEN, len(pkt)),
                          hdr, ts_frac*1000000, pkt)
        self.write(msg)

    def parseIsis2Msg(self, plen, pdata, verbose=1, level=0):

        rv = { "T":  MSG_TYPES["PROTOCOL_ISIS2"],
               "ST": 0L,
               "L":  plen,
               "H":  { "TIME": 0L },
               "V":  {}
               }

        (ts_frac, )     = struct.unpack(">L", pdata[:ISIS2_SUBTYPE_HDR_LEN])
        rv["H"]["TIME"] = ts_frac*0.000001
        rv["V"].update(isis.parseIsisMsg(plen, pdata[ISIS2_SUBTYPE_HDR_LEN:],
                                         verbose, level))
        return rv

    #---------------------------------------------------------------------------

    def writeOspfMsg(self, ptype, plen, pkt):

        (ts, hdr) = self.mkHdr(ptype, plen+OSPF2_SUBTYPE_HDR_LEN)
        (ts_frac, ts_int) = math.modf(ts)
        msg = struct.pack(">%ds L %ds" %(
            COMMON_HDR_LEN, len(pkt)), hdr, ts_frac*1000000, pkt)
        self.write(msg)

    def parseOspfMsg(self, plen, pdata, verbose=1, level=0):

        rv = { "T": MSG_TYPES["PROTOCOL_OSPF2"],
               "ST": 0L,
               "L": plen,
               "H": { "TIME": 0L, },
               "V": {}
            }

        (ts_frac, ) = struct.unpack(">L", pdata[:OSPF2_SUBTYPE_HDR_LEN])
        rv["H"]["TIME"] = ts_frac * 0.000001
        ospfh = ospf.parseOspfHdr(pdata[OSPF2_SUBTYPE_HDR_LEN+ospf.IP_HDR_LEN:
                                        OSPF2_SUBTYPE_HDR_LEN+ospf.IP_HDR_LEN+ospf.OSPF_HDR_LEN], 0, 0)
        rv["ST"] = ospfh["TYPE"]
        rv["V"].update(ospf.parseOspfMsg(pdata[OSPF2_SUBTYPE_HDR_LEN:], verbose, level))
        return rv

    #---------------------------------------------------------------------------

    def parseTableDump(self, psubtype, plen, pdata, verbose=1, level=0):

        rv = { "T":  MSG_TYPES["TABLE_DUMP"],
               "ST": psubtype,
               "L":  plen,
               "H":  { "TIME": 0L },
               "V":  []
               }

        if verbose > 1:
            print prtbin(level*INDENT, pdata[:TABLE_DUMP_HDR_LEN])

        view, seqno = struct.unpack(">HH", pdata[:TABLE_DUMP_HDR_LEN])

        rv["H"]["VIEW"]  = view
        rv["H"]["SEQNO"] = seqno

        if verbose:
            print INDENT*level + "view: %d, seqno: %d" % (view, seqno)

        pdata = pdata[TABLE_DUMP_HDR_LEN:]
        while len(pdata):
            erv = bgp.parseTableEntry(plen, pdata, verbose, level)
            pdata = pdata[erv["L"]:]
            rv["V"].append(erv)

        return rv

    #---------------------------------------------------------------------------

################################################################################

if __name__ == "__main__":

    VERBOSE = 1

    file_name  = DEFAULT_FILE
    file_size  = -1

    #---------------------------------------------------------------------------

    def usage():

        print """Usage: %s [ options ]:
        -h|--help      : Help
        -q|--quiet     : Be quiet
        -v|--verbose   : Be verbose

        -f|--file      : Set file name to parse (def: %s)
        -z|--file-size : Set size of output file(s)""" %\
            (os.path.basename(sys.argv[0]), DEFAULT_FILE)
        sys.exit(0)

    #---------------------------------------------------------------------------

    if len(sys.argv) < 2:
        usage()

    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:],
                                       "hqvVf:z:",
                                       ("help", "quiet", "verbose", "VERBOSE",
                                        "file=", "size=" ))
        except (getopt.error):
            usage()

        for (x, y) in opts:
            if x in ('-h', '--help'):
                usage()

            elif x in ('-q', '--quiet'):
                VERBOSE = 0

            elif x in ('-v', '--verbose'):
                VERBOSE = 2

            elif x in ('-V', '--VERBOSE'):
                VERBOSE = 3

            elif x in ('-f', '--file'):
                file_name = y

            elif x in ('-z', '--size'):
                file_size = string.atof(y)

            else:
                usage()

        #-----------------------------------------------------------------------

        mrt = Mrtd(file_name, "rb", file_size)
        while 1:
            rv = mrt.parse(mrt.read(), VERBOSE)
            if VERBOSE > 2: pprint.pprint(rv)

    except (EOFExc):
        print "End of file"
    except (KeyboardInterrupt):
        print "Interrupted"

    mrt.close()
    sys.exit(0)

################################################################################
################################################################################
