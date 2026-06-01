# Simulación de Vulnerabilidad en Protocolos de Sincronización Temporal mediante Técnicas Man-in-the-Middle (MitM) y Spoofing de Capa de Aplicación

Este repositorio contiene la documentación, el código fuente y el análisis de la implementación práctica de un entorno controlado destinado a simular la interceptación, manipulación e inyección de datos sobre el protocolo de tiempo de red **NTPv3 (Network Time Protocol)**. El objetivo primordial es analizar los vectores de riesgo en infraestructuras de sincronización y evaluar los mecanismos de defensa integrados en los sistemas operativos modernos.

---

## 1. Fundamento Teórico y Mecanismos del Protocolo NTPv3

El protocolo NTPv3 (especificado en la RFC 1305) opera sobre el protocolo de transporte UDP utilizando el puerto asignado 123. Su arquitectura se basa en una jerarquía de niveles de confianza denominados *Strata* (Estratos), donde Stratum 0 representa a los dispositivos de hardware de reloj atómico o GPS directos, y Stratum 1 representa a los servidores directamente conectados a estos.

A diferencia de otros protocolos de red, NTP no se limita a transferir un dato estático; implementa un algoritmo matemático complejo de estimación de desfase de fase (*offset*) y retraso de ida y vuelta (*round-trip delay*). Para lograr esto de forma asíncrona a través de una red inherentemente inestable, cada intercambio estándar consta de cuatro marcas de tiempo (Timestamps) esenciales de 64 bits:

1. **Originate Timestamp ($T_1$):** El tiempo local del cliente en el momento de despachar la solicitud.
2. **Receive Timestamp ($T_2$):** El tiempo local del servidor en el momento de recibir la solicitud.
3. **Transmit Timestamp ($T_3$):** El tiempo local del servidor en el momento de despachar la respuesta.
4. **Destination Timestamp ($T_4$):** El tiempo local del cliente en el momento de recibir la respuesta del servidor.

El cliente calcula el desplazamiento real del reloj ($\theta$) utilizando la ecuación:

$$\theta = \frac{(T_2 - T_1) + (T_3 - T_4)}{2}$$

### El Desafío de los "Sanity Checks" (Controles de Sanidad)
Los clientes NTP implementan filtros rígidos para evitar ataques de repetición (*replay attacks*) o inyecciones de datos desfasados. El control más estricto es la validación del **Originate Timestamp**: el cliente almacena temporalmente el valor $T_1$ enviado en su paquete de solicitud. Cuando recibe la respuesta del servidor, el campo correspondiente a *Originate Timestamp* en el datagrama de retorno debe coincidir bit a bit con el $T_1$ guardado. Si existe una discrepancia en un solo bit, el paquete se descarta de forma automática en la capa de aplicación sin procesar el cálculo.

---

## 2. Arquitectura de Red y Vector de Ataque Implementado

La simulación se estructuró a partir de una topología de tres nodos diseñada para subvertir el canal de comunicación sin alterar la configuración IP nativa del host objetivo:


```

[ Host Víctima (Windows) ]
│ (Consulta NTP legítima a pool externo)
▼
[ Interceptor AP (ESP32) ] ── (DNS Spoofing: fuerza resolución local) ──► [ Servidor Falso (Ubuntu) ]
│ (Genera paquete espejo v3)
▼
[ Inyección de Desfase (+600s) ]

```

1. **Ataque de Capa de Enlace y Red (Rogue AP + DNS Spoofing en ESP32):** El microcontrolador despliega un punto de acceso inalámbrico que clona una red conocida o legítima. Mediante un servidor DNS embebido que escucha en el puerto 53 UDP, intercepta las peticiones de resolución de nombres de servidores de tiempo (como `time.windows.com` o `time.google.com`) y responde de forma maliciosa apuntando hacia la dirección IP del host Ubuntu.
2. **Manipulación en Capa de Aplicación (`fake_ntp.py` en Ubuntu):** Escuchando en el puerto 123 UDP, el script de Python recibe el datagrama desviado. En lugar de responder con la hora de su propio reloj de hardware, ejecuta una ingeniería inversa del paquete del cliente en tiempo real para generar una respuesta válida y acoplada a sus expectativas matemáticas.

---

## 3. Desglose Técnico del Script `fake_ntp.py`

El script implementa una reconstrucción dinámica de datagramas binarios mediante el uso intensivo del módulo `struct` de Python para el empaquetado de estructuras en formato de red Big-Endian (`!`).

### Puntos Críticos del Código:
* **Aislamiento de Origen:** El script lee dinámicamente los bytes del 40 al 47 del paquete entrante (`data[40:48]`), los cuales contienen la marca exacta de transmisión del cliente. Este bloque se inyecta directamente en la posición de respuesta asignada al *Originate Timestamp* (bytes 24 al 31), superando el filtro de sanidad principal del sistema operativo.
* **Conversión de Épocas Temporales:** Python y los sistemas Unix miden el tiempo en segundos acumulados desde el 1 de enero de 1970 (Época Unix). Por su parte, el protocolo NTP mide el tiempo en segundos transcurridos desde el 1 de enero de 1900. El script compensa esta brecha sumando la constante matemática de **2,208,988,800 segundos**, dividiendo la fracción decimal resultante en un entero de 32 bits para alcanzar la precisión requerida de microsegundos en la red.
* **Modelado de Parámetros de Estabilidad:** Los sistemas operativos descartan servidores temporales que demuestren inestabilidad o alta variabilidad. El script fuerza los campos de **Root Delay** (retraso de raíz) y **Root Dispersion** (dispersión de raíz) a valores hexadecimales mínimos estables (`0x00000A00`), simulando una red de latencia ultra-baja y una precisión de reloj de hardware atómico (Stratum 2, precisión `-20`).

---

## 4. Análisis de las Directivas locales de Windows (`w32time`)

Durante la fase de experimentación en laboratorios locales, se constató que las versiones modernas del servicio de tiempo de Windows (`w32time`) implementan protecciones de kernel adicionales para mitigar ataques de inyección temporal abruptos. Dos de estas directivas críticas operan directamente en el Registro del Sistema:

* **MaxPosPhaseCorrection / MaxNegPhaseCorrection:** Definen el umbral máximo de segundos (hacia adelante o hacia atrás) que el sistema operativo está dispuesto a aceptar de un servidor NTP en una sola transacción. Si el desfase inyectado supera este límite establecido por la directiva local, el paquete se descarta de forma silenciosa por considerarse una anomalía de red o un ataque.
* **Mecanismo MS-SNTP:** En entornos corporativos o de dominio, Windows requiere obligatoriamente firmas criptográficas de clave simétrica integradas con Kerberos y Active Directory. 

*Nota del laboratorio:* El entorno simulado demostró una efectividad del 100% en las capas de red, enlace y transporte al procesar, clonar e inyectar el tráfico modificado. Para validar el impacto final en la capa de interfaz de usuario de la víctima en este entorno local aislado, se emuló la aceptación del cambio temporal desactivando localmente los filtros de fase mediante la flexibilización de los registros de corrección máxima (`ffffffff`), forzando al motor a asimilar el salto temporal inyectado de **600 segundos**.

---

## 5. Guía de Despliegue y Validación Financiera / Técnica

### Paso 1: Ejecución del Script Interceptor (Ubuntu)
Se inicializa el servidor especificando el desfase exacto de 10 minutos (600 segundos) como argumento de ejecución:
```bash
sudo python3 fake_ntp.py 600

```

### Paso 2: Ejecución de Comandos de Sincronización (Windows)

Desde una consola CMD con privilegios de Administrador, se limpia la caché del despachador y se fuerza la consulta instantánea a través de la red controlada por la ESP32:

```cmd
net stop w32time
w32tm /config /manualpeerlist:"[IP_DE_UBUNTU],0x8" /syncfromflags:manual /update
net start w32time
w32tm /resync /rediscover

```

## 6. Conclusiones y Contramedidas Académicas

La realización de esta práctica de laboratorio evidencia que las debilidades del protocolo NTP estándar no residen en su robustez matemática para el cálculo de latencias, sino en su **ausencia nativa de mecanismos de autenticación y cifrado en el canal**. Si un atacante adquiere la capacidad de controlar el enrutamiento de los paquetes (a través de capas de enlace comprometidas como un Rogue AP o envenenamientos ARP/DNS), las validaciones estructurales básicas del protocolo se vuelven insuficientes.

Como principales líneas de defensa recomendadas para mitigar estos riesgos en infraestructuras críticas, se plantean:

1. **Implementación de NTS (Network Time Security):** Extensión moderna de NTP que utiliza TLS para autenticar las fuentes de tiempo y asegurar criptográficamente los datagramas contra manipulaciones de terceros en tránsito.
2. **Autenticación Simétrica Clásica:** Configurar archivos de llaves compartidas (`ntp.keys`) entre los servidores y los clientes de la organización, forzando al daemon a descartar cualquier paquete que no incorpore un hash MAC válido generado con la clave simétrica correspondiente.
3. **Hardening de Políticas Locales:** Mantener configuraciones restrictivas de `MaxPosPhaseCorrection` en los endpoints corporativos para asegurar que, ante un eventual bypass de red, el sistema operativo rechace saltos temporales bruscos que comprometan la validez de los logs de auditoría o los tokens de autenticación.
