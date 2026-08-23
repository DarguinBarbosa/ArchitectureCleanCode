# ADR 0006: El puerto del repositorio se declara en `application`

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

Los casos de uso necesitan guardar y leer productos. Si llaman directo a `ProductModel.objects`, la capa de aplicación pasa a depender del ORM y con eso se rompe la regla de dependencia del [ADR 0002](0002-arquitectura-limpia.md).

Hace falta una interfaz. La pregunta es dónde vive y qué contrato tiene.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Sin interfaz: el caso de uso usa el ORM | Menos código | La capa de aplicación queda atada a Django y no se puede testear sin DB |
| La interfaz vive en `domain` | Es donde la pone buena parte de la literatura de DDD | El dominio de este proyecto no persiste nada; le agregaría un concepto que no usa |
| La interfaz vive en `application` | Está donde se consume; la implementación en `infra` la satisface | Si mañana el dominio necesitara persistir algo, habría que moverla |
| Protocolo estructural (`typing.Protocol`) | Sin herencia, más liviano | El error por método faltante aparece recién en el momento de llamarlo, no al instanciar |

## Decisión

`ProductRepository` es una **ABC** y vive en `products/application/repository.py`, junto a los casos de uso que la usan. `DjangoProductRepository`, en `products/infra/`, la implementa.

La interfaz la declara quien la necesita, y la satisface quien está afuera: la dependencia queda invertida y `application` no importa nada de `infra`.

El contrato define cinco operaciones —`create`, `get_by_id`, `list_all`, `update`, `delete`— y una regla explícita sobre el ausente:

```python
def get_by_id(self, product_id: UUID) -> Product | None:
    """Return the product, or None if it does not exist (no exception)."""
```

**El repositorio no lanza `ProductNotFound`.** Se limita a devolver `None`. Que la ausencia constituya un error, y a qué código HTTP se traduce, es una decisión de negocio, y esas decisiones no corresponden a un adaptador: quedan del lado del caso de uso ([ADR 0007](0007-casos-de-uso-como-clases-planas.md)).

Se eligió ABC sobre `Protocol` porque falla antes: si una implementación omite un método, Python lanza `TypeError` al instanciarla, y no en el momento en que alguien invoque ese método en producción.

## Consecuencias

- Los tests de casos de uso usan `InMemoryProductRepository`, un doble que implementa la misma ABC con un diccionario. No hace falta base de datos.
- La firma `Product | None` obliga a que quien llama decida qué hacer con el `None`. No hay un caso silencioso.
- El repositorio devuelve y recibe entidades de dominio, nunca instancias del ORM. El mapeo queda contenido adentro del adaptador.
- Con una sola implementación real, la ABC es una indirección que por sí misma no se justifica. Lo que la justifica es el testing y la posibilidad de cambiar el motor sin tocar el negocio.
