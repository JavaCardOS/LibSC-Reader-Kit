/*
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
*/

#include <Arduino.h>
#include "LibSC_Reader.h"

LibSC_Reader::LibSC_Reader(	byte chipSelectPin,		///< Arduino pin connected to MFRC522's SPI slave select input (Pin 24, NSS, active low)
					byte resetPowerDownPin	///< Arduino pin connected to MFRC522's reset and power down input (Pin 6, NRSTPD, active low)
				):MFRC522(chipSelectPin,resetPowerDownPin)
{
}

void LibSC_Reader::DumpHex(byte* pData,int data_len)
{
    for (int i=0;i<data_len;i++) {
        byte byValue=pData[i];
        if (byValue<0x10){
            Serial.print(F(" 0"));
        }
        else{
             Serial.print(F(" "));
        }
        Serial.print(byValue,HEX);
    }
}

void LibSC_Reader::DumpBin(byte* pData,int data_len)
{
    for (int i=0;i<data_len;i++) {
        Serial.write(pData[i]);
    }
}

bool LibSC_Reader::IoCtrl_IsCmd(byte* pCmdData)
{
    if (memcmp(IFD_CMD_MAGIC,pCmdData,IFD_CMD_MAGIC_LEN)==0)
        return true;
    return false;
}

word LibSC_Reader::GetCmdCode(byte* pCmdParam)
{
    return (pCmdParam[OFFSET_CMD]<<8)|pCmdParam[OFFSET_CMD+1];
}

byte LibSC_Reader::GetCmdParamLen(byte* pCmdParam)
{
    return pCmdParam[OFFSET_LEN];
}

void LibSC_Reader::CmdProcess()
{
    byte cmdData[MAX_CMD_SIZE];
    byte* pCmdParam=cmdData+IFD_CMD_MAGIC_LEN;
    char bHasData=0;

    memset(cmdData,0,sizeof(cmdData));
    while(Serial.available()>0)
    {
        char chCount=Serial.readBytes(cmdData,MAX_CMD_SIZE);
        bHasData=1;
    }
    if(bHasData)
    {
        Serial.print(F("CmdData:"));
        DumpHex(cmdData,32);
        EndMsg();

        if (IoCtrl_IsCmd(cmdData)){
            this->CmdDispatch(pCmdParam);
        }
        else{
            Serial.println(F("Error:Wrong CMD tag"));
        }
    }
}

void LibSC_Reader::IoCtrl_Magic()
{
    Serial.print(ICC_CMD_MAGIC);
}

void LibSC_Reader::IoCtrl_ResponseStart(word wCmdCode,word cmdDataLen)
{
    EndMsg();   //
    cmdDataLen+=3;
    IoCtrl_Magic();
    Serial.write((cmdDataLen&0xff00)>>8);
    Serial.write(cmdDataLen&0xff);
    Serial.write((wCmdCode&0xff00)>>8);
    Serial.write(wCmdCode&0xff);
    Serial.write(STATUS_OK);
}

void LibSC_Reader::ReportErr(byte byCmdCode,byte err)
{
    EndMsg();   //
    IoCtrl_Magic();
    Serial.write(0);
    Serial.write(2);
    Serial.write(byCmdCode);
    Serial.write(err);
}

void LibSC_Reader::EndMsg()
{
    Serial.println(F("$"));
}

int32_t LibSC_Reader::LoadInt32(byte *pBuf)
{
    int32_t val = (((uint32_t)pBuf[0])<<24)|(((uint32_t)pBuf[1])<<16)|(((uint16_t)pBuf[0])<<8)|(pBuf[3]);
    return val;
}

bool  LibSC_Reader::IsCloneCard()
{
    PCD_StopCrypto1();
	
	// Activate UID backdoor
	if (!MIFARE_OpenUidBackdoor(true)) {
			Serial.println(F("Activating the UID backdoor failed."));
		return false;
	}
	
	// Wake the card up again
	byte atqa_answer[2];
	byte atqa_size = 2;
	PICC_WakeupA(atqa_answer, &atqa_size);
    return true;
}

void LibSC_Reader::CmdDispatch(byte* pCmdParam)
{
    LibSC_Reader::StatusCode result;
    word wCmdCode = GetCmdCode(pCmdParam);
    byte nParamLen = GetCmdParamLen(pCmdParam);

    Serial.print(F("LibSC CmdDispatch CmdCode:"));
    Serial.print(wCmdCode,HEX);
    Serial.print(F(" ParamLen:"));
    Serial.print(nParamLen);
    EndMsg();

    switch (wCmdCode)
    {
    case PICC_CMD_WUPA:
    case PICC_CMD_REQA:
        {
            Serial.print(F("Enter REQA"));
            EndMsg();
            byte bufferATQA[2];
            byte bufferSize = sizeof(bufferATQA);
            result = PICC_REQA_or_WUPA(wCmdCode, bufferATQA, &bufferSize);

            Serial.print(F("ATQA:"));
            DumpHex(bufferATQA,2);
            Serial.print(F("status:"));
            Serial.print(result);
            EndMsg();
            if (result == STATUS_OK )
            {
                IoCtrl_ResponseStart(wCmdCode,2);
                DumpBin(bufferATQA,2);
            }
            else
            {
                ReportErr(wCmdCode,result);
            }
        }break;
    case PICC_CMD_HLTA:
        {
            result = PICC_HaltA();

            if (result == STATUS_OK)
            {
                IoCtrl_ResponseStart(wCmdCode);
            }
            else
            {
                ReportErr(wCmdCode,result);
            }
        }break;
    case 0x90:      //PICC AUTO SEL
        {
            result = PICC_Select(&uid);
            Serial.print("sak:");
            Serial.print(uid.sak);
            Serial.print(" uid size:");
            Serial.print(uid.size);

            Serial.print(" uid:");
            DumpHex(uid.uidByte,uid.size);
            EndMsg();
            
            if(result == STATUS_OK)
            {
                IoCtrl_ResponseStart(wCmdCode,uid.size+1);
                DumpBin(&uid.sak,1);
                DumpBin(uid.uidByte,uid.size);
            }
            else
            {
                ReportErr(wCmdCode,result);
            }
        }break;
    case PICC_CMD_MF_AUTH_KEY_A:
    case PICC_CMD_MF_AUTH_KEY_B:
        {            
            MIFARE_Key mfKey;
            if (nParamLen == 7)
            {
                byte blkAddr = pCmdParam[OFFSET_DATA];
                byte* pKey  = pCmdParam + OFFSET_DATA+1;

                memcpy(&mfKey.keyByte,pKey,6);

                result = PCD_Authenticate(wCmdCode,blkAddr,&mfKey, &uid);
                if (result != STATUS_OK) {
                    ReportErr(wCmdCode,result);
                }
                else{
                    IoCtrl_ResponseStart(wCmdCode);
                }
            }
            else{
                ReportErr(wCmdCode,STATUS_INVALID);
            }
        }break;
    case PICC_CMD_MF_READ:
    {
        byte buf[18];
        byte byteCount=sizeof(buf);
        byte blkAddr = pCmdParam[OFFSET_DATA];
        if (nParamLen==1)
        {
            result = MIFARE_Read(blkAddr,buf,&byteCount);
            if (result != STATUS_OK) {
                ReportErr(wCmdCode,result);
            }
            else{
                IoCtrl_ResponseStart(wCmdCode,byteCount);
                DumpBin(buf,byteCount);
            }
        }
        else{
                ReportErr(wCmdCode,STATUS_INVALID);
        }        
    }break;
    case PICC_CMD_MF_WRITE:
    {
        byte buf[18];
        byte blkAddr  =pCmdParam[OFFSET_DATA];
        byte byteCount=pCmdParam[OFFSET_DATA+1];
        memcpy(buf,pCmdParam+OFFSET_DATA+2,byteCount);
        Serial.print("MF_WRITE: blkAddr:");
        Serial.print(blkAddr);
        Serial.print(" byteCount:");
        Serial.print(byteCount);
        DumpHex(buf,byteCount);
        EndMsg();

        if ( (nParamLen>=2)&&(nParamLen<=18) )
        {
            result = MIFARE_Write(blkAddr, buf, byteCount); 
            if (result != STATUS_OK) {
                ReportErr(wCmdCode,result);
            }
            else{
                IoCtrl_ResponseStart(wCmdCode);
            }
        }
        else{
                ReportErr(wCmdCode,STATUS_INVALID);
        }
    }break;
    case PICC_CMD_MF_DECREMENT:
    {
        byte blkAddr = pCmdParam[OFFSET_DATA];
        int32_t  detaVal = LoadInt32(pCmdParam+OFFSET_DATA+1);
        Serial.print("MF DEC:");
        Serial.print("BlkNum:");
        Serial.print(blkAddr);
        Serial.print(" DetaValue:");
        Serial.print(detaVal);

        if (nParamLen==5)
        {
            result = MIFARE_Decrement(blkAddr, detaVal); 
            if (result != STATUS_OK) {
                ReportErr(wCmdCode,result);
            }
            else{
                IoCtrl_ResponseStart(wCmdCode);
            }
        }
        else{
                ReportErr(wCmdCode,STATUS_INVALID);
        }        
    }break;
    case PICC_CMD_MF_INCREMENT:
    {
        byte blkAddr = pCmdParam[OFFSET_DATA];
        int32_t  detaVal = LoadInt32(pCmdParam+OFFSET_DATA+1);
        Serial.print("MF INC:");
        Serial.print(" BlkNum:");
        Serial.print(blkAddr);
        Serial.print(" DetaValue:");
        Serial.print(detaVal);
        EndMsg();

        if (nParamLen==5)
        {
            result = MIFARE_Increment(blkAddr, detaVal); 
            if (result != STATUS_OK) {
                ReportErr(wCmdCode,result);
            }
            else{
                IoCtrl_ResponseStart(wCmdCode);
            }
        }
        else{
                ReportErr(wCmdCode,STATUS_INVALID);
        }        
    }break;
    case PICC_CMD_MF_TRANSFER:
    {
        byte blkAddr = pCmdParam[OFFSET_DATA];

        Serial.print("MF TRANS:");
        Serial.print(" BlkNum:");
        Serial.print(blkAddr);
        EndMsg();

        if (nParamLen==1)
        {
            result = MIFARE_Transfer(blkAddr); 
            if (result != STATUS_OK) {
                ReportErr(wCmdCode,result);
            }
            else{
                IoCtrl_ResponseStart(wCmdCode);
            }
        }
        else{
                ReportErr(wCmdCode,STATUS_INVALID);
        }        
    }break;
    case PICC_CMD_MF_RESTORE:
    {
        byte blkAddr = pCmdParam[OFFSET_DATA];

        Serial.print("MF RESTORE:");
        Serial.print(" BlkNum:");
        Serial.print(blkAddr);
        EndMsg();

        if (nParamLen==1)
        {
            result = MIFARE_Restore(blkAddr); 
            if (result != STATUS_OK) {
                ReportErr(wCmdCode,result);
            }
            else{
                IoCtrl_ResponseStart(wCmdCode);
            }
        }
        else{
                ReportErr(wCmdCode,STATUS_INVALID);
        }        
    }break;
    case CMD_IS_CLONE:
    {
        byte bVal=0;
        if (nParamLen==0)
        {
            bool bRetVal = IsCloneCard();
            IoCtrl_ResponseStart(wCmdCode);
            if(bRetVal)
            {
                bVal=1;
            }
            else
            {
                bVal=0;
            }
            DumpBin(&bVal, 1);
            
        }
        else{
                ReportErr(wCmdCode,STATUS_INVALID);
        }

    }break;
    case CMD_SET_UID :
    {
        byte buf[8];
        byte uidSize  =pCmdParam[OFFSET_DATA];
        memcpy(buf,pCmdParam+OFFSET_DATA+1,uidSize);
        Serial.print("UID size:");
        Serial.print(uidSize);
        Serial.print(" UID:");
        DumpHex(buf,uidSize);
        EndMsg();
        
        if ( (nParamLen>=2)&&(nParamLen<=17) )
        {
            bool bRetVal = MIFARE_SetUid(buf,uidSize,true);
            if (bRetVal != true) {
                ReportErr(wCmdCode,STATUS_ERROR);
            }
            else{
                IoCtrl_ResponseStart(wCmdCode);
            }
        }
        else{
                ReportErr(wCmdCode,STATUS_INVALID);
        }

    }break;
    default:
        {
            Serial.print(F("Error:Unknow CMD"));
            IoCtrl_ResponseStart(TAG_ERR,1);
            Serial.write(0xff);  //unknow cmd
        }
    }
    EndMsg(); //end of ICC_ResponseStart
}
