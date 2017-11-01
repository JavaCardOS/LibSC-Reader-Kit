
'''
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
'''

import  sys
import  struct

import  LibSC_Serial

from LibSC_Util     import *

MIN_RESPONSE_LEN             = 6    #LEN:2|CMD:2|STA:1|'$':1

OFFSET_CMD_CODE              = 2
OFFSET_STATUS_CODE           = 4
OFFSET_DATA                  = 5

CMD_REQA                     = 0x26
CMD_WUPA                     = 0x52
CMD_SEL                      = 0x90
CMD_HLTA                     = 0x50
CMD_RATS                     = 0xE0

CMD_MF_AUTH_KEY_A            = 0x60
CMD_MF_AUTH_KEY_B            = 0x61
CMD_MF_READ                  = 0x30
CMD_MF_WRITE                 = 0xA0
CMD_MF_DECREMENT             = 0xC0
CMD_MF_INCREMENT             = 0xC1
CMD_MF_RESTORE               = 0xC2
CMD_MF_TRANSFER              = 0xB0
CMD_UL_WRITE                 = 0xA2

CMD_MF_IS_CLONE              = 0x8001
CMD_MF_SET_UID               = 0x8002

CMD_TPDU                     = 0x00

STATUS_OK                   =0
STATUS_ERROR                =1
STATUS_COLLISION            =2
STATUS_TIMEOUT              =3
STATUS_NO_ROOM              =4
STATUS_INTERNAL_ERROR       =5
STATUS_INVALID              =6
STATUS_CRC_WRONG            =7
STATUS_MIFARE_NACK          =8


g_curSerObj=None

g_mapCmdExpectMinLen={
CMD_REQA:2,
CMD_WUPA:2,
CMD_SEL:6,
CMD_HLTA:0,
CMD_RATS:0,

CMD_MF_AUTH_KEY_A:0,
CMD_MF_AUTH_KEY_B:0,
CMD_MF_READ:0,
CMD_MF_WRITE:0,

CMD_MF_IS_CLONE:1,
}

g_mapDeviceErrorText={
    STATUS_OK:                  "Success.",
    STATUS_ERROR:               "Error in communication.",
    STATUS_COLLISION:           "Collission detected.",
    STATUS_TIMEOUT:             "Timeout in communication.",
    STATUS_NO_ROOM:             "A buffer is not big enough.",
    STATUS_INTERNAL_ERROR:      "Internal error in the code. Should not happen.",
    STATUS_INVALID:             "Invalid argument.",
    STATUS_CRC_WRONG:           "The CRC_A does not match.",
    STATUS_MIFARE_NACK:         "A MIFARE PICC responded with NAK.",
}

def InitComm(portName):
    global g_curSerObj
    serObj = LibSC_Serial.InitPort(portName)
    g_curSerObj = serObj
    return serObj

def FinalComm(serObj):
    serObj.close()

def ErrToStr(errCode):
    if errCode in g_mapDeviceErrorText.keys():
        return g_mapDeviceErrorText[errCode]
    return "Unknow error"

def _is_rsp_data_min_len_ok(cmdCode,nRspDataLen):
    if cmdCode in g_mapCmdExpectMinLen.keys():
        nExpectLen = g_mapCmdExpectMinLen[cmdCode]
        if nRspDataLen >=nExpectLen:
            return True
        else:
            return False
    return True

def _is_check_rsp_ok(rspData,cmdCode):
    rspCmdCode =  LoadWord(rspData,OFFSET_CMD_CODE)
    rspStatusCode = rspData[OFFSET_STATUS_CODE]
    if rspCmdCode == cmdCode:
        if  rspStatusCode == STATUS_OK:
            nRspDataLen = _get_rsp_data_len(rspData)
            if _is_rsp_data_min_len_ok(cmdCode,nRspDataLen):
                return True
            else:
                return False
        else :
            logging.error(ErrToStr(rspStatusCode))
            return False
    else:       # rspCmdCode!=cmdCode:
        logging.error("protocol error,response code is mismatch")
        return False

def _get_rsp_data_len(rspData):
    if(rspData<MIN_RESPONSE_LEN):
        logging.error("Response data LEN is wrong[%d]"%rspData)
    return LoadWord(rspData,0)

def _bool_io_ctl(nCmd,param=""):
    rspData = LibSC_Serial.TransIoCmd(g_curSerObj,nCmd,param)
    if _is_check_rsp_ok(rspData,nCmd):
        return True
    else:
        return False

def _access_icc(nCmd):
    rspData = LibSC_Serial.TransIoCmd(g_curSerObj,nCmd)
    if _is_check_rsp_ok(rspData,nCmd):
        atqa=rspData[OFFSET_DATA]
        return atqa
    else:
        return 0

def _mf_auth(cmdCode,blkNum,key):
    param = "%c"%(blkNum)+key
    return _bool_io_ctl(cmdCode,param)

def ReqA():
    LogTitle("REQA")
    nCmd = CMD_REQA
    return _access_icc(nCmd)

def WupA():
    LogTitle("WUPA")
    nCmd = CMD_WUPA
    return _access_icc(nCmd)

def HaltA():
    LogTitle("HLTA")
    nCmd= CMD_HLTA
    return _bool_io_ctl(cmdCode)

def Sel(cmdCode=CMD_SEL):
    LogTitle("SEL")
    if cmdCode == CMD_SEL:
        rspData = LibSC_Serial.TransIoCmd(g_curSerObj,cmdCode)
        if _is_check_rsp_ok(rspData,cmdCode):
            sak=rspData[OFFSET_DATA]
            uid=rspData[OFFSET_DATA+1:-1]
            return sak,uid
        else:
            return 0,""
    else:
        pass

def MF_AuthA(blkNum,key):
    sTitle = "MF_AuthA %d %s"%(blkNum,key.encode('HEX'))
    LogTitle(sTitle)
    return _mf_auth(CMD_MF_AUTH_KEY_A,blkNum,key)

def MF_AuthB(blkNum,key):
    sTitle = "MF_AuthB %d %s"%(blkNum,key.encode('HEX'))
    LogTitle(sTitle)
    return _mf_auth(CMD_MF_AUTH_KEY_B,blkNum,key)

def MF_Read(blkNum):
    LogTitle("MF_Read %d"%blkNum)
    param = "%c"%(blkNum)
    nCmd = CMD_MF_READ
    rspData = LibSC_Serial.TransIoCmd(g_curSerObj,nCmd,param)
    if _is_check_rsp_ok(rspData,nCmd):
        return rspData[OFFSET_DATA:-3]
    else:
        return None

def MF_Write(blkNum,buf):
    LogTitle("MF_Write %d"%blkNum)
    bufSize = len(buf)
    param = "%c%c"%(blkNum,bufSize)
    param += buf
    nCmd = CMD_MF_WRITE
    return _bool_io_ctl(nCmd,param)

def MF_Dec(blkNum,deta):
    LogTitle("MF_Dec %d %d"%(blkNum,deta))
    strDeta = struct.pack(">i",deta)
    param = "%c"%(blkNum)
    param += strDeta
    nCmd = CMD_MF_DECREMENT
    return _bool_io_ctl(nCmd,param)

def MF_Inc(blkNum,deta):
    LogTitle("MF_Inc %d %d"%(blkNum,deta))
    strDeta = struct.pack(">i",deta)
    param = "%c"%(blkNum)
    param += strDeta
    nCmd = CMD_MF_INCREMENT
    return _bool_io_ctl(nCmd,param)

def MF_Transfer(blkNum):
    LogTitle("MF_Transfer %d"%(blkNum))
    param = "%c"%(blkNum)
    nCmd = CMD_MF_TRANSFER
    return _bool_io_ctl(nCmd,param)

def MF_Restore(blkNum):
    LogTitle("MF_Restore %d"%(blkNum))
    param = "%c"%(blkNum)
    nCmd = CMD_MF_RESTORE
    return _bool_io_ctl(nCmd,param)

def MF_SetValue(blkAddr,value):
    buffer = bytearray(16)

    # Translate the int32_t into 4 bytes repeated 2x in value block
    buffer[0] = buffer[ 8] = (value & 0xFF)
    buffer[1] = buffer[ 9] = (value & 0xFF00) >> 8
    buffer[2] = buffer[10] = (value & 0xFF0000) >> 16
    buffer[3] = buffer[11] = (value & 0xFF000000) >> 24
    # Inverse 4 bytes also found in value block
    buffer[4] = UcBitN(buffer[0])
    buffer[5] = UcBitN(buffer[1])
    buffer[6] = UcBitN(buffer[2])
    buffer[7] = UcBitN(buffer[3])
    # Address 2x with inverse address 2x
    buffer[12] = buffer[14] = blkAddr
    buffer[13] = buffer[15] = UcBitN(blkAddr)
    # Write the whole data block
    sData = "".join(map(chr, buffer))

    return MF_Write(blkAddr,sData)

def MF_IsClone():
    LogTitle("MF_IsClone")
    param = ""
    nCmd = CMD_MF_IS_CLONE

    rspData = LibSC_Serial.TransIoCmd(g_curSerObj,nCmd,param)
    if _is_check_rsp_ok(rspData,nCmd):
        return rspData[OFFSET_DATA]
    else:
        return 0

def MF_SetUid(uidBuf):
    LogTitle("MF_SetUid")
    logging.debug("uidbuf:%s"%uidBuf)
    uidData = HexToBin(uidBuf)
    logging.debug("uidbuf:%s"%BinToHex(uidData))
    uidSize = len(uidData)
    param = "%c"%(uidSize)
    param += uidData
    nCmd = CMD_MF_SET_UID
    return _bool_io_ctl(nCmd,param)