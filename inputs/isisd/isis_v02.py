#! /usr/bin/env python2

##     PyRT: Python Routeing Toolkit

##     ISIS module: provides ISIS listener and ISIS PDU parsers

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

# refs: http://www.rware.demon.co.uk/isis.htm, RFC1195, RFC1142,

# This is a good deal grimmer than the BGP module since ISIS, by default on
# Ethernet/802.3 links, is encapsulated directly within the frame.  As a
# consequence we need PF_PACKET and SOCK_RAW to get it -- THESE ARE ONLY
# SUPPORTED IN PYTHON >= 2.0.  As a result this will not be as portable as I'd
# like.  Stick to Linux 2.2.x and higher kernels with packet sockets
# (CONFIG_PACKET) enabled; I've tested on RH7.1 std. install.  Also, it must
# run as root :-((

# Explanation of which bits we slurp: we are looking for ISIS packets carried
# in IEEE 802.3 frames.  This means that we have the following octet layout:

# MAC header (IEEE 802.3):

#   ss-ss-ss-ss-ss-ss :: <6:src MAC>
#   dd-dd-dd-dd-dd-dd :: <6:dst MAC>
#   ll-ll             :: <2:length> == 0x05dc == 1500 (payload only)

# LLC header (IEEE 802.2):
#   dsap :: <1:DSAP> == 0xfe ...by RFC1340, p53, "IEEE 802 Numbers of interest"
#   ssap :: <1:SSAP> == 0xfe ...("ISO CLNS IS 8473")
#   ctrl :: <1 or 2: control> == 0x03 ("unnumbered information")

# In fact, from (after some moulinexing :-)
# http://cell-relay.indiana.edu/cell-relay/docs/rfc/1483/1483.4.1.html

# In LLC Encapsulation the protocol of the routed PDU is identified by
# prefixing the PDU by an IEEE 802.2 LLC header, which is possibly followed by
# an IEEE 802.1a SubNetwork Attachment Point (SNAP) header. ...  The presence
# of a SNAP header is indicated by the LLC header value 0xAA-AA-03.

# ...

# The LLC header value 0xFE-FE-03 identifies that a routed ISO PDU (see [6]
# and Appendix B) follows. The Control field value 0x03 specifies Unnumbered
# Information Command PDU.  ... The routed ISO protocol is identified by a one
# octet NLPID field that is part of Protocol Data. NLPID values are
# administered by ISO and CCITT. They are defined in ISO/IEC TR 9577 [6] and
# some of the currently defined ones are listed in Appendix C.

# ...

# Appendix C. Partial List of NLPIDs
#  0x00    Null Network Layer or Inactive Set (not used with ATM)
#  0x80    SNAP
#  0x81    ISO CLNP
#  0x82    ISO ESIS
#  0x83    ISO ISIS
#  0xCC    Internet IP

# ie. we have 14 octets MAC header, 3 octets LLC header, and then we are in
# the ISIS packet, starting with the NLPID 0x83.  Phew.

# Note 1: AFI 49 (pfx on area code) is public CLNS space a la 10.x.x.x in IP

# Note 2: Actually, although the intro. above says this is grimmer, it is in
# fact quite a lot nicer once adjacency is established.  ISIS is a much nicer
# protocol than BGP which sucks high vacuum.

import sys, getopt, socket, string, os.path, struct, time, select, math
from mutils import *
from isisdb import *
from pprint import pprint
#-------------------------------------------------------------------------------

VERSION = "3.0"
INDENT  = "    "

RETX_THRESH = 1
RCV_BUF_SZ  = 2048

MAC_PKT_LEN  = 1514
MAC_HDR_LEN  = 17
ISIS_PKT_LEN = 1500
ISIS_PDU_LEN = ISIS_PKT_LEN-3
ISIS_LLC_HDR = (0xfe, 0xfe, 0x03, 0x83)

ISIS_HDR_LEN       =  8
ISIS_HELLO_HDR_LEN = 19
ISIS_LSP_HDR_LEN   = 19
ISIS_CSN_HDR_LEN   = 25
ISIS_PSN_HDR_LEN   =  9

AllL1ISs = struct.pack("6B", 0x01, 0x80, 0xc2, 0x00, 0x00, 0x14)
AllL2ISs = struct.pack("6B", 0x01, 0x80, 0xc2, 0x00, 0x00, 0x15)

#node list for now
nodes = []
################################################################################

DLIST = []

NLPIDS = { 0x00L: "NULL",
           0x80L: "SNAP",
           0x81L: "CLNP",
           0x82L: "ESIS",
           0x83L: "ISIS",
           0x8EL: "IPV6",
           0xCCL: "IP",
           }
DLIST = DLIST + [NLPIDS]

MSG_TYPES = { 0L:  "NULL",
              2L:  "ESH",
              4L:  "ISH",
              6L:  "RD",
              15L: "L1LANHello",
              16L: "L2LANHello",
              17L: "PPHello",
              18L: "L1LSP",
              20L: "L2LSP",
              24L: "L1CSN",
              25L: "L2CSN",
              26L: "L1PSN",
              27L: "L2PSN",
              }
DLIST = DLIST + [MSG_TYPES]

CIRCUIT_TYPES = { 0L: "reserved", # ignore entire PDU
                  1L: "L1Circuit",
                  2L: "L2Circuit",
                  3L: "L1L2Circuit",
                  }
DLIST = DLIST + [CIRCUIT_TYPES]

FLAGS = {1L: "SUPPORT_IP",
         2L: "SUPPORT_CLNP",
         }
DLIST = DLIST + [FLAGS]

VLEN_FIELDS = { 0L:   "Null",                # null
                1L:   "AreaAddress",         # area address
                2L:   "LSPIISNeighbor",      # ISIS (CLNP) neighbour (in LSP)
                3L:   "ESNeighbor",          # end system (CLNP) neighbour
                4L:   "PartDIS",             #
                5L:   "PrefixNeighbor",      #
                6L:   "IIHIISNeighbor",      # ISIS (CLNP) neighbour (in ISH)
                8L:   "Padding",             # zero padding
                9L:   "LSPEntries",          # LSPs ack'd in this CSNP/PSNP
                10L:  "Authentication",      #
                12L:  "OptionalChecksum",    #
                14L:  "LSPBufferSize",       #

                22L: "ExtendedISReach",      # RFC5305

                128L: "IPIntReach",          # 'internal' reachable IP subnets
                129L: "ProtoSupported",      # NLPIDs this IS can relay
                130L: "IPExtReach",          # 'external' reachable IP subnets
                131L: "IPInterDomInfo",      # interdomain routeing info
                132L: "IPIfAddr",            # IP address(es) of the interface
                133L: "IPAuthInfo_ILLEGAL",  # deprecated
                134L: "TERouterID",          # TE router ID
                135L: "TEIPReach",           # 'wide metric TLV'
                137L: "DynamicHostname",     # dynamic hostname support

                180L: "LeafNode",            #

                222L: "MultipleTopologyISN", #
                229L: "MultipleTopologies",  #
                232L: "IPv6IfAddr",          #
                235L: "MTIPReach",           #
                236L: "IPv6IPReach",         #
                240L: "ThreeWayHello",       #

                254L: "IPSumReach",          #
                }
DLIST = DLIST + [VLEN_FIELDS]

STATES = { 0L: "NULL",
           1L: "INITIALISING",
           2L: "UP",
           3L: "DOWN",
           }
DLIST = DLIST + [STATES]

for d in DLIST:
    for k in d.keys():
        d[ d[k] ] = k

################################################################################

def padPkt(tgt_len, pkt):

    pad_len = tgt_len - len(pkt)
    if pad_len > 0:
        full, part = divmod(pad_len, 257)

        pkt = pkt + (full*struct.pack("BB 255s",
                                 VLEN_FIELDS["Padding"], 255, 255*'\000'))
        pkt = pkt + struct.pack("BB %ds" % (part-2, ),
                           VLEN_FIELDS["Padding"], part-2, (part-2)*'\000')
    return pkt

def api():
    return "OK"
#-------------------------------------------------------------------------------

def parseMacHdr(pkt):

    (dst_mac, src_mac, length, dsap, ssap, ctrl, nlpid) =\
              struct.unpack(">6s 6s H B B B B", pkt[0:MAC_HDR_LEN+1])

    if (dsap, ssap, ctrl, nlpid) != ISIS_LLC_HDR:
        raise LLCExc

    return (src_mac, dst_mac, length, dsap, ssap, ctrl)

#-------------------------------------------------------------------------------

def parseIsisHdr(pkt):

    (nlpid, hdr_len, ver_proto_id, resvd, msg_type, ver, eco, user_eco) =\
            struct.unpack(">8B", pkt[0:ISIS_HDR_LEN])

    return (nlpid, hdr_len, ver_proto_id, resvd,
            msg_type, ver, eco, user_eco)

#-------------------------------------------------------------------------------

def parsePsnHdr(pkt):

    (pdu_len, src_id) = struct.unpack("> H 7s", pkt[:ISIS_PSN_HDR_LEN])

    return (pdu_len, src_id)

#-------------------------------------------------------------------------------

def parseCsnHdr(pkt):

    (pdu_len, src_id, start_lsp_id, end_lsp_id) =\
              struct.unpack("> H 7s 8s 8s", pkt[:ISIS_CSN_HDR_LEN])

    return (pdu_len, src_id, start_lsp_id, end_lsp_id)

#-------------------------------------------------------------------------------

def parseLspHdr(pkt):

    (pdu_len, lifetime, lsp_id, seq_no, cksm, bits) =\
              struct.unpack("> HH 8s LHB", pkt[:ISIS_LSP_HDR_LEN])
    lsp_id = struct.unpack("> 6sBB", lsp_id)

    return (pdu_len, lifetime, lsp_id, seq_no, cksm, bits)

################################################################################

def parseIsisMsg(msg_len, msg, verbose=0, level=0):

    (src_mac, dst_mac, length, dsap, ssap, ctrl) = parseMacHdr(msg)
    (nlpid, hdr_len, ver_proto_id, resvd, msg_type, ver, eco, user_eco) =\
            parseIsisHdr(msg[MAC_HDR_LEN:MAC_HDR_LEN+ISIS_HDR_LEN])

    if verbose > 1:
        print prtbin(level*INDENT, msg[:MAC_HDR_LEN])

    if verbose > 0:
        print level*INDENT +\
              "%s (len=%d):" % (MSG_TYPES[msg_type], length)
        print (level+1)*INDENT +\
              "src mac: %s, dst mac: %s" %\
              (str2hex(src_mac), str2hex(dst_mac))
        print (level+1)*INDENT +\
              "len: %d, LLC: 0x%0.2x.%0.2x.%0.2x" %\
              (length, dsap, ssap, ctrl)

    if verbose > 1:
        print prtbin((level+1)*INDENT,
                     msg[MAC_HDR_LEN:MAC_HDR_LEN+ISIS_HDR_LEN])

    if verbose > 0:
        print (level+1)*INDENT +\
              "hdr_len: %d, protocol id: %d, version: %d, " %\
              (hdr_len, ver_proto_id, ver) +\
              "eco: %d, user eco: %d" % (eco, user_eco)

    rv = {"T": msg_type,
          "L": msg_len,
          "H": {},
          "V": {}
          }

    rv["H"]["SRC_MAC"] = src_mac
    rv["H"]["DST_MAC"] = dst_mac
    rv["H"]["LENGTH"]  = length
    rv["H"]["DSAP"]    = dsap
    rv["H"]["SSAP"]    = ssap
    rv["H"]["CTRL"]    = ctrl

    rv["H"]["NLPID"]        = nlpid
    rv["H"]["HDR_LEN"]      = hdr_len
    rv["H"]["VER_PROTO_ID"] = ver_proto_id
    rv["H"]["VER"]          = ver
    rv["H"]["ECO"]          = eco
    rv["H"]["USER_ECO"]     = user_eco

    msg = msg[MAC_HDR_LEN+ISIS_HDR_LEN:]
    if msg_type in MSG_TYPES.keys():
        if   msg_type in (MSG_TYPES["L1LANHello"], MSG_TYPES["L2LANHello"]):
            (rv["V"]["CIRCUIT_TYPE"],
             rv["V"]["SRC_ID"],
             rv["V"]["HOLDTIMER"],
             rv["V"]["PDU_LEN"],
             rv["V"]["PRIO"],
             rv["V"]["LAN_ID"],
             rv["V"]["VFIELDS"]) = parseIsisIsh(msg_len, msg, verbose, level)

        elif msg_type == MSG_TYPES["PPHello"]:
            parseIsisPPIsh(msg_len, msg, verbose, level)

        elif msg_type in (MSG_TYPES["L1LSP"], MSG_TYPES["L2LSP"]):
            (rv["V"]["PDU_LEN"],
             rv["V"]["LIFETIME"],
             rv["V"]["LSP_ID"],
             rv["V"]["SEQ_NO"],
             rv["V"]["CKSM"],
             rv["V"]["BITS"],
             rv["V"]["VFIELDS"]) = parseIsisLsp(msg_len, msg, verbose, level)

        elif msg_type in (MSG_TYPES["L1CSN"], MSG_TYPES["L2CSN"]):
            (rv["V"]["PDU_LEN"],
             rv["V"]["SRC_ID"],
             rv["V"]["START_LSP_ID"],
             rv["V"]["END_LSP_ID"],
             rv["V"]["VFIELDS"]) = parseIsisCsn(msg_len, msg, verbose, level)

        elif msg_type in (MSG_TYPES["L1PSN"], MSG_TYPES["L2PSN"]):
            (rv["V"]["PDU_LEN"],
             rv["V"]["SRC_ID"],
             rv["V"]["VFIELDS"]) = parseIsisPsn(msg_len, msg, verbose, level)

        else:
            if verbose > 0:
                print level*INDENT + "[ *** %s *** ]" % MSG_TYPES[msg_type]

    else:
        if verbose > 0:
            print level*INDENT + "[ UNKNOWN ISIS message: ", `msg_type`, " ]"

    return rv

################################################################################

def parseIsisIsh(msg_len, msg, verbose=0, level=0):

    (circuit_type, src_id, holdtimer,
     pdu_len, prio, lan_id) = struct.unpack("> B 6s H H B 7s",
                                            msg[:ISIS_HELLO_HDR_LEN])

    if verbose > 1:
        print prtbin(level*INDENT, msg[:ISIS_HELLO_HDR_LEN])

    if verbose > 0:
        print (level+1)*INDENT +\
              "circuit type: %s, holdtimer: %d, " %\
              (CIRCUIT_TYPES[circuit_type], holdtimer) +\
              "PDU len: %d, priority: %d" % (pdu_len, (prio&0x7f))
        print (level+1)*INDENT + "src id: %s, LAN id: %s" %\
              (str2hex(src_id), str2hex(lan_id))

    vfields = parseVLenFields(msg[ISIS_HELLO_HDR_LEN:], verbose, level)
    return (circuit_type, src_id, holdtimer, pdu_len, prio, lan_id, vfields)

#-------------------------------------------------------------------------------

def parseIsisPPIsh(msg_len, msg, verbose=0, level=0):

    print level*INDENT + "[ *** PP ISH NOT PARSED *** ]"

#-------------------------------------------------------------------------------

def parseIsisLsp(msg_len, msg, verbose=1, level=0):
    (pdu_len, lifetime, lsp_id, seq_no, cksm, bits) = parseLspHdr(msg)
    if verbose > 0:

        if verbose > 1:
            print prtbin(level*INDENT, msg[:ISIS_LSP_HDR_LEN])
        print (level+1)*INDENT +\
              "PDU len: %d, lifetime: %d, seq.no: %d, cksm: %s" %\
              (pdu_len, lifetime, seq_no, int2hex(cksm))
        print (level+1)*INDENT +\
              "LSP ID: src: %s, pn: %s, LSP no: %d" %\
              (str2hex(lsp_id[0]), int2hex(lsp_id[1]), lsp_id[2])

        p   = bits & (1<<7)
        att = (bits & (1<<6)) * "error " + (bits & (1<<5)) * "expense " +\
              (bits & (1<<4)) * "delay " + (bits & (1<<3)) * "default"
        hty = (bits & (1<<2)) >> 2
        ist = bits & ((1<<1) | (1<<0))

        print (level+1)*INDENT +\
              "partition repair: %s, hippity: %s, type: %s" %\
              (("no", "yes")[p], ("no", "yes")[hty],
               ("UNUSED", "L1", "UNUSED", "L1+L2")[ist])
        print (level+1)*INDENT + "attached: %s" % att
    vfields = parseVLenFieldsLnetD(msg[ISIS_LSP_HDR_LEN:], lsp_id, seq_no , verbose, level)
    #print 'ISISLSP:',INDENT,'lsp_id:{} \n seq_no: {} \n'.format(lsp_id,seq_no)
    #print 'lsp_id:{} \n'.format(lsp_id)
    #print 'ISISLSP:',INDENT*2,'vfields are :{} '.format(vfields)
    print '\n------------ISIS-LSP----------\n'
    node_id = hex2isisd(lsp_id[0])
    pseudonode = lsp_id[1]
    fragment = lsp_id[2]
    print '\n Nodes List :{} \n'.format(nodes)
    print ('node_id: {} - pseudonode {} - fragment: {} - seq_no: {}' ).format(node_id,pseudonode,fragment,seq_no) 
    if pseudonode == 3:
      print "ignore"
    else:
      node = Node(node_id,pseudonode,fragment,seq_no,vfields)
      print 'found a new  node : {} and create a Node class'.format(node)
      if node not in nodes:
        print 'found a new node with node: {} that is not in nodes: '.format(node)
        nodes.append(node)
        #print 'update ^'
        #for i in nodes:
          #print 'what are the nodes at the moment : \n \n {} \n \n ----'.format(i)
      else:
        position = nodes.index(node)
        print ' position of {} is {} position'.format(node,position)
        if (node.seq_no == 0 or lifetime ==0):
          print 'found a seq_no with 0 please remove : seq: {} lifetime {}'.format(node.seq_no,lifetime)
          del nodes[position]
          print 'delete previous lsp_id'
        elif node.seq_no > nodes[position].seq_no:
          print ' node is :{} and seg_no is :{} and its higher that {} with {}'.format(node,node.seq_no,nodes[position],nodes[position].seq_no) 
          print ' found a newer seq_no'
          del nodes[position]
          #print ' delete old lsp_id'
          nodes.append(node)
          #print 'add new one'
        else:
          pass
    print '\n------------END ISIS-LSP---------- \n'
    return (pdu_len, lifetime, lsp_id, seq_no, cksm, bits, vfields)

#-------------------------------------------------------------------------------

def parseIsisCsn(msg_len, msg, verbose=0, level=0):

    (pdu_len, src_id, start_lsp_id, end_lsp_id) = parseCsnHdr(msg)

    if verbose > 0:

        if verbose > 1:
            print prtbin(level*INDENT, msg[:ISIS_CSN_HDR_LEN])
        print (level+1)*INDENT +\
              "PDU len: %d, src ID: %s" % (pdu_len, str2hex(src_id))
        print (level+1)*INDENT +\
              "start LSP ID: %s" % (str2hex(start_lsp_id),)
        print (level+1)*INDENT +\
              "end LSP ID: %s" % (str2hex(end_lsp_id),)

    vfields = parseVLenFieldsLnetD(msg[ISIS_CSN_HDR_LEN:], verbose, level)
    #print 'vfields in IsisCsn are : {}'.format(vfields)
    print '\n------------IsisCSN----------\n'
    #print '\n Nodes List :{} \n'.format(nodes)
    for i in vfields[9][0]['V']:
      node_id = hex2isisd(i['ID'])
      pseudonode = i['PN']
      fragment = i['NM']
      seq_no = i['SEQ_NO']
      checksum = i['CKSM']
      lifetime = i['LIFETIME']
      if pseudonode == 3:
        print "ignore - pseudonode for DIS"
      else:
        #print '----node.seq_no: {} checksum: {} lifetime: {}'.format(seq_no,checksum,lifetime)
        #print 'creating a dummy node class with no data'
        node = Node(node_id,pseudonode,fragment,seq_no,{})
        try:
          if node in nodes:
            position = nodes.index(node)
            #print '----position of {} is {} position'.format(node,position)
            #print '----node.seq_no: {} checksum: {} lifetime: {} and node[position]seq_no:{}'.format(node.seq_no,checksum,lifetime,nodes[position].seq_no)
            if (node.seq_no == 0 or checksum == 0 or lifetime ==0 or node.seq_no >= nodes[position].seq_no + 2): #this is not correct , need to find out the rfc...
              #print '--------found a seq_no or checksum or lifetime with 0...removing node'
              del nodes[position]
            else:
              print '--------node seq_no or checksum or lifetime NOT 0...nothing to do here'
          else:
            print 'node {} not in nodes ... nothing to do here'.format(node)
            #print ' this is the nodes list'.format(nodes)
        except:
          print 'something went wrong'
    print '\n------------END - IsisCSN----------\n'
    return (pdu_len, src_id, start_lsp_id, end_lsp_id, vfields)

#-------------------------------------------------------------------------------

def parseIsisPsn(msg_len, msg, verbose=0, level=0):

    (pdu_len, src_id) = parsePsnHdr(msg)

    if verbose > 0:

        if verbose > 1:
            print prtbin(level*INDENT, msg[:ISIS_PSN_HDR_LEN])
        print (level+1)*INDENT +\
              "PDU len: %d, src ID: %s" % (pdu_len, str2hex(src_id))

    vfields = parseVLenFields(msg[ISIS_PSN_HDR_LEN:], verbose, level)
    return (pdu_len, src_id, vfields)

################################################################################

def parseVLenFields(fields, verbose=0, level=0):

    vfields = {}

    while len(fields) > 1:
        # XXX: strange -- have seen single null byte vfields...

        (ftype, flen) = struct.unpack(">BB", fields[0:2])

        if not vfields.has_key(ftype):
            vfields[ftype] = []

        vfields[ftype].append(
            parseVLenField(ftype, flen, fields[2:2+flen], verbose, level+1)
            )

        fields = fields[2+flen:]

    return vfields

#-------------------------------------------------------------------------------
#------------------------------------------------cp-----------------------------
def parseVLenFieldsLnetD(fields, lsp_id, seq_no, verbose=0, level=0):

    vfields = {}
    #print 'this is the lsp_id {} with lsp_id_xx {}'.format(str2hex(lsp_id[0]),lsp_id[1])
    #print 'this is the seq_no {}'.format(seq_no)

    while len(fields) > 1:
        # XXX: strange -- have seen single null byte vfields...

        (ftype, flen) = struct.unpack(">BB", fields[0:2])

        if not vfields.has_key(ftype):
            vfields[ftype] = []

        vfields[ftype].append(
            parseVLenFieldLnetD(ftype, flen, fields[2:2+flen], verbose, level+1)
            )

        fields = fields[2+flen:]
    return vfields

#------------------------------------------------cp-----------------------------
def parseVLenFieldLnetD(ftype, flen, fval, verbose=0, level=0):
    node = None
    verbose = 0
    rv = { "L" : flen,
           }
    if verbose > 1 and ftype not in (VLEN_FIELDS["Padding"],
                                     VLEN_FIELDS["Null"]):
        print prtbin(level*INDENT,`ftype`+`flen`+fval)
    verbose = 0

    if ftype in VLEN_FIELDS.keys():
        if verbose > 0 and ftype not in (VLEN_FIELDS["Padding"],
                                         VLEN_FIELDS["Null"]):
            print level*INDENT +\
                  "field: %s, length: %d" % (VLEN_FIELDS[ftype], flen)

        level = level + 1
        if   ftype == VLEN_FIELDS["Null"]:
            pass

        elif ftype == VLEN_FIELDS["AreaAddress"]:
            ## 1
            rv["V"] = []
            areas = ""
            while len(fval) > 0:

                (l,) = struct.unpack("> B", fval[0])

                #rv["V"].append(fval[1:1+l])

                areas = areas + '0x' + str2hex(fval[1:1+l]) + ", "
                fval = fval[1+l:]

            if verbose > 0:
                print level*INDENT + "area addresses: " + areas
            pass

        elif ftype == VLEN_FIELDS["LSPIISNeighbor"]:
            verbose = 0
            ## 2
            rv["V"] = []
            vflag = struct.unpack("> B", fval[0])
            fval  = fval[1:]
            cnt   = 0
            while len(fval) > 0:
                cnt = cnt + 1
                default, delay, expense, error, nid =\
                         struct.unpack("> BBBB 7s", fval[0:11])

                is_neighbour = { 'DEFAULT': default,
                                 'DELAY'  : delay,
                                 'EXPENSE': expense,
                                 'ERROR'  : error,
                                 'NID'    : nid,
                                 }
                #rv["V"].append(is_neighbour)

                if verbose > 0:
                    print level*INDENT +\
                          "IS Neighbour %d: id: %s" % (cnt, str2hex(nid))
                    print (level+1)*INDENT +\
                          "default: %d, delay: %d, expense: %d, error: %d" %\
                          (default, delay, expense, error)

                fval = fval[11:]
            pass  
        elif ftype == VLEN_FIELDS["ESNeighbor"]:
            ## 3
            default, delay, expense, error = struct.unpack("> 4B", fval[0:4])
            rv["V"] = { 'DEFAULT' : default,
                        'DELAY'   : delay,
                        'EXPENSE' : expense,
                        'ERROR'   : error,
                        'NIDS'    : []
                        }

            if verbose > 0:
                print level*INDENT +\
                      "default: %d, delay: %d, expense: %d, error: %d" %\
                      (default, delay, expense, error)

            fval = fval[4:]
            cnt  = 0
            while len(fval) > 0:
                cnt = cnt + 1
                (nid,) = struct.unpack("> 6s", fval[0:6])

                #rv["V"]["NIDS"].append(nid)

                if verbose > 0:
                    print level*INDENT +\
                          "ES Neighbour %d: %s" % (cnt, str2hex(nid))

                fval = fval[6:]
            pass
        elif ftype == VLEN_FIELDS["IIHIISNeighbor"]:
            ## 6
            rv["V"] = []
            cnt = 0
            while len(fval) > 0:
                cnt = cnt + 1
                (nid,) = struct.unpack("> 6s", fval[0:6])

                #rv["V"].append(nid)

                if verbose > 0:
                    print level*INDENT +\
                          "IS Neighbour %d: %s" % (cnt, str2hex(nid))

                fval = fval[6:]
            pass
        elif ftype == VLEN_FIELDS["Padding"]:
            ## 8
            rv["V"] = None

        elif ftype == VLEN_FIELDS["LSPEntries"]:
            ## 9
            rv["V"] = []
            cnt = 0
            while len(fval) > 0:
                cnt = cnt + 1
                lifetime, lsp_id, lsp_seq_no, cksm =\
                          struct.unpack("> H 8s L H", fval[:16])
                #print 'lsp_id before unpack again',lsp_id
                lsp_id = struct.unpack("> 6sBB", lsp_id)
                #print 'lsp_id after unpack ',lsp_id

                lsp_entry = { "ID"       : lsp_id[0],
                              "PN"       : lsp_id[1],
                              "NM"       : lsp_id[2],
                              "LIFETIME" : lifetime,
                              "SEQ_NO"   : lsp_seq_no,
                              "CKSM"     : cksm
                              }

                rv["V"].append(lsp_entry)
                if verbose > 0:
                    print level*INDENT +\
                          "%d: LSP ID: src: %s, pn: %s, LSP no: %d" %\
                          (cnt, str2hex(lsp_id[0]), int2hex(lsp_id[1]), lsp_id[2])
                    print (level+1)*INDENT +\
                          "lifetime: %d, seq.no: %d, cksm: %s" %\
                          (lifetime, lsp_seq_no, int2hex(cksm))
                fval = fval[16:]

        elif ftype == VLEN_FIELDS["ExtendedISReach"]:
            ## 22
            rv["V"] = []
            rv["SV"] = []
            cnt = -1
            #print INDENT + "inside first if: found TLV 22 let's start working on it: " 
            while len(fval) > 0:
              cnt += 1
              '''
              we are in lsp packet now
              that may contain multiple lsp_ip neighbours each with subtlv
              we take lsp_ip and metric and push it to rv['V']
              '''
              lsp_id = struct.unpack("> 7s", fval[0:7])
              metric = struct.unpack("> sss", fval[7:10])
              tlv_len = struct.unpack(">B",fval[10])
              #print "LSP: %s , METRIC: %s , tlv_l: %s" %(hex2isisd(lsp_id[0]),str2dec(metric),tlv_len)
              metric = int(str2dec(metric))
              #print 'tlv_len---------:',tlv_len[0]
              #print 'fval_len--------:',len(fval)
              '''
              after lsp_id and metric found move packet and check for subtlv
              '''
              rv['V'].append({'lsp_id':hex2isisd(lsp_id[0]),
                              'metric':metric,
                              'l_ip': None,
                              'r_ip': None})
              #print INDENT*1,'***packet at: {}'.format(len(fval))
              #print INDENT*1,'***Found a neighbour(len7):',hex2isisd(lsp_id[0])
              #print INDENT*1,'***Found a metric(len3):',metric
              #print INDENT*1,'***Found a tlv:(len1)',tlv_len[0]
              fval = fval[11:]
              #print INDENT*1,'***packet at: {}'.format(len(fval))
              rem_tvl = tlv_len[0]  # is for the subtlv , nee a better way ,new variable for tlv lenght 
              #print INDENT*1,'remaining tlv: {}'.format(rem_tvl)
              while tlv_len[0] > 0 and rem_tvl > 0: #and len(fval) > 0: do i need both ?
                '''
                while we have packets in buffer we find what type of sub_tlv and len
                we have
                '''
                #print prthex(':',fval)
                #print '*******************************enter here ? ********************'
                rem_tvl  -= 2
                #print INDENT*2,'remaining tlv: {}'.format(rem_tvl)
                (sub_ftype, sub_flen) = struct.unpack(">BB", fval[0:2]) # find sub_tlv type and len
                fval = fval[2:] # move packet to sub_tlv content 
                #print INDENT*2,'***found a sub_tlv with type:{} and len: {} packet(len2-sub_type,sub_len) is at position: {}'.format(sub_ftype,sub_flen,len(fval))
                #print 'sub_ftype and len',sub_ftype,sub_flen
                #print "before sub_type RV is : {}".format(rv['V'][cnt])
                if sub_ftype == 6 and sub_flen >0: # if we found the sub_tlv we are looking for and the sub_tlv not 0 ? can this happen 
                    #print INDENT*4,'found subtlv 6'
                    #print prthex('l_ip:',fval[0:sub_flen])
                    l_ip = struct.unpack(">L",fval[0:sub_flen]) # get local_ip
                    l_ip =id2str(l_ip[0])
                    #print 'l_ip:{}'.format(l_ip)
                    fval = fval[sub_flen:] #move packet forward 
                    rem_tvl -= sub_flen # decrease remaining tvl with this subtlv lenght 
                    #print INDENT*2,'remaining tlv: {}'.format(rem_tvl)
                    #print prthex('next:',fval[17:21])
                    #print len(fval)
                    rv["V"][cnt]['l_ip'] = l_ip #append the info to something ? need to find a clean way
                    #print "rv[V][0][l_ip]:{}".format(rv["V"][cnt]['l_ip'])
                    #print "at this stage RV is : {}".format(rv)
                    #print INDENT*2,'***with local_ip:{} and packet at: {}'.format(l_ip,len(fval))
                elif sub_ftype == 8 and sub_flen >0: #if we found the sub_tlv we are looking for and the sub_tlv not 0 ? can this happen
                    #print INDENT*4,'found subtlv 8'
                    #print prthex('FFF:',fval[0:sub_flen])
                    r_ip = struct.unpack(">L",fval[0:sub_flen]) # get remove_ip
                    r_ip = id2str(r_ip[0])
                    #print 'r_ip:{}'.format(r_ip)
                    rv["V"][cnt]['r_ip'] = r_ip  #append the info to something ? need to find a clean way 
                    #print "rv[V][0][r_ip]: {}".format(rv["V"][cnt]['r_ip'])
                    #print "at this stage RV is : {}".format(rv)
                    fval = fval[sub_flen:] #move packet forward
                    rem_tvl -=sub_flen # decrease rem_tlv
                    #print INDENT*2,'remaining tlv: {}'.format(rem_tvl)
                    #print INDENT*2,'***with remote_ip:{} and packet at: {}'.format(r_ip,len(fval))
                else: # we don't care about rest of sub_tlv's
                    fval = fval[sub_flen:] # move packet forward
                    rem_tvl -=sub_flen # decrease rem_tlv
                    #print 'else tlv '
                    #print "at this stage RV is : {}".format(rv)
                    #print INDENT*2,'remaining tlv: {}'.format(rem_tvl)
                    #print INDENT*2,'**did not match 6 or 8 and packet at: {} and remaing tlv_len is:{}'.format(len(fval),rem_tvl)
              #print 'anything left in the packet ? '
              '''try:
                  entry_final = { "lsp_id" : hex2isisd(lsp_id[0]),
                                  "metric" : metric,
                                  "l_ip": l_ip,
                                  "r_ip": r_ip
                               }
              #except:
              entry_final = { "lsp_id" : hex2isisd(lsp_id[0]),
                                  "metric" : metric,
                                  "l_ip": rv['SV'],
                                  "r_ip": rv['SV'],
                                  }               	

              rv["V"].append(entry_final)
              ''' 
            #print 'print rv here: ------------------',rv
            ''' 
            entry_final = {"RV": rv['V'],
                           'SRV': rv['SV']}
            #print INDENT*5,'entry_final:\n\n',entry_final,'\n'
            rv["V"].append(entry_final)
            '''
            fval = fval[11+tlv_len[0]:] # move packet just in case there was no tlv otherwise the packet is already moved by sub_tlv routine

        elif ftype == VLEN_FIELDS["IPIntReach"]:
            ## 128
            rv["V"] = []
            cnt = 0
            while len(fval) > 0:
                cnt = cnt + 1
                default, delay, expense, error, addr, mask =\
                         struct.unpack("> 4B LL", fval[0:12])

                ipif = { 'DEFAULT': default,
                         'DELAY'  : delay,
                         'EXPENSE': expense,
                         'ERROR'  : error,
                         'ADDR'   : addr,
                         'MASK'   : mask
                         }
                #rv["V"].append(ipif)

                if verbose > 0:
                    print level*INDENT +\
                          "%d: default: %d, delay: %d, expense: %d, error: %d" %\
                          (cnt, default, delay, expense, error)
                    print (level+1)*INDENT +\
                          "addr/mask: %s/%s" % (id2str(addr), id2str(mask))

                fval = fval[12:]

        elif ftype == VLEN_FIELDS["ProtoSupported"]:
            ## 129
            prots = struct.unpack("> %dB" % flen, fval)
            prots_strs = map(lambda x: '%s' % x,
                             map(lambda x: NLPIDS[x], prots))

            #rv["V"] = prots_strs

            if verbose > 0:
                print level*INDENT + "protocols supported: " + `prots_strs`

        elif ftype == VLEN_FIELDS["IPExtReach"]:
            ## 130
            rv["V"] = []
            cnt = 0
            while len(fval) > 0:
                cnt = cnt + 1
                default, delay, expense, error, addr, mask =\
                         struct.unpack("> 4B LL", fval[0:12])

                ipif = { 'DEFAULT': default,
                         'DELAY'  : delay,
                         'EXPENSE': expense,
                         'ERROR'  : error,
                         'ADDR'   : addr,
                         'MASK'   : mask
                         }
                #rv["V"].append(ipif)

                if verbose > 0:
                    print level*INDENT +\
                          "%d: default: %d, delay: %d, expense: %d, error: %d" %\
                          (cnt, default, delay, expense, error)
                    print (level+1)*INDENT +\
                          "addr/mask: %s/%s" % (id2str(addr), id2str(mask))

                fval = fval[12:]

        elif ftype == VLEN_FIELDS["IPInterDomInfo"]:
            ## 131
            rv["V"] = None

            if verbose > 0:
                print level*INDENT + "[ IPInterDomInfo ]"

        elif ftype == VLEN_FIELDS["IPIfAddr"]:
            ## 132
            addrs = struct.unpack("> %dL" % (flen/4, ), fval)
            addrs_strs = map(lambda x: id2str(x), addrs)

            #rv["V"] = addrs_strs
            if verbose > 0:
                print level*INDENT + "interface IP addresses: " + `addrs_strs`
        elif ftype == VLEN_FIELDS["DynamicHostname"]:
            ## 137
            name = struct.unpack("> %ds" % flen, fval)
            rv["V"] = name

            if verbose > 0:
                print level*INDENT + "dynamic hostname: '%s'" % name

        else:
            if verbose > 0:
                print level*INDENT + "[ *** %s *** ]" % VLEN_FIELDS[ftype]

    else:
        if verbose > 0:
            print level*INDENT + \
                  "[ UNKNOWN ISIS variable length field: ", `ftype`, " ]"
    #print lnetd
    return rv

#------------------------------------------------cp-----------------------------
#------------------------------------------------
def parseVLenField(ftype, flen, fval, verbose=0, level=0):
    node = None
    verbose = 0
    rv = { "L" : flen,
           }

    if verbose > 1 and ftype not in (VLEN_FIELDS["Padding"],
                                     VLEN_FIELDS["Null"]):
        print prtbin(level*INDENT,`ftype`+`flen`+fval)

    if ftype in VLEN_FIELDS.keys():
        if verbose > 0 and ftype not in (VLEN_FIELDS["Padding"],
                                         VLEN_FIELDS["Null"]):
            print level*INDENT +\
                  "field: %s, length: %d" % (VLEN_FIELDS[ftype], flen)

        level = level + 1
        if   ftype == VLEN_FIELDS["Null"]:
            pass

        elif ftype == VLEN_FIELDS["AreaAddress"]:
            ## 1
            rv["V"] = []
            areas = ""
            while len(fval) > 0:

                (l,) = struct.unpack("> B", fval[0])

                rv["V"].append(fval[1:1+l])

                areas = areas + '0x' + str2hex(fval[1:1+l]) + ", "
                fval = fval[1+l:]

            if verbose > 0:
                print level*INDENT + "area addresses: " + areas
            pass

        elif ftype == VLEN_FIELDS["LSPIISNeighbor"]:
            verbose = 0
            ## 2
            rv["V"] = []
            vflag = struct.unpack("> B", fval[0])
            fval  = fval[1:]
            cnt   = 0
            while len(fval) > 0:
                cnt = cnt + 1
                default, delay, expense, error, nid =\
                         struct.unpack("> BBBB 7s", fval[0:11])

                is_neighbour = { 'DEFAULT': default,
                                 'DELAY'  : delay,
                                 'EXPENSE': expense,
                                 'ERROR'  : error,
                                 'NID'    : nid,
                                 }
                rv["V"].append(is_neighbour)

                if verbose > 0:
                    print level*INDENT +\
                          "IS Neighbour %d: id: %s" % (cnt, str2hex(nid))
                    print (level+1)*INDENT +\
                          "default: %d, delay: %d, expense: %d, error: %d" %\
                          (default, delay, expense, error)

                fval = fval[11:]
            pass  
        elif ftype == VLEN_FIELDS["ESNeighbor"]:
            ## 3
            default, delay, expense, error = struct.unpack("> 4B", fval[0:4])
            rv["V"] = { 'DEFAULT' : default,
                        'DELAY'   : delay,
                        'EXPENSE' : expense,
                        'ERROR'   : error,
                        'NIDS'    : []
                        }

            if verbose > 0:
                print level*INDENT +\
                      "default: %d, delay: %d, expense: %d, error: %d" %\
                      (default, delay, expense, error)

            fval = fval[4:]
            cnt  = 0
            while len(fval) > 0:
                cnt = cnt + 1
                (nid,) = struct.unpack("> 6s", fval[0:6])

                rv["V"]["NIDS"].append(nid)

                if verbose > 0:
                    print level*INDENT +\
                          "ES Neighbour %d: %s" % (cnt, str2hex(nid))

                fval = fval[6:]
            pass
        elif ftype == VLEN_FIELDS["IIHIISNeighbor"]:
            ## 6
            rv["V"] = []
            cnt = 0
            while len(fval) > 0:
                cnt = cnt + 1
                (nid,) = struct.unpack("> 6s", fval[0:6])

                rv["V"].append(nid)

                if verbose > 0:
                    print level*INDENT +\
                          "IS Neighbour %d: %s" % (cnt, str2hex(nid))

                fval = fval[6:]
            pass
        elif ftype == VLEN_FIELDS["Padding"]:
            ## 8
            rv["V"] = None

        elif ftype == VLEN_FIELDS["LSPEntries"]:
            ## 9
            rv["V"] = []
            cnt = 0
            while len(fval) > 0:
                cnt = cnt + 1
                lifetime, lsp_id, lsp_seq_no, cksm =\
                          struct.unpack("> H 8s L H", fval[:16])
                lsp_id = struct.unpack("> 6sBB", lsp_id)

                lsp_entry = { "ID"       : lsp_id[0],
                              "PN"       : lsp_id[1],
                              "NM"       : lsp_id[2],
                              "LIFETIME" : lifetime,
                              "SEQ_NO"   : lsp_seq_no,
                              "CKSM"     : cksm
                              }

                rv["V"].append(lsp_entry)
                if verbose > 0:
                    print level*INDENT +\
                          "%d: LSP ID: src: %s, pn: %s, LSP no: %d" %\
                          (cnt, str2hex(lsp_id[0]), int2hex(lsp_id[1]), lsp_id[2])
                    print (level+1)*INDENT +\
                          "lifetime: %d, seq.no: %d, cksm: %s" %\
                          (lifetime, lsp_seq_no, int2hex(cksm))
                fval = fval[16:]

        elif ftype == VLEN_FIELDS["ExtendedISReach"]:
            ## 22
            rv["V"] = []
            while len(fval) > 0:
              lsp_id = struct.unpack("> 6s", fval[0:6])
              metric = struct.unpack("> sss", fval[7:10])
              tlv_l = struct.unpack(">B",fval[10])
              fval = fval[11+tlv_l[0]:]

        elif ftype == VLEN_FIELDS["IPIntReach"]:
            ## 128
            rv["V"] = []
            cnt = 0
            while len(fval) > 0:
                cnt = cnt + 1
                default, delay, expense, error, addr, mask =\
                         struct.unpack("> 4B LL", fval[0:12])

                ipif = { 'DEFAULT': default,
                         'DELAY'  : delay,
                         'EXPENSE': expense,
                         'ERROR'  : error,
                         'ADDR'   : addr,
                         'MASK'   : mask
                         }
                rv["V"].append(ipif)

                if verbose > 0:
                    print level*INDENT +\
                          "%d: default: %d, delay: %d, expense: %d, error: %d" %\
                          (cnt, default, delay, expense, error)
                    print (level+1)*INDENT +\
                          "addr/mask: %s/%s" % (id2str(addr), id2str(mask))

                fval = fval[12:]

        elif ftype == VLEN_FIELDS["ProtoSupported"]:
            ## 129
            prots = struct.unpack("> %dB" % flen, fval)
            prots_strs = map(lambda x: '%s' % x,
                             map(lambda x: NLPIDS[x], prots))

            rv["V"] = prots_strs

            if verbose > 0:
                print level*INDENT + "protocols supported: " + `prots_strs`

        elif ftype == VLEN_FIELDS["IPExtReach"]:
            ## 130
            rv["V"] = []
            cnt = 0
            while len(fval) > 0:
                cnt = cnt + 1
                default, delay, expense, error, addr, mask =\
                         struct.unpack("> 4B LL", fval[0:12])

                ipif = { 'DEFAULT': default,
                         'DELAY'  : delay,
                         'EXPENSE': expense,
                         'ERROR'  : error,
                         'ADDR'   : addr,
                         'MASK'   : mask
                         }
                rv["V"].append(ipif)

                if verbose > 0:
                    print level*INDENT +\
                          "%d: default: %d, delay: %d, expense: %d, error: %d" %\
                          (cnt, default, delay, expense, error)
                    print (level+1)*INDENT +\
                          "addr/mask: %s/%s" % (id2str(addr), id2str(mask))

                fval = fval[12:]

        elif ftype == VLEN_FIELDS["IPInterDomInfo"]:
            ## 131
            rv["V"] = None

            if verbose > 0:
                print level*INDENT + "[ IPInterDomInfo ]"

        elif ftype == VLEN_FIELDS["IPIfAddr"]:
            ## 132
            addrs = struct.unpack("> %dL" % (flen/4, ), fval)
            addrs_strs = map(lambda x: id2str(x), addrs)

            rv["V"] = addrs_strs
            if verbose > 0:
                print level*INDENT + "interface IP addresses: " + `addrs_strs`
        elif ftype == VLEN_FIELDS["DynamicHostname"]:
            ## 137
            name = struct.unpack("> %ds" % flen, fval)
            rv["V"] = name

            if verbose > 0:
                print level*INDENT + "dynamic hostname: '%s'" % name

        else:
            if verbose > 0:
                print level*INDENT + "[ *** %s *** ]" % VLEN_FIELDS[ftype]

    else:
        if verbose > 0:
            print level*INDENT + \
                  "[ UNKNOWN ISIS variable length field: ", `ftype`, " ]"

    return rv

################################################################################

class LLCExc(Exception): pass
class VLenFieldExc(Exception): pass

#-------------------------------------------------------------------------------

class Isis:

    _eth_p_802_2 = socket.htons(0x0004)
    _dev_str     = "eth0"

    _version          = 1
    _version_proto_id = 1

    _hold_multiplier  = 3
    _holdtimer        = 10

    #---------------------------------------------------------------------------

    class Adj:

        def __init__(self, atype, rx_ish, tx_ish):

            self._state  = STATES["INITIALISING"]
            self._type   = atype
            self._tx_ish = tx_ish
            self._rx_ish = rx_ish

            self._rtx_at = 0

            (src_mac, _, _, _, _,_) = parseMacHdr(rx_ish)
            self._nbr_mac_addr = src_mac

            hdr_start = MAC_HDR_LEN + ISIS_HDR_LEN
            hdr_end   = hdr_start + ISIS_HELLO_HDR_LEN
            (_, src_id, ht, _, prio, lan_id) =\
                   struct.unpack(">B 6s H H B 7s", rx_ish[hdr_start:hdr_end])

            self._holdtimer  = ht
            self._nbr_src_id = src_id
            self._nbr_lan_id = lan_id

            self._nbr_areas = []
            fields = rx_ish[MAC_HDR_LEN+ISIS_HDR_LEN+ISIS_HELLO_HDR_LEN:]
            while len(fields) > 0:

                (ftype, flen) = struct.unpack(">BB", fields[0:2])
                fval          = fields[2:2+flen]
                if ftype == VLEN_FIELDS["AreaAddress"]:
                    while len(fval) > 0:
                        (l,) = struct.unpack("B", fval[0])
                        self._nbr_areas.append(fval[1:1+l])
                        fval = fval[1+l:]

                fields = fields[2+flen:]

        def __repr__(self):

            ret = """st: %s, ht: %d, retx: %d, neighbour areas: %s,
            nbr src id: %s, lan id: %s""" %\
            (STATES[self._state], self._holdtimer, self._rtx_at,
             `map(str2hex, self._nbr_areas)`,
             str2hex(self._nbr_src_id), str2hex(self._nbr_lan_id))

            return ret

    #---------------------------------------------------------------------------

    def __init__(self, dev, area_addr, src_id=None, lan_id=None, src_ip=None):

        self._sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                                   Isis._eth_p_802_2)
        self._sockaddr = (dev, 0x0000)
        self._sock.bind(self._sockaddr)
        self._sockname = self._sock.getsockname()

        # XXX HACK: want to query _sock for IP addr; can't figure out
        # how at the moment
        if src_ip:
            self._src_ip = src_ip
        else:
            self._src_ip = str2id(socket.gethostbyname(socket.gethostname()))

        self._src_mac   = self._sockname[-1]
        self._area_addr = area_addr

        if src_id:
            self._src_id = src_id
        else:
            self._src_id = self._src_mac

        if lan_id:
            self._lan_id = lan_id
        else:
            self._lan_id = self._src_id + '\001'

        self._adjs  = { }
        self._rcvd  = ""
        self._mrtd  = None

    def __repr__(self):

        ret = """Passive ISIS speaker, version %s:
        Src IP: %s, Src MAC: %s
        Area address: %s
        Src ID: %s
        LAN ID: %s
        Adjs: %s\n""" %\
            (VERSION,
             id2str(self._src_ip), str2hex(self._src_mac),
             str2hex(self._area_addr), str2hex(self._src_id),
             str2hex(self._lan_id), `self._adjs`)

        return ret

    def close(self):

        self._sock.close()
        self._mrtd.close()

    #---------------------------------------------------------------------------

    def recvMsg(self, verbose=0, level=0):

        self._rcvd = self._sock.recv(RCV_BUF_SZ)
        (src_mac, dst_mac, length, dsap, ssap, ctrl) = parseMacHdr(self._rcvd)

        if verbose > 2:
            print "%srecvMsg: recv: len=%d%s" %\
                  (level*INDENT,
                   len(self._rcvd), prthex((level+1)*INDENT, self._rcvd))

        if verbose > 1:
            print "%srecvMsg: src: %s\n         dst: %s" %\
                  (level*INDENT, str2hex(src_mac), str2hex(dst_mac))
            print "         len: %d" % (length, )
            print "         dsap: %#0.2x, ssap: %#0.2x, ctl: %#0.2x" %\
                  (dsap, ssap, ctrl)

        return (len(self._rcvd), self._rcvd)

    def sendMsg(self, pkt, verbose=0, level=0):

        (src_mac, dst_mac, length, dsap, ssap, ctrl) = parseMacHdr(pkt)
        (nlpid, hdr_len, ver_proto_id, resvd,
         msg_type, ver, eco, user_eco) = parseIsisHdr(pkt)

        if DUMP_MRTD == 1:
            self._mrtd.writeIsisMsg(msg_type, len(pkt), pkt)

        elif DUMP_MRTD == 2:
            self._mrtd.writeIsis2Msg(msg_type, len(pkt), pkt)

        if verbose > 2:
            print "%ssendMsg: send: len=%d%s" %\
                  (level*INDENT, len(pkt), prthex((level+1)*INDENT, pkt))

        if verbose > 1:
            print "%ssendMsg: src: %s\n         dst: %s" %\
                  (level*INDENT, str2hex(src_mac), str2hex(dst_mac))
            print "         len: %d" % (length, )
            print "         dsap: %#0.2x, ssap: %#0.2x, ctl: %#0.2x" %\
                  (dsap, ssap, ctrl)
        #print '--------- what are we sending now ----------\n'
        verbose = 0
        if verbose > 0:
            parseIsisMsg(len(pkt), pkt, verbose, level)
        verbose = 0
        if len(pkt) <= MAC_PKT_LEN:
            self._sock.send(pkt)

    def parseMsg(self, verbose=0, level=0):

        try:
            (msg_len, msg) = self.recvMsg(verbose, level)

        except (LLCExc):
            if verbose > 1:
                print "[ *** Non ISIS frame received *** ]"
            return

        (nlpid, hdr_len, ver_proto_id, resvd,
         msg_type, ver, eco, user_eco) = parseIsisHdr(msg)

        if DUMP_MRTD == 1:
            self._mrtd.writeIsisMsg(msg_type, msg_len, msg)

        elif DUMP_MRTD == 2:
            self._mrtd.writeIsis2Msg(msg_type, msg_len, msg)

        if verbose > 2:
            print "%sparseMsg: len=%d%s" %\
                  (level*INDENT, msg_len, prthex((level+1)*INDENT, msg))

        rv = parseIsisMsg(msg_len, msg, verbose, level)
        self.processFsm(msg, verbose, level)

        return rv

    #---------------------------------------------------------------------------

    def mkMacHdr(self, dst_mac, src_mac):

        hdr = struct.pack(">6s 6s H 3B ", dst_mac, src_mac, ISIS_PKT_LEN,
                          ISIS_LLC_HDR[0], ISIS_LLC_HDR[1], ISIS_LLC_HDR[2])
        return hdr

    def mkIsisHdr(self, msg_type, hdr_len):

        nlpid = NLPIDS["ISIS"]
        ret   = struct.pack("8B", nlpid, hdr_len, Isis._version_proto_id,
                            0, msg_type, Isis._version, 0, 0)
        return ret

    def mkIshHdr(self, circuit, src_id, holdtimer, pdu_len, prio, lan_id):

        ret = struct.pack(">B 6s H H B 7s",
                          circuit, src_id, holdtimer, pdu_len, prio, lan_id)
        return ret

    def mkVLenField(self, ftype_str, flen, fval=None):

        ftype = VLEN_FIELDS[ftype_str]
        ret = struct.pack("2B", ftype, flen)
        if   ftype == VLEN_FIELDS["AreaAddress"]:
            for i in range(len(fval)):
                ret = ret +\
                      struct.pack("B %ds" % fval[i][0], fval[i][0], fval[i][1])

        elif ftype == VLEN_FIELDS["Padding"]:
            return padPkt(flen+2, "")

        elif ftype == VLEN_FIELDS["ProtoSupported"]:
            for i in range(flen):
                ret = ret + struct.pack("B", fval[i])

        elif ftype == VLEN_FIELDS["IPIfAddr"]:
            for i in range(flen/4):
                ret = ret + struct.pack(">L", fval[i])

        elif ftype == VLEN_FIELDS["IIHIISNeighbor"]:
            for i in range(flen/6):
                ret = ret + struct.pack("6s", fval[i])

        else:
            raise VLenFieldExc

        return ret

    def mkIsh(self, ln, lan_id, holdtimer):

        isns = []
        if ln == 1:
            dst_mac = AllL1ISs
            for adj in self._adjs.keys():
                if self._adjs[adj].has_key(1):
                    isns.append(str2mac(adj))

            msg_type = MSG_TYPES["L1LANHello"]

        elif ln == 2:
            dst_mac = AllL2ISs
            for adj in self._adjs.keys():
                if self._adjs[adj].has_key(2):
                    isns.append(str2mac(adj))

            msg_type = MSG_TYPES["L2LANHello"]

        ish = self.mkMacHdr(dst_mac, self._src_mac)
        ish = ish + self.mkIsisHdr(msg_type, ISIS_HDR_LEN + ISIS_HELLO_HDR_LEN)

        prio = 0 # we don't ever want to be elected Designated System
        ish  = ish + self.mkIshHdr(CIRCUIT_TYPES["L1L2Circuit"], self._src_id,
                             holdtimer, ISIS_PDU_LEN, prio, lan_id)

        ish = ish + self.mkVLenField("ProtoSupported", 1, (NLPIDS["IP"],))
        ish = ish + self.mkVLenField("AreaAddress", 1+len(self._area_addr),
                                ((len(self._area_addr), self._area_addr),))
        ish = ish + self.mkVLenField("IPIfAddr", 4, (self._src_ip,))

        if len(isns) > 0:
            ish = ish + self.mkVLenField("IIHIISNeighbor", len(isns)*6, isns)
        ish  = padPkt(MAC_PKT_LEN, ish)

        return ish

    ############################################################################

    def processFsm(self, msg, verbose=0, level=0):

        (src_mac, _, _, _, _, _) = parseMacHdr(msg)
        (_, _, _, _, msg_type, _, _, _) = parseIsisHdr(msg[MAC_HDR_LEN:])

        hdr_start = MAC_HDR_LEN + ISIS_HDR_LEN
        hdr_end   = hdr_start + ISIS_HELLO_HDR_LEN
        (_, src_id, _, _, _, lan_id) =\
               struct.unpack("> B 6s H H B 7s", msg[hdr_start:hdr_end])

        smac = str2hex(src_mac)
        if not self._adjs.has_key(smac):
            self._adjs[smac] = { }

        if msg_type in (MSG_TYPES["L1LANHello"], MSG_TYPES["L2LANHello"]):

            k = msg_type - 14 # L1 or L2?
            if not self._adjs[smac].has_key(k):
                # new adjacency
                #print 'is this a new adj ? '
                adj = Isis.Adj(k, msg, self.mkIsh(k, self._lan_id, Isis._holdtimer))
                self._adjs[smac][k] = adj

            else:
                # existing adjacency
                #print 'is this existing adj ?'
                adj = self._adjs[smac][k]
                adj._state = STATES["UP"]
                adj._rx_ish = msg
                adj._tx_ish = self.mkIsh(k, lan_id,
                                         Isis._holdtimer*Isis._hold_multiplier)

            if adj._rtx_at <= RETX_THRESH:
                self.sendMsg(adj._tx_ish, verbose, level)

        else:
            pass

    #---------------------------------------------------------------------------

################################################################################

#if __name__ == "__main__":
def run_it():
    import mrtd

    #---------------------------------------------------------------------------

    global VERBOSE, DUMP_MRTD

    VERBOSE   = 0
    DUMP_MRTD = 0

    file_pfx  = mrtd.DEFAULT_FILE
    file_sz   = mrtd.DEFAULT_SIZE
    mrtd_type = None
    area_addr = '49.00.01'
    src_id    = '00.05.03.30.01.10'
    lan_id    = '00.05.03.30.01.10.00'
    src_ip    = '10.100.100.1'
    #---------------------------------------------------------------------------


    Isis._dev_str = 'ens4.100'
    src_id = map(lambda x: int(x, 16), string.split(src_id, '.'))
    src_id = struct.pack("6B",
                                 src_id[0], src_id[1], src_id[2],
                                 src_id[3], src_id[4], src_id[5])

    lan_id = map(lambda x: int(x, 16), string.split(lan_id, '.'))
    lan_id = struct.pack("7B",
                                 lan_id[0], lan_id[1], lan_id[2],
                                 lan_id[3], lan_id[4], lan_id[5], lan_id[6])


    area_addr = map(lambda x: int(x, 16), string.split('49.00.01', '.'))

            # this is grim, but that's not important right now...
    area_addr_str = ""
    for i in range(len(area_addr)):
        area_addr_str = struct.pack("%ds B" % len(area_addr_str),
                                            area_addr_str, area_addr[i])
    area_addr = area_addr_str
    
    src_ip = str2id(src_ip)

    
    isis = Isis(Isis._dev_str, area_addr, src_id, lan_id, src_ip)
    isis._mrtd = mrtd.Mrtd(file_pfx, "w+b", file_sz, mrtd_type, isis)
    nodes = {}
    if VERBOSE > 1:
        print `isis`

    try:

        timeout = Isis._holdtimer
        while 1: # main loop
            #for node in nodes:
            #  out.append({'name': node.name,'neighbours': node.to_json() } )

            before  = time.time()
            rfds, _, _ = select.select([isis._sock], [], [], timeout)
            after   = time.time()
            elapsed = after - before

            if rfds != []:
                # need to rx pkt(s)
                rv = isis.parseMsg(VERBOSE, 0)
            else:
                # need to tx pkt(s) of some sort
                timeout = Isis._holdtimer
                for mac in isis._adjs.keys():
                    for a in isis._adjs[mac].keys():
                        adj = isis._adjs[mac][a]
                        adj._rtx_at = adj._rtx_at - elapsed
                        if adj._rtx_at <= RETX_THRESH:
                            isis.sendMsg(adj._tx_ish, VERBOSE, 0)
                            adj._rtx_at = adj._holdtimer
                        timeout = min(timeout, adj._rtx_at-RETX_THRESH)

    except (KeyboardInterrupt):
        isis.close()
        sys.exit(1)

################################################################################
################################################################################
