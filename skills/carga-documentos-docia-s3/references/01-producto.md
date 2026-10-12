# Producto y reglas de negocio

## Qué aplicación se debe generar

Un gestor de cargas de programaciones didácticas para un centro y un corpus pequeño de aula. Se ejecuta en el ordenador o servidor del aula; S3 conserva objetos, no ejecuta Python. El navegador habla con Flask/Waitress y el servidor accede a S3 mediante sus credenciales privadas.

El catálogo muestra las cargas conservadas, incluidos borradores y revisiones anteriores. No presenta una única versión oficial vigente. Relacionar dos cargas documenta una decisión del aportante; no es una revisión institucional.

Un lector puede consultar y descargar. Un usuario con `upload` puede incorporar. El script actual de creación concede ambos permisos; una cuenta de lectura se configura localmente por un administrador. No existe alta pública, recuperación de contraseña por correo ni SSO en el mínimo. No enviar comunicaciones como efecto lateral.

## Requisitos funcionales

| ID | Funcionalidad | Criterio |
|---|---|---|
| RF01 | Sesión local | Credenciales válidas de cuenta activa abren el catálogo; el resto no revela si existe la cuenta. |
| RF02 | Alta autenticada | Requiere permiso upload y CSRF, además de metadatos y archivo. |
| RF03 | Catálogo cerrado | Enseñanza, módulo y curso proceden de config/catalogo.json y se validan en servidor. |
| RF04 | Archivos admitidos | PDF, DOCX y TXT UTF-8 válidos dentro del límite; sin conversión del original. |
| RF05 | Hash | SHA-256 del contenido recibido, longitud en bytes y MIME validado guardados en ficha. |
| RF06 | Copia exacta | HTTP 409, enlace a carga existente y ausencia de nueva ficha/original. |
| RF07 | Posible revisión | Igual identidad con bytes diferentes requiere relación y motivo antes de guardar. |
| RF08 | Conservación | La nueva relación no modifica ni elimina documentos anteriores. |
| RF09 | Catálogo | Filtros por título, módulo, curso y estado declarado; lista ordenada por fecha de incorporación descendente. |
| RF10 | Detalle | Metadatos, original, hash, usuario, fecha y relación consultables. |
| RF11 | Descarga | Autenticación, permiso read, clave válida y hash verificado antes de servir adjunto. |
| RF12 | Fallos S3 | Error visible sin anuncio falso de éxito, con orientación de reintento cuando corresponda. |
| RF13 | Desactivar cuenta | El siguiente acceso protegido comprueba cuenta activa y permisos actuales. |
| RF14 | Configuración segura | Secretos externos al código y sin cuenta/contraseña universal por defecto. |
| RF15 | Preparación del bucket | Cuaderno separado de la web, con credenciales ocultas y verificación de privacidad. |

## Campos y límites del formulario

| Campo | Validación |
|---|---|
| titulo | 5–150 caracteres tras quitar espacios exteriores. |
| ensenanza | Código existente en catálogo. |
| modulo | Código que pertenece a la enseñanza elegida. |
| curso_academico | Valor incluido expresamente en catálogo; no basta un patrón de fecha. |
| estado_declarado | Solo `borrador` o `final`. No aceptar `aprobado` como alias. |
| procedencia | Texto de 3–200 caracteres; departamento, responsable o URL de referencia. |
| observaciones | Opcional, máximo 2000 caracteres. |
| centro | Inyectado desde configuración, nunca aceptado libremente del formulario. |
| archivo | Obligatorio, bytes no vacíos, extensión y contenido válidos. |

Catálogo de referencia: enseñanza IABD con SBD, BDA y PIA; cursos 2025-2026, 2026-2027 y 2027-2028. Son datos configurables del piloto. No inventar una validación curricular oficial ni inferir que todo curso futuro está autorizado.

Identidad lógica: `(centro, ensenanza, modulo, curso_academico)`. Es un criterio de comparación, no un identificador UUID compartido por toda una familia de versiones. Cada alta válida tiene su propio `id` y su propio original. No añadir un modelo complejo de documento/version/extracción de la skill MongoDB sin una ampliación pedida.

## Validación técnica del archivo

Límite inicial: 20 × 1024 × 1024 bytes. La variable heredada se llama `MAX_FILE_MB`, pero la medida efectiva es MiB. La petición completa permite 1 MiB adicional para el formulario. El nombre se reduce a su componente final normalizando separadores; máximo 200 caracteres y sin controles. Comparar extensión en minúsculas.

**PDF:** comprobar cabecera `%PDF-`, apertura estructural con pypdf, ausencia de cifrado y al menos una página. Recorrer páginas para detectar errores de estructura. No exigir texto ni ejecutar OCR: una página escaneada o una página en blanco válida puede guardarse. Legibilidad estructural no garantiza contenido útil para RAG.

**DOCX:** paquete ZIP legible con `word/document.xml` y `[Content_Types].xml`, integridad y apertura con python-docx. Máximo 2000 entradas y 80 MiB descomprimidos como límites del piloto. Rechazar `vbaProject`, formatos macroEnabled y `word/embeddings/`. No admitir DOCM, DOC heredado ni un ZIP renombrado. Las imágenes normales dentro del DOCX no equivalen por sí solas a objetos ejecutables incrustados.

**TXT:** decodificar como UTF-8 con BOM opcional (`utf-8-sig`) para validar; exigir texto no vacío tras trim. Rechazar controles salvo tabulación, retorno de carro y salto de línea. Guardar los bytes originales, incluido BOM si lo tenía. No convertir automáticamente Latin-1 a UTF-8 ni cambiar finales de línea.

No confiar solo en `Content-Type` del navegador o en la extensión. La inspección no es antivirus; no afirmar que detecta todo contenido dañino. En una nueva implementación, mantener límites de lectura y descompresión sin ejecutar contenido activo ni descargar vínculos externos.

## Secuencia de alta

1. Verificar sesión, permiso, CSRF y límites HTTP.
2. Validar metadatos y archivo; calcular SHA-256.
3. Dentro del bloqueo compartido de altas, leer todas las fichas del prefijo usando paginación S3.
4. Si alguna tiene el mismo hash, no crear nada y devolver copia exacta. Si cambia la identidad lógica, añadir advertencia de discrepancia.
5. Si los bytes son distintos, buscar fichas con la misma identidad lógica.
6. Si existen candidatas y falta relación, volver al formulario con candidatas y HTTP 422. El navegador obliga a seleccionar otra vez el archivo.
7. Validar que el destino está entre las candidatas, tipo `revision` o `complemento`, y motivo de 5–500 caracteres.
8. Generar UUID, fecha UTC y ficha. Guardar original y ficha mediante el puerto de persistencia.
9. Solo tras confirmación, redirigir al detalle con mensaje de éxito técnico.

Si no existen candidatas, `relacion=null`. No persistir una relación arbitraria enviada por el cliente. La versión base ignora campos de relación cuando no hay candidatas; una reconstrucción puede devolver un error más explícito, siempre que no acepte un vínculo ilegítimo y lo documente.

## Casos que no se deben confundir

| Situación | Tratamiento |
|---|---|
| Mismo archivo, otro nombre | Copia exacta. |
| Mismo archivo, otro curso declarado | Copia exacta con metadatos discordantes; pedir revisar datos. |
| Mismo nombre, bytes distintos | Comparar identidad; el nombre no determina duplicado. |
| Módulo y curso iguales, contenido diferente | Solicitar revisión/complemento y motivo. |
| Curso distinto y bytes distintos | Nueva carga independiente salvo futura regla explícita. |
| Mismo texto en PDF y DOCX diferentes | No se detecta equivalencia semántica en esta versión. |
| Usuario declara final | Se almacena la declaración, sin aprobar ni publicar. |
| Archivo nuevo relacionado | Ambos continúan visibles; no hay retirada automática. |

## Límites funcionales deliberados

No existe API pública JSON de ingesta, edición de fichas, flujo de aprobación/rechazo, eliminación ordinaria, historial de auditoría completo, OCR, extracción de texto, hash semántico, chunks, embeddings o base vectorial. No convertir estos límites en funcionalidades inventadas del repositorio. Son posibles evoluciones que se presupuestan y prueban por separado.
