# Pruebas y entregables

## Implementación por incrementos

1. Configuración, modelos y puertos; autenticación local y permisos.
2. Ruta completa con TXT: formulario, validación, alta mediante repositorio, catálogo y descarga.
3. Validación PDF/DOCX, filtros, duplicados y relaciones sin sobrescrituras.
4. Fallos S3, respuesta perdida, integridad, límites, CSRF y accesibilidad.
5. Asistentes de usuarios/AWS, Colab, pruebas de configuración y documentación.
6. Verificación final de equivalencia funcional y separación MVC/hexagonal.

Cada incremento debe producir comportamiento verificable. El alcance no termina al mostrar una interfaz que no persiste datos. Una refactorización debe conservar los contratos existentes y actualizar sus imports/tests a medida que cambia la organización.

## Estrategia de pruebas

Usar un repositorio en memoria para dominio/casos de uso y un cliente S3 simulado para probar el adaptador con errores SDK, paginación y escrituras condicionales. Son niveles diferentes: un FakeRepository que siempre guarda no prueba que S3Repository maneje una respuesta perdida.

Las pruebas deben aislar entorno, archivo de usuarios y configuración. No cargar `.env` real ni intentar resolver credenciales del equipo. Deshabilitar acceso al servicio de metadatos AWS en el entorno de pruebas y comprobar que las rutas no construyen un cliente real cuando se inyecta el doble. En la base, la fábrica llama a load_dotenv antes de aplicar test_config; al reconstruir, mejorar ese aislamiento de manera explícita.

Crear fixtures sintéticas pequeñas: TXT UTF-8 con/sin BOM, PDF digital, PDF con página de imagen, PDF cifrado y corrupto, DOCX simple y paquete con señales de macros/objetos prohibidos. La prueba original usa una página PDF en blanco para demostrar que no se exige texto; eso no demuestra OCR ni lectura de un escaneo. Añadir un PDF de imagen real como prueba de admisión estructural si se declara ese caso cubierto.

## Matriz de aceptación de la implementación futura

| ID | Caso | Resultado esperado |
|---|---|---|
| P01 | Abrir catálogo/alta/descarga sin sesión | Redirección a login; ningún acceso documental exitoso. |
| P02 | Contraseña incorrecta o cuenta inactiva | Mensaje genérico, no sesión válida. |
| P03 | POST sin CSRF o con token incorrecto | HTTP 400 y ausencia de escritura. |
| P04 | Lector intenta subir por URL/POST | HTTP 403, aunque modifique HTML. |
| P05 | Desactivar usuario con sesión abierta | Próxima petición protegida deja de autorizarlo. |
| P06 | Alta válida TXT | Dos objetos, ficha con hash correcto, 302 a detalle. |
| P07 | PDF digital y PDF de imagen | Se conservan sin OCR ni requisito de texto. |
| P08 | DOCX válido | Conserva bytes, MIME y ficha. |
| P09 | TXT UTF-8 con BOM | Valida y descarga bytes idénticos, sin perder BOM. |
| P10 | Archivo vacío, extensión falsa o controles TXT | HTTP 422, ningún objeto creado. |
| P11 | PDF cifrado/corrupto | Rechazo controlado, sin éxito parcial anunciado. |
| P12 | DOCM/macros/objetos DOCX | Rechazo con mensaje, nada ejecutado. |
| P13 | DOCX excede límites descomprimidos | Rechazo controlado antes de procesamiento abusivo. |
| P14 | Límite de archivo y límite HTTP | Respuestas diferenciadas 422/413 según dónde se detecta. |
| P15 | Módulo no pertenece a enseñanza | HTTP 422 aunque ambos códigos existan por separado. |
| P16 | Curso no autorizado o estado aprobado | HTTP 422; solo catálogo y borrador/final. |
| P17 | Metadatos fuera de longitud | Errores por campo y valores válidos conservados. |
| P18 | Mismos bytes con otro nombre | HTTP 409, no crea segundo original/ficha. |
| P19 | Mismos bytes con otro curso/módulo | Duplicado con discordancia explicada, no reetiquetado silencioso. |
| P20 | Bytes distintos, identidad coincidente | Pide relación, mantiene carga anterior intacta. |
| P21 | Revisión/complemento válida | Nuevo UUID, relación correcta, ambos originales descargables. |
| P22 | Relación inventada o de otra identidad | Rechazo; no vínculo arbitrario. |
| P23 | Motivo de relación fuera de longitud | HTTP 422. |
| P24 | Dos altas idénticas en hilos del proceso | Solo una se guarda, la otra detecta duplicado. |
| P25 | Listado S3 con varias páginas | Se leen todas las fichas antes de filtrar/deduplicar. |
| P26 | Filtro título, módulo, curso y declaración | Resultados y recuentos coherentes; orden descendente. |
| P27 | ID no UUID o ficha inexistente | 404; no lectura de clave arbitraria. |
| P28 | Título/observaciones con HTML | Escape correcto, sin ejecución de scripts. |
| P29 | Original alterado | Descarga bloqueada por hash. |
| P30 | Clave de ficha fuera de prefijo/UUID | Error de integridad, no descarga de otro objeto. |
| P31 | Fallo de listado/credenciales | 503, no catálogo vacío fingido ni alta ciega. |
| P32 | Original guardado y ficha denegada | Sin mensaje de éxito; limpieza solo del original de la operación si se confirma ausencia de ficha. |
| P33 | Respuesta de ficha perdida tras guardarse | Se comprueba la ficha y conserva original; no destrucción por asumir fallo. |
| P34 | Verificación de ficha imposible | Resultado incierto visible y original conservado. |
| P35 | Escritura condicional conflictiva | No sobrescribe ni elimina objeto preexistente. |
| P36 | Ficha JSON corrupta o demasiado grande | Error explícito; no omisión silenciosa que permita duplicados. |
| P37 | Dos adaptadores de repositorio | Mismos casos de uso operan con memoria y S3 simulado. |
| P38 | Importar dominio | No importa Flask, Boto3 ni parsers; tests puros sin servicios. |
| P39 | Crear cuenta existente o contraseña inválida | No sobrescribe, no almacena contraseña en claro. |
| P40 | Asistente AWS sin entrada oculta o sesión inválida | Cancela sin cambiar configuración privada. |
| P41 | Cuaderno con secreto/salidas persistidas | Validación de publicación falla. |
| P42 | Bucket devuelve 403 | No se crea ni modifica como si no existiera. |
| P43 | Región distinta y us-east-1 | Parámetros correctos y rechazo de región incompatible con bucket existente. |
| P44 | Bucket usa KMS | No se cambia silenciosamente a SSE-S3. |
| P45 | Prueba de objetos Colab | Solo su clave aleatoria se retira; nunca prefijo ni bucket. |
| P46 | Pantallas móvil/teclado/zoom | Controles utilizables y mensajes completos. |

Estos son criterios para quien implemente la skill, no resultados de pruebas ejecutadas por escribir esta documentación. Si se mantiene el proyecto original, adaptar primero la suite existente y completar las comprobaciones nuevas que se hayan implementado. No inventar una cifra de tests superados.

## Comandos y evidencias

En la aplicación de referencia:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m compileall -q app scripts run.py
```

Si se cambia empaquetado, actualizar estos comandos. Registrar versión Python, dependencias, fecha y resultados, distinguiendo pruebas locales con dobles, revisión visual y prueba real AWS. `docs/VALIDACION.md` de la base contiene resultados históricos en varias etapas; no copiarlos como si los hubiera producido una nueva implementación.

Una prueba real AWS requiere autorización y configuración del usuario. Preparar un objeto sintético y un prefijo de prueba, mostrar qué se creará y qué limpieza corresponde; nunca utilizar como fixture un documento real del centro. La validación de documentación por sí sola no necesita ninguna llamada AWS.

## Entregables esperados del asistente implementador

- Aplicación funcional, estructura MVC/hexagonal y adaptadores sustituibles.
- Catálogo configurable, esquema JSON compatible, configuración de ejemplo y scripts auxiliares.
- Cuaderno Colab limpio, política IAM orientativa diferenciada de permisos de preparación y atajos locales cuando proceda.
- Pruebas de reglas, HTTP y errores S3, fixtures sintéticas y evidencia de ejecución.
- README con instalación, credenciales ocultas, creación de usuarios, arranque, límites y relación futura con RAG.
- Explicación de cambios y límites, especialmente un proceso escritor, coste de leer fichas y ausencia de transacción entre objetos.

No incluir secretos, usuarios reales, `.venv`, cachés, programas originales del centro ni recursos del laboratorio en el paquete público. No elegir licencia en nombre del titular si no la ha pedido.
