
/***************************************************************************
  ANYNET WEATHERSTATION
  Eseye AnyNet Click and Weather Click Demo
  Sends temperature data to AWS
  Written by John Hughes for Eseye

  Based on:
  
  Example for BME280 Weather Station
  written by Thiago Barros for BlueDot UG (haftungsbeschränkt)
  BSD License

  Make sure the BlueDot BME280 Library is installed
  Make sure the AWS rule and DynamoDB tables have been
  created to store the data
  
 ***************************************************************************/


#include <Wire.h>
#include <avr/wdt.h>
#include "BlueDot_BME280.h"
BlueDot_BME280 bme280 = BlueDot_BME280();

bool complete = false;

void setup() {
  Serial.begin(9600);

  // BME280 Setup
  bme280.parameter.communication = 0;                  //Choose communication protocol
  bme280.parameter.I2CAddress = 0x76;                  //Choose I2C Address
  bme280.parameter.sensorMode = 0b11;                   //Choose sensor mode
  bme280.parameter.IIRfilter = 0b100;                    //Setup for IIR Filter
  bme280.parameter.humidOversampling = 0b101;            //Setup Humidity Oversampling
  bme280.parameter.tempOversampling = 0b101;             //Setup Temperature Ovesampling
  bme280.parameter.pressOversampling = 0b101;            //Setup Pressure Oversampling 
  bme280.parameter.pressureSeaLevel = 1013.25;           //default value of 1013.25 hPa
  bme280.parameter.tempOutsideCelsius = 15;              //default value of 15°C
  
  if (bme280.init() == 0x60) {  
    //Serial.println("BME280 Found.");
  }

  // Set up the communication link with AWS
  Serial.println("AT+AWSPUBOPEN=0,\"MyTopic\"");
  Serial.flush();
  delay(8000);

  // Change to true now setup is complete
  complete = true;
}


void loop() 
{ 

  if (complete) {

      // Prepare to send a message of length 5 bytes
      Serial.println("AT+AWSPUBLISH=0,5");
      Serial.flush();
      delay(8000);
      // Read the temperature sensor and send to AWS
      Serial.println(bme280.readTempC());
      Serial.flush();
      // Set to repeat every 10 minutes (CHANGE FOR TESTING)
      delay(600000);
  }
 
}
