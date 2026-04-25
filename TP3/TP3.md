# Redes de Computadoras - Trabajo Práctico N° 3

# Introducción a infraestructura de servicios web con perspectiva de redes 

**Integrantes:**

- _Maria Wanda Molina_
- _Marcos Moran_
- _Martina Juri_
- _Francisco Gomez Neimann_

**Nombre del grupo:**

Subnet Surfers

**Nombre del centro educativo o institución:**

Facultad de Ciencias Exactas, Físicas y Naturales

**Profesores:**

Santiago M. Henn

**Materia:**

Redes de Computadoras

**Fecha:**

23 de Abril de 2026

---

### Información de los autores

- Información de contacto:

* [wanda.molina@mi.unc.edu.ar](mailto:wanda.molina@mi.unc.edu.ar)
* [mmoran@mi.unc.edu.ar](mailto:mmoran@mi.unc.edu.ar)
* [martina.juri@mi.unc.edu.ar](mailto:martina.juri@mi.unc.edu.ar)
* [francisco.gomez.neimann@mi.unc.edu.ar](mailto:francisco.gomez.neimann@mi.unc.edu.ar)

---

## Resumen
En este trabajo práctico se abordó una introducción a la infraestructura de servicios web desde una perspectiva de redes, poniendo en práctica conceptos vistos en la materia mediante el uso de máquinas virtuales en la nube, conexión remota por SSH, captura y análisis de tráfico con Wireshark, y pruebas de comunicación con netcat y HTTP. El desarrollo del trabajo permitió observar diferencias importantes entre protocolos y mecanismos de seguridad, especialmente en relación con la confidencialidad de la información transmitida. A partir de las experiencias realizadas, se pudo reconocer que algunos servicios, como SSH, protegen el contenido de la comunicación, mientras que otros, como HTTP sin cifrado o ciertas pruebas con netcat, exponen los datos y permiten su inspección en la red.

---

## Introducción
El presente trabajo práctico tiene como finalidad repasar fundamentos de acceso a infraestructura virtualizada y tomar contacto con infraestructura desplegada en la nube. Para eso, se propusieron actividades que combinan investigación conceptual y experimentación práctica sobre conexiones remotas, captura de tráfico y despliegue básico de servicios. Entre las herramientas utilizadas se encuentran SSH, Wireshark y netcat, además de un servidor HTTP simple ejecutado sobre una máquina virtual con Debian.

A lo largo del trabajo se busca no solo verificar que las conexiones funcionen, sino también analizar qué ocurre realmente en la red cuando se establece una comunicación. En ese sentido, se espera que la observación del tráfico se vincule con los contenidos teóricos de la materia, permitiendo comprender situaciones concretas como el establecimiento de conexiones TCP, el uso de UDP, la autenticación mediante claves, el acceso remoto seguro y la diferencia entre transmitir información cifrada o en texto visible. De esta manera, el práctico se orienta tanto a comprender el funcionamiento de los servicios como a reflexionar sobre la confidencialidad y la seguridad en redes de computadoras.

---

## Marco Teórico
Desde el punto de vista de la materia, un sistema de comunicación implica el intercambio de información entre entidades a través de un medio de transmisión, donde intervienen distintos mecanismos y protocolos para que los datos lleguen de forma correcta. En este marco, las comunicaciones de datos y las arquitecturas de protocolos permiten organizar el intercambio entre sistemas, tanto en redes locales como en redes más amplias, y constituyen la base para entender el funcionamiento de servicios como SSH o HTTP.

Uno de los ejes del trabajo es el uso de **SSH** para acceder de forma remota a una máquina virtual. Este tipo de acceso se vincula con la necesidad de administrar sistemas a distancia de manera segura. En el plano teórico, esto se relaciona con la seguridad en redes, particularmente con mecanismos de cifrado y autenticación. **Stallings** distingue las amenazas pasivas, orientadas a obtener información de una comunicación, de las amenazas activas, orientadas a modificar datos o generar transmisiones falsas; por eso el cifrado y la autenticación cumplen funciones centrales al momento de proteger el intercambio de información.

En relación con esto, es importante diferenciar **cifrado** y **autenticación**. El cifrado apunta a preservar la privacidad del contenido transmitido, impidiendo que terceros puedan interpretarlo fácilmente. La autenticación, en cambio, busca verificar el origen o legitimidad de una entidad o mensaje. En el material de Stallings ambos conceptos aparecen tratados como funciones distintas dentro de la seguridad de red: por un lado la privacidad mediante cifrado, y por otro la autenticación de mensajes y las firmas digitales.

En la parte práctica se utilizara **Wireshark** y **netcat** para observar el tráfico de red. El uso de estas herramientas se relaciona con el estudio de protocolos de transporte y con el análisis de cómo circulan los datos en una comunicación. El TP propone capturar tráfico SSH, conexiones TCP y UDP, y también tráfico HTTP generado por un servidor simple desplegado con Python. Esto permite comparar distintos casos: cuando la comunicación se encuentra protegida, el contenido no puede interpretarse directamente en la captura; en cambio, cuando se trata de protocolos sin cifrado, como HTTP en este contexto, los datos pueden observarse con mayor facilidad. 

Finalmente, el despliegue de un servidor HTTP sencillo dentro de la VM permite vincular lo trabajado con la idea de servicios web básicos funcionando sobre la arquitectura de red. Al acceder desde la PC local al recurso publicado en la máquina virtual, se pone en juego la relación entre aplicación, transporte y red, a la vez que se evidencian cuestiones de seguridad: si el tráfico HTTP se transmite sin cifrado, el contenido puede ser inspeccionado e incluso potencialmente alterado por un tercero con acceso al canal. Por eso, uno de los aportes principales de este trabajo no fue solo poner en funcionamiento herramientas y servicios, sino también comprender por qué la confidencialidad y la protección del tráfico son aspectos fundamentales en redes de computadoras.

---

## Investigación conceptual

1) ¿Qué es SSH y qué problema resuelve? 
    SSH es un protocolo de red que permite el acceso remoto seguro a otro equipo mediante una conexión cifrada. Resuelve el problema de que se filtren las credenciales de acceso o datos transmitidos entre los equipos como sucede con los protocolos no cifrados como Telnet o FTP.

2) Diferencia entre autenticación y cifrado
    La autenticación sirve para verificar la identidad de un usuario o dispositivo, mientras que el cifrado se utiliza para proteger los datos transmitidos entre dos partes, asegurando que solo el destinatario previsto pueda leerlos.

3) ¿Qué es una clave pública y una clave privada? 
    La clave pública y la clave privada un par de claves de un sistema de cifrado asimétrico: la clave pública puede difundirse y la privada debe mantenerse en secreto. Lo que se cifra o firma con una (clave privada) se verifica o descifra con la otra (clave pública).

4) ¿Por qué la clave privada no debe compartirse? 
    La clave privada no debe compartirse porque es el dato secreto que permite descifrar mensajes dirigidos al dueño y generar firmas digitales en su nombre, si otra persona la conoce, se pierde la confidencialidad y la autenticidad.

5) ¿Qué ventajas tienen las claves SSH frente a contraseñas?
    Las claves SSH ofrecen mayor seguridad y comodidad que las contraseñas, porque son más resistentes a ataques, no dependen de secretos fáciles de adivinar y permiten autenticación robusta sin exponer credenciales de forma tradicional.

---

## Resultados

-TCP-
Se puede ver el mensaje enviado a la VM desde local, pero no el mensaje enviado desde la VM a la compu local

-UDP-
El mensaje se puede ver tanto de un lado como del otro

-HTTP-
Se puede ver el trafico de la página en wireshark


---

## Conclusión