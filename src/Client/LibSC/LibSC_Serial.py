
'''
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
'''

import struct
import logging
import serial

from LibSC_Util     import *
from serial         import Serial

IFD_CMD_MAGIC       = "$LibSC.C:"
ICC_CMD_MAGIC       = "$LibSC.R:"
CMD_MAGIC_LEN       = 9

g_nMaxRetry         = 0
g_dataCache         = ""

def InitPort(portName):
    serObj = serial.Serial(portName, 9600, timeout=0.001)
    strFirmwareInfo = RecvFrom(serObj,64);
    print strFirmwareInfo
    return serObj

def FinalPort(serObj):
    serObj.close()

def RecvFrom(serObj,maxBlkSize=8,tryLimits=1000):
    global g_nMaxRetry
    data = ""
    nErrCount=0
    while True:
        data =serObj.read(maxBlkSize)
        if data == '':
            continue
            nErrCount+=1
            if nErrCount > g_nMaxRetry:
                g_nMaxRetry = nErrCount
            if nErrCount>tryLimits:
                print "[Error] rcv data",tryLimits,"max:",g_nMaxRetry
                exit(1)
            continue
        else:
            nErrCount=0
            break
    return data

def  ExtractCmd(dataBuf):
    dataPreMsg=""
    dataCmd=""
    dataCache=dataBuf

    nDataLen = len(dataBuf)
    for i in range(nDataLen):
        nIndex = dataBuf.find(ICC_CMD_MAGIC)
        if nIndex != -1 and nIndex + 2 >nDataLen: # a ICC response CMD with 2bytes cmdLen
            nCmdLenOffset = nIndex+CMD_MAGIC_LEN
            nIccCmdLen = LoadWord(dataBuf,nCmdLenOffset) #ICC CMD is one byte
            if nIndex + nIccCmdLen+2>nDataLen: #not a complete ICC CMD, continue to recv cmd
                break
            dataPreMsg=dataBuf[:nIndex]
            dataCmd=dataBuf[nIndex:(nIndex+CMD_MAGIC_LEN+2+nIccCmdLen)]
            dataCache=dataBuf[(nIndex+CMD_MAGIC_LEN + nIccCmdLen+2):-1]
            break
        else:
            if (dataBuf[i]=='\x0d') :
                if i+1<nDataLen and (dataBuf[i+1]=='\x0a'):
                        dataCmd=dataBuf[:i]
                        dataCache=dataBuf[i+2:]  #cut cmd into half,skip 0x0d and 0x0a so plus 2
                        break
    return dataPreMsg,dataCmd,dataCache

def hibyte(w):
    v=(w&0xff00)>>8
    return v

def lobyte(w):
    v=(w&0xff)
    return v

def TransIoCmd(serObj,cmdCode,cmdParam=""):
    global g_dataCache

    hb = hibyte(cmdCode)
    lb = lobyte(cmdCode)
    sTemp = "%s%c%c%c"%(IFD_CMD_MAGIC,hb,lb,len(cmdParam))
    sTemp += cmdParam
    logging.debug("SEND->::%s"%BinToHex(sTemp[CMD_MAGIC_LEN:]))
    serObj.write(sTemp)

    rcvLen=1
    dataCache=g_dataCache
    while rcvLen:
        rcvData = RecvFrom(serObj)
        rcvLen = len(rcvData)
        dataPreMsg,singleCmd,dataCache=ExtractCmd(dataCache+rcvData)
        if len(singleCmd):
            if singleCmd.startswith(ICC_CMD_MAGIC):
                rspData = singleCmd[CMD_MAGIC_LEN:]
                g_dataCache = dataCache #save the remain data after ICC response cmd

                logging.debug("\t\tComMSG::%s"%(dataPreMsg))
                logging.debug("RECV<-::%s"%BinToHex(singleCmd[CMD_MAGIC_LEN:]))
                logging.debug("rspData:%s"%BinToHex(rspData))
                logging.debug("Global data cache:%s"%(g_dataCache))

                nLen =  len(rspData)
                sFmt = "%dB"%nLen
                binBuf = struct.unpack(sFmt,rspData)

                return binBuf
            else:
                logging.debug("\t\tComMSG::%s%s"%(dataPreMsg,singleCmd))