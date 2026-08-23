# ADR 0002: Clean Architecture como arquitectura del proyecto

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

La actividad evalúa la organización del código. Un proyecto Django armado con la estructura por defecto termina con las reglas de negocio repartidas entre `models.py` (validaciones en el modelo del ORM), `serializers.py` (validaciones de formulario) y `views.py` (todo lo demás). Funciona, pero deja el negocio atado a Django: no se puede probar sin base de datos ni razonar sobre las reglas sin tener el framework delante.

El objetivo es que las reglas de producto vivan en un solo lugar, se puedan leer sin conocer Django y se puedan probar sin levantar nada.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Estructura estándar de Django (MTV) | Cero fricción, es lo que espera cualquiera que abra el repositorio | El negocio queda disperso y acoplado al ORM; no se puede testear sin DB |
| Capas por tipo (`models/`, `services/`, `views/`) | Separa un poco, sigue siendo familiar | La capa de "services" acumula todo lo que no encaja en otro lado y nada garantiza la dirección de las dependencias |
| **Arquitectura hexagonal** (puertos y adaptadores, Cockburn) | Aísla el núcleo detrás de puertos; es el mismo principio y más simple de explicar | Define un solo borde entre "dentro" y "fuera": no distingue entidades de casos de uso, y esa distinción es justamente la que se quiere marcar |
| **Clean Architecture** (Martin) | Capas concéntricas con la regla de dependencia explícita; separa entidades de casos de uso; el dominio queda aislado y testeable | Más archivos y más indirección de la que un CRUD de una entidad necesita; la regla no la impone el lenguaje |
| Vertical slices por caso de uso | Cada feature autocontenida | Duplica el andamiaje en cada slice y con un solo agregado no aporta ventaja |

## Decisión

Se adopta **Clean Architecture**, el modelo de capas concéntricas de Robert C. Martin, empleando **puertos y adaptadores** como mecanismo para cruzar los bordes.

Frente a la arquitectura hexagonal —que comparte el principio y es su antecedente directo— Clean Architecture aporta la distinción entre el anillo de entidades y el de casos de uso. Esa separación es la que este proyecto necesita explicitar: las reglas de `Product` valen por sí solas, mientras que "obtener un producto o fallar con 404" es una regla de aplicación, y cada una vive en su propia capa.

Lo que define la decisión es la **regla de dependencia** (*Dependency Rule*): las dependencias del código fuente apuntan siempre hacia el interior. `shared/domain ← domain ← application ← infra/api`. Las capas internas no conocen a las externas.

Donde el flujo de control necesita cruzar un borde hacia afuera, se aplica el **principio de inversión de dependencias** (*DIP*): la capa interna declara la interfaz —el puerto— y la externa aporta el adaptador que la implementa.

```
shared/domain/    Kernel compartido: excepciones base. Python puro.
products/
├── domain/       Entidad Product + excepciones de validación. Sin imports de Django.
├── application/  Puerto del repositorio (ABC) + casos de uso. Solo depende de domain.
├── infra/        Modelo del ORM + repositorio concreto. Único lugar que toca el ORM.
└── api/          Serializers + vistas + rutas. Sin reglas de negocio.
config/           settings, urls y el handler global de errores.
```

Los dos anillos internos concentran el valor del diseño: `domain` contiene las reglas que seguirían siendo ciertas aunque no existieran ni la API ni la base de datos; `application` orquesta esas reglas en casos de uso. Django, MySQL y HTTP quedan en el anillo exterior, el de los detalles, y se conectan a través de las interfaces que declara la capa interna ([ADR 0006](0006-puerto-del-repositorio-en-application.md)).

La organización es por feature (`products/`) y dentro de cada feature por capa, no a la inversa. Incorporar una segunda entidad implica agregar una carpeta hermana, no modificar cuatro carpetas transversales.

## Consecuencias

- Un CRUD de una sola entidad queda con más archivos de los que necesitaría. Es el costo aceptado a cambio de que el negocio resulte legible y testeable por separado.
- El aislamiento del dominio no lo garantiza el lenguaje: es una convención que hay que sostener. Por eso existe un test que falla si aparece un import de Django en `domain` o `application` ([ADR 0012](0012-tests-unitarios-sin-django.md)).
- Sustituir MySQL por otro motor, o el ORM de Django por SQLAlchemy, afecta únicamente a `products/infra/`.
- Django espera encontrar los modelos en `products/models.py`. Como el modelo real vive en `products/infra/models.py`, se requiere un shim en `products/models.py` que lo re-exporte para que el registro de apps lo detecte. Es una concesión al framework, contenida en un archivo de una línea.
