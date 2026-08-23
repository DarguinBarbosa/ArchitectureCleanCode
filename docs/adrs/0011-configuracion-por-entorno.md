# ADR 0011: Configuración por variables de entorno con python-decouple

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

`settings.py` está versionado. Ahí viven la `SECRET_KEY`, la contraseña de la base y el flag `DEBUG`. Dejar esos valores escritos en el archivo significa commitear credenciales, y además obliga a que todos los entornos compartan la misma configuración o a parchear el archivo en cada máquina.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Valores literales en `settings.py` | Funciona sin instalar nada | Credenciales en el repositorio. Descartado de entrada |
| `os.environ` directo | Sin dependencias | Sin casteo ni defaults; hay que exportar las variables a mano en cada shell |
| `settings_local.py` no versionado | Patrón conocido en Django | Un archivo Python fuera del repo que igual puede terminar commiteado por error |
| `python-decouple` con `.env` | Lee `.env` o el entorno real, castea tipos, admite defaults | Una dependencia más |
| `django-environ` | Más features, `DATABASE_URL` en una sola variable | Más superficie de la necesaria para seis variables |

## Decisión

**python-decouple**, leyendo un `.env` en la raíz que no está versionado.

```python
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

Dos criterios en cómo se declara cada variable:

`SECRET_KEY` va **sin default**. Si falta, la app no arranca. Un default de conveniencia es exactamente el que termina en producción.

`DEBUG` va con `default=False`. El default inseguro sería `True`, así que el valor por omisión es el que no expone tracebacks.

El repositorio incluye `.env.example` con la lista completa de variables y valores de relleno. Es la documentación de qué hace falta configurar. El `.gitignore` excluye `.env` y `.env.*` pero mantiene la excepción para `.env.example`.

Decouple busca primero en las variables de entorno del proceso y después en el `.env`, así que el mismo código sirve en desarrollo con archivo y en un contenedor con variables inyectadas, sin cambiar nada.

## Consecuencias

- Clonar el repo y correrlo requiere copiar `.env.example` a `.env` y completarlo. Está en el README.
- No hay credenciales en el historial de git.
- Si falta una variable sin default, el arranque falla con `UndefinedValueError` diciendo cuál. Es un error claro y temprano, mejor que un fallo raro más adelante.
- Agregar una variable nueva obliga a actualizar `.env.example` también, o el próximo que clone se queda trabado.
