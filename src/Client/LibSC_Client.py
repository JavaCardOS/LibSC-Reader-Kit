
'''
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
'''

import sys

from datetime import datetime

from LibSC import *
from LibSC.test_mifare import *
from LibSC import test_cmd

g_picc_type     = 0xffff

def test_mifare_card():
    PrintTitle("testing mifare card")
    test_mifare_set_default_key("ffff ffff ffff")
    nBlk = 3

    test_mifare_auth(nBlk)
    #test_mifare_set_value(nBlk,9)
    #test_mifare_dec_value(nBlk,5)
    #test_mifare_inc_value(nBlk,3)
    t1 = datetime.now()
    test_mifare_read_all()
    t2 = datetime.now()
    print "TotalTime:",t2 - t1

def test_cpu_card(serObj):
    PrintTitle("testing cpu card")
    test_cmd.test_cpu_card(serObj)

def test_libsc_api(serObj):
    global g_picc_type
    PrintTitle("test libsc api")

    atqa,sak,uid = Connect()
    DumpSession(atqa,sak,uid)

    g_picc_type = GetCardType(sak)
    print "PICC type:",GetCardTypeString(g_picc_type)

    if IsMifareCard(sak):
        blk_count = GetMifareBlocks(g_picc_type)
        test_mifare_set_block_count(blk_count)
        print "Mifare Block Count:",blk_count
        test_mifare_card()
    else:
        test_cpu_card(serObj)

def test_clone_card():
    #strUid = "70 D8 C9 80"
    strUid = "11 22 33 44"

    if MF_IsClone():
        print "Write UID(%s) to this CLONE card"%strUid
        MF_SetUid(strUid)
    else:
        print "Not a CLONE card"

def main():
    portName = sys.argv[1]

    serObj = InitComm(portName)

    #test_clone_card()
    test_libsc_api(serObj)

    FinalComm(serObj)

if __name__ == '__main__':
    main()