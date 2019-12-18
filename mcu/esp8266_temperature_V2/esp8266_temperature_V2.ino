#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <EEPROM.h>

#include "DHT.h"
#define DHTTYPE DHT11
#define dht_dpin 5
DHT dht(dht_dpin, DHTTYPE);

const char* ssid = "";
const char* password = "";
IPAddress hostIP(192, 168, 1, 150);
int UdpPort = 9996;
int wifi_timeout = 10 * 1000;

const long utcOffsetInSeconds = 0;
char incomingPacket[255];
String MAC;
String packet;

WiFiUDP Udp;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds);

void setup() {
  Serial.begin(115200);
  EEPROM.begin(64);
  IPAddress IP(EEPROM.read(0) , EEPROM.read(1) , EEPROM.read(2) , EEPROM.read(3));
  hostIP = IP;

  WiFi.begin(ssid, password);
  Serial.print("\nConnecting to WiFi");
  unsigned long start_wait = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start_wait <= wifi_timeout) {
    Serial.print(".");
    delay(500);
  }

  MAC = WiFi.macAddress();
  Serial.println("\nConnected to: " + String(ssid));
  Serial.println("Gateway IP: " + WiFi.gatewayIP().toString());
  Serial.println("Local IP: " + WiFi.localIP().toString());
  Serial.printf("UDP port: %d\n", UdpPort);
  Serial.println("Host IP: " + hostIP.toString());

  dht.begin();
  timeClient.begin();
  Udp.begin(UdpPort);
  udp_send("[" + MAC + "|on]");
}

String get_data() {
  timeClient.update();
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  int time_stamp = timeClient.getEpochTime();
  String return_data = "";
  
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String http_insert = "http://" + hostIP.toString() + "/php/insert.php?" + "mac=" + MAC + "&time=" + (String)time_stamp + "&temp=" + (String)temp + "&hum=" + (String)hum;
    return_data = (String)time_stamp + "|" + (String)temp + "|" + (String)hum;
    Serial.println(http_insert);
    http.begin(http_insert);
    int httpCode = http.GET();
    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println(payload);
    }
    http.end();
  }
  return return_data;
}

IPAddress str_to_ip(String msg) {
  int Parts[4] = {0, 0, 0, 0};
  int Part = 0;
  for ( int i = 0; i < msg.length(); i++ ) {
    char c = msg[i];
    if ( c == '.' ) Part++; continue;
    Parts[Part] *= 10;
    Parts[Part] += c - '0';
  }
  IPAddress IP(Parts[0], Parts[1], Parts[2], Parts[3]);
  EEPROM.write(0, Parts[0]); EEPROM.write(1, Parts[1]);
  EEPROM.write(2, Parts[2]); EEPROM.write(3, Parts[3]);
  EEPROM.commit();
  return IP;
}

void udp_send(String msg) {
  if (WiFi.status() == WL_CONNECTED) {
    Udp.beginPacket(hostIP, UdpPort);
    Udp.printf((msg + "\n").c_str());
    Udp.endPacket();
  }
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(incomingPacket, 255);
    if (len > 0) incomingPacket[len] = 0;
    Serial.printf("Received %d bytes from %s:%d\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort());
    Serial.printf("UDP Packet Contents: %s", incomingPacket);
    if (String(incomingPacket).indexOf("get_data") >= 0) {
      String data_set = get_data();
      udp_send("[" + MAC + "|" + data_set + "]");
    }
    else if (String(incomingPacket).indexOf("ping") >= 0) {
      udp_send("[" + MAC + "|" + hostIP.toString() + "|" + WiFi.localIP().toString() + "]");
    }
    else if (String(incomingPacket).indexOf("reboot") >= 0) {
      udp_send("[" + MAC + "|rebooting]");
      delay(1000);
      ESP.restart();
    }
    else if (String(incomingPacket).indexOf("set_ip") >= 0) {
      int start_index = String(incomingPacket).indexOf("|") + 1;
      int end_index = String(incomingPacket).indexOf("]");
      String msg = String(incomingPacket).substring(start_index, end_index);
      IPAddress IP = str_to_ip(msg);
      hostIP = IP;
      Serial.println("Host IP Set: " + hostIP.toString());
      udp_send("[" + MAC + "|set_ip_ack]");
    }
  }
}
