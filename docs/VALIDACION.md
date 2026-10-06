# Verificación de esta entrega

- Entorno: Python 3.12; dependencias exactas en `requirements-lock.txt`.
- `python -m pytest -q`: **18 pruebas superadas**.
- `python -m compileall -q app scripts run.py`: sin errores de sintaxis.
- Las pruebas recorren los formularios, catálogo, detalle y descarga mediante el cliente HTTP de Flask y un doble de S3 en memoria.
- Se verifica el rechazo de duplicados, la conservación de originales al relacionar revisiones, acceso/CSRF/permisos, paginación, validación PDF/DOCX/TXT, límites, escape HTML e integridad.
- Se simulan fallos de ficha, credenciales caducadas y pérdida de respuesta tras una escritura confirmada. No se han cargado documentos ni creado recursos en AWS.
- Pendiente de configuración del centro: prueba real contra su bucket y comprobación visual en sus navegadores.

## Cuaderno Colab para S3

- Validación de estructura JSON, celdas sin salidas y compilación del código Python.
- 6 pruebas específicas del cuaderno: región us-east-1, otras regiones, nombres, acceso denegado, creación/reutilización, controles privados y negativa a cambiar cifrado KMS.
- Entradas de credenciales ocultas y ausencia de exportación de secretos verificadas en el código.
- No se ha ejecutado el cuaderno en Colab ni contra una cuenta AWS real.

## Arranque local

- Bucket y región indicados por el usuario configurados en el `.env` privado.
- Servidor Waitress iniciado en 127.0.0.1:5050.
- Inicio de sesión real comprobado por HTTP (302) y formulario autenticado (200).
- Pantalla de acceso comprobada en el navegador integrado.
- Suite actual: 24 pruebas superadas.
- Validación real de catálogo y subida a S3 completada tras configurar las credenciales temporales.

## Prueba integrada con el bucket real

- Servidor reiniciado con las credenciales temporales del laboratorio.
- Catálogo S3 accesible desde la aplicación (HTTP 200).
- TXT sintético subido mediante el formulario HTTP; original y ficha confirmados en S3.
- Descarga idéntica al contenido enviado.
- Segunda carga rechazada como duplicado exacto (HTTP 409).
- Los dos objetos temporales de esa prueba fueron retirados; no se modificaron otros documentos.
- Catálogo visible y operativo en el navegador integrado.
