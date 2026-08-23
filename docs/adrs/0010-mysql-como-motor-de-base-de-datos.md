# ADR 0010: MySQL como motor de base de datos

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

El proyecto necesita persistencia relacional para una tabla con clave primaria UUID y una columna monetaria de precisión exacta ([ADR 0004](0004-uuid-generado-en-el-dominio.md), [ADR 0005](0005-decimal-para-el-precio.md)). El esquema tiene que crearse de forma reproducible, sin scripts sueltos.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| SQLite | Cero instalación, viene con Python | Tipado dinámico: `DECIMAL` termina siendo texto o float según el caso. No representa el entorno real |
| MySQL | Motor relacional estándar, `DECIMAL` exacto, soportado de primera por Django | Requiere servidor instalado y un driver que compila (`mysqlclient`) |
| PostgreSQL | Tipo `uuid` nativo, `NUMERIC` exacto, mejor comportamiento con claves no secuenciales | No es el motor que usa el equipo; sumaría otra pieza a instalar |

## Decisión

**MySQL**, accedido por el ORM de Django con el driver `mysqlclient`. El acceso está confinado a `products/infra/` ([ADR 0002](0002-arquitectura-limpia.md)).

El esquema lo crea la migración `products/migrations/0001_initial.py`, versionada en el repositorio: `python manage.py migrate` deja la tabla `product` lista. No hay `schema.sql` ni pasos manuales.

Dos detalles del mapeo:

- El `UUIDField` de Django, sobre MySQL, se guarda como `CHAR(32)` —MySQL no tiene tipo UUID nativo—. El ORM se ocupa de la conversión en los dos sentidos, así que el dominio nunca ve la representación de la base.
- `price` es `DECIMAL(12, 2)`, exacto. No `FLOAT` ni `DOUBLE`.

Se descartó SQLite precisamente por el tipado: permitiría en desarrollo valores que fallan en producción, algo inadmisible tratándose de importes monetarios.

## Consecuencias

- Correr el proyecto requiere un MySQL levantado. La configuración va por `.env` ([ADR 0011](0011-configuracion-por-entorno.md)).
- `mysqlclient` compila contra las libs de MySQL. En Windows suele resolverse con el wheel; en Linux hace falta `default-libmysqlclient-dev` y compilador.
- Guardar el UUID como `CHAR(32)` ocupa más que 16 bytes binarios y el índice es menos compacto. Con este volumen no importa.
- Cambiar de motor es cambiar `DB_ENGINE` en el `.env` y regenerar migraciones. Nada del dominio ni de la aplicación se entera.
