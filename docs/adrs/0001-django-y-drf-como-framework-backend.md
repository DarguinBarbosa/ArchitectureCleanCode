# ADR 0001: Django y Django REST Framework como framework backend

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

La actividad pide construir una API REST con operaciones CRUD sobre una base de datos, usando un framework que empuje hacia buenas prácticas y una organización de código clara. La lectura del módulo acota el universo de referencia a cuatro frameworks: Laravel, Express.js, Django y Spring.


## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Django + Django REST Framework | ORM y migraciones incluidos, serializers y manejo de errores propios de DRF, convención de apps y módulos ya establecida | Trae bastante que no se usa en una API pura (templates, admin, sesiones) |
| Express.js | Curva mínima, arranque inmediato | El ORM y la estructura de carpetas quedan fuera del framework; hay que decidir todo por afuera |
| Spring Boot | Convención de capas explícita, JPA integrado, ecosistema maduro | Otro lenguaje y otro toolchain; el equipo no trabaja en JVM |
| FastAPI | Ligero, OpenAPI automático, tipado nativo | Fuera del universo de referencia del módulo y sin capa de persistencia integrada |

## Decisión

Se adopta **Django 6.0.4 con Django REST Framework 3.17** sobre **Python 3.14**.

Django resuelve dentro del framework las tres cosas que la actividad exige: la persistencia con un ORM y migraciones versionadas, el manejo centralizado de errores (`REST_FRAMEWORK['EXCEPTION_HANDLER']`) y una convención de organización en apps que no hay que inventar de cero. DRF agrega encima la capa HTTP: serializers, vistas y códigos de estado.

Lo que Django trae de más —admin, templates, sesiones— se deja instalado pero sin uso en las rutas de la API. Sacarlo daría un `settings.py` más limpio a cambio de romper el `manage.py check` estándar y complicar cualquier extensión futura.

## Consecuencias

- El proyecto hereda la convención de apps de Django, que es también con lo que se evalúa la organización del código.
- Django empuja fuerte hacia el patrón MTV y hacia que el modelo del ORM sea la entidad de negocio. Ese acoplamiento se corta a propósito en el [ADR 0003](0003-entidad-de-dominio-pura.md).
- Las migraciones quedan versionadas en `products/migrations/`, así que el esquema de la tabla es parte del repositorio y no un script suelto.
- Al no usar `ModelSerializer` ni `ModelViewSet`, se renuncia a parte del código que DRF genera automáticamente. El motivo está en el [ADR 0008](0008-serializers-de-forma-validacion-en-el-dominio.md).
