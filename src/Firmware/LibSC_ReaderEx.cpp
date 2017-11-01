/*
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
*/

#include <Arduino.h>
#include "LibSC_ReaderEx.h"

LibSC_ReaderEx::LibSC_ReaderEx(	byte chipSelectPin,		///< Arduino pin connected to MFRC522's SPI slave select input (Pin 24, NSS, active low)
					byte resetPowerDownPin	///< Arduino pin connected to MFRC522's reset and power down input (Pin 6, NRSTPD, active low)
				):LibSC_Reader(chipSelectPin,resetPowerDownPin)
{
}

void LibSC_ReaderEx::CmdDispatch(byte* pCmdParam)
{
    LibSC_ReaderEx::StatusCode result;
    bool bRet;
    word wCmdCode = GetCmdCode(pCmdParam);
    byte nParamLen = GetCmdParamLen(pCmdParam);

    Serial.print(F("LibSC EX CmdDispatch CmdCode:"));
    Serial.print(wCmdCode,HEX);
    Serial.print("nParamLen:");
    Serial.print(nParamLen);
    EndMsg();

    switch (wCmdCode)
    {
    case 0:     //TPDU command First
        {
            byte*   pTpduStart=pCmdParam+2;     //First byte is PCB
            byte    nTpduLen = pTpduStart[0];
            byte    rsp_apdu[64];
            byte    nRspLen;

            Serial.print("SendLen:");
            Serial.print(nTpduLen,HEX);

            memset(rsp_apdu,0,64);
            result = PICC_TransmitTPDU(pTpduStart,nTpduLen,rsp_apdu,&nRspLen);
            Serial.print("RspLen:");
            Serial.print(nRspLen,HEX);
            DumpHex(rsp_apdu,nRspLen);
            EndMsg();
            
            if (result == STATUS_OK )
            {
                IoCtrl_ResponseStart(wCmdCode,nRspLen);
                DumpBin(rsp_apdu,nRspLen);
            }
            else
            {
                ReportErr(wCmdCode,result);
            }
        }break;
    case PICC_CMD_RATS:
        {
             byte pAts[64];
             byte ats_len=64;
             result = PICC_Rats(0,pAts,&ats_len);

             Serial.print("RATS END");
             EndMsg();

             if (result == STATUS_OK) 
             {
                 Serial.print("RATS ok");
                 EndMsg();
                 IoCtrl_ResponseStart(wCmdCode,ats_len);
                 DumpBin(pAts,ats_len);
             }
             else
            {
                ReportErr(wCmdCode,result);
            }
        }break;
    default:
        {
            LibSC_Reader::CmdDispatch(pCmdParam);
            return ;
        }
    }
    EndMsg(); //end of ICC_ResponseStart
    Serial.print(F("LibSC_EX_CmdDispatch_End"));
    EndMsg();
}

LibSC_ReaderEx::StatusCode LibSC_ReaderEx::PICC_Rats(byte cid,byte* pAts,byte* p_ats_len)
{
    LibSC_ReaderEx::StatusCode result;
	byte buffer[4];
	
	// Build command buffer
	buffer[0] = PICC_CMD_RATS;
	buffer[1] = 0x50 | (cid&0x0E);      //FSDI|CID
	// Calculate CRC_A
	result = PCD_CalculateCRC(buffer, 2, &buffer[2]);
	if (result != STATUS_OK) {
		return result;
	}

    Serial.print(F("RATS: "));
    DumpHex(buffer,4);
    EndMsg();
	
	result = PCD_TransceiveData(buffer, sizeof(buffer), pAts, p_ats_len);

	if (result == STATUS_OK) { // That is ironically NOT ok in this case ;-)
		Serial.print(F("ATS IS: "));
        DumpHex(pAts,*p_ats_len);
        EndMsg();
        m_blockNum = 0;//reset block num
	}
    else
    {
        Serial.print(F("ATS ERR: "));
        Serial.print(result,HEX);
    }
     return result;
}

LibSC_ReaderEx::StatusCode LibSC_ReaderEx::PICC_TransmitTPDU(byte* pTpdu,byte nSendLen,byte* pRspTpdu,byte* p_rsp_len)
{
    LibSC_ReaderEx::StatusCode result;

	// Build command buffer
	pTpdu[0] = 0x02 | m_blockNum;
	result = PCD_CalculateCRC(pTpdu, nSendLen+1, pTpdu+1+nSendLen);
	if (result != STATUS_OK) {
		return result;
	}

    Serial.print(F("T-APDU: "));
    DumpHex(pTpdu,nSendLen+3);
    EndMsg();
	
    *p_rsp_len = 64; //??PCD_TransceiveData need to specify  output size,currently output buffer must be 64 bytes
	result = PCD_TransceiveData(pTpdu, nSendLen+3, pRspTpdu, p_rsp_len);
    m_blockNum ^=1;

	if (result == STATUS_OK) { 
        Serial.print(F("R-APDU: "));
        DumpHex(pRspTpdu,*p_rsp_len);
        EndMsg();
	}
    else
    {
        Serial.print(F("APDU Transmit ERR: "));
        Serial.print(result,HEX);
    }
    return result;
}
