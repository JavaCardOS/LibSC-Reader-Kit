
'''
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
'''

import logging
import types

PICC_TYPE_UNKNOWN		    = 0
PICC_TYPE_ISO_14443_4	    = 1
PICC_TYPE_ISO_18092		    = 2
PICC_TYPE_MIFARE_MINI	    = 3
PICC_TYPE_MIFARE_1K		    = 4
PICC_TYPE_MIFARE_4K		    = 5
PICC_TYPE_MIFARE_UL		    = 6
PICC_TYPE_MIFARE_PLUS	    = 7
PICC_TYPE_TNP3XXX		    = 8
PICC_TYPE_NOT_COMPLETE	    = 0xff

g_mapSak2CardType = {0x04:PICC_TYPE_NOT_COMPLETE,
    0x09:PICC_TYPE_MIFARE_MINI,
    0x08:PICC_TYPE_MIFARE_1K,
    0x18:PICC_TYPE_MIFARE_4K,
    0x00:PICC_TYPE_MIFARE_UL,
    0x10:PICC_TYPE_MIFARE_PLUS,
    0x11:PICC_TYPE_MIFARE_PLUS,
    0x01:PICC_TYPE_TNP3XXX,
    0x20:PICC_TYPE_ISO_14443_4,
    0x40:PICC_TYPE_ISO_18092,}

g_mapCardType2Str = {
    PICC_TYPE_UNKNOWN               :"PICC_TYPE_UNKNOWN",
    PICC_TYPE_ISO_14443_4           :"PICC_TYPE_ISO_14443_4",
    PICC_TYPE_ISO_18092             :"PICC_TYPE_ISO_18092",
    PICC_TYPE_MIFARE_MINI           :"PICC_TYPE_MIFARE_MINI",
    PICC_TYPE_MIFARE_1K             :"PICC_TYPE_MIFARE_1K",
    PICC_TYPE_MIFARE_4K             :"PICC_TYPE_MIFARE_4K",
    PICC_TYPE_MIFARE_UL             :"PICC_TYPE_MIFARE_UL",
    PICC_TYPE_MIFARE_PLUS           :"PICC_TYPE_MIFARE_PLUS",
    PICC_TYPE_TNP3XXX               :"PICC_TYPE_TNP3XXX",
    PICC_TYPE_NOT_COMPLETE          :"PICC_TYPE_NOT_COMPLETE",
}

g_typeMifareCard = (PICC_TYPE_MIFARE_MINI,PICC_TYPE_MIFARE_1K,PICC_TYPE_MIFARE_4K,
    PICC_TYPE_MIFARE_UL,PICC_TYPE_MIFARE_PLUS)

def LoadByte(val):
    if type(val) is types.StringType:
        return ord(val)
    else:
        return val

def LoadWord(buf,offset):
    lowByte = LoadByte(buf[offset+1])
    hiByte = LoadByte(buf[offset])
    return hiByte*256+lowByte

def DumpHex(s,endCh=''):
    if s:
        for i in range(len(s)):
            print "%02X"%LoadByte(s[i]),
        if len(endCh):
            print(endCh)

def HexToBin(sHex):
    sHex = sHex.replace(' ',"")
    sBin = sHex.decode('hex')
    return sBin

def BinToHex(s,sep=' '):
    sOut=""
    for i in range(len(s)):
        sOut+="%02X%s"%(LoadByte(s[i]),sep)
    return sOut

def UcBitN(valIn):
    val=~valIn
    if(val>=0 and val<256):
        return val
    else:
        return (val%256)

def PrintTitle(title):
    print '-'*20,title,'-'*20

def LogTitle(title):
    logging.debug('-'*20+' '+title+' '+'-'*20)

def GetCardType(sak):
    sak &= 0x7F
    if sak in g_mapSak2CardType.keys():
        return g_mapSak2CardType[sak];
    else:
        return PICC_TYPE_UNKNOWN

def GetCardTypeString(piccType):
    if piccType in g_mapCardType2Str.keys():
        return g_mapCardType2Str[piccType];
    else:
        return "PICC_TYPE_UNKNOWN"

def IsMifareCard(sak):
    cardType = GetCardType(sak)
    if cardType in g_typeMifareCard:
        return True
    return False

def GetMifareBlocks(piccType):
    if piccType == PICC_TYPE_MIFARE_MINI:
        return 5*4              #5  sectors
    elif piccType == PICC_TYPE_MIFARE_1K:
        return  16*4            #16 sectors
    elif piccType == PICC_TYPE_MIFARE_4K:
        return 32*4+8*4*4       #32+8=40 sectors
    return 0