# Interfaz y seguridad

## Pantallas y recorrido

**Acceso:** usuario y contraseña; mensaje genérico si falla o la cuenta está inactiva. Token CSRF también en el login. Tras autenticar, limpiar sesión anterior y generar nuevo token de formulario.

**Catálogo:** título, módulo, curso, declaración, aportante y acciones. Filtros `q`, `modulo`, `curso_academico`, `estado_declarado`. La búsqueda de título es parcial sin distinguir mayúsculas. Los demás filtros comparan valores exactos. Mostrar cantidad resultante y un estado vacío comprensible. El botón de alta aparece solo si la cuenta dispone de upload.

**Alta:** formulario con archivo, campos y ayuda. Enseñanza/módulo deben ser coherentes aunque el usuario manipule HTML. Conservar campos válidos al volver por error, salvo el archivo, que deberá seleccionarse otra vez por comportamiento del navegador.

**Relación:** cuando hay candidatas, selector de ficha, tipo revisión/complemento y motivo. Mostrar que ambos originales se conservan y que la relación no publica ni retira documentos. No exigir seleccionar relación si no hay candidatas.

**Duplicado:** indicar copia exacta, carga existente y enlace; si la identidad difiere, explicar la discordancia. No crear otra ficha para «registrar que hubo un intento»; un registro de auditoría adicional sería una ampliación separada.

**Detalle:** metadatos completos, ID, SHA-256, fecha UTC, aportante, nombre, tamaño, formato y enlace al relacionado si existe. Diferenciar Guardado y Estado declarado. Descarga como adjunto del original.

**Errores:** distinguir acceso denegado, formulario incorrecto, archivo demasiado grande, ID inexistente y fallo de almacenamiento. No mostrar traceback. No decir «guardado» si S3 quedó en estado incierto.

## Contrato HTTP que debe mantenerse

| Ruta | Método | Permiso y comportamiento |
|---|---|---|
| `/login` | GET, POST | Formulario y autenticación con CSRF; éxito redirige, fallo 401, límite 429. |
| `/logout` | POST | CSRF; vacía sesión y redirige. |
| `/` | GET | read; catálogo y filtros. |
| `/programaciones/nueva` | GET, POST | upload; alta o validación/relación pendiente. |
| `/programaciones/<uuid>` | GET | read; detalle o 404. |
| `/programaciones/<uuid>/descargar` | GET | read; original íntegro como adjunto. |

Estados de referencia: 302 para redirecciones de navegador y alta correcta; 400 para CSRF; 403 para usuario autenticado sin permiso; 409 para copia exacta; 422 para validación o relación pendiente; 413 para límite HTTP; 503 para almacenamiento. Sin sesión en una ruta protegida, redirigir al login. No crear API REST adicional como requisito.

## Cuenta local y sesión

Estructura de cuentas: JSON indexado por login, con `password_hash`, `active` y `permissions`. Contraseñas de 12–256 caracteres; login de 3–40 letras ASCII, números, punto, guion o guion bajo. Crear cuenta por CLI con servidor detenido, dos entradas ocultas de contraseña y rechazo de nombre ya existente.

Usar scrypt de Werkzeug, no SHA-256 directo para contraseñas. SHA-256 de archivo y hash de contraseña cumplen propósitos distintos. Releer estado activo y permisos en cada petición para que desactivar una cuenta tenga efecto. No registrar contraseña en argumentos, logs o `.env`.

Cookie de sesión HttpOnly y SameSite=Lax; Secure al servir por HTTPS. Duración de referencia: dos horas con la política de sesión de Flask configurada. Explicar si la renovación es por actividad; no prometer un límite absoluto si se usa la política deslizante predeterminada. SECRET_KEY aleatoria de al menos 32 caracteres y distinta por instalación.

Limitador de referencia: diez fallos por IP dentro de cinco minutos. Es memoria de un proceso y se reinicia con él; no sustituye un sistema de identidad institucional. La información de proxy solo se acepta desde proxies de confianza configurados, no desde cualquier cabecera enviada por el cliente.

## Entradas, ficheros y presentación

- Validación rápida del navegador para campos requeridos y longitudes; réplica completa de reglas en servidor. El cliente no decide autorización, hash, centro, ruta o usuario.
- Nombres con separadores tratados como nombres de presentación; claves generadas por servidor. No aceptar rutas del disco ni destinos S3 en el POST.
- Escape Jinja y CSP; no marcar `safe` el título, observaciones, procedencia o contenido aportado. Una URL declarada como procedencia no activa una descarga remota.
- Inspección estructural con límites, sin ejecutar macros ni objetos incrustados. Los escaneos se conservan, no se leen con un modelo.
- Límite de referencia del formulario: 128 KiB de memoria para campos y máximo 30 partes multipart. Controlar también el límite total antes de procesar el archivo.
- No incluir documentos privados ni datos individualizados de alumnado en el corpus de práctica. Usar fuentes autorizadas o muestras sintéticas.

Cabeceras de referencia: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`, `Cache-Control: no-store` y CSP limitada a recursos propios, sin objetos embebidos ni scripts inline. Si se añade JavaScript de mejora, servirlo localmente y mantener la política coherente.

## Accesibilidad y tamaños de pantalla

Asociar label y control, foco visible, errores junto al campo y resumen de errores, navegación por teclado y enlaces comprensibles. La información de estado se expresa por texto, no solo por color. El hash y UUID largos deben ajustarse o permitir scroll sin romper el diseño.

Probar formularios a 360 px de ancho, escritorio y zoom 200 %. Una tabla puede tener desplazamiento horizontal controlado. Web adaptable no significa app móvil nativa ni almacenamiento offline. No usar un service worker que cachee documentos autenticados sin necesidad explícita.

## Secretos y permisos AWS

Credenciales AWS solo en servidor, a través de perfil o entorno privado. Nunca en HTML, JavaScript, notebook guardado con valores, ejemplos públicos o fichas S3. Las cuentas del gestor no son usuarios IAM.

No imprimir valores de entorno para diagnosticar. Mostrar nombres de variables pendientes, códigos públicos y acciones sugeridas. Las rutas de excepción tampoco deben filtrar cadenas de conexión, tokens ni peticiones firmadas.

La aplicación del piloto comparte un catálogo para el centro configurado entre usuarios con read. No afirmar aislamiento por autor, multitenencia o permisos por documento que no se han implementado. Si se solicita ese aislamiento, diseñarlo en casos de uso y repositorios, no solo filtrando botones.

## Límites y refuerzos

El repositorio aporta controles de piloto, no una certificación de seguridad de producción. Exponerlo a internet requiere una decisión de despliegue y controles adicionales. No introducir a la vez SSO, antivirus, API pública o multiusuario institucional sin nueva petición.

En una reconstrucción, reforzar la validación de fichas leídas y la comprobación exacta de claves/tamaños de descarga. Es una mejora concreta del adaptador que conserva el contrato, no una afirmación sobre protección ya presente en la base examinada.
