# Instalación y operación con AWS Academy

## Componentes y ubicación

La web Flask/Waitress se ejecuta en el ordenador o servidor del aula. El bucket privado aloja originales y fichas. El cuaderno Colab prepara/comprueba el bucket; no despliega Flask. La autenticación del gestor y el acceso IAM a AWS son mecanismos diferentes.

Dependencias de ejecución de la base: Flask, boto3, python-dotenv, pypdf, python-docx y waitress; pytest para desarrollo. Mantener los rangos y el fichero de versiones probadas coherentes. No instalar Tesseract, modelos, MongoDB ni ChromaDB para reproducir este gestor.

Usar Python 3.11 o 3.12. La versión Python predeterminada de Ubuntu 22.04 no tiene por qué cumplir ese requisito: la guía de una nueva implementación debe indicar cómo se obtiene una versión admitida en el entorno del centro, sin reemplazar el Python del sistema ni inventar disponibilidad en los repositorios del sistema operativo.

## Instalación local que debe documentarse y comprobarse

Ejemplo desde la raíz del repositorio, con Python admitido ya instalado:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

En Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

La variante PowerShell usa el intérprete directamente y no exige cambiar políticas globales de ejecución para activar el entorno. En macOS/Linux usar el intérprete disponible 3.11/3.12; estos comandos no instalan Python. Si la aplicación generada cambia su empaquetado, actualizar todos los comandos y probarlos.

Crear una SECRET_KEY aleatoria local, por ejemplo con `secrets.token_hex(32)`, y guardarla privadamente. El marcador REEMPLAZAR debe provocar error de configuración, no convertirse en una clave de producción. No publicar la salida de generación.

## Variables de configuración

| Variable | Regla |
|---|---|
| SECRET_KEY | Secreto local aleatorio, al menos 32 caracteres, sin valor universal. |
| S3_BUCKET | Nombre sin `s3://`; no incluir un bucket real del docente en ejemplos. |
| AWS_DEFAULT_REGION | Región del bucket y del laboratorio, us-east-1 como valor inicial configurable. |
| S3_PREFIX | Prefijo no vacío, inicialmente programaciones; quitar barras inicial/final. |
| AWS_PROFILE | Alternativa de perfil local; no mezclarla con credenciales directas. |
| AWS_ACCESS_KEY_ID | Primera credencial temporal del laboratorio. |
| AWS_SECRET_ACCESS_KEY | Segunda credencial temporal. |
| AWS_SESSION_TOKEN | Tercera credencial temporal; necesaria para la sesión Academy. |
| CENTRO | Centro que el servidor añade a las fichas. |
| MAX_FILE_MB | Límite de archivo; 20 por defecto, calculado en MiB. |
| HOST, PORT | 127.0.0.1 y 5000 por defecto; puerto configurable para coexistir con otras aplicaciones. |
| COOKIE_SECURE | true con HTTPS; false en la demostración local HTTP. |

Bucket, región y prefijo no son las tres credenciales. Las credenciales autorizan el acceso y caducan; la configuración indica dónde almacenar. No pedir que se peguen secretos en una conversación con el asistente.

En macOS/Linux, proteger `.env` y cuentas con permisos privados. En Windows, documentar protección mediante permisos de archivos de usuario, sin afirmar que chmod impone las mismas ACL. No guardar secretos en argumentos de shell ni en ficheros `.command`.

## Asistente de credenciales

Reproducir `scripts/configurar_aws.py` con entradas ocultas independientes para Access Key ID, Secret Access Key y Session Token. Si no se garantiza entrada oculta o faltan valores, cancelar sin escribir. No mostrar los valores al terminar.

Antes de guardar, validar la identidad con STS, comprobar acceso al bucket de esa cuenta con `ExpectedBucketOwner` y probar listado del prefijo de fichas. No subir archivos como parte de este diagnóstico. Si falla, conservar configuración anterior y explicar red, sesión caducada o permisos.

Tras validación, escribir `.env` de forma atómica mediante temporal privado, quitar AWS_PROFILE si se optó por credenciales directas y conservar las demás opciones. Reiniciar la aplicación: un cliente Boto3 ya creado no se actualiza solo al editar el fichero. Las tres credenciales deben proceder de la misma sesión vigente.

Este asistente comprueba acceso de lectura/listado; no acredita por sí solo todos los permisos de escritura ni la privacidad completa del bucket. Esas comprobaciones pertenecen al cuaderno y a una prueba de alta específica.

## Usuarios y servidor

Con el servidor detenido:

```bash
python scripts/crear_usuario.py profesor01
python run.py
```

En Windows, utilizar `.venv\Scripts\python.exe` si el entorno no está activado. El script pide y confirma contraseña con entrada oculta, guarda hash scrypt en `instance/users.json` y no envía esa cuenta a AWS. Rechaza sobrescribir una cuenta existente.

Waitress arranca sin debug, en un proceso con cuatro hilos de referencia. Todos comparten el mismo servicio y bloqueo. No iniciar una segunda copia contra el mismo bucket/prefijo. Los atajos macOS solo cambian a la carpeta y ejecutan los scripts del entorno; no contienen credenciales pegadas al final del archivo.

Para compartir en la red del centro se necesita configurar interfaz accesible, cortafuegos y HTTPS. Mantener el bucket privado y las credenciales en el servidor. S3 no debe convertirse en alojamiento estático de esta aplicación Python.

## Cuaderno Colab como parte de la entrega

Debe ser un `.ipynb` válido, sin valores secretos, salidas ni números de ejecución al publicarlo. Mantener estos pasos:

1. Instalar Boto3 en el entorno temporal de Colab, sin acceder a la cuenta aún.
2. Definir funciones de nombre, región, creación/reutilización, verificación y mensajes de error seguros.
3. Pedir las tres credenciales con getpass y validar STS. Guardarlas solo en memoria del runtime de Colab; campo oculto no significa ejecución en el ordenador local.
4. Solicitar región y bucket dedicado; proponer nombre aleatorio para evitar colisiones. No fijar el nombre privado del docente.
5. Crear/reutilizar únicamente después de verificar propiedad y región. En us-east-1 no enviar LocationConstraint; en otras regiones configurarlo adecuadamente.
6. Verificar bloqueo completo de acceso público, BucketOwnerEnforced y cifrado SSE-S3/AES256. Si un bucket existente usa KMS, detenerse sin degradar su configuración.
7. Probar un TXT sintético bajo una clave aleatoria de `_pruebas/`, leerlo y retirar exclusivamente ese objeto. No crear fichas falsas ni borrar documentos del corpus.
8. Mostrar solo bucket/región/prefijo para copiar al entorno local, distinguiendo preparación del bucket y resultado de prueba de objetos.
9. Retirar referencias de sesión e indicar desconectar/eliminar runtime. No prometer borrado seguro de memoria por asignar None.

Un 403 no significa que el bucket no exista y no autoriza a crearlo o modificarlo. Un fallo a mitad puede haber creado el bucket: reintentar con el mismo nombre tras diagnóstico, sin borrarlo automáticamente. No imprimir trazas de peticiones firmadas.

No activar alojamiento estático, CORS público, ACL públicas ni políticas de acceso anónimo. No habilitar versionado como si fuera requisito heredado: la base no lo activa. Si se añade posteriormente, documentar sus costes y sus efectos en borrado/recuperación.

## Permisos de ejecución y preparación

La aplicación necesita `s3:ListBucket` restringido al prefijo y `s3:GetObject`/`s3:PutObject` para su corpus. El permiso de eliminar originales se utiliza para compensar una carga incompleta, no para borrado ordinario de documentos. La política orientativa del repositorio separa esos permisos.

Crear/configurar el bucket requiere acciones adicionales; no presentar `docs/iam-policy.example.json` como política suficiente para todo el cuaderno. AWS Academy puede restringir incluso consultas de configuración: informar la limitación, sin intentar ampliar IAM desde la aplicación. La privacidad no se confirma si las comprobaciones fallan.

## Diagnóstico y conservación

| Síntoma | Acción indicada |
|---|---|
| ExpiredToken | Renovar las tres credenciales y reiniciar. |
| AccessDenied | Revisar permiso y prefijo de la operación concreta. |
| Catálogo vacío | Distinguir listado correcto sin fichas de error de acceso. |
| No hay carpetas en S3 | Se crean claves al subir el primer documento. |
| Original existe sin ficha | Incidencia parcial; no es un documento confirmado del catálogo. |
| Descarga no coincide con hash | Bloquear entrega e inspeccionar objeto/ficha; no recalcular la ficha para ocultar el cambio. |
| Otro proceso ya usa el puerto | Elegir puerto o detener esa instancia; no lanzar copias escritoras al mismo prefijo. |

La conservación de AWS Academy depende del laboratorio. La guía debe explicar cómo respaldar originales y fichas juntos a un destino autorizado, verificar hashes y recuperar un corpus en otro prefijo de prueba. Esto es una pauta operativa para implementar/documentar; el repositorio base no aporta un sistema automático de backups. No confundir la persistencia del bucket con una copia independiente.
