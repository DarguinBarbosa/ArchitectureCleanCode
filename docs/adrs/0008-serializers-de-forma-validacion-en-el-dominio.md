# ADR 0008: Los serializers validan forma; las reglas de negocio están en la entidad

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

DRF invita a poner las validaciones en el serializer: `max_length`, `min_value`, `allow_blank=False`, `validate_price()`. Con `ModelSerializer` van todavía más lejos y se derivan solas del modelo del ORM.

El problema es que esas mismas reglas ya están en la entidad `Product`, que valida en `__post_init__` ([ADR 0003](0003-entidad-de-dominio-pura.md)). Tenerlas en los dos lados significa dos fuentes de verdad que se van a desincronizar, y que el error que ve el cliente dependa de por dónde entró la request.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| `ModelSerializer` + `ModelViewSet` | El CRUD queda resuelto con muy poco código | Acopla la API al modelo del ORM y omite por completo los casos de uso |
| Validar todo en el serializer | Errores de DRF bien formados, con el campo señalado | Duplica las reglas; la entidad queda sin protección si se la construye por otra vía |
| Validar todo en la entidad, serializer solo de forma | Una sola fuente de verdad para el negocio | Los mensajes de error de negocio no traen el nombre del campo en el formato de DRF |
| Validar solo en la entidad y sin serializer | Menos capas | Un payload mal formado llegaría al dominio como `TypeError` en vez de un 400 |

## Decisión

El serializer valida **forma**: que los campos estén, que sean del tipo esperado, que el formato sea parseable. Nada más.

```python
class ProductInputSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True)                 # sin max_length
    description = serializers.CharField(allow_blank=True, required=False, default="")
    price = serializers.DecimalField(max_digits=..., decimal_places=...)  # sin min_value
```

`allow_blank=True` y la ausencia de `max_length` y `min_value` son deliberados: dejan pasar el valor para que la entidad sea la que lo rechace. Si el serializer cortara antes, habría dos lugares definiendo la misma regla.

Los límites que sí están (`max_digits`, `decimal_places`) no son reglas de negocio sino la forma del número que la columna puede almacenar, y salen de las constantes del modelo.

Las vistas son `APIView` planas y **solo orquestan**: deserializan, llaman al caso de uso, serializan la respuesta.

```python
def post(self, request):
    input_serializer = ProductInputSerializer(data=request.data)
    input_serializer.is_valid(raise_exception=True)
    product = CreateProduct(create_repository()).execute(**input_serializer.validated_data)
    return Response(ProductOutputSerializer(product).data, status=201)
```

No hay `ModelViewSet` porque un ViewSet trabaja contra un queryset, y eso volvería a atar la capa HTTP al ORM salteando los casos de uso.

## Consecuencias

- Las reglas de producto están escritas una sola vez. Si mañana el máximo de `name` pasa a 300, se toca la entidad (y la migración), no el serializer.
- Una regla de negocio violada llega como excepción del dominio y el handler global la traduce a 400 ([ADR 0009](0009-kernel-de-excepciones-y-handler-global.md)). El cliente ve un 400 igual que con DRF, pero con el tipo concreto (`InvalidPrice`) en la respuesta.
- Se pierde el detalle por campo que da DRF (`{"price": ["..."]}`). A cambio, el error dice exactamente qué regla se rompió.
- Hay que escribir manualmente el CRUD que `ModelViewSet` resolvería solo. Son unas 50 líneas de vistas: un costo acotado y conocido.
- Los serializers son `Serializer` a secas, no `ModelSerializer`, así que un cambio en el modelo no altera el contrato de la API sin que alguien lo decida.
