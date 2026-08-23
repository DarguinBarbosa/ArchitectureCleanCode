# ADR 0005: El precio es `Decimal`, nunca `float`

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

`price` representa dinero. En Python, `float` es punto flotante binario IEEE 754: no puede representar exactamente valores como `0.1` o `19.99`, y las sumas acumulan error. `0.1 + 0.2 == 0.3` es `False`. En un catálogo de productos eso se traduce en totales que no cierran por centavos.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| `float` | Nativo, rápido, serializa directo a JSON | Redondeo binario: los importes no son exactos y el error se acumula |
| `int` de centavos | Exacto y compacto; una sola unidad | Cada lectura y escritura necesita conversión; el valor crudo en la DB no se entiende sin contexto |
| `Decimal` | Aritmética decimal exacta, precisión y escala explícitas, mapea directo a `DECIMAL` de MySQL | Más lento que `float` y hay que cuidar el tipo en los bordes |

## Decisión

`Product.price` es un `Decimal`. La entidad **rechaza cualquier otro tipo**, incluso los que Python convertiría sin quejarse:

```python
if not isinstance(self.price, Decimal):
    raise InvalidPrice("Price must be a Decimal.")
```

Es a propósito. Aceptar un `float` "porque se puede convertir" es justamente la conversión implícita que introduce el error. Si llega algo que no es `Decimal`, es un bug en el borde, y conviene que explote ahí.

En la base, la columna es `DECIMAL(12, 2)`: 12 dígitos totales, 2 decimales. El `DecimalField` de DRF usa las mismas constantes (`PRICE_MAX_DIGITS`, `PRICE_DECIMAL_PLACES`), importadas del modelo para que no haya dos fuentes de verdad.

La regla de negocio sobre el valor —no puede ser negativo— vive en la entidad, no en el serializer ni en la columna.

## Consecuencias

- DRF entrega `Decimal` desde el `DecimalField`, así que el camino HTTP normal ya llega con el tipo correcto. Quien construya un `Product` a mano tiene que pasar `Decimal`.
- En la respuesta JSON el precio sale como string (`"19.99"`), que es el comportamiento por defecto de DRF y evita que el cliente lo reciba como float y pierda la exactitud del otro lado.
- El límite de 12 dígitos con 2 decimales acepta hasta 9.999.999.999,99. Si algún día hace falta más escala hay que cambiar la migración, el modelo y el serializer a la vez, porque los tres leen las mismas constantes.
