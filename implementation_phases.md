# Plan de implementación: Etiqueta

Mini-tienda para vendedores de ropa por redes sociales. Cada vendedor tiene un enlace público donde sus clientes ven las prendas y hacen su pedido. El pedido le llega al vendedor por WhatsApp y lo administra en un panel. Incluye cálculo de envío local con Uber.

Este documento es la guía de trabajo. Se va marcando fase por fase.

---

## 1. Reglas de trabajo

**Convención de idioma:** todo el código va en inglés (nombres de apps, modelos, campos, funciones, URLs, comentarios y mensajes de commit). La documentación y las explicaciones en el chat se quedan en español.

Estás aprendiendo y quieres entender lo que copias, así que el método es este:

1. **Claude muestra el código en el chat, en bloques pequeños.** Tú lo pasas al editor y lo ejecutas. Nada de archivos grandes de golpe.
2. **Cada bloque trae cuatro cosas:** el nombre del archivo, el código, una explicación corta de lo importante (el porqué, no solo el qué) y el comando para probarlo con el resultado esperado.
3. **No se avanza sin pasar el checkpoint.** Cada fase termina con una lista de cosas que deben funcionar. Si una falla, se arregla antes de seguir.
4. **Si algo falla, pega el error completo**, no un resumen. Con el mensaje entero se ve la causa real.
5. **Un reto por fase.** Al final de cada fase hay un ejercicio pequeño que haces tú solo, sin copiar. Es lo que fija lo aprendido. Claude revisa tu solución después.
6. **Un commit de Git por fase** (o por subfase si es larga), con un mensaje claro. Así tienes puntos de retorno y un historial limpio para el portafolio.
7. **Nada de secretos en el repositorio.** Tokens, contraseñas y claves van en un archivo `.env` que está en `.gitignore`.
8. **Si algo no queda claro, se pregunta antes de seguir.** Es mejor detenerse que avanzar sin entender.

---

## 2. Alcance

**Entra en la versión 1:**
- Mini-tienda pública por vendedor, con catálogo de prendas, tallas y colores.
- Carrito y pedido con datos de entrega.
- Panel del vendedor para administrar productos, existencias y pedidos.
- Aviso de pedido nuevo por WhatsApp.
- Cálculo de envío local: recoger en persona, tarifa fija y cotización con Uber.
- Pruebas automáticas, despliegue y documentación.

**No entra (queda en "siguientes pasos" del README):**
- Pagos en línea. El vendedor confirma el pago a mano (transferencia o depósito).
- Integración con Instagram o Facebook Messenger.
- Bot con IA que conversa con los clientes.
- Suscripciones y cobro a vendedores.
- Envíos nacionales con paqueterías.

---

## 3. Tecnología

| Parte | Herramienta | Para qué |
|---|---|---|
| Lenguaje | Python | Todo el backend |
| Framework | Django | Páginas, panel, base de datos, usuarios |
| Base de datos | PostgreSQL | Productos, pedidos, negocios |
| Variables secretas | python-dotenv | Leer el archivo `.env` |
| Llamadas a APIs | requests | WhatsApp y Uber |
| Pruebas | Sistema de pruebas de Django | Verificar que la lógica funciona |
| Servidor | Gunicorn + WhiteNoise | Producción |
| Hosting | Railway, Render o un VPS | Publicarlo en internet |
| Control de versiones | Git y GitHub | Historial y portafolio |

Ya conoces Python, PostgreSQL y Git, así que lo nuevo de verdad es Django. Por eso las primeras fases van más despacio.

---

## 4. Modelo de datos (resumen)

```
Store ──< Product ──< Variant
   │
   └──< Order ──< OrderLine >── Variant
```

- **Store** (negocio): `name`, `slug` (para el enlace), `whatsapp_number`, `pickup_address`, `owner` (usuario).
- **Product:** `name`, `description`, `photo`, `base_price`, `is_active`.
- **Variant:** `size`, `color`, `stock`. Pertenece a un producto.
- **Order:** `store`, datos de la clienta, dirección, `shipping_method`, `shipping_cost`, `total`, `status`.
- **OrderLine:** `variant`, `quantity`, `unit_price` (precio al momento de la compra).

Estados del pedido: `pending_payment`, `paid`, `shipped`, `delivered`, `cancelled`.

Métodos de envío: `pickup`, `flat_rate`, `uber`.

**Regla de oro:** todas las consultas del panel filtran por la tienda (`Store`) del usuario. Un vendedor jamás debe ver datos de otro.

---

## 5. Fases

Las duraciones son aproximadas y dependen de cuántas horas por semana le dediques. Con unas 8 a 10 horas semanales, el total ronda las 6 a 8 semanas. Tómalas como orientación, no como compromiso.

---

### Fase 0: Preparación del entorno
**Duración:** 1 sesión

**Objetivo:** tener el proyecto Django corriendo en tu computadora con PostgreSQL y Git.

**Aprenderás:** entornos virtuales, estructura de un proyecto Django, configuración con `.env`.

**Pasos:**
1. Usar el entorno de Miniconda `DjangoEnvironment` (ya creado) en lugar de `venv`.
2. Verificar que Django, psycopg, python-dotenv, requests y Pillow estén instalados en ese entorno.
3. Crear el proyecto y las apps: `storefront` (tienda pública), `dashboard` (panel del vendedor) y `orders` (pedidos).
4. Crear la base de datos en PostgreSQL y conectarla.
5. Mover los datos sensibles a `.env` y crear `.gitignore`.
6. Inicializar Git y subir el primer commit a GitHub.

**Checkpoint:**
- [ ] `python manage.py runserver` muestra la página de bienvenida de Django.
- [ ] `python manage.py migrate` termina sin errores contra PostgreSQL.
- [ ] El archivo `.env` no aparece en `git status`.

**Reto:** crea una vista que responda "hello" en la ruta `/health/` y verifícala en el navegador.

---

### Fase 1: Modelos y administración
**Duración:** 1 a 2 sesiones

**Objetivo:** definir la base de datos y poder cargar datos desde el admin de Django.

**Aprenderás:** modelos, relaciones (ForeignKey), migraciones, el admin de Django.

**Pasos:**
1. Escribir los modelos `Store`, `Product`, `Variant`.
2. Crear y aplicar las migraciones.
3. Registrar los modelos en el admin.
4. Crear un superusuario y cargar un negocio de prueba con 4 o 5 prendas.
5. Escribir los modelos `Order` y `OrderLine` (sin vistas todavía).

**Checkpoint:**
- [ ] Puedes crear un negocio, productos y variantes desde `/admin/`.
- [ ] Una variante sin existencias se puede guardar con valor 0, pero no con un número negativo.
- [ ] Las migraciones están en el repositorio.

**Reto:** agrega un campo `is_active` a `Variant` y haz que el admin permita filtrar por él.

---

### Fase 2: Mini-tienda pública
**Duración:** 2 sesiones

**Objetivo:** que cualquiera abra `/t/mi-negocio/` y vea el catálogo.

**Aprenderás:** URLs con parámetros, vistas, plantillas, archivos estáticos y de medios.

**Pasos:**
1. Ruta por `slug` del negocio.
2. Vista que lista los productos activos con foto y precio.
3. Vista de detalle con selector de talla y color.
4. Mostrar solo las variantes con existencias.
5. Estilos sencillos pensados para celular primero (la mayoría entrará desde Instagram).

**Checkpoint:**
- [ ] El enlace de un negocio muestra solo sus productos.
- [ ] Una talla agotada no se puede elegir.
- [ ] Un `slug` que no existe devuelve error 404.
- [ ] Se ve bien en un celular o en el modo móvil del navegador.

**Reto:** agrega una página de "Sobre la tienda" con el nombre y el WhatsApp del negocio.

---

### Fase 3: Carrito y pedido
**Duración:** 2 a 3 sesiones

**Objetivo:** que la clienta arme un carrito, deje sus datos y se cree el pedido.

**Aprenderás:** sesiones, formularios de Django, transacciones y control de existencias.

**Pasos:**
1. Carrito guardado en la sesión del navegador.
2. Formulario de entrega: nombre, teléfono, dirección o "recoger en persona".
3. Campo de método de envío en el pedido. Por ahora solo `pickup` y `flat_rate`. **Se deja listo para sumar Uber en la Fase 6.**
4. Crear `Order` y `OrderLine` dentro de una transacción atómica que descuenta las existencias.
5. Página de confirmación con el número de pedido.

**Checkpoint:**
- [ ] Un pedido descuenta las existencias correctas.
- [ ] No se puede pedir más cantidad de la que hay.
- [ ] Si algo falla a la mitad, no queda un pedido a medias ni existencias descontadas.
- [ ] El total del pedido incluye el costo de envío.

**Reto:** muestra el resumen del carrito con subtotal, envío y total antes de confirmar.

---

### Fase 4: Panel del vendedor
**Duración:** 3 sesiones

**Objetivo:** que el vendedor administre su tienda sin entrar al admin de Django.

**Aprenderás:** autenticación, permisos, aislamiento de datos entre negocios, formularios de edición.

**Pasos:**
1. Inicio de sesión y cierre de sesión.
2. Relacionar cada usuario con su negocio.
3. Lista de pedidos con filtro por estado.
4. Detalle del pedido y cambio de estado.
5. Alta, edición y baja de productos y variantes.
6. Pantalla de ajustes del negocio: WhatsApp, dirección de recogida, tarifa fija.

**Checkpoint:**
- [ ] Sin sesión iniciada, el panel redirige al login.
- [ ] El vendedor A **no puede** ver ni editar pedidos o productos del vendedor B, ni escribiendo la URL a mano.
- [ ] Cambiar el estado de un pedido queda guardado.
- [ ] El vendedor puede subir una foto de producto.

**Reto:** agrega un contador de pedidos pendientes de pago en la parte superior del panel.

---

### Fase 5: Aviso por WhatsApp
**Duración:** 2 a 3 sesiones

**Objetivo:** que al crearse un pedido, el vendedor reciba un mensaje de WhatsApp.

**Aprenderás:** consumir una API externa, webhooks, variables de entorno, manejo de errores de red.

**Pasos:**
1. Crear la app en Meta for Developers y obtener el número de pruebas y el token temporal.
2. Agregar el número del vendedor como destinatario de prueba.
3. Función `send_whatsapp()` aislada en su propio archivo.
4. Enviar un mensaje de plantilla (Meta trae una de ejemplo para pruebas) y verificar que llega.
5. Crear una plantilla propia de "pedido nuevo" y enviarla al crear cada pedido.
6. Crear el webhook que recibe y registra los eventos de Meta (verificación inicial y mensajes entrantes).
7. Si el envío falla, el pedido **no** se pierde: se registra el error y se sigue.

**Nota importante:** para escribirle primero a alguien fuera de la ventana de 24 horas de conversación, WhatsApp exige una plantilla aprobada. Por eso el aviso de pedido nuevo debe ser una plantilla. Revisa en la documentación de Meta el proceso de aprobación y los costos actuales antes de cotizar a un cliente.

**Checkpoint:**
- [ ] Al hacer un pedido de prueba, tu teléfono recibe el aviso.
- [ ] Si quitas el token a propósito, el pedido igual se crea y el error queda registrado.
- [ ] El webhook responde correctamente a la verificación de Meta.
- [ ] El token no está en el código ni en Git.

**Reto:** agrega al mensaje el enlace directo al pedido en el panel.

---

### Fase 6: Envío local con Uber
**Duración:** 3 a 4 sesiones

**Objetivo:** que en el checkout la clienta vea el costo real de un envío local con Uber, y que quede guardado en el pedido.

#### Qué hay que saber antes de empezar

- **"Uber Envíos" y "Uber Direct" no son lo mismo.** Uber Envíos es el servicio para personas, que se usa desde la app. La integración para negocios y programadores se llama **Uber Direct**, y es la que tiene API.
- Uber Direct tiene un endpoint de **cotización** que, según su documentación, sirve para evaluar si se puede entregar entre dos direcciones y cuánto cuesta. La respuesta trae el monto en centavos, la duración estimada y un identificador de cotización que expira.
- Para obtener credenciales se necesita una cuenta en `direct.uber.com`, con tarjeta de crédito registrada. La propia documentación avisa que el proceso de creación de cuenta solo está disponible en ciertas regiones.
- En México, Uber Direct se abrió a pymes y, según una nota de prensa de 2023, estaba disponible en 68 ciudades. **No he podido confirmar que Ciudad Juárez esté cubierta ni que el registro autoservicio funcione para ti.** Eso se verifica en el primer paso de esta fase, antes de escribir código.
- Cada vendedor que quiera usar Uber probablemente necesite **su propia cuenta de Uber Direct**, porque el cobro va a la tarjeta del comercio. Esto afecta el diseño: las credenciales se guardan por negocio.
- En algunas regiones hay que mandar **latitud y longitud** en la cotización, no solo la dirección escrita. Hay que comprobar si aplica en México.

#### Decisión de diseño

El cálculo de envío va detrás de una pieza intercambiable. Así, si Uber no está disponible o falla, la tienda sigue funcionando con tarifa fija.

```
checkout → calculate_shipping(store, customer_address)
              ├── pickup        → $0
              ├── flat_rate     → tarifa del negocio
              └── uber           → cotización de Uber Direct
                                   (si falla → ofrecer tarifa fija)
```

#### Pasos

**6.1 Verificar disponibilidad (sin código)**
1. Entrar a `direct.uber.com` e intentar crear la cuenta de pruebas.
2. Confirmar si Ciudad Juárez tiene cobertura y qué pide Uber (sandbox, requisitos, aprobación).
3. Anotar `client_id`, `client_secret` y `customer_id` en tu `.env`.
4. Si no se puede, **saltar a 6.7** y dejar Uber como mejora futura. No bloquea el resto del proyecto.

**6.2 Configuración por negocio**
1. En el modelo `Store`: dirección de recogida (con coordenadas si se necesitan), método(s) de envío habilitados, tarifa fija.
2. En ajustes del panel: el vendedor elige qué opciones ofrece.

**6.3 Dirección de la clienta**
1. Pedir calle, número, colonia y referencias en campos separados.
2. Si Uber exige coordenadas, convertir la dirección a latitud y longitud con un servicio de geocodificación. El servicio se elige en este paso, comparando precio y precisión para México.

**6.4 Cliente de Uber**
1. Archivo `shipping/uber.py` aislado del resto.
2. Función para obtener el token de acceso (flujo `client_credentials`) y guardarlo en memoria hasta que expire.
3. Función `get_quote(origin, destination)` que llama al endpoint de cotización.
4. Convertir el monto de centavos a pesos o a la moneda que devuelva la API. Hay que leer el campo de moneda, no asumir pesos.
5. Manejar errores: sin cobertura, dirección inválida, tiempo de espera agotado.

**6.5 Integración con el checkout**
1. Cuando la clienta elige "Envío con Uber", cotizar y mostrar costo y tiempo estimado.
2. Guardar en el pedido: método, costo, identificador de la cotización y su fecha de expiración.
3. Si la cotización falla, mostrar un mensaje claro y ofrecer tarifa fija o recoger.
4. Si la cotización expiró antes de confirmar, volver a cotizar.

**6.6 Pruebas**
1. Pruebas con respuestas simuladas de Uber (sin llamar a la API real): éxito, sin cobertura, error de red, token vencido.
2. Una prueba manual contra el entorno de pruebas de Uber, si lo permite.

**6.7 Plan B si Uber no está disponible**
1. Calcular la distancia entre la tienda y la clienta y aplicar una tarifa por rangos que el vendedor configura (por ejemplo, hasta 3 km, hasta 6 km, etc.).
2. Documentar en el README que Uber queda como mejora futura.

**Fuera de esta fase:** crear la entrega real en Uber desde el panel (pedir al repartidor, seguimiento). Se deja como siguiente paso, porque implica cobros reales y estados adicionales.

**Checkpoint:**
- [ ] En el checkout aparecen las opciones habilitadas por el negocio.
- [ ] Con Uber, la clienta ve un costo y un tiempo estimado antes de confirmar.
- [ ] El costo de envío queda guardado en el pedido y se suma al total.
- [ ] Si Uber falla, la compra sigue siendo posible con otra opción.
- [ ] Las credenciales de Uber no están en el código ni en Git.
- [ ] Las pruebas con respuestas simuladas pasan.

**Reto:** muestra en el panel qué método de envío eligió cada clienta y cuánto costó.

---

### Fase 7: Pruebas y calidad
**Duración:** 2 sesiones

**Objetivo:** tener pruebas automáticas de lo que no puede fallar.

**Aprenderás:** pruebas unitarias y de integración en Django, qué conviene probar y qué no.

**Qué probar:**
- Descuento de existencias y rechazo de pedidos que exceden el stock.
- Aislamiento: un vendedor no accede a datos de otro.
- Cálculo del total con envío.
- Envío de WhatsApp (simulado) y manejo de fallos.
- Cotización de Uber (simulada).

**Checkpoint:**
- [ ] `python manage.py test` pasa completo.
- [ ] Hay al menos una prueba por cada regla crítica de arriba.
- [ ] Una prueba falla cuando rompes a propósito la regla que protege.

**Reto:** escribe tú una prueba para un caso que no se haya cubierto.

---

### Fase 8: Despliegue
**Duración:** 2 sesiones

**Objetivo:** que la app esté en internet con HTTPS y funcione el webhook de WhatsApp.

**Aprenderás:** configuración de producción, variables de entorno en el servidor, archivos estáticos, bases de datos en la nube.

**Pasos:**
1. Separar la configuración de desarrollo y producción.
2. Desactivar `DEBUG`, configurar `ALLOWED_HOSTS` y claves secretas.
3. Archivos estáticos con WhiteNoise y fotos de productos en un almacenamiento persistente.
4. Subir a Railway, Render o un VPS, con PostgreSQL.
5. Apuntar el webhook de Meta a la URL pública.
6. Respaldos de la base de datos.

**Nota:** los costos de hosting cambian con frecuencia. Revisa la página de precios del proveedor al momento de elegir.

**Checkpoint:**
- [ ] La app abre desde cualquier celular con `https://`.
- [ ] Un pedido hecho desde tu celular genera el aviso por WhatsApp.
- [ ] El panel exige iniciar sesión en producción.
- [ ] `DEBUG` está en falso y no se muestran errores internos.

---

### Fase 9: Documentación y primeros usuarios
**Duración:** 1 a 2 sesiones, más el tiempo de prueba con vendedores

**Objetivo:** convertir el proyecto en algo mostrable y probarlo con gente real.

**Pasos:**
1. README con descripción, capturas, tecnologías, cómo correrlo y decisiones técnicas.
2. Video corto de la demo (1 a 2 minutos).
3. Diagrama simple de la arquitectura.
4. Sección "Siguientes pasos" con lo que quedó fuera del alcance.
5. Dárselo a 2 o 3 vendedores reales durante unas semanas, sin cobrarles.
6. Anotar qué usan, qué ignoran y qué piden.

**Checkpoint:**
- [ ] Alguien que no te conoce puede entender el proyecto leyendo solo el README.
- [ ] Al menos un vendedor real lo usó con pedidos reales.
- [ ] Tienes una lista de lo que aprendiste de ellos.

---

## 6. Después de la versión 1

Solo si hay vendedores usándolo y pidiendo estas cosas:
1. Pagos en línea (Mercado Pago o similar).
2. Crear la entrega con Uber directamente desde el panel.
3. Más de un usuario por negocio.
4. Conexión con Instagram.
5. Asistente con IA que conteste preguntas frecuentes.
6. Cobro de suscripción a los vendedores.

---

## 7. Seguimiento

| Fase | Estado | Fecha de inicio | Fecha de fin |
|---|---|---|---|
| 0. Preparación del entorno | Pendiente | | |
| 1. Modelos y administración | Pendiente | | |
| 2. Mini-tienda pública | Pendiente | | |
| 3. Carrito y pedido | Pendiente | | |
| 4. Panel del vendedor | Pendiente | | |
| 5. Aviso por WhatsApp | Pendiente | | |
| 6. Envío local con Uber | Pendiente | | |
| 7. Pruebas y calidad | Pendiente | | |
| 8. Despliegue | Pendiente | | |
| 9. Documentación y primeros usuarios | Pendiente | | |

---

## 8. Decisiones pendientes

- [x] Nombre definitivo de la app: Etiqueta.
- [ ] Si Uber Direct está disponible para ti en Ciudad Juárez (se resuelve en 6.1).
- [ ] Servicio de geocodificación, si Uber requiere coordenadas (se resuelve en 6.3).
- [ ] Hosting: Railway, Render o VPS (se resuelve en la Fase 8).
