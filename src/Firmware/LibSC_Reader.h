/*
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
*/

#ifndef LIBSC_RD_h
#define LIBSC_RD_h

#include <MFRC522.h>

#define MAX_CMD_SIZE        64
#define IFD_CMD_MAGIC       "$LibSC.C:"
#define IFD_CMD_MAGIC_LEN   9
#define ICC_CMD_MAGIC       F("$LibSC.R:")

#define CMD_NORMAL          0
#define TAG_ERR             0xff

#define OFFSET_CMD          0
#define OFFSET_LEN          2
#define OFFSET_DATA         3

#define HIBYTE(w)           ( (((word)w)&0xff00)>> 8 )
#define LOBYTE(w)           (((word)w)&0xff)

#define CMD_IS_CLONE        0x8001
#define CMD_SET_UID         0x8002

class LibSC_Reader :public MFRC522
{
public:
    LibSC_Reader(byte chipSelectPin, byte resetPowerDownPin);

    void DumpHex(byte* pData,int data_len);
    void DumpBin(byte* pData,int data_len);
    void EndMsg();
    void ReportErr(byte byCmdCode,byte err);
    int32_t LoadInt32(byte *pBuf);
    bool IsCloneCard();

    void IoCtrl_Magic();
    void IoCtrl_ResponseStart(word wCmdCode,word cmdDataLen=0);
    bool IoCtrl_IsCmd(byte* pCmdData);
    word GetCmdCode(byte* pCmdParam);
    byte GetCmdParamLen(byte* pCmdParam);
    
    void CmdProcess();
    virtual void CmdDispatch(byte* pCmdParam);
};

#endif