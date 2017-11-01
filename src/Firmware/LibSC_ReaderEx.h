/*
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
*/

#ifndef LIBSC_RDEX_h
#define LIBSC_RDEX_h

#include <LibSC_Reader.h>


class LibSC_ReaderEx :public LibSC_Reader
{
public:
    LibSC_ReaderEx(byte chipSelectPin, byte resetPowerDownPin);

    virtual void CmdDispatch(byte* pCmdParam);

    byte m_blockNum;
    StatusCode PICC_Rats(byte cid,byte* pAts,byte* p_ats_len);
    StatusCode PICC_TransmitTPDU(byte* pTpdu,byte nSendLen,byte* pRspTpdu,byte* p_rsp_len);
};

#endif