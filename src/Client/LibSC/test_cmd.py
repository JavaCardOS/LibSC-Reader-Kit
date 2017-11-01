
'''
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
'''

import sys

import LibSC_Serial

from LibSC_Util     import *
from LibSC_Cmd      import *

def test_long_var_apdu(serObj):
    apduHeader="80a00102"
    apduInitData = "0102030405060708090A0B0C0D0E0F101112131415161718191a1b1c1d1e1f20"

    apduNewData = ""
    #for i in range(0x21,0x20+0x20):
    for i in range(0x21,0x21+5):
        apduNewData+="%02X"%i
        apduDataCur = apduHeader+"%02X"%i+apduInitData+apduNewData
        test_cmd(serObj,"long var apdu of %02X"%i,CMD_TPDU,apduDataCur)

def test_cmd(serObj,msg,cmd_code,cmd_param=""):
    PrintTitle(msg)
    rspData = LibSC_Serial.TransIoCmd(serObj,cmd_code,HexToBin(cmd_param))
    print " \tRetData::",
    DumpHex(rspData)
    print
    rspLen = LoadWord(rspData,0)
    if (rspData[OFFSET_STATUS_CODE]!=STATUS_OK):
        nErrCode = rspData[OFFSET_STATUS_CODE]
        print "\ndevice error[%02X] %s"%(nErrCode,ErrToStr(nErrCode))
        exit(1)
    return rspData

def test_cpu_card(serObj):
    print "test cpu card ..."

    test_cmd(serObj,"RATS",CMD_RATS)

    apduSel="00A4040007 11223344556600"
    test_cmd(serObj,"SELECT APP",CMD_TPDU,apduSel)

    apduData="80a0010203 112233"
    test_cmd(serObj,"simple apdu",CMD_TPDU,apduData)

    #normal block size
    apduData="80a00102 10 0102030405060708090A0B0C0D0E0F10"
    test_cmd(serObj,"FSC 24",CMD_TPDU,apduData)

    apduData="80a00102 18 0102030405060708090A0B0C0D0E0F101112131415161718"
    test_cmd(serObj,"FSC 32",CMD_TPDU,apduData)

    apduData="80a00102 1f 0102030405060708090A0B0C0D0E0F101112131415161718191a1b1c1d1e1f"
    test_cmd(serObj,"FSC 39*",CMD_TPDU,apduData)

    #3.3 with good hub
    apduData="80a00102 20 0102030405060708090A0B0C0D0E0F101112131415161718191a1b1c1d1e1f20"
    test_cmd(serObj,"FSC 40",CMD_TPDU,apduData)

    #apduSelSDM="00A4040000"
    #test_cmd(serObj,"select domain",CMD_TPDU,apduSelSDM)

    test_long_var_apdu(serObj)

    apduData="80a00102260102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F20212223242526"
    test_cmd(serObj,"long fixed --2 apdu",CMD_TPDU,apduData)

def test_mifare_card(serObj):
    print "test mifare card..."

    auth_param = "04   ff ff ff ff ff ff"
    test_cmd(serObj,"test MF_AUTH_KEY_A",CMD_MF_AUTH_KEY_A,auth_param)

    rd_param = "04"
    test_cmd(serObj,"test MF_MF_READ",CMD_MF_READ,rd_param)

    rd_param = "05"
    test_cmd(serObj,"test MF_MF_READ",CMD_MF_READ,rd_param)

    rd_param = "06"
    test_cmd(serObj,"test MF_MF_READ",CMD_MF_READ,rd_param)

    rd_param = "07"
    test_cmd(serObj,"test MF_MF_READ",CMD_MF_READ,rd_param)

    rd_param = "08"
    test_cmd(serObj,"test MF_MF_READ",CMD_MF_READ,rd_param)

def do_test_cmd_direct(serObj):
    rspData = test_cmd(serObj,"REQA",CMD_REQA)
    rspData = test_cmd(serObj,"SEL",CMD_SEL)

    if IsMifareCard(rspData[OFFSET_DATA]):
        test_mifare_card(serObj)
    else:
        test_cpu_card(serObj)

def do_test_all_cmd():
    portName = sys.argv[1]
    serObj=LibSC_Serial.InitPort(portName)

    do_test_cmd_direct(serObj)

def main():
    do_test_all_cmd()

if __name__ == '__main__':
    main()