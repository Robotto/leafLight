#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>


#include <Wire.h>  // Only needed for Arduino 1.6.5 and earlier
//#include "SSD1306.h" // alias for `#include "SSD1306Wire.h"`
#include "SSD1306Wire.h"

#include <WiFiManager.h>          //https://github.com/tzapu/WiFiManager

//CREATE MORE FONTS AT: http://oleddisplay.squix.ch/
//FONT LIST:
//		Found in standard fonts file in library
//ArialMT_Plain_10 
//ArialMT_Plain_16
//		Included below:
//Roboto_Bold_36
//Roboto_36
#include "Roboto_36.h"

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
SSD1306Wire  display(0x3c, D2, D1);
 //SSD1306  display(0x3c, 3, 2);
// SH1106 display(0x3c, D3, D5);


//URL informationer
const char* host = "sardukar.moore.dk"; // fx ddlab.dk
//String url = "test"; //fx: detDerKommerEfterSkråstregen i ddlab.dk/test

//WiFi informationer
//const char* ssid     = "If it bleeds we can kill it!";
//const char* password = "IamthegummybearofcandycornIa89";

int blinkPin = D6;

void configModeCallback (WiFiManager *myWiFiManager) {
  Serial.println("Entered config mode");
  Serial.println(WiFi.softAPIP());
  //if you used auto generated SSID, print it
  Serial.println(myWiFiManager->getConfigPortalSSID());

  display.clear();
  display.display();
  display.drawString(0, 10, "Connection failed");
  display.drawString(0, 20, "Creating accesspoint: ");
  display.drawString(0, 30, myWiFiManager->getConfigPortalSSID());
  display.drawString(0, 40, String(WiFi.softAPIP()));

  display.display();

  //ticker.attach_ms(5,fade);
}


void setup() {
  WiFi.hostname("LeafLight");
  pinMode(blinkPin,OUTPUT);
  Serial.begin(115200);
  Serial.println();
  Serial.println();


  // Initialising the UI will init the display too.
  display.init();

  display.flipScreenVertically();
  display.setFont(ArialMT_Plain_10); //CREATE MORE FONTS AT: http://oleddisplay.squix.ch/


  drawLeaf();

  digitalWrite(blinkPin, HIGH);
  delay(1500);
  digitalWrite(blinkPin, LOW);
  
  display.clear();
  display.display();

//WiFiManager
  //Local intialization. Once its business is done, there is no need to keep it around
  WiFiManager wifiManager;
  //reset settings - for testing
  //wifiManager.resetSettings();

  display.drawString(0, 10, "Connecting to wifi..");
  
  display.display();

  //set callback that gets called when connecting to previous WiFi fails, and enters Access Point mode
  wifiManager.setAPCallback(configModeCallback);

  wifiManager.setConnectTimeout(60); //try to connect to known wifis for a long time before defaulting to AP mode

  //fetches ssid and pass and tries to connect
  //if it does not connect it starts an access point with the specified name
  //here  "leaflight"
  //and goes into a blocking loop awaiting configuration
  if (!wifiManager.autoConnect("leafLight")) {
    Serial.println("failed to connect and hit timeout");
    //reset and try again, or maybe put it to deep sleep
    alarm();

  }


  //wifiConnect();
}

void alarm()
{


  display.clear();
  display.setFont(ArialMT_Plain_10);
  display.drawString(0, 10, "wifi config failed.");
  display.drawString(0, 20, "Please reboot.");
  display.display();


	while(1){
		digitalWrite(blinkPin, HIGH);
 		delay(1000);
  		digitalWrite(blinkPin, LOW);
	}
}
/*
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
*/

void drawLeaf() {
    display.clear();
    // see http://blog.squix.org/2015/05/esp8266-nodemcu-how-to-create-xbm.html
    // on how to create xbm files
    //display.drawXbm(34, 14, WiFi_Logo_width, WiFi_Logo_height, WiFi_Logo_bits);
    display.fillRect(0, 0, 32, 64); //square to the left
    display.fillRect(96, 0, 32, 64); //square to the right
    display.drawXbm(32, 0, leafsLogo_width, leafsLogo_height, leafsLogo_bits);
    display.display();
}

bool activeGame;
String homeTeam;
String awayTeam;
String homeScore;
String awayScore;
String gameStart;
String gameTime;

int pound2;
int pound3;
int pound4;
int pound5;
int pound6;

int oldHomeScore;
int oldAwayScore;

bool scoreByHome;
bool scoreByAway;

void loop() {

WiFiClient client;
const int httpPort = 9999;

  if (!client.connect(host, httpPort)) {
    Serial.println(">>> tcp connection failed!");
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
  
  Serial.print(">>> RX!: ");

  //int inputPointer=0;
  // Read all the lines of the reply 
  while(client.available()){
    //tcpBuffer[inputPointer++]=client.read();
    //if(inputPointer>127) inputPointer=0; //safety joe.
    //tcpBuffer = client.readStringUntil('\r');
    String line = client.readStringUntil('\r');
    Serial.println(line);

    client.stop();
    Serial.println();
    Serial.println(">>> Disconnecting.");

    parseLine(line);

    }

   
   


    Serial.println(">>> Sleep for 2 minutes.");
    delay(2*60*1000);
    //delay(15000);

//if((char)tcpBuffer[0]=='1') Serial.println("active game!");
//    else if((char)tcpBuffer[0]=='0') Serial.println("upcoming game.");
 //   else if((char)tcpBuffer[0]=='e') Serial.println("error");
    
}


void parseLine(String line)
{
    if(line.charAt(0) == '1') activeGame=true;

    else if(line.charAt(0) == '0') activeGame=false;//upcoming games in data

    else if(line.charAt(0) == 'e') { drawLeaf(); return; }//no games with target team in data 

    else { drawLeaf(); return; }//error in data
    
    //1#Blackhawks#Lightning#2#4#1st quarter#
    // |          |         | | |           |
    // 1          2         3 4 5           6

    if(activeGame){ 
        Serial.println("Game active!");
        
        pound2=line.indexOf('#',2);
        pound3=line.indexOf('#',pound2+1);
        pound4=line.indexOf('#',pound3+1);
        pound5=line.indexOf('#',pound4+1);
        pound6=line.indexOf('#',pound5+1);

        homeScore = line.substring(pound3+1,pound4);
        awayScore = line.substring(pound4+1,pound5);
        gameTime  = line.substring(pound5+1,pound6);

        if(homeScore.toInt()!=oldHomeScore) {scoreByHome=true; oldHomeScore=homeScore.toInt();}
        else scoreByHome=false;
        if(awayScore.toInt()!=oldAwayScore) {scoreByAway=true; oldAwayScore=awayScore.toInt();}
        else scoreByAway=false; 

      }

    //0#Blackhawks#Lightning#2017-01-25 02:30:00#
    // |          |         |                   |
    // 1          2         3                   4


    else{ 

        Serial.println("Upcoming game!");

        pound2=line.indexOf('#',2);
        pound3=line.indexOf('#',pound2+1);
        pound4=line.indexOf('#',pound3+1);

        //Serial.print("pound2 index: "); Serial.println(pound2);
        //Serial.print("pound3 index: "); Serial.println(pound3);
        //Serial.print("pound4 index: "); Serial.println(pound4);


        gameStart = line.substring(pound3+1,pound4);
      }

    homeTeam = line.substring(2,pound2);
    awayTeam = line.substring(pound2+1,pound3);

    Serial.print("Home Team: "); Serial.println(homeTeam);
    Serial.print("Away Team: "); Serial.println(awayTeam);

    if(activeGame){

        Serial.print("Home Score: "); Serial.println(homeScore);
        Serial.print("Away Score: "); Serial.println(awayScore);
        Serial.print("@: "); Serial.println(gameTime);
        
        //print active game screen
        display.clear();
        display.setTextAlignment(TEXT_ALIGN_CENTER);

        display.setFont(Roboto_36); //CREATE MORE FONTS AT: http://oleddisplay.squix.ch/
        
        if(scoreByHome) display.setFont(Roboto_Bold_36);
        display.drawString(20, 2, homeScore);
        if(scoreByAway) display.setFont(Roboto_Bold_36);
        display.drawString(110, 2, awayScore);

        display.setFont(ArialMT_Plain_10);
        display.drawString(64, 32, gameTime);        
        display.drawString(64, 48, "VS");        

        display.setFont(ArialMT_Plain_10);
        display.setTextAlignment(TEXT_ALIGN_LEFT);
        display.drawString(0, 48, homeTeam);        
        display.setTextAlignment(TEXT_ALIGN_RIGHT);
        display.drawString(128, 48, awayTeam);        
        display.display();        

        if(scoreByAway || scoreByHome) { 
          digitalWrite(blinkPin, HIGH); 
          delay(5000); 
          digitalWrite(blinkPin, LOW);
          scoreByHome=false;
          scoreByAway=false;
        }
      }
    else{
        Serial.print("Game starts at: "); Serial.println(gameStart);

        //print upcoming game info
        display.clear();
        display.setTextAlignment(TEXT_ALIGN_CENTER);        
        display.setFont(ArialMT_Plain_16);
        display.drawString(64, 0, "Next game @ :");        
        display.drawString(64, 48, "VS");        

        display.setFont(ArialMT_Plain_10);
        display.drawString(64, 20, gameStart);        

        display.setTextAlignment(TEXT_ALIGN_LEFT);
        display.drawString(0, 36, homeTeam);        
        display.setTextAlignment(TEXT_ALIGN_RIGHT);
        display.drawString(128, 36, awayTeam);        
        display.display();    
        

      }

    

}
  
  

