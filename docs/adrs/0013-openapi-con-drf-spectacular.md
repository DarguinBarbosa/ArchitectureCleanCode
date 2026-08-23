# ADR 0013: Documentación OpenAPI con drf-spectacular, apagable por entorno

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

La API necesita documentación navegable. El requisito que condiciona la decisión es que no cueste rendimiento: la documentación no puede meter trabajo en el camino de las requests reales.

Existe un riesgo concreto en ese punto. Las librerías de documentación para Django exponen una vista que **genera el esquema en cada request**: recorre el `urlconf`, inspecciona vistas y serializers y compone el YAML. Es una operación costosa y, si la ruta queda montada en producción, queda expuesta a invocaciones repetidas desde el exterior.

Hay un problema adicional propio de este proyecto: las vistas son `APIView` con serializers planos, no `ModelViewSet` ([ADR 0008](0008-serializers-de-forma-validacion-en-el-dominio.md)). Un generador automático no tiene de dónde deducir el request ni la respuesta; hay que decírselo.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Escribir el `openapi.yaml` a mano | Control total, cero dependencias | Se desincroniza del código de inmediato y no hay forma de detectarlo |
| `rest_framework.schemas` (el generador que trae DRF) | Sin dependencias nuevas | Genera OpenAPI 3.0 pobre y está deprecado |
| drf-yasg | Muy usado históricamente | Sigue en Swagger 2.0 y el proyecto está prácticamente parado |
| drf-spectacular | OpenAPI 3.0 real, anotaciones explícitas, Swagger UI y Redoc incluidos, CLI para generar el archivo | Una dependencia más; con vistas planas hay que anotar a mano |

## Decisión

**drf-spectacular**, con tres decisiones sobre cómo se sirve.

### 1. Las rutas de docs se montan solo si `DOCS_ENABLED`

```python
DOCS_ENABLED = config('DOCS_ENABLED', default=DEBUG, cast=bool)
```

En `config/urls.py`, las URLs de esquema, Swagger UI y Redoc están dentro de un `if`. Con la bandera apagada **ni siquiera se importa drf-spectacular**: las rutas no existen, el `urlconf` es más corto y no hay forma de disparar la generación del esquema desde afuera.

El default es `DEBUG`, así que en desarrollo está encendido sin configurar nada y en producción está apagado salvo que alguien lo pida explícitamente. Es una variable aparte y no `DEBUG` a secas porque a veces se quieren las docs en un staging que corre con `DEBUG=False`.

### 2. El esquema versionado se genera por CLI, no en runtime

```bash
python manage.py spectacular --file docs/openapi/schema.yaml
```

El archivo queda en `docs/openapi/schema.yaml`, dentro del repositorio. Ese es el artefacto que se comparte con clientes, se usa para generar SDKs o se sube a un portal. Nadie necesita levantar la app para leerlo, y el diff en el PR muestra cuándo cambió el contrato.

### 3. Las anotaciones viven en `products/api/schema.py`

Los `@extend_schema` no van escritos dentro de las vistas. Están definidos en un módulo aparte y las vistas solo aplican el decorador ya armado:

```python
class ProductDetailView(APIView):
    @get_product_schema
    def get(self, request, product_id):
        ...
```

Las vistas siguen siendo tres líneas de orquestación y toda la metadata está junta en un lugar. Ahí también se declara `ErrorResponseSerializer`, que describe el sobre de error del [ADR 0009](0009-kernel-de-excepciones-y-handler-global.md), con ejemplos concretos de `InvalidPrice` y `ProductNotFound`. Sin eso, un 400 aparecería en la doc como una respuesta vacía.

### Sobre el costo

Los decoradores se evalúan **una vez, al importar el módulo**. No corren por request ni envuelven el handler: drf-spectacular solo cuelga metadata en la función y la lee después, al generar. El camino de una request a `/api/v1/products/` es idéntico con y sin documentación.

Lo único que sí cuesta es generar el esquema, y eso pasa en dos momentos: cuando se abre `/api/schema/` en desarrollo, y cuando se corre el comando de CLI. Ninguno de los dos está en el camino de un cliente.

## Consecuencias

- Con `DOCS_ENABLED=False` el impacto en producción es cero: no hay import, no hay rutas, no hay generación.
- En desarrollo, `/api/docs/` (Swagger UI) y `/api/redoc/` quedan disponibles sin tocar nada.
- Agregar o cambiar un endpoint obliga a actualizar `schema.py` y a regenerar `schema.yaml`. Es trabajo manual y se puede olvidar; drf-spectacular avisa con warnings al generar cuando no puede deducir algo, pero no obliga.
- `SERVE_INCLUDE_SCHEMA: False` evita que la vista de esquema se documente a sí misma.
- El esquema hereda de DRF la declaración de `cookieAuth` / `basicAuth`, que son los authenticators por defecto aunque ningún endpoint exija autenticación. Cuando se agregue autenticación real habrá que revisarlo.
- Queda una dependencia más en `requirements.txt`. Sus transitivas (`PyYAML`, `jsonschema`, `inflection`, `uritemplate`) solo se cargan si las docs están encendidas.
