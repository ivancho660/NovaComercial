# NovaComercial

NovaComercial es un prototipo académico de aplicación web para gestionar productos, inventario y ventas. Está desarrollado con Python y Flask, utiliza SQLite para la persistencia y presenta la interfaz mediante plantillas HTML con Jinja y estilos CSS.

## Objetivo académico

Servir como ejercicio de Arquitectura de Software para identificar la separación entre presentación, reglas de negocio y persistencia de datos en una aplicación web pequeña.

## Funcionalidades implementadas

Según el código de la aplicación, permite:

- Consultar un panel con resumen del inventario y de las ventas.
- Registrar productos con nombre, categoría, precio y existencias.
- Consultar y editar productos existentes.
- Registrar ventas con uno o varios productos.
- Calcular los subtotales y el total de cada venta.
- Descontar del inventario las unidades vendidas.
- Rechazar cantidades inválidas y ventas que superen las existencias disponibles.
- Consultar el historial de ventas y el detalle de cada venta.
- Conservar en los detalles de venta el nombre y el precio usados al momento de la operación.

## Tecnologías

- Python
- Flask
- SQLite (`sqlite3`, incluido en Python)
- HTML y plantillas Jinja
- CSS
- Git y GitHub para control de versiones y publicación del código

Las dependencias de Python declaradas se encuentran en `requirements.txt`. Gunicorn está incluido para un posible uso en entornos Linux; no es necesario para ejecutar localmente con el servidor de desarrollo de Flask.

## Estructura del proyecto

```text
NovaComercial/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── novacomercial/
    ├── __init__.py
    ├── db.py
    ├── repositories.py
    ├── routes.py
    ├── services.py
    ├── static/
    │   └── styles.css
    └── templates/
        ├── base.html
        ├── dashboard.html
        ├── products.html
        ├── product_form.html
        ├── sales.html
        └── sale_form.html
```

La carpeta `instance/` se crea al iniciar la aplicación y almacena la base de datos local `novacomercial.db`. La base de datos no se incluye en el repositorio de código: cada instalación la crea automáticamente.

### Responsabilidad de los módulos

- `app.py`: punto de entrada para iniciar la aplicación local.
- `novacomercial/__init__.py`: contiene `create_app()`, configura Flask, prepara la carpeta de instancia, inicializa la base de datos y registra el blueprint.
- `novacomercial/routes.py`: define las rutas HTTP y coordina formularios, mensajes y renderizado de páginas.
- `novacomercial/services.py`: valida los datos y aplica las reglas de negocio para productos y ventas.
- `novacomercial/repositories.py`: encapsula consultas SQL para productos y ventas.
- `novacomercial/db.py`: gestiona la conexión SQLite, el esquema y el cierre de la conexión.
- `novacomercial/templates/`: contiene las plantillas HTML renderizadas con Jinja.
- `novacomercial/static/styles.css`: contiene los estilos de presentación.

## Arquitectura y patrones identificables

La aplicación utiliza una estructura de monolito modular con responsabilidades separadas:

1. **Presentación y HTTP:** rutas en `routes.py` y plantillas en `templates/`.
2. **Reglas de negocio:** servicios en `services.py`.
3. **Persistencia:** repositorios en `repositories.py` y conexión/esquema en `db.py`.

### Repository

`ProductRepository` y `SaleRepository`, definidos en `repositories.py`, encapsulan consultas y operaciones de persistencia. Los servicios usan estos repositorios para las operaciones de productos y para consultar ventas. La creación de ventas también utiliza la conexión SQLite directamente para ejecutar una transacción que incluye la cabecera, los detalles y la actualización del inventario.

### Application Factory

`create_app()` en `novacomercial/__init__.py` es una función fábrica de la aplicación Flask: configura la instancia y registra las rutas. Esta es una forma de organización habitual en Flask; no debe describirse automáticamente como una implementación completa del patrón GoF *Factory Method*.

No se identifican en el código revisado otros patrones GoF que deban declararse como implementados.

## Requisitos previos

- Windows 10/11 u otro sistema compatible con Python.
- Python instalado y disponible desde la terminal. En Windows puede comprobarse con `py --version`.
- `pip`, incluido normalmente con Python.
- Un navegador web moderno.

## Instalación en Windows (PowerShell o terminal de VS Code)

1. Descarga o clona el repositorio y abre la carpeta del proyecto en la terminal. Sitúate en la carpeta que contiene `app.py` y `requirements.txt`.

2. Comprueba Python:

   ```powershell
   py --version
   ```

3. Crea el entorno virtual:

   ```powershell
   py -m venv .venv
   ```

4. Activa el entorno virtual:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación, puedes permitirla solo para la sesión actual y volver a intentarlo:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

5. Instala las dependencias declaradas:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

6. Inicia la aplicación:

   ```powershell
   python app.py
   ```

7. Abre en el navegador la dirección local que indique Flask; normalmente:

   `http://127.0.0.1:5000`

Para detener el servidor, pulsa `Ctrl+C` en la terminal.

## Base de datos

Al crear la aplicación, `init_db()` en `novacomercial/db.py` crea la carpeta de instancia si hace falta y ejecuta el esquema SQL con `CREATE TABLE IF NOT EXISTS`. La base de datos predeterminada está en:

`instance/novacomercial.db`

En una instalación nueva, las tablas se crean automáticamente, pero no se cargan productos ni ventas de ejemplo. Puedes registrar datos de prueba desde la interfaz. La base de datos local se excluye de Git para evitar publicar accidentalmente registros de una máquina de desarrollo.

## Pruebas

El ZIP revisado no contiene una suite de pruebas automatizadas. Las comprobaciones siguientes son pruebas manuales sugeridas; deben ejecutarse y registrarse antes de afirmar que pasaron:

1. Inicia la aplicación y verifica que carga el panel principal.
2. Registra un producto con nombre, categoría, precio y existencias.
3. Consulta el producto y edita uno de sus campos.
4. Registra una venta de una cantidad menor que las existencias y verifica que el inventario disminuya.
5. Intenta vender más unidades de las disponibles y confirma que la operación se rechaza sin descontar existencias.
6. Registra una venta con varios productos y verifica el total.
7. Envía datos inválidos, como nombre vacío, precio negativo o cantidad no entera, y comprueba los mensajes de validación.
8. Detén y reinicia la aplicación y verifica que los registros locales persisten.

Estas instrucciones no significan que todas las pruebas hayan sido ejecutadas en este repositorio.

## Limitaciones conocidas

- Es un prototipo académico y no incluye autenticación ni gestión de roles.
- No implementa facturación electrónica, impuestos ni devoluciones.
- No se encontraron pruebas automatizadas en los archivos revisados.
- La aplicación usa SQLite local. Para una implementación multiusuario de producción, debe evaluarse la concurrencia, el respaldo de datos y las necesidades de despliegue.
- La aplicación usa una clave secreta predeterminada para desarrollo si no se define `SECRET_KEY`. Antes de cualquier despliegue real, debe configurarse una clave aleatoria y privada mediante una variable de entorno.
- El servidor integrado de Flask es para desarrollo, no para producción.

## Autoría académica

Proyecto desarrollado como prototipo académico para la asignatura de Arquitectura de Software de la Tecnológica del Oriente.

Completa aquí el nombre del autor o los integrantes tal como deban aparecer en la entrega académica.

## Licencia

No se especifica una licencia en esta versión. Si el proyecto se publicará para reutilización por terceros, debe elegirse y añadirse una licencia explícita.
