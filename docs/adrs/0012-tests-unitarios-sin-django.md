# ADR 0012: Tests unitarios sin Django ni base de datos

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

Lo que hay que probar es el negocio: las validaciones de la entidad y el flujo de los casos de uso. Nada de eso necesita HTTP ni SQL.

El camino habitual en Django es `manage.py test` con `TestCase`, que arranca el framework y crea una base de test. Para probar que un precio negativo tira `InvalidPrice`, eso es levantar toda la infraestructura para no usarla.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| `django.test.TestCase` | Estándar, integrado con `manage.py test` | Arranca Django y crea la DB de test para probar reglas que no la usan |
| pytest + pytest-django | Fixtures cómodas, mejor salida | Dos dependencias más para lo que `unittest` ya resuelve |
| `unittest` puro contra `domain` y `application` | Rápido, sin dependencias, y demuestra que el aislamiento es real | Deja `infra`, `api` y `config` sin cobertura automática |
| Mocks del repositorio con `unittest.mock` | Sin escribir un doble | El mock no valida que se respete la interfaz; acepta cualquier llamada |

## Decisión

Los tests viven en `tests_unit/` —fuera de las apps— y corren con `unittest` a secas:

```bash
python -m unittest discover -s tests_unit -t . -v
```

Sin `manage.py`, sin `django.setup()`, sin base de datos. 30 tests que cubren `domain` (validaciones de la entidad) y `application` (los cinco casos de uso).

Los casos de uso se prueban contra `InMemoryProductRepository`, un doble que implementa la misma ABC guardando en un diccionario ([ADR 0006](0006-puerto-del-repositorio-en-application.md)). Es un doble escrito a mano y no un mock, a propósito: al heredar de la ABC, si la interfaz cambia y el doble no lo sigue, Python falla al instanciarlo. Un mock se quedaría callado.

Además hay un guardarraíl. `test_isolation.py` importa los módulos de dominio y aplicación y verifica que Django **no** haya quedado cargado:

```python
for module in MODULES_UNDER_TEST:
    importlib.import_module(module)
self.assertNotIn("django", sys.modules)
```

La regla de dependencia del [ADR 0002](0002-arquitectura-limpia.md) no la impone el lenguaje. Este test la vuelve verificable: cuando alguien la infringe, la suite falla, en lugar de quedar como una convención documentada que nadie controla.

## Consecuencias

- La suite corre en menos de un segundo, sin MySQL levantado. Se puede ejecutar en cualquier máquina recién clonada.
- Que estos tests pasen sin Django es la evidencia de que el dominio está desacoplado. Si en el futuro se introduce un import indebido, el guardarraíl lo detecta.
- **`infra`, `api` y `config` no tienen tests automáticos hoy.** El repositorio concreto, las vistas y el handler global están sin cubrir. Es la deuda conocida de esta decisión.
- Cerrar esa deuda no cambia lo de acá: son tests de integración, con `APITestCase` de DRF o Playwright en modo API, en un directorio aparte que sí levante Django.
- El guardarraíl depende de que `MODULES_UNDER_TEST` se mantenga al día. Un módulo nuevo en `application` que no se agregue a esa lista queda sin vigilar.
