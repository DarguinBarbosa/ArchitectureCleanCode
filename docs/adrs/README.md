# Decisiones de arquitectura (ADRs)

Cada archivo de esta carpeta registra una decisión de diseño: qué se decidió, qué otras opciones había sobre la mesa y qué se aceptó pagar a cambio. Están para que quien llegue al proyecto entienda **por qué** el código está armado así, sin tener que reconstruirlo leyendo commits.

Un ADR no se edita cuando cambia de opinión el proyecto: se marca como reemplazado y se escribe uno nuevo que lo suceda.

## Índice

| # | Decisión | Estado |
|---|---|---|
| [0001](0001-django-y-drf-como-framework-backend.md) | Django y Django REST Framework como framework backend | aceptada |
| [0002](0002-arquitectura-limpia.md) | Clean Architecture como arquitectura del proyecto | aceptada |
| [0003](0003-entidad-de-dominio-pura.md) | La entidad de dominio es una dataclass pura, no el modelo del ORM | aceptada |
| [0004](0004-uuid-generado-en-el-dominio.md) | El identificador es un UUIDv4 que genera la entidad | aceptada |
| [0005](0005-decimal-para-el-precio.md) | El precio es `Decimal`, nunca `float` | aceptada |
| [0006](0006-puerto-del-repositorio-en-application.md) | El puerto del repositorio se declara en `application` | aceptada |
| [0007](0007-casos-de-uso-como-clases-planas.md) | Casos de uso como clases planas con inyección por constructor | aceptada |
| [0008](0008-serializers-de-forma-validacion-en-el-dominio.md) | Los serializers validan forma; las reglas de negocio están en la entidad | aceptada |
| [0009](0009-kernel-de-excepciones-y-handler-global.md) | Kernel compartido de excepciones y handler global de errores | aceptada |
| [0010](0010-mysql-como-motor-de-base-de-datos.md) | MySQL como motor de base de datos | aceptada |
| [0011](0011-configuracion-por-entorno.md) | Configuración por variables de entorno con python-decouple | aceptada |
| [0012](0012-tests-unitarios-sin-django.md) | Tests unitarios sin Django ni base de datos | aceptada |
| [0013](0013-openapi-con-drf-spectacular.md) | Documentación OpenAPI con drf-spectacular, apagable por entorno | aceptada |

## Formato

Todos siguen la misma estructura:

```
# ADR NNNN: Título
Estado / Fecha
## Contexto              Qué problema había y qué lo restringía
## Alternativas consideradas   Tabla: opción / a favor / en contra
## Decisión              Qué se eligió y por qué
## Consecuencias         Lo que se gana y lo que se paga
```

Los estados posibles son `propuesta`, `aceptada`, `reemplazada por ADR NNNN` y `descartada`.
