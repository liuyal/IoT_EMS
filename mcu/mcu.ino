#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <NTPClient.h>
#include <WiFiUdp.h> 

#include "DHT.h"
#define DHTTYPE DHT11
#define dht_dpin 5
DHT dht(dht_dpin, DHTTYPE); 

const char* ssid = "****";
const char* password = "****";
String remote_ip = "192.168.1.150";
const long utcOffsetInSeconds = 0;
String INSERT_REQ;
String MAC;

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds);

void setup() {
  dht.begin();
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {delay(500); Serial.print(".");}
  Serial.println("");
  Serial.print("WiFi connected!");
  Serial.print("Local IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC: ");
  Serial.println(WiFi.macAddress());
  MAC = WiFi.macAddress();
  timeClient.begin();
}

void loop(){
  timeClient.update();
  float temp = dht.readTemperature();      
  float hum = dht.readHumidity();
  int time_stamp = timeClient.getEpochTime();
  
  if (WiFi.status() == WL_CONNECTED) { 
    HTTPClient http;
    INSERT_REQ = "http://"+remote_ip+"/insert.php?"+"mac="+MAC+"&time="+(String)time_stamp+"&temp="+(String)temp+"&hum="+(String)hum;
    Serial.println(INSERT_REQ);
    http.begin(INSERT_REQ); 
    int httpCode = http.GET();
    if (httpCode > 0) {String payload = http.getString(); Serial.println(payload);}
    http.end();
  }
  
  delay(60*1000); //consider longer period
}
