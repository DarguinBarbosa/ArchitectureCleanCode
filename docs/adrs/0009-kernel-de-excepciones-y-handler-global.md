# ADR 0009: Kernel compartido de excepciones y handler global de errores

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

La actividad pide manejo centralizado de errores. Y el diseño trae un requisito propio: el dominio lanza excepciones que no son de Django (`InvalidPrice`, `ProductNotFound`), así que alguien tiene que traducirlas a códigos HTTP. Si esa traducción queda en cada vista con `try/except`, se repite cinco veces y se olvida a la sexta.

Hace falta un punto único. El riesgo es que ese punto único termine importando excepciones de cada feature, y entonces `config/` —lo más externo— pase a depender de todas las features.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| `try/except` en cada vista | Explícito y local | Se repite en todas las vistas y se desincroniza; las vistas dejan de solo orquestar |
| Middleware de Django | Atrapa todo, incluso fuera de DRF | Trabaja con `HttpResponse` cruda; hay que rearmar a mano el contenido negociado |
| Handler de DRF que conoce cada excepción concreta | Directo de escribir | `config/` termina importando `products`; la dependencia queda al revés |
| Handler de DRF + jerarquía base compartida | Punto único que solo conoce categorías abstractas | Hay que sostener la jerarquía y que cada feature herede bien |

## Decisión

Dos piezas.

**Un kernel compartido** en `shared/domain/exceptions.py`, Python puro, sin Django y sin conocer ninguna feature:

```
DomainError
├── NotFoundError    → 404
└── ValidationError  → 400
```

Cada feature extiende esas bases. `products` define `InvalidProduct(ValidationError)` con `InvalidName` / `InvalidDescription` / `InvalidPrice`, y `ProductNotFound(NotFoundError)`.

**Un handler global** en `config/exception_handler.py`, registrado en `REST_FRAMEWORK['EXCEPTION_HANDLER']`, que mapea **por categoría**:

- `NotFoundError` → 404
- `ValidationError` → 400
- Errores de forma de DRF → su propio código, normalizado al mismo sobre
- Cualquier otra excepción → `None`

Ese último caso importa: devolver `None` hace que Django responda 500 y registre el traceback. Un bug no se disfraza de error de negocio.

El handler **nunca importa `products`**. Solo conoce el kernel, así que agregar una feature nueva no lo toca: alcanza con que sus excepciones hereden de las bases.

Toda respuesta de error sale con el mismo sobre:

```json
{ "error": { "status": 400, "type": "InvalidPrice", "detail": "Price cannot be negative." } }
```

`type` es el nombre de la clase de la excepción, así que el cliente puede distinguir un `InvalidPrice` de un `InvalidName` sin parsear el mensaje.

## Consecuencias

- Las vistas no tienen un solo `try`. Lanzan hacia arriba y el handler resuelve.
- Agregar una regla de negocio es agregar una excepción que herede de la base correcta. El mapeo HTTP ya está resuelto.
- El kernel vive en `shared/`, fuera de `products/`, para que una segunda feature no tenga que importar excepciones de la primera.
- Se paga en granularidad: los errores de forma de DRF pierden su estructura original al reenvolverse, aunque el contenido queda en `detail`.
- Un error no previsto sale como 500 sin detalle hacia afuera. Es lo correcto, pero implica que hace falta mirar los logs para diagnosticarlo.
