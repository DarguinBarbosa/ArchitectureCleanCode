# ADR 0014: GraphQL con Strawberry, como segundo adaptador

**Estado:** aceptada
**Fecha:** 2026-09-06

## Contexto

Hace falta exponer el catálogo por GraphQL, para que el cliente pida de forma declarativa exactamente los campos que necesita y pueda resolver varias consultas en un solo request.

La pregunta de diseño no es cómo devolver JSON —eso ya está resuelto— sino **dónde entra GraphQL**. El proyecto tiene los casos de uso aislados detrás de un puerto ([ADR 0006](0006-puerto-del-repositorio-en-application.md), [ADR 0007](0007-casos-de-uso-como-clases-planas.md)), así que GraphQL no es una feature nueva: es otro protocolo de entrada al mismo núcleo. Si termina con una sola regla de negocio propia, la integración está mal hecha.

Eso condiciona la elección de librería más que cualquier comparación de rendimiento o de API.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| No agregar GraphQL | Un solo protocolo que mantener | No cubre el caso: el cliente no puede elegir campos ni agrupar consultas |
| `graphene-django` | La opción más difundida en Django; `DjangoObjectType` deriva los tipos solo | Su principal atractivo es exactamente lo que este proyecto no puede hacer: derivar tipos del ORM acopla la capa web a la persistencia y saltea los casos de uso. Además el desarrollo está prácticamente detenido |
| `ariadne` | Schema-first: el SDL como fuente de verdad, legible | Duplica la declaración de tipos entre el `.graphql` y el código Python, y hay que mantener las dos sincronizadas a mano |
| `strawberry-graphql` | Code-first sobre type hints; `Product` ya es una dataclass tipada. Activamente mantenida, con integración Django propia | Menos ejemplos en español que graphene; los tipos hay que escribirlos |

## Decisión

Se adopta **Strawberry GraphQL 0.327**, instalado con `pip install "strawberry-graphql[django]"`.

El motivo es arquitectónico antes que técnico. `graphene-django` se descarta justamente por su función más vendida: `DjangoObjectType` construye el tipo GraphQL leyendo el modelo del ORM, lo que arrastraría la persistencia hasta la capa web y dejaría los casos de uso de lado. Es el mismo criterio con el que ya se había descartado `ModelSerializer` en el [ADR 0008](0008-serializers-de-forma-validacion-en-el-dominio.md).

GraphQL queda como **un adaptador del anillo externo, hermano de REST**, en `products/api/graphql/`. Los dos ejecutan los mismos casos de uso: un producto creado por REST se consulta por GraphQL y al revés.

### Los resolvers reciben casos de uso, nunca el repositorio

Es la decisión que ordena el resto. Si un resolver conociera el repositorio, la capa de presentación sabría que existe la persistencia, y el puerto —que es un detalle de la capa de aplicación— se filtraría hacia afuera. El resolver solo conoce el caso de uso; quién le inyecta el repositorio es responsabilidad del composition root.

El cableado se reparte en dos módulos, y la separación es deliberada:

- `products/api/composition.py` declara `ProductUseCases` y `build_use_cases(repository)`. **No importa ningún framework**, solo la capa de aplicación.
- `products/api/dependencies.py` es el único que nombra `DjangoProductRepository`.

Los casos de uso llegan al resolver por el contexto de Strawberry, que arma `ProductsGraphQLView.get_context()`. Como consecuencia, el schema entero se puede ejecutar con `InMemoryProductRepository`, sin base de datos y sin Django.

La misma corrección se aplicó a las vistas REST, que hasta acá construían `CreateProduct(create_repository())` en el cuerpo de la vista y tenían esa misma fuga.

### Los tipos no son la entidad

`ProductType` es forma de transporte, igual que los serializers. Se mapea desde `Product` con `from_entity`. Renombrar u ocultar un campo en la API no puede obligar a tocar `domain`.

### Los errores se traducen en un solo lugar

`DomainErrorExtension` es una `SchemaExtension` que envuelve cada resolver y conoce **solo el kernel compartido**, nunca una feature. Es el espejo de `config/exception_handler.py`. GraphQL siempre responde 200, así que la categoría viaja en `extensions.code`:

| Excepción | `extensions.code` |
|---|---|
| `NotFoundError` y derivadas | `NOT_FOUND` |
| `ValidationError` y derivadas | `BAD_REQUEST` |

Lo que no es un `DomainError` no se toca, para que un bug no se disfrace de error de negocio.

### CSRF

El endpoint va con `csrf_exempt`. Sin eso, Django responde 403 a todo POST y GraphQL queda inutilizable. Es correcto porque la API es stateless y no tiene autenticación por cookies: DRF omite la verificación en el adaptador REST por la misma razón. **Si algún día entra autenticación por sesión, la exención tiene que irse**, y así está anotado en el código.

## Consecuencias

- Un producto creado por REST se consulta por GraphQL sin nada que sincronizar: la fuente de verdad es única.
- Las reglas de negocio no se repiten. Un precio negativo enviado por GraphQL lo rechaza la entidad, y el error que llega al cliente dice `InvalidPrice`.
- El schema tiene tests que corren sin base de datos (`tests_unit/api/test_graphql_schema.py`). Es el primer adaptador con cobertura automática, lo que reduce la deuda declarada en el [ADR 0012](0012-tests-unitarios-sin-django.md).
- El guardarraíl de aislamiento pasó a ejecutarse en un subproceso. Medía `sys.modules` del proceso de tests, y como los tests de GraphQL importan Strawberry legítimamente, habría dado un falso positivo. Ahora mide en un intérprete limpio, que es lo que realmente prueba de qué dependen los módulos internos.
- GraphiQL se monta bajo `DOCS_ENABLED`, la misma bandera que Swagger ([ADR 0013](0013-openapi-con-drf-spectacular.md)). Apagada, no se sirve el explorador ni queda expuesta la introspección.
- Hay dos superficies de API que mantener. Cada operación nueva hay que exponerla dos veces, aunque la lógica se escriba una sola.
- No se agregó paginación, filtros ni DataLoader. Con un solo agregado y sin relaciones anidadas no hay problema N+1 que resolver; incorporarlo sería complejidad sin caso.
