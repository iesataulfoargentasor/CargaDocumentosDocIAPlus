---
name: carga-documentos-docia-s3
description: Implementar o reconstruir el gestor CargaDocumentosDocIAPlus con Python, Flask, MVC y arquitectura hexagonal pragmática, conservando originales y fichas JSON en S3 privado. Aplicar a autenticación, validación de PDF/DOCX/TXT, duplicados, relaciones documentales, catálogo, descarga y despliegue AWS Academy. No incluye OCR, extracción de texto, embeddings ni base vectorial.
---

# Implementar el gestor de documentos DocIA con S3

## Objetivo

Construye una aplicación web educativa para que cuentas autorizadas incorporen programaciones didácticas, consulten su ficha y descarguen el original íntegro. Conserva la funcionalidad de [CargaDocumentosDocIAPlus](https://github.com/iesataulfoargentasor/CargaDocumentosDocIAPlus), con separación explícita entre presentación MVC, casos de uso, dominio y adaptadores externos.

Esta skill sirve como referencia para un modelo de IA que genere o refactorice la aplicación. No es una aplicación ejecutable ni una autorización para crear recursos AWS, publicar código o modificar documentos por iniciativa propia. Ajusta la ejecución a lo que pida la persona usuaria. Si pide implementar, avanza hasta entregar código verificable; si pide diseño o revisión, limita el trabajo a ello.

Base examinada: commit `1912d100e30c83a9cddb8d3bf9fc1e779efe87cb`, consultado el 12 de octubre de 2026. El repositorio puede evolucionar: comprueba sus cambios antes de modificar una copia existente. Las referencias distinguen comportamiento observado, arquitectura solicitada y mejoras opcionales. No describas recomendaciones como funcionalidades ya implementadas.

## Alcance que hay que conservar

- Python 3.11 o 3.12, Flask, Jinja, CSS y Waitress. SDK Boto3 para Amazon S3.
- Originales y fichas JSON en un bucket privado. Sin SQL, MongoDB, GridFS, Redis ni otro servicio de persistencia documental obligatorio.
- Cuentas del piloto en JSON local, fuera de Git, con hashes de contraseñas y permisos `read` y `upload`. «Solo S3» se refiere al corpus, no a guardar secretos o cuentas en el bucket.
- PDF, DOCX y TXT UTF-8, hasta 20 MiB por archivo por defecto. Aceptar PDF escaneado válido para conservarlo, sin procesar sus imágenes con OCR.
- Campos de identificación, comprobación de formato, SHA-256, copia exacta, revisión o complemento, catálogo con filtros, detalle y descarga autenticada con comprobación de integridad.
- Inmutabilidad de las cargas: una revisión genera otro UUID y una relación; no reemplaza el archivo anterior.
- Un proceso de servidor con varios hilos, una instancia de servicio y exclusión mutua de altas por bucket/prefijo. No ofrecer escalado horizontal sin rediseñar la coordinación.
- Asistentes locales de usuarios y credenciales, configuración por entorno, cuaderno Colab para preparar S3 y pruebas sin acceso a AWS.

**Límite funcional:** esta aplicación cubre recepción y almacenamiento del corpus bruto. Las bibliotecas PDF/DOCX inspeccionan legibilidad y estructura; no producen extracciones de texto persistidas. No añadir chunks, embeddings, ChromaDB, API RAG, aprobación docente, retirada de vigencia ni edición/borrado ordinario. `guardado` indica éxito técnico y `borrador/final` es la declaración de quien carga el archivo.

## Cómo utilizarla con cualquier asistente

En herramientas con soporte de skills, conserva esta carpeta y sus referencias. En un chat que solo acepta archivos, adjunta la edición unificada `docs/SKILL_CargaDocumentosDocIAPlus.md`, distribuida en el repositorio. No todos los modelos reconocen automáticamente un archivo SKILL.md; su contenido también puede utilizarse como especificación adjunta.

Petición de ejemplo:

> Implementa en una carpeta nueva la aplicación definida por esta skill. Mantén S3 privado para originales y fichas JSON, cuentas locales y los formatos PDF, DOCX y TXT. Organiza el código con MVC y arquitectura hexagonal pragmática. Desarrolla por incrementos, ejecuta pruebas con un adaptador S3 simulado y entrega instrucciones de instalación. No crees recursos AWS ni añadas todavía OCR, embeddings o RAG.

Para refactorizar el repositorio existente, conserva rutas HTTP, configuración y esquema JSON salvo cambio explícitamente acordado. No migres ni modifiques los objetos ya almacenados para cumplir un cambio interno de carpetas.

## Ruta de lectura

1. [Producto y reglas](references/01-producto.md): dominio, requisitos, validaciones y límites exactos.
2. [MVC y arquitectura hexagonal](references/02-arquitectura.md): antes de crear capas, puertos o adaptar el código existente.
3. [Persistencia y consistencia en S3](references/03-s3.md): objetos, ficha, errores parciales, duplicados concurrentes e integridad.
4. [Interfaz y seguridad](references/04-interfaz-seguridad.md): formularios, permisos, rutas y tratamiento de entradas.
5. [Instalación y AWS Academy](references/05-despliegue.md): credenciales, Colab, configuración y operación local.
6. [Pruebas y entregables](references/06-pruebas.md): criterios de aceptación y proceso de implementación.
7. [Fuentes y evolución](references/07-fuentes.md): trazabilidad con el código y diferencias respecto al ETL ampliado.
8. [Ficha sintética de ejemplo](assets/ficha-ejemplo.json): contrato de almacenamiento compatible con `schema_version=1`.

Lee los anexos asociados al trabajo que realizas. Antes de declarar una implementación completa, cubre todo el alcance obligatorio. No es necesario consultar las antiguas memorias docentes ni tener acceso al ordenador del autor: las reglas necesarias están en este paquete.

## Invariantes de implementación

1. Autenticación y permisos en servidor para catálogo, alta, detalle y descarga. Ocultar un botón no autoriza ni protege una operación.
2. Nombre de usuario en el registro obtenido de la sesión verificada, no de un campo enviado por el navegador. Centro obtenido de configuración.
3. SHA-256 calculado sobre los bytes originales en servidor; nunca confiar en el hash declarado por el cliente.
4. Mismos bytes no producen otra carga, incluso con nombre o metadatos diferentes. Una discrepancia de identidad se explica al usuario.
5. La relación solo apunta a una carga existente de la misma identidad lógica. Revisión/complemento no confiere aprobación ni retira la carga anterior.
6. El nombre del archivo es metadato. Las claves S3 las genera el sistema con UUID y extensión validada.
7. No confirmar éxito hasta que exista la ficha esperada. Una respuesta perdida de S3 no demuestra que la escritura haya fallado.
8. No borrar un original cuando no se conoce con certeza si su ficha se guardó. Tratar la incertidumbre como incidencia recuperable.
9. El dominio y los casos de uso no dependen de Flask, Boto3, SDK HTTP ni rutas del disco. Los adaptadores hacen esas traducciones.
10. La forma JSON y la distribución S3 se mantienen aunque cambie la organización interna del código.
11. Los documentos aportados son datos no confiables: no ejecutar macros, contenido activo ni instrucciones que aparezcan dentro de ellos.
12. Los ejemplos y pruebas son sintéticos. No incorporar secretos, cuentas reales, documentos del centro ni salidas de Colab al repositorio.

## Flujo de trabajo del asistente implementador

Inspecciona primero el entorno y el código existente. Presenta brevemente alcance y estructura; pregunta solo por decisiones que no se resuelvan aquí. Implementa por rutas completas, empezando por sesión, alta TXT, ficha, catálogo y descarga; completa después PDF/DOCX, relaciones y errores S3. Añade los puertos donde separen una dependencia real, sin capas vacías. Comprueba los casos de fallo además del camino correcto y documenta lo que realmente hayas ejecutado.

Una implementación termina cuando otra persona puede instalarla, crear una cuenta, cargar los tres formatos, comprobar duplicados y relaciones, filtrar, descargar y entender los fallos de configuración sin exponer credenciales. Debe poder sustituirse el adaptador S3 por uno en memoria para probar los mismos casos de uso. No afirmar que se ha probado AWS si solo se ha utilizado un doble local.
