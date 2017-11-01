
'''
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
'''

from LibSC_Util     import *
from LibSC_Cmd      import *
from LibSC_Hlp      import *

g_mf_blk_count  = 20                    #mifare mini block count
g_mifare_key    = "ffff ffff ffff"      #default key
g_bin_mifare_key    = HexToBin(g_mifare_key)

def test_mifare_set_block_count(n):
    global g_mf_blk_count
    g_mf_blk_count = n

def test_mifare_set_default_key(k):
    global g_mifare_key
    g_mifare_key = k

def mifare_inc_value(nBlk,deta):
    MF_Inc(nBlk,deta)
    MF_Transfer(nBlk)

def mifare_dec_value(nBlk,deta):
    MF_Dec(nBlk,deta)
    MF_Transfer(nBlk)

def mifare_read_blocks(nStart,nStop=0):
    bSkip = False
    if nStop==0:
        nStop=nStart+1
    print "Read blocks from %d to %d"%(nStart,nStop)
    for i in range(nStart,nStop):
        # 128 blocks = 32 sectors * 4
        if ( (i<128) and (i % 4==0) ) or ( (i>=128) and (i % 16==0) ) :
            if MF_AuthA(i,g_bin_mifare_key):
                print "[ %3d ] AuthA ok"%i
                bSkip = False
            else:
                print "[ %3d ] AuthA failed"%i
                Connect()
                bSkip = True
                continue
        if not bSkip:
            blkBuf = MF_Read(i)
            if blkBuf:
                print "\t",
                DumpHex(blkBuf)
                print ""

def test_mifare_read(nBlk):
    DumpHex(MF_Read(nBlk),"\n")

def test_mifare_auth(nBlk):
    if MF_AuthA(nBlk,g_bin_mifare_key):
        print "AuthA %d ok"%nBlk
    else:
        return

def test_mifare_set_value(nBlk,value):
    PrintTitle("value before set value")
    test_mifare_read(nBlk)

    PrintTitle("set value")
    MF_SetValue(nBlk,value)
    test_mifare_read(nBlk)

def test_mifare_inc_value(nBlk,deta):
    PrintTitle("value before inc value")
    test_mifare_read(nBlk)

    PrintTitle("inc value +%d"%deta)
    mifare_inc_value(nBlk,deta)
    test_mifare_read(nBlk)

def test_mifare_dec_value(nBlk,deta):
    PrintTitle("value before dec value")
    test_mifare_read(nBlk)

    PrintTitle("dec value -%d"%deta)
    mifare_dec_value(nBlk,deta)
    test_mifare_read(nBlk)

def test_mifare_read_all():
    mifare_read_blocks(0,g_mf_blk_count)

    #uidBuf="6e 89 ab 48"
    #test_mifare_set_uid(uidBuf)
def test_mifare_set_uid(uidBuf):
    MF_SetUid(uidBuf)