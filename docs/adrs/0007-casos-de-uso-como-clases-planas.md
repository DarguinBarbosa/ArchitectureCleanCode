# ADR 0007: Casos de uso como clases planas con inyección por constructor

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

Cada operación de la API —crear, obtener, listar, actualizar, eliminar— tiene un flujo propio: qué se valida, en qué orden se toca el repositorio, qué pasa si el producto no existe. Ese flujo tiene que estar en algún lado que no sea la vista, porque la vista es un detalle de HTTP.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Un `ProductService` con los cinco métodos | Un solo archivo, una sola inyección | Crece sin límite y termina siendo el cajón donde va todo lo que no tiene casa |
| Funciones sueltas `create_product(repo, ...)` | Lo más simple posible | El repositorio viaja como parámetro en cada llamada; sin lugar natural para dependencias |
| Una clase por caso de uso con `execute` | Una responsabilidad por clase; el nombre dice qué hace | Más archivos y más ceremonia para operaciones triviales |
| Casos de uso como `@Service` de un contenedor DI | Cableado automático | Mete el framework en la capa de aplicación, que es justo lo que se evita |

## Decisión

Una **clase por caso de uso**, con el repositorio inyectado por constructor y un único método `execute`:

```python
class GetProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, product_id: UUID) -> Product:
        return _get_or_fail(self._repository, product_id)
```

Tres reglas que salen de ahí:

**El caso de uso nunca instancia su repositorio.** Lo recibe. La única función que sabe cuál es la implementación concreta es `create_repository()` en `products/api/views.py`.

**El caso de uso recibe primitivos, no entidades.** La vista le pasa `name`, `description`, `price`; el caso de uso construye o reemplaza la entidad. Así la capa HTTP no necesita saber cómo se arma un `Product`.

**El caso de uso decide qué es un "no encontrado".** El repositorio devuelve `None` ([ADR 0006](0006-puerto-del-repositorio-en-application.md)) y es el caso de uso el que lo convierte en `ProductNotFound`. Ese guard aparece en tres de los cinco casos, así que está centralizado en un helper:

```python
def _get_or_fail(repository: ProductRepository, product_id: UUID) -> Product:
    product = repository.get_by_id(product_id)
    if product is None:
        raise ProductNotFound(product_id)
    return product
```

`DeleteProduct` lo llama aunque descarte el resultado. Sin eso, borrar algo inexistente devolvería 204 y el cliente no se enteraría de nada.

## Consecuencias

- Los nombres de las clases son el índice de lo que la aplicación sabe hacer. Abrir `use_cases.py` alcanza para saberlo.
- Cada caso de uso se prueba solo, pasándole `InMemoryProductRepository`.
- Se instancia un caso de uso por request. Son objetos con un atributo; el costo es nulo.
- No hay contenedor de inyección de dependencias. El cableado es a mano en una función de tres líneas. Con una sola implementación de repositorio, alcanza; si crecen las dependencias, ese es el punto donde habría que revisarlo.
- `UpdateProduct` lee antes de escribir para poder fallar con 404 y para conservar el id. Son dos consultas donde una podría bastar, a cambio de una semántica correcta.
