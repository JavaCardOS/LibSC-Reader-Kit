
'''
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
'''

import sys
import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)-8s] %(filename)-15s:%(lineno)-4d:%(funcName)-20s:%(message)s',
                datefmt='%y%m%d %H:%M:%S',
                filename='AppLog_runtime.log',
                filemode='w')

#################################################################################################
#def a StreamHandler output info both console and file#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


import LibSC_Serial

from LibSC_Util     import *
from LibSC_Cmd      import *
from LibSC_Hlp      import *

print "logging Module Init Ok"