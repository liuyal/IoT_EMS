#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <EEPROM.h>
#include "DHT.h"

#define DHTTYPE DHT11
#define dht_dpin 5
DHT dht(dht_dpin, DHTTYPE);

//DOTO: Serial set Wi-Fi & Save to EEPROM
const char* WIFI_SSID = "";
const char* WIFI_PWD = "";

IPAddress HOST_IP(0, 0, 0, 0);
int HOST_IP_ADDR = 0;
int PORT_ADDR = 4;
int UPD_PORT = 9996;
int WIFI_TIMEOUT = 10 * 1000;

const long utcOffsetInSeconds = 0;
char incomingPacket[255];
String MAC;
String packet;
String mode = "http";

WiFiUDP Udp;
NTPClient timeClient(Udp, "pool.ntp.org", utcOffsetInSeconds);

void Serial_Print(String msg) {
  Serial.print(msg);
}

void setup() {
  Serial.begin(115200);
  EEPROM.begin(64);
  IPAddress IP(EEPROM.read(HOST_IP_ADDR) , EEPROM.read(HOST_IP_ADDR + 1) , EEPROM.read(HOST_IP_ADDR + 2) , EEPROM.read(HOST_IP_ADDR + 3));
  HOST_IP = IP;

  WiFi.begin(WIFI_SSID, WIFI_PWD);
  Serial_Print("\r\nConnecting to WiFi");
  unsigned long start_wait = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start_wait <= WIFI_TIMEOUT) {
    Serial_Print(".");
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED) {
    MAC = WiFi.macAddress();
    Serial_Print("\r\nConnected to: " + String(WIFI_SSID) + "\r\n");
    Serial_Print("Gateway IP: " + WiFi.gatewayIP().toString() + "\r\n");
    Serial_Print("Host IP: " + HOST_IP.toString() + "\r\n");
    Serial_Print("Local IP: " + WiFi.localIP().toString() + "\r\n");
    Serial_Print("UDP port: " + String(UPD_PORT) + "\r\n");
    dht.begin();
    timeClient.begin();
    Udp.begin(UPD_PORT);
    http_request("http://" + HOST_IP.toString() + "/IoT_Environment_Monitor_System/backend/php/node_status_check.php?mac=" + MAC + "&state=on");
    udp_send("[" + MAC + "|on|" + WiFi.localIP().toString() + "]");
  }
}

void http_request(String request) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, request);
    if (http.GET() > 0) {
      String payload = http.getString();
      Serial_Print(request + "\r\n");
      Serial_Print(payload + "\r\n");
    } else {
      Serial_Print("HTTP ERROR\r\n");
    }
    http.end();
  }
}

void udp_send(String msg) {
  if (WiFi.status() == WL_CONNECTED) {
    Udp.beginPacket(HOST_IP, UPD_PORT);
    Udp.printf((msg + "\r\n").c_str());
    Udp.endPacket();
  }
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
  EEPROM.write(HOST_IP_ADDR, Parts[0]); EEPROM.write(HOST_IP_ADDR + 1, Parts[1]);
  EEPROM.write(HOST_IP_ADDR + 2, Parts[2]); EEPROM.write(HOST_IP_ADDR + 3, Parts[3]);
  EEPROM.commit();
  return IP;
}

void cmd(String udp_packet) {
  if (String(udp_packet).indexOf("fetch_data") >= 0) {
    timeClient.update();
    int time_stamp = timeClient.getEpochTime();
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    http_request("http://" + HOST_IP.toString() + "/IoT_Environment_Monitor_System/backend/php/node_insert_data.php?" + "mac=" + MAC + "&time=" + (String)time_stamp + "&temp=" + (String)temp + "&hum=" + (String)hum);
    udp_send("[" + MAC + "|data_sent|" + (String)time_stamp + "|" + (String)temp + "|" + (String)hum + "]");
  }
  else if (String(udp_packet).indexOf("ping") >= 0) {
    http_request("http://" +  HOST_IP.toString() + "/IoT_Environment_Monitor_System/backend/php/node_status_check.php?mac=" + MAC + "&state=pong");
    udp_send("[" + MAC + "|pong|" + HOST_IP.toString() + "|" + WiFi.localIP().toString() + "]");
  }
  else if (String(udp_packet).indexOf("reboot") >= 0) {
    udp_send("[" + MAC + "|rebooting]");
    delay(1000);
    ESP.restart();
  }
  else if (String(udp_packet).indexOf("set_host") >= 0) {
    String msg_ip = String(udp_packet).substring(String(udp_packet).indexOf("|") + 1,  String(udp_packet).indexOf(":"));
    IPAddress IP = setIP(msg_ip);
    HOST_IP = IP;

    // TODO: save port to EEPROM
    String msg_port = String(udp_packet).substring(String(udp_packet).indexOf(":") + 1,  String(udp_packet).indexOf("]"));
    UPD_PORT = msg_port.toInt();

    udp_send("[" + MAC + "|host_set" + HOST_IP.toString() + ":" + UPD_PORT + "]");
    Serial_Print("Host Set: " + HOST_IP.toString() + ":" + UPD_PORT + "\r\n");
  }
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(incomingPacket, 255);
    if (len > 0) incomingPacket[len] = 0;
    Serial_Print("\r\nReceived " + String(packetSize) + " bytes from " + Udp.remoteIP().toString().c_str() + ":" + String(Udp.remotePort()) + "\r\n");
    Serial_Print("UDP Packet Contents: " + String(incomingPacket));
    cmd(String(incomingPacket));
  }
}
