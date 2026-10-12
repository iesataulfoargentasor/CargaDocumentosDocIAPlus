# Fuentes y evolución

## Base verificable

Repositorio: [iesataulfoargentasor/CargaDocumentosDocIAPlus](https://github.com/iesataulfoargentasor/CargaDocumentosDocIAPlus).

Commit de referencia: [1912d100e30c83a9cddb8d3bf9fc1e779efe87cb](https://github.com/iesataulfoargentasor/CargaDocumentosDocIAPlus/tree/1912d100e30c83a9cddb8d3bf9fc1e779efe87cb). Revisión de documentación y código realizada el 12 de octubre de 2026.

| Archivo en la base | Información utilizada |
|---|---|
| README.md | Propósito, alcance S3, arquitectura existente, despliegue y límites. |
| app/models/document.py | Esquema de ficha, identidad de cuatro campos, UUID y claves. |
| app/services/document_service.py | Orden de duplicados/relaciones y Lock de proceso. |
| app/services/validation.py | Campos, longitudes, formatos y límites de contenido. |
| app/repositories/s3_repository.py | Paginación, fichas, escrituras condicionales, fallo parcial e integridad. |
| app/controllers/ | Rutas, filtros, redirecciones y códigos HTTP. |
| app/models/user.py y app/security.py | Cuentas, permisos, sesión, CSRF y limitador local. |
| app/__init__.py y run.py | Fábrica, composición, configuración, cabeceras y Waitress. |
| app/templates/ | Formularios, mensajes, duplicado, ficha y catálogo. |
| scripts/ | Creación local de cuentas y validación de credenciales AWS. |
| Crear_bucket_S3_AWS_Academy.ipynb | Preparación separada del bucket y prueba de objetos. |
| tests/ y docs/VALIDACION.md | Casos implementados y evidencia histórica, no resultados de esta skill. |
| .env.example, config/catalogo.json y docs/iam-policy.example.json | Configuración sin secretos, catálogo y permisos orientativos. |

Se usaron archivos versionados; las credenciales del equipo, las cuentas locales y el corpus privado no forman parte del material de esta skill.

## Qué se conserva y qué se solicita como mejora

**Conservado:** producto con S3, cuentas locales, formatos PDF/DOCX/TXT, validaciones, duplicados por SHA-256, relaciones, catálogo, descarga y preparación AWS Academy. Los escaneos se admiten como PDF; no existe OCR en el gestor.

**Solicitado por el docente:** una especificación reutilizable para cualquier modelo de IA y arquitectura MVC/hexagonal. La base es MVC con servicios/repositorio; los puertos explícitos, DTO y separación detallada de adaptadores son el diseño recomendado para su nueva implementación/refactorización.

**Refuerzos concretos de la especificación:** validación exhaustiva de fichas externas, clave exacta/tamaño de descarga, aislamiento del entorno de pruebas y cobertura explícita de conflictos de escritura. Se identifican en los anexos y no se atribuyen al código original como si ya existieran completos.

**Fuera de alcance:** OCR, extracción persistida, Markdown del contenido, revisión docente, publicación vigente, jobs de extracción, MongoDB/GridFS, chunks, embeddings y ChromaDB. Pertenecen a otra aplicación o a una ampliación autorizada. La skill de ETL MongoDB elaborada previamente no cambia el alcance de este repositorio.

## Continuidad con el ETL

Un consumidor futuro leerá la ficha, obtendrá el original por su clave y comprobará su hash. Generará una extracción con localizadores y mantendrá como `document_id` el UUID de esta carga. Una revisión del mismo módulo tendrá otro UUID y una relación; no debe mezclarse silenciosamente con el contenido anterior.

Antes de generar un índice consultable hará falta acordar aprobación, vigencia y política de versiones. `estado_declarado=final` y `registro.estado=guardado` no acreditan esos requisitos. Esta skill conserva la información útil para el futuro sin fingir que esos procesos ya están implementados.

## Fuentes técnicas oficiales

- [Escrituras condicionales S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html): precondiciones por clave y respuestas de conflicto.
- [Modelo de consistencia S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html#ConsistencyModel): garantías de objetos y limitaciones de operaciones entre claves.
- [Crear bucket con Boto3](https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/create_bucket.html): parámetros que debe verificar la implementación según región.

Las URLs de documentación técnica pueden evolucionar; fijar versiones de dependencias y consultar sus APIs al implementar. La referencia funcional está fijada al commit anterior para poder distinguir evoluciones posteriores.
