# Archi — Products API

API de productos construida con **Clean Architecture** sobre Django, expuesta por **REST y GraphQL** contra MySQL.

Esta wiki explica cómo está organizado el proyecto por dentro. El video recorre lo mismo en 10 minutos; el texto que sigue sirve para consultarlo después, sin volver a mirarlo.

---

## 🎥 Video: recorrido por la arquitectura

[![Ver el recorrido por la arquitectura](https://img.youtube.com/vi/lsR9zHbkV-A/maxresdefault.jpg)](https://youtu.be/lsR9zHbkV-A)

### ▶️ [Ver en YouTube](https://youtu.be/lsR9zHbkV-A) · ~10 min

También queda una copia en el repositorio, en [`docs/video/clean-architecture.mp4`](https://github.com/DarguinBarbosa/ArchitectureCleanCode/blob/main/docs/video/clean-architecture.mp4), versionada con Git LFS.

---

## De qué trata el proyecto

Es un CRUD de productos. Lo relevante no es qué hace, sino cómo está organizado.

Está construido con Django contra una base MySQL y se expone por dos protocolos, REST y GraphQL. Toda la organización responde a un objetivo: **que la lógica de negocio no dependa del framework**. Django queda conectado por afuera y podría sustituirse sin tocar el núcleo del sistema.

Que haya dos protocolos sobre el mismo núcleo es la mejor prueba de que eso funciona: GraphQL se agregó entero sin modificar una línea del dominio ni de los casos de uso.

---

## La regla que ordena todo

El proyecto implementa **Clean Architecture**, el modelo de capas concéntricas de Robert C. Martin. Hay cuatro capas y un kernel compartido, gobernados por una sola regla: la **regla de dependencia** (*Dependency Rule*). Las dependencias del código fuente apuntan siempre hacia el interior.

```
shared/domain  ←  domain  ←  application  ←  infra / api
```

En la práctica: el dominio, en el centro, desconoce que Django existe. La capa de aplicación desconoce que hay una base de datos y que hay una API. Cada capa conoce a las que tiene adentro, nunca a las que la contienen.

Cuando el flujo de control necesita ir en sentido contrario —la aplicación tiene que llegar a la base de datos— se aplica el **principio de inversión de dependencias** (*DIP*): la capa interna declara la interfaz y la externa la implementa.

---

## Las capas, una por una

### 1. Dominio — el centro

📄 `products/domain/product.py`

`Product` es una clase de Python común. No hereda de nada de Django ni importa nada de Django.

Tiene cuatro campos: `id`, `name`, `description` y `price`. Cuatro decisiones detrás de eso:

- **El `id` es un UUID que genera la propia entidad**, no la base de datos. Así un producto es válido y está completo por sí mismo, antes de persistirse.
- **El precio se maneja con `Decimal`, nunca con `float`.** Con dinero, `float` pierde precisión y acumula errores de redondeo. `Decimal` es exacto.
- **La entidad es inmutable.** Actualizar un producto no lo modifica: construye uno nuevo con los datos nuevos, y eso vuelve a pasar por las validaciones. Nunca queda un producto en estado inválido.
- **Las validaciones están dentro de la entidad.** Que el nombre no vaya vacío, que el precio no sea negativo. Si una regla no se cumple, la entidad lo rechaza con un error propio del dominio, no con uno genérico.

### 2. Aplicación — los casos de uso

📄 `products/application/repository.py` · `products/application/use_cases.py`

Un caso de uso por operación: crear, obtener, listar, actualizar y eliminar.

Antes de los casos de uso está el **puerto**: una interfaz que declara qué debe saber hacer un repositorio de productos —crear, buscar por id, listar, actualizar y eliminar— sin decir cómo. El cómo llega después, en otra capa.

Cada caso de uso **recibe el repositorio desde afuera**; no lo construye. Por eso le resulta indistinto si por detrás hay Django, MySQL o una lista en memoria: le habla a la interfaz, no a la implementación.

Un ejemplo del reparto de responsabilidades: el caso de uso que obtiene un producto le pide el producto al repositorio y, si el repositorio no devuelve nada, **es el caso de uso el que decide que eso constituye un "no encontrado"** y lanza el error. El repositorio no toma esa decisión.

### 3. Infraestructura — acá aparece Django

📄 `products/infra/models.py` · `products/infra/django_repository.py`

La primera capa donde Django está presente. Contiene dos piezas.

El **modelo del ORM**, que es lo que Django usa para hablar con la tabla.

Y el **adaptador**: la clase que implementa el puerto declarado en la capa de aplicación. Su único trabajo es traducir —toma una entidad del dominio y la convierte en columnas, o toma lo que llega de la base y arma la entidad—. Toda esa traducción está centralizada en un solo lugar, para no repetirla.

Si mañana hubiera que reemplazar MySQL, se tocaría únicamente este archivo. El dominio y los casos de uso no se enteran.

### 4. API — la capa web, que solo coordina

📄 `products/api/serializers.py` · `products/api/views.py` · `products/api/composition.py`

Es la capa que recibe los requests HTTP, con una regla explícita: **las vistas no deciden nada de negocio, solo coordinan.**

Los serializers se ocupan de la **forma** del request: que los campos estén presentes, que el precio venga como número. Las reglas de negocio no se repiten acá. Si alguien envía un precio negativo, el serializer lo deja pasar y es la entidad la que lo rechaza. La regla vive en un solo lugar.

La vista se limita a pedir los casos de uso al composition root, ejecutar el que corresponde y devolver la respuesta. En una vista no hay lógica de negocio, y eso es deliberado.

Un detalle que importa: **la vista tampoco conoce el repositorio**. Recibe casos de uso ya construidos. Que exista una persistencia por detrás es un asunto de las capas internas, y la capa web no tiene por qué enterarse.

### 5. GraphQL — un segundo adaptador, el mismo núcleo

📄 `products/api/graphql/`

Además de REST, el catálogo se expone por GraphQL en `/graphql/`, con **Strawberry**. No es una funcionalidad aparte: es otro protocolo de entrada a los mismos casos de uso. Un producto creado por REST se consulta por GraphQL sin nada que sincronizar.

Los resolvers siguen exactamente la misma regla que las vistas: toman el caso de uso del contexto, lo ejecutan y mapean el resultado. Si se envía un precio negativo por GraphQL, quien lo rechaza es la entidad, y el cliente recibe `InvalidPrice` — la misma regla, escrita una sola vez.

La elección de librería fue arquitectónica. Se descartó `graphene-django` justamente por su función más promocionada: derivar los tipos automáticamente desde los modelos del ORM, que acoplaría la capa web a la persistencia y dejaría los casos de uso de lado.

Lo que aporta GraphQL es la **consulta declarativa**: el cliente pide los campos que necesita y recibe eso y nada más.

```graphql
{ products { name } }              # solo el nombre
{ products { name price } }        # nombre y precio, sin tocar el servidor
```

---

## Un request de punta a punta

Creación de un producto, de principio a fin:

1. El request entra por la vista.
2. El serializer verifica la forma de los datos.
3. La vista construye el caso de uso y le pasa los datos.
4. El caso de uso construye la entidad. **Ahí corren las validaciones de negocio.**
5. Si todo está bien, le pide al repositorio que la guarde.
6. El adaptador de Django escribe en MySQL.
7. De vuelta: la entidad se serializa a JSON y se responde `201 Created`.

Los datos entran de afuera hacia adentro y salen de adentro hacia afuera, siempre respetando la misma regla.

---

## Manejo de errores

Los errores también se resuelven en un solo lugar, un handler global.

| Situación | Respuesta |
|---|---|
| Una regla de negocio no se cumple (precio negativo, nombre vacío) | `400` |
| El producto solicitado no existe | `404` |
| Un error no previsto | `500` |

Todas las respuestas de error salen con el mismo formato, de modo que quien consume la API siempre recibe la misma estructura:

```json
{
  "error": {
    "status": 400,
    "type": "InvalidPrice",
    "detail": "Price cannot be negative."
  }
}
```

El último caso importa: un error no previsto **no se disfraza de 400**. Devuelve `500`, como corresponde, para que quede claro que ahí hay un bug real que hay que revisar.

---

## En resumen

La lógica de negocio está en el centro y Django queda en la capa más externa. Si cambia la base de datos, o incluso el framework, el núcleo del sistema no se toca. Ese es el propósito de toda la arquitectura.

---

## Para seguir

| Recurso | Dónde |
|---|---|
| Instalación, endpoints y ejemplos | [`README.md`](../blob/main/README.md) del repositorio |
| El fundamento de cada decisión | [14 ADRs](../blob/main/docs/adrs/README.md) en `docs/adrs/` |
| Documentación interactiva de la API | Swagger UI en `/api/docs/` |
| Explorador de GraphQL | GraphiQL en `/graphql/` |
| Esquema OpenAPI | [`docs/openapi/schema.yaml`](../blob/main/docs/openapi/schema.yaml) |
