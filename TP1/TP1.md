# Redes de Computadoras – Trabajo Práctico N°1

Simulación de envío de paquetes, ARP y ruteo entre redes

**Integrante:** 
- *Maria Wanda Molina*
- Marcos Moran
- Martina Juri
- Francisco Gomez Neimann

**Fecha:** 13 de marzo de 2026
**Materia:** Redes de Computadoras

---

# 1. Introducción

El objetivo de este trabajo práctico fue comprender de manera práctica el funcionamiento del envío de paquetes en redes, incluyendo los mecanismos de encapsulación, resolución ARP, uso de gateway por defecto y ruteo entre redes.

Durante la actividad se simuló el comportamiento de hosts y routers dentro de una topología de red, permitiendo observar cómo los paquetes se transmiten salto por salto hasta alcanzar su destino.

Este informe documenta únicamente la Parte 1 del trabajo práctico, correspondiente a la simulación del envío de paquetes y el proceso de ruteo entre redes.

---

# 2. Aclaraciones sobre la realización del laboratorio

Debido a que en la reunión de laboratorio solo se encontraba presente un integrante de este grupo, la actividad se realizó en conjunto con otro grupo de la clase (Ethernautas v2). En este contexto, el integrante participó representando un host dentro de la red del otro grupo, actuando como dispositivo final dentro de su LAN para poder completar la simulación de transmisión de paquetes.

---

# 3. Identidad de red del dispositivo

En esta sección se documenta la configuración de red asignada al dispositivo representado durante la simulación.

| Campo               | Valor                |
| ------------------- | -------------------- |
| Dispositivo         | Host                 |
| Rol                 | Host                 |
| Dirección IP        | **10.6.0.104**  |
| Dirección MAC       | **AA:43:12** |
| Máscara de subred   | **10.6**        |
| Gateway por defecto | **10.6.0.1**        |

---

# 4. Topología de red utilizada

Aquí se describe la topología utilizada durante la simulación.

La red estaba compuesta por:

* 3 hosts dentro de una red local (LAN)
* Un router actuando como default gateway
* 3 routers intermedios que conectaban distintas subredes

---

# 5. Resolución ARP

Durante la simulación se realizó el proceso de resolución ARP para determinar la dirección MAC del siguiente salto.

El host necesitó conocer la dirección MAC del **gateway por defecto** para poder enviar paquetes a un destino ubicado en otra red.

| IP consultada        | MAC obtenida          |
| -------------------- | --------------------- |
| **10.6.0.1** | **AA:44:43** |

---

# 6. Construcción del paquete

Cada host debía construir un **frame Ethernet** que contuviera un **paquete IP** con un payload en formato binario.

## Frame Ethernet enviado

| Campo       | Valor        |
| ----------- | ------------ |
| MAC destino | **AA:44:43** |
| MAC origen  | **AA:43:12** |

## Paquete IP

El paquete enviado por el host contiene la siguiente información:

| Campo      | Valor                   |
| ---------- | ----------------------- |
| IP origen  | **10.6.0.102**          |
| IP destino | **10.6.0.104**          |
| TTL        | 6                       |
| Payload    | **0111 0111 0011 1100** |
| CRC        | No calculado            |

En este caso, la dirección IP destino (**10.6.0.104**) pertenece a la **misma subred** que la dirección IP del host origen (**10.6.0.102**).
Debido a esto, el paquete no necesitó ser enviado al *gateway* ni atravesar routers intermedios.

El host determinó, utilizando la máscara de subred, que el destino se encontraba dentro de la misma red local. Por lo tanto, resolvió mediante **ARP** la dirección **MAC del host destino** y envió directamente el **frame Ethernet** dentro de la misma LAN.

---

# 8. Paquete recibido

En esta sección se documenta el paquete que fue recibido por el host destino.

## Frame recibido

| Campo       | Valor                         |
| ----------- | ----------------------------- |
| MAC destino | **(MAC del host destino)**    |
| MAC origen  | **(MAC del router anterior)** |

## Paquete IP recibido

| Campo      | Valor                            |
| ---------- | -------------------------------- |
| IP origen  | **(IP del host origen)**         |
| IP destino | **(IP destino)**                 |
| TTL final  | **(valor luego de los routers)** |
| Payload    | **(PAYLOAD recibido)**           |

---

# 9. Reflexiones

## Diferencia entre direccionamiento IP y MAC

La dirección IP destino permanece constante durante todo el recorrido del paquete porque representa el direccionamiento lógico del dispositivo final en la red.

Por otro lado, la dirección MAC cambia en cada salto porque corresponde al direccionamiento físico utilizado dentro de cada enlace local. Cada router reconstruye el frame Ethernet con nuevas direcciones MAC correspondientes al siguiente salto.

---

## Uso del gateway por defecto

Cuando un host necesita comunicarse con un dispositivo que pertenece a otra red, envía el paquete al **gateway por defecto**. Este dispositivo tiene la capacidad de reenviar paquetes hacia otras redes utilizando su tabla de ruteo.

---

## Ruteo hop-by-hop

El ruteo hop-by-hop permite que cada router tome decisiones utilizando únicamente su propia tabla de ruteo. Este modelo facilita la escalabilidad de redes grandes como Internet, ya que ningún dispositivo necesita conocer el camino completo hacia el destino.

---

## Reencapsulación del frame Ethernet

Los routers deben reconstruir el frame Ethernet en cada enlace porque las direcciones MAC solo tienen validez dentro de la red local en la que se transmiten.

---

## Función del TTL

El campo TTL evita que los paquetes circulen indefinidamente en la red en caso de que exista un bucle de ruteo. Cada router decrementa este valor y, cuando llega a cero, el paquete es descartado.
