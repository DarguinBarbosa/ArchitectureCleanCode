# ADR 0003: La entidad de dominio es una dataclass pura, no el modelo del ORM

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

En Django lo normal es que `Product(models.Model)` sea a la vez la entidad de negocio, el mapeo a la tabla y el objeto que viaja por toda la aplicación. Instanciarlo requiere que Django esté configurado; validarlo pasa por `full_clean()`, que trae su propio `ValidationError`; y cualquier regla escrita ahí queda atada al framework.

El [ADR 0002](0002-arquitectura-limpia.md) exige que `domain` no importe Django. Con el modelo del ORM haciendo de entidad, eso es imposible.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| El modelo del ORM es la entidad | Cero mapeo, cero duplicación, es lo idiomático en Django | Arrastra Django al dominio; no se puede instanciar ni validar sin configurar el framework |
| Modelo del ORM + validaciones en `clean()` | Aprovecha el ciclo de validación de Django | Las validaciones solo corren si alguien llama `full_clean()`; `.update()` del queryset las saltea |
| Dataclass pura + modelo separado con mapeo explícito | El dominio no depende de nada; se instancia y se valida en memoria | Hay que escribir y mantener el mapeo entidad ↔ columnas |
| Pydantic como entidad | Validación declarativa y mensajes listos | Mete una dependencia externa en el dominio y sus errores no son excepciones de negocio propias |

## Decisión

`Product` es una **dataclass congelada** (`frozen=True, slots=True, kw_only=True`) que vive en `products/domain/product.py` y no importa nada fuera de la stdlib y sus propias excepciones.

El modelo del ORM (`ProductModel`) vive en `products/infra/models.py` y solo describe la tabla. La traducción entre uno y otro está centralizada en `_to_entity` / `_to_columns` dentro del repositorio concreto, en un único lugar.

`frozen=True` implica que un producto no se modifica: se reemplaza. El caso de uso de actualización usa `dataclasses.replace()`, que construye una instancia nueva y vuelve a ejecutar `__post_init__`. Es decir, **toda actualización revalida**; no hay forma de dejar una entidad en estado inválido después de un update.

`slots=True` evita el `__dict__` por instancia y cierra la puerta a agregarle atributos sueltos a una entidad en runtime.

## Consecuencias

- Hay dos declaraciones de la misma forma de datos: la entidad y el modelo. Es duplicación real, aceptada a cambio del desacople. El límite de longitud de `name` y `description` se define en el dominio y el modelo lo importa, así que al menos las constantes no se repiten.
- Ninguna operación del dominio necesita base de datos ni `django.setup()`. Los tests de `domain` corren con `unittest` a secas.
- Cualquier código que reciba un `Product` sabe que es válido: no existe la instancia inválida, porque el constructor tira excepción.
- Si mañana se agrega un campo hay que tocarlo en tres lugares: entidad, modelo y migración.
