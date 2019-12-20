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

const char* ssid = "TELUS3854";
const char* password = "tsp5df7yfy";
IPAddress hostIP(1, 1, 1, 1);
int ip_addr = 0;
int port_addr = 4;
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
  IPAddress IP(EEPROM.read(ip_addr) , EEPROM.read(ip_addr + 1) , EEPROM.read(ip_addr + 2) , EEPROM.read(ip_addr + 3));
  hostIP = IP;
  WiFi.begin(ssid, password);
  Serial_Print("\nConnecting to WiFi");
  unsigned long start_wait = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start_wait <= wifi_timeout) {
    Serial_Print(".");
    delay(500);
  }

  MAC = WiFi.macAddress();
  Serial_Print("\nConnected to: " + String(ssid) + "\n");
  Serial_Print("Gateway IP: " + WiFi.gatewayIP().toString() + "\n");
  Serial_Print("Local IP: " + WiFi.localIP().toString() + "\n");
  Serial_Print("UDP port: " + String(UdpPort) + "\n");
  Serial_Print("Host IP: " + hostIP.toString() + "\n");

  dht.begin();
  timeClient.begin();
  Udp.begin(UdpPort);
  udp_send("[" + MAC + "|node_on]");
}

void Serial_Print(String msg) {
  Serial.print(msg);
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
    Serial_Print(http_insert + "\n");
    http.begin(http_insert);
    int httpCode = http.GET();
    if (httpCode > 0) {
      String payload = http.getString();
      Serial_Print(payload + "\n");
    }
    http.end();
  }
  return return_data;
}

IPAddress setIP(String msg) {
  int Parts[4] = {0, 0, 0, 0};
  int Part = 0;
  for ( int i = 0; i < msg.length(); i++ ) {
    char c = msg[i];
    if ( c == '.' ) {
      Part++; continue;
    }
    Parts[Part] *= 10;
    Parts[Part] += c - '0';
  }
  IPAddress IP(Parts[0], Parts[1], Parts[2], Parts[3]);
  EEPROM.write(ip_addr, Parts[0]); EEPROM.write(ip_addr + 1, Parts[1]);
  EEPROM.write(ip_addr + 2, Parts[2]); EEPROM.write(ip_addr + 3, Parts[3]);
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

// TODO: set port
void cmd(String udp_packet) {
  if (String(udp_packet).indexOf("get_data") >= 0) {
    String data_set = get_data();
    udp_send("[" + MAC + "|" + data_set + "]");
  }
  else if (String(udp_packet).indexOf("ping") >= 0) {
    udp_send("[" + MAC + "|" + hostIP.toString() + "|" + WiFi.localIP().toString() + "]");
  }
  else if (String(udp_packet).indexOf("reboot") >= 0) {
    udp_send("[" + MAC + "|rebooting]");
    delay(1000);
    ESP.restart();
  }
  else if (String(udp_packet).indexOf("set_ip") >= 0) {
    int start_index = String(udp_packet).indexOf("|") + 1;
    int end_index = String(udp_packet).indexOf("]");
    String msg = String(udp_packet).substring(start_index, end_index);
    IPAddress IP = setIP(msg);
    hostIP = IP;
    Serial_Print("Host IP Set: " + hostIP.toString() + "\n");
    udp_send("[" + MAC + "|set_ip_ack]");
  }
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(incomingPacket, 255);
    if (len > 0) incomingPacket[len] = 0;
    Serial_Print("Received " + String(packetSize) + " bytes from " + Udp.remoteIP().toString().c_str() + ":" + String(Udp.remotePort()) + "\n");
    Serial_Print("UDP Packet Contents: " + String(incomingPacket) + "\n");
    cmd(String(incomingPacket));
  }
}
