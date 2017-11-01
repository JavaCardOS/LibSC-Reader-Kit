/*
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
*/

#include <SPI.h>
#include <LibSC_Reader.h>

#define RST_PIN         9          // Configurable, see typical pin layout above
#define SS_PIN          10         // Configurable, see typical pin layout above

LibSC_Reader libscRdr(SS_PIN, RST_PIN);  // Create LibSC_Reader instance base on MFRC522 

void setup() {  
  Serial.begin(9600);
  while (!Serial);		// Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
	SPI.begin();			// Init SPI bus
	libscRdr.PCD_Init();		// Init MFRC522
	libscRdr.PCD_DumpVersionToSerial();	// Show details of PCD - MFRC522 Card Reader details
} 

void loop() {
    delay(500);    
    libscRdr.CmdProcess();
}
