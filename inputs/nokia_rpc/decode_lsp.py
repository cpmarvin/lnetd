#! /usr/bin/env python3

import sys
import getopt
import socket
import string
import os.path
import struct
import time
import select
import math

from pprint import pprint

VERSION = "0.1"
INDENT = "    "
RETX_THRESH = 1
RCV_BUF_SZ = 2048

MAC_PKT_LEN = 1514
MAC_HDR_LEN = 17
ISIS_PKT_LEN = 1500
ISIS_PDU_LEN = ISIS_PKT_LEN - 3
ISIS_LLC_HDR = (0xfe, 0xfe, 0x03, 0x83)

ISIS_HDR_LEN = 8
ISIS_HELLO_HDR_LEN = 19
ISIS_LSP_HDR_LEN = 19
ISIS_CSN_HDR_LEN = 25
ISIS_PSN_HDR_LEN = 9

VLEN_FIELDS = {"0L": "Null",                # null
               "1L": "AreaAddress",         # area address
               "2L": "LSPIISNeighbor",      # ISIS (CLNP) neighbour (in LSP)
               "3L": "ESNeighbor",          # end system (CLNP) neighbour
               "4L": "PartDIS",             #
               "5L": "PrefixNeighbor",      #
               "6L": "IIHIISNeighbor",      # ISIS (CLNP) neighbour (in ISH)
               "8L": "Padding",             # zero padding
               "9L": "LSPEntries",          # LSPs ack'd in this CSNP/PSNP
               "10L": "Authentication",      #
               "12L": "OptionalChecksum",    #
               "14L": "LSPBufferSize",       #
               22: "ExtendedISReach",      # RFC5305
               "128L": "IPIntReach",          # 'internal' reachable IP subnets
               "129L": "ProtoSupported",      # NLPIDs this IS can relay
               "130L": "IPExtReach",          # 'external' reachable IP subnets
               "131L": "IPInterDomInfo",      # interdomain routeing info
               "132L": "IPIfAddr",            # IP address(es) of the interface
               134: "TERouterID",          # TE router ID
               "135L": "TEIPReach",           # 'wide metric TLV'
               137: "DynamicHostname",     # dynamic hostname support
               "232L": "IPv6IfAddr",          #
               "236L": "IPv6IPReach",         #
               }
MSG_TYPES = {0: "NULL",
             18: "L1LSP",
             20: "L2LSP",
             }

DLIST = [MSG_TYPES] + [VLEN_FIELDS]

# add reverse keys to both dict
for d in DLIST:
    for k in list(d.keys()):
        d[d[k]] = k


def parseIsisHdr(pkt):

    (nlpid, hdr_len, ver_proto_id, resvd, msg_type, ver, eco, user_eco) =\
        struct.unpack(">8B", pkt[0:ISIS_HDR_LEN])

    return (nlpid, hdr_len, ver_proto_id, resvd,
            msg_type, ver, eco, user_eco)


def parseLspHdr(pkt):
    # print('here-parseLspHdr', pkt)
    (pdu_len, lifetime, lsp_id, seq_no, cksm, bits) =\
        struct.unpack("> HH 8s LHB", pkt[:ISIS_LSP_HDR_LEN])
    # print('here', lsp_id)
    lsp_id = struct.unpack("> 6sBB", lsp_id)

    return (pdu_len, lifetime, lsp_id, seq_no, cksm, bits)


def parseIsisLsp(msg_len, msg, verbose=1, level=0):
    '''main function to parse the ISIS pdu starting with LSP HDR followed by
    any TLVs that we are interested in'''

    # parse header to get pdu_len ( i don't need it so maybe remove in the future )and lsp_id ( but this i can get it from yang )
    (pdu_len, lifetime, lsp_id, seq_no, cksm, bits) = parseLspHdr(msg)
    '''
    if verbose:
        print (level + 1) * INDENT +\
            "PDU len: %d, lifetime: %d, seq.no: %d, cksm: %s" %\
              (pdu_len, lifetime, seq_no, int2hex(cksm))
        print (level + 1) * INDENT +\
            "LSP ID: src: %s, pn: %s, LSP no: %d" %\
              (str2hex(lsp_id[0]), int2hex(lsp_id[1]), lsp_id[2])

        p = bits & (1 << 7)
        att = (bits & (1 << 6)) * "error " + (bits & (1 << 5)) * "expense " +\
              (bits & (1 << 4)) * "delay " + (bits & (1 << 3)) * "default"
        hty = (bits & (1 << 2)) >> 2
        ist = bits & ((1 << 1) | (1 << 0))
        print (level + 1) * INDENT +\
            "partition repair: %s, hippity: %s, type: %s" %\
              (("no", "yes")[p], ("no", "yes")[hty],
               ("UNUSED", "L1", "UNUSED", "L1+L2")[ist])
        print (level + 1) * INDENT + "attached: %s" % att
    '''
    # parse all TLV in PDU
    vfields = parseVLenFieldsLnetD(
        msg[ISIS_LSP_HDR_LEN:], lsp_id, seq_no, verbose, level)

    return (pdu_len, lifetime, lsp_id, seq_no, cksm, bits, vfields)


def parseVLenFieldsLnetD(fields, lsp_id, seq_no, verbose=0, level=0):
    '''function to parse TLV and their associated sub-TLVs
    with the help of parseVLenFieldLnetD and retrun a dict <insert dict example>'''

    vfields = {}

    while len(fields) > 1:
        # get the type and len for each TLV
        (ftype, flen) = struct.unpack(">BB", fields[0:2])

        # print(f'ftype:{ftype}-flen:{flen}')

        if ftype not in vfields:
            vfields[ftype] = []

        # for each TLV type parse the content and append the data
        vfields[ftype].append(
            parseVLenFieldLnetD(
                ftype, flen, fields[2:2 + flen], verbose, level + 1)
        )

        fields = fields[2 + flen:]
    # return vfields to parseIsisLsp as we are done parsing everything
    return vfields


def parseVLenFieldLnetD(ftype, flen, fval, verbose=0, level=0):
    '''TLV data parser'''
    rv = {"L": flen,
          }
    if ftype in VLEN_FIELDS.keys():
        #print('***********', ftype)
        # ignore
        if ftype == VLEN_FIELDS["Null"]:
            pass
        elif ftype == VLEN_FIELDS["ExtendedISReach"]:
            # TLV 22
            # print(f'TLV:22 with packet at: {fval}')
            #print(''.join(format(x, '02x') for x in fval))
            rv["V"] = []
            rv["SV"] = []
            cnt = -1
            TLV_END = False
            while not TLV_END:
                lsp_id = struct.unpack(">7s", fval[0:7])
                # print(f'lsp_id{lsp_id}')
                #print(''.join(format(x, '02x') for x in fval[0:7]))
                # move packet
                fval = fval[7:]
                metric = struct.unpack(">sss", fval[0:3])
                # print(f'metric{metric}')
                #print(''.join(format(x, '02x') for x in fval[0:3]))
                # move packet
                fval = fval[3:]
                sub_tlv_total_len = struct.unpack(">B", fval[0:1])
                # print(f'sub_tlv:{sub_tlv_total_len}')
                #print(''.join(format(x, '02x') for x in fval[0:1]))
                fval = fval[1:]
                rv['V'].append({'lsp_id': lsp_id[0],
                                'metric': metric,
                                'l_ip': None,
                                'r_ip': None})
                # print(f'TLV:22 with packet at: {fval}')
                SUB_TLV_END = False
                while not SUB_TLV_END:
                    '''need to test with multiple links
                    '''
                    (sub_ftype, sub_flen) = struct.unpack(">BB", fval[0:2])
                    fval = fval[2:]
                    # print(f'sub_ftype:{sub_ftype}-{sub_flen}')
                    if sub_ftype == 6:
                        l_ip = struct.unpack(">L", fval[0:sub_flen])
                        # print(f'l_ip:{l_ip}')
                        # print(''.join(format(x, '02x')
                        # for x in fval[0:sub_flen]))
                        rv["V"][0]["l_ip"] = l_ip[0]
                        fval = fval[sub_flen:]
                    elif sub_ftype == 8:
                        r_ip = struct.unpack(">L", fval[0:sub_flen])
                        # print(f'r_ip:{r_ip}')
                        # print(''.join(format(x, '02x')
                        # for x in fval[0:sub_flen]))
                        rv["V"][0]['r_ip'] = r_ip[0]
                        fval = fval[sub_flen:]
                    else:
                        # stop parsing SUB_TLVs
                        SUB_TLV_END = True
                TLV_END = True

        elif ftype == VLEN_FIELDS["TERouterID"]:
            # TLV 134
            router_id = struct.unpack(">L", fval)
            rv["V"] = router_id
        elif ftype == VLEN_FIELDS["DynamicHostname"]:
            # print(f'TLV:137 with packet at: {fval}')
            #print(''.join(format(x, '02x') for x in fval))
            name = struct.unpack("> %ds" % flen, fval)
            rv["V"] = name

    return rv


def parseIsisMsg(msg_len, msg, verbose=0, level=0):
    '''Main function to parse ISIS msg
    will parse in order the header to get the LSP type
    in this case i know it's L1/L2 as this is what nokia sros
    returns in yang model'''

    # parse header mostly to get the message_type ( that i already know),maybe remove in future
    (nlpid, hdr_len, ver_proto_id, resvd, msg_type, ver,
     eco, user_eco) = parseIsisHdr(msg[0:ISIS_HDR_LEN])

    rv = {"T": msg_type,
          "L": msg_len,
          "H": {},
          "V": {}
          }
    rv["H"]["NLPID"] = nlpid
    rv["H"]["HDR_LEN"] = hdr_len
    rv["H"]["VER_PROTO_ID"] = ver_proto_id
    rv["H"]["VER"] = ver
    rv["H"]["ECO"] = eco
    rv["H"]["USER_ECO"] = user_eco
    # header is parsed so move packet after ISIS_HDR
    msg = msg[ISIS_HDR_LEN:]
    # i only care about L1LSP/L2LSP so pass the packet to parseIsisLsp
    # if MSG_TYPES[str(msg_type)] in ("L1LSP", "L2LSP"):
    if msg_type in (MSG_TYPES["L1LSP"], MSG_TYPES["L2LSP"]):
        # parse the lsp content
        (rv["V"]["PDU_LEN"],
         rv["V"]["LIFETIME"],
         rv["V"]["LSP_ID"],
         rv["V"]["SEQ_NO"],
         rv["V"]["CKSM"],
         rv["V"]["BITS"],
         rv["V"]["VFIELDS"]) = parseIsisLsp(msg_len, msg, verbose, level)

    hostname = rv["V"]["VFIELDS"][137][0]["V"][0]
    return rv


def id2str(id):
    '''return ip address'''
    return "%d.%d.%d.%d" %\
           (int(((id & 0xff000000) >> 24) & 0xff),
            int(((id & 0x00ff0000) >> 16) & 0xff),
            int(((id & 0x0000ff00) >> 8) & 0xff),
            int((id & 0x000000ff) & 0xff))


def hex2isisd(str):
    '''return lsp_id from byte array'''
    str = str.hex()
    str = "%s.%s.%s" % (str[0:4], str[4:8], str[8:12])
    #"%s.%s.%s.%s" % (str[0:3], str[3:6], str[6:9], str[9:12])
    return str


def str2dec(str):
    '''return dec from byte string'''
    if str == None or str == "":
        return ""
    ret = map(lambda x: '%0.2x' % x, map(ord, str))
    ret = ''.join(ret)
    ret = int(ret, 16)
    return ret
