#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>


#include <Wire.h>  // Only needed for Arduino 1.6.5 and earlier
#include "SSD1306.h" // alias for `#include "SSD1306Wire.h"`

// Include custom images
#include "leafs.h"

// Initialize the OLED display using SPI
// D5 -> CLK
// D7 -> MOSI (DOUT)
// D0 -> RES
// D2 -> DC
// D8 -> CS
// SSD1306Spi        display(D0, D2, D8);
// or
// SH1106Spi         display(D0, D2);

// Initialize the OLED display using brzo_i2c
// D3 -> SDA
// D5 -> SCL
// SSD1306Brzo display(0x3c, D3, D5);
// or
// SH1106Brzo  display(0x3c, D3, D5);

// Initialize the OLED display using Wire library
SSD1306  display(0x3c, D2, D1);
 //SSD1306  display(0x3c, 3, 2);
// SH1106 display(0x3c, D3, D5);


//URL informationer
const char* host = "sardukar.moore.dk"; // fx ddlab.dk
//String url = "test"; //fx: detDerKommerEfterSkråstregen i ddlab.dk/test

//WiFi informationer
const char* ssid     = "robottoAP";
const char* password = "dillerdiller";


void setup() {
  WiFi.hostname("LeafLight");
  pinMode(D6,OUTPUT);
  Serial.begin(115200);
  Serial.println();
  Serial.println();


  // Initialising the UI will init the display too.
  display.init();

  display.flipScreenVertically();
  display.setFont(ArialMT_Plain_10);


  drawLeaf();

  delay(1500);

display.clear();
  
display.display();
  wifiConnect();
}

void wifiConnect() {
  // We start by connecting to a WiFi network
  display.drawString(0, 10, "Connecting to:");
  display.drawString(0, 20, ssid);

  display.display();

  WiFi.begin(ssid, password);

  int dotCounter=0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    display.drawString(0+dotCounter*4,30,".");
    dotCounter++;
    display.display();
  }

  display.clear();
  display.drawString(0,10,"WiFi connected!");
  display.drawString(0,20,"IP address:");
  String ipString=String(WiFi.localIP()[0]) + "." + String(WiFi.localIP()[1]) + "." + String(WiFi.localIP()[2]) + "." + String(WiFi.localIP()[3]);
  display.drawString(0,30, ipString);
  display.display();
}

void drawFontFaceDemo() {
    // Font Demo1
    // create more fonts at http://oleddisplay.squix.ch/
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.setFont(ArialMT_Plain_10);
    display.drawString(0, 0, "Hello world");
    display.setFont(ArialMT_Plain_16);
    display.drawString(0, 10, "Hello world");
    display.setFont(ArialMT_Plain_24);
    display.drawString(0, 26, "Hello world");
}


void drawLeaf() {
    // see http://blog.squix.org/2015/05/esp8266-nodemcu-how-to-create-xbm.html
    // on how to create xbm files
    //display.drawXbm(34, 14, WiFi_Logo_width, WiFi_Logo_height, WiFi_Logo_bits);
    display.fillRect(0, 0, 32, 64); //square to the left
    display.fillRect(96, 0, 32, 64); //square to the right
    display.drawXbm(32, 0, leafsLogo_width, leafsLogo_height, leafsLogo_bits);
    display.display();
}



void loop() {

WiFiClient client;

  const int httpPort = 9999;
  if (!client.connect(host, httpPort)) {
    Serial.println("connection failed");
    return;
  }
 
  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 5000) {
      Serial.println(">>> Client Timeout !");
      client.stop();
      delay(30000);
      return;
    }
  }
  
  delay(500);

  //int inputPointer=0;
  // Read all the lines of the reply 
  while(client.available()){
    //tcpBuffer[inputPointer++]=client.read();
    //if(inputPointer>127) inputPointer=0; //safety joe.
    //tcpBuffer = client.readStringUntil('\r');
    String line = client.readStringUntil('\r');
    Serial.print(line);
    }

//if((char)tcpBuffer[0]=='1') Serial.println("active game!");
//    else if((char)tcpBuffer[0]=='0') Serial.println("upcoming game.");
 //   else if((char)tcpBuffer[0]=='e') Serial.println("error");
    
}


    
  
  

