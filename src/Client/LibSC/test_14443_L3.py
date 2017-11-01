
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
from LibSC_Hlp      import *


def test_loop_connect():
    PrintTitle("test loop connect")
    atqa,sak,uid = Connect()
    DumpSession(atqa,sak,uid)
    atqa = ReqA()
    print "\tJust for restry ERR ATQA:%02X"%atqa
    atqa,sak,uid = Connect()
    DumpSession(atqa,sak,uid)
    atqa = ReqA()
    print "\tJust for restry ERR ATQA:%02X"%atqa

def test_haltA():
    PrintTitle("test HaltA")
    atqa=ReqA()
    print "First  ReqA Card:%02X"%atqa
    HaltA()
    atqa=ReqA()
    print "Second ReqA Card:%02X"%atqa
    HaltA()

    atqa,sak,uid =  Connect()
    DumpSession(atqa,sak,uid)
    HaltA()
    atqa,sak,uid =  Connect()
    DumpSession(atqa,sak,uid)
    HaltA()

def do_test_all():
    test_haltA()
    test_loop_connect()

def main():
    portName = sys.argv[1]
    serObj = LibSC_Serial.InitPort(portName)
    Init(serObj)

    do_test_all()

if __name__ == '__main__':
    main()