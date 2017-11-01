
'''
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
'''

import logging

from LibSC_Cmd      import *

def Connect(bReq=False):
    if bReq:
        atqa = ReqA()
    else:
        atqa = WupA()

    sak,uid = Sel()

    return atqa,sak,uid

def DumpSession(atqa,sak,uid):
    print "ATQA:%02X"%atqa
    print "SAK:%02X"%sak
    print "UID:%s"%BinToHex(uid)