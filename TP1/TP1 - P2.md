# Redes de Computadoras – Trabajo Práctico N°1 (Parte 2)

## Inyección y detección de errores (EDAC)

---

**Integrantes:**

- Maria Wanda Molina
- Marcos Moran
- Martina Juri
- Francisco Gomez Neimann

**Nombre del grupo:**
Subnet Surfers

**Nombre de la institución:**
Facultad de Ciencias Exactas, Físicas y Naturales

**Profesor:**
Santiago M. Henn

**Materia:**
Redes de Computadoras

**Fecha:**
15 de marzo de 2026

---

### Información de contacto

- [wanda.molina@mi.unc.edu.ar](mailto:wanda.molina@mi.unc.edu.ar)
- [mmoran@mi.unc.edu.ar](mailto:mmoran@mi.unc.edu.ar)
- [martina.juri@mi.unc.edu.ar](mailto:martina.juri@mi.unc.edu.ar)
- [francisco.gomez.neimann@mi.unc.edu.ar](mailto:francisco.gomez.neimann@mi.unc.edu.ar)

---

# Resumen

En esta segunda parte del trabajo práctico se analizó el problema de la integridad de los datos durante la transmisión en redes, mediante la implementación de mecanismos de detección de errores.

A través de una simulación controlada, se enviaron mensajes compuestos por un payload binario y un código de redundancia (EDAC), los cuales fueron posteriormente manipulados de forma intencional por un intermediario. Los grupos receptores debieron evaluar si los datos recibidos habían sido alterados, utilizando un método de verificación distinto al empleado en el envío.

La actividad permitió observar el comportamiento de diferentes algoritmos de detección de errores, así como sus limitaciones, destacando la importancia de estos mecanismos en sistemas de comunicación reales.

---

# Introducción

En los sistemas de comunicación, los datos transmitidos pueden verse afectados por diversos factores, como ruido en el canal, interferencias o fallas en los dispositivos intermedios. Esto puede provocar alteraciones en la información enviada, comprometiendo su integridad.

Para mitigar este problema, se utilizan mecanismos de detección de errores, que consisten en agregar información redundante al mensaje original. Esta redundancia permite al receptor verificar si los datos han sido modificados durante la transmisión.

En esta actividad se simuló un canal de comunicación no confiable, donde un intermediario podía alterar los datos. Cada grupo generó un mensaje utilizando un método de detección de errores, y luego recibió un mensaje de otro grupo que debía analizar para determinar si había sido corrompido.

---

# Marco Teórico

## Detección de errores

Los mecanismos de detección de errores permiten identificar si un mensaje ha sido alterado durante su transmisión.

Estos métodos se basan en la incorporación de información redundante, que se calcula a partir del contenido del mensaje. Al recibir los datos, el receptor recalcula dicha información y la compara con la recibida para verificar su validez.

---

## Método XOR entre nibbles

El método XOR se basa en la operación lógica exclusiva OR, que se aplica bit a bit entre dos valores.

En este trabajo práctico, el payload de 16 bits se dividió en cuatro nibbles de 4 bits cada uno. Luego, se aplicó la operación XOR de forma secuencial entre ellos, obteniendo un valor final que se utilizó como código EDAC.

Este método permite detectar ciertas modificaciones en los datos, aunque no es capaz de identificar todos los posibles errores.

---

## Método de paridad por nibble

El método de paridad consiste en analizar la cantidad de bits en 1 dentro de un bloque de datos.

Para cada nibble de 4 bits:

- Se cuenta la cantidad de bits en 1
- Si la cantidad es par, se asigna un bit 0
- Si la cantidad es impar, se asigna un bit 1

Los bits obtenidos se concatenan para formar el valor EDAC.

Este método es simple de implementar, pero presenta limitaciones, especialmente cuando se producen múltiples errores.

---

# Resultados

## Generación del paquete (envío)

Cada grupo construyó un mensaje compuesto por un payload de 16 bits y un código EDAC calculado mediante el método XOR.

### Datos del paquete enviado

| Campo      | Valor                          |
| ---------- | ------------------------------ |
| IP origen  | **10.7.0.1**                   |
| Payload    | **0000 1111 0101 1110 (0F5E)** |
| EDAC (XOR) | **0100**                       |

_Tabla 1. Paquete enviado_

El cálculo del EDAC se realizó aplicando la operación XOR entre los nibbles del payload de izquierda a derecha:

0000 **XOR** 1111 = 1111

1111 **XOR** 0101 = 1010

1010 **XOR** 1110 = 0100

## Recepción del paquete

Los mensajes generados fueron entregados al docente, quien actuó como intermediario del canal de comunicación. Durante este proceso, algunos mensajes fueron modificados intencionalmente, alterando uno o más bits del payload.

Posteriormente, los mensajes fueron redistribuidos de manera aleatoria entre los grupos.

### Datos del paquete recibido

| Campo            | Valor                          |
| ---------------- | ------------------------------ |
| IP origen        | **10.16.0.1**                  |
| Payload recibido | **0101 1111 1100 1110 (5FCE)** |
| EDAC recibido    | **0101**                       |

_Tabla 2. Paquete recibido_

---

## Análisis del resultado

A partir del payload recibido, se recalculó el valor EDAC utilizando el método de paridad por nibble. El resultado obtenido fue:

- **EDAC calculado:** 0001
- **EDAC recibido:** 0101

Dado que ambos valores difieren, se concluye que el mensaje fue **corrupto durante la transmisión**.

La diferencia entre ambos códigos EDAC indica que existe al menos un nibble cuyo valor de paridad fue alterado. En particular, el segundo bit del EDAC presenta una discrepancia, lo que sugiere que el error se encuentra en el nibble correspondiente a esa posición.

A partir de esta información, es posible inferir posibles valores originales del payload. Considerando que el bit de paridad cambia cuando se altera la cantidad de bits en 1, se pueden plantear escenarios donde:

- Se haya modificado 1 bit dentro del nibble afectado
- Se hayan modificado 3 bits dentro del mismo nibble

En ambos casos, la paridad del bloque se invierte, generando la discrepancia observada en el EDAC.

Por lo tanto, los posibles valores originales del payload incluyen:

- 1 bit flipeado : 57CE - 5BCE - 5DCE - 5ECE
- 3 bit flipeados : 51CE - 52CE - 54CE - 58CE

Sin embargo, no es posible determinar con certeza cuál de estos corresponde al mensaje original.

## ![alt text](/TP1/resources/Reporte_RX.jpeg)

_Imagen 1. Reporte de RX. Fuente propia_

## Discusión

El análisis realizado pone de manifiesto las limitaciones del método de detección de errores basado en paridad.

Si bien el algoritmo permite detectar que ocurrió una alteración en el mensaje, no proporciona información suficiente para identificar con precisión qué bits fueron modificados. En particular, distintos patrones de error pueden producir el mismo cambio en el valor de paridad.

En este caso, se observó que:

- Un cambio de 1 bit en un nibble altera su paridad
- Un cambio de 3 bits también produce el mismo efecto
- Incluso, modificaciones en un número mayor de bits podrían no alterar la paridad si se mantiene la cantidad total de unos

Esto implica que múltiples configuraciones de errores pueden ser indistinguibles desde el punto de vista del EDAC utilizado.

Asimismo, el hecho de que el emisor y el receptor utilicen métodos distintos (XOR y paridad) introduce una dificultad adicional, ya que no existe una correspondencia directa entre ambos códigos. Esto reduce la capacidad de validación del sistema.

En consecuencia, el método empleado permite detectar errores de manera parcial, pero no garantiza ni la identificación exacta del error ni la reconstrucción del mensaje original.

---

## Conclusiones

A partir del análisis del mensaje recibido, se determinó que el payload fue efectivamente alterado durante la transmisión, lo cual pudo verificarse mediante la discrepancia entre el EDAC calculado y el recibido.

El estudio de los posibles valores originales del payload evidenció que existen múltiples configuraciones compatibles con el mismo resultado de paridad, lo que impide determinar de forma unívoca el contenido original del mensaje.

Esto demuestra que los métodos de detección de errores basados en paridad:

- permiten identificar la presencia de errores
- pero no permiten su corrección
- ni garantizan la detección de todos los patrones posibles

En particular, se observó que ciertos errores múltiples pueden no ser detectados si preservan la cantidad total de bits en 1 dentro de un bloque.

En consecuencia, este tipo de mecanismos resulta insuficiente para aplicaciones donde la integridad de los datos es crítica, siendo necesario el uso de técnicas más robustas que permitan mejorar la capacidad de detección y, eventualmente, la corrección de errores.
