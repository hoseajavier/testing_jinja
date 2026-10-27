# Run This Command to use
curl -fsSL https://raw.githubusercontent.com/Clickbait-Agency/flask/main/init_flask_monolith.py | python3 - --project-name my-project

# Flask Monolith Structure Guide

This guide shows how to build another Flask monolith using the same structure as this project.

The goal is not to split the app into microservices. The goal is to keep one deployable Flask application, but organize it clearly so each feature has its own routes, business logic, database access, templates, and schemas.

## Big Idea

A Flask monolith should be one application with clear internal layers:

```text
browser
  -> route
  -> service
  -> repository
  -> model/database
  -> service
  -> schema
  -> template or JSON response
```

Each layer has a job:

```text
routes.py       receives HTTP requests and returns responses
service.py      owns business rules and validation
repository.py   owns database queries and persistence
schemas.py      converts model objects into simple dictionaries
models/         defines database tables and relationships
templates/      renders HTML pages
static/         stores CSS, JavaScript, images, and frontend assets
core/           stores app-wide infrastructure
config/         stores app configuration
shared/         stores reusable constants, helpers, validators, and enums
```

This makes the app easy to grow because new features can be added as new modules without changing the whole project.

## Recommended Folder Structure

```text
project-root/
  run.py
  requirements.txt
  .env.example
  README.md
  guide.md

  app/
    __init__.py

    config/
      __init__.py
      settings.py

    core/
      __init__.py
      extensions.py
      database.py
      exceptions.py
      responses.py
      transactions.py
      auth/
        __init__.py
        decorators.py
        current_user.py
        client.py

    models/
      __init__.py
      mixins.py
      user.py
      employee.py
      product.py

    modules/
      __init__.py
      dashboard/
        __init__.py
        routes.py
        service.py
      inventory/
        __init__.py
        routes.py
        service.py
        repository.py
        schemas.py

    templates/
      base.html
      auth/
        login.html
      dashboard/
        index.html
      inventory/
        list.html
        detail.html
      errors/
        error.html

    static/
      css/
        app.css
      js/
        app-auth.js
      img/
        logo.webp

    shared/
      __init__.py
      constants/
        __init__.py
      enums/
        __init__.py
      helpers/
        __init__.py
      validators/
        __init__.py

  migrations/
    add_product_table.sql

  seeds/
    initial_roles.sql

  docs/
    ARCHITECTURE.md
    FEATURES.md
    CHANGELOG.md
```

## Root Files

### `run.py`

Starts the app. Keep this file small.

Example:

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
```

### `requirements.txt`

Lists Python dependencies.

Example:

```text
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Cors
python-dotenv
```

### `.env.example`

Shows required environment variables without real secrets.

Example:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/app_db
SECRET_KEY=change-me
AUTH_API_ORIGIN=http://localhost:8000
```

### `README.md`

Explains what the app is and how to run it.

### `guide.md`

Explains how the codebase is structured and how to add more features.

## `app/__init__.py`

This is the Flask application factory.

It creates the Flask app, loads configuration, initializes extensions, registers error handlers, and registers blueprints.

Example:

```python
from importlib import import_module

from flask import Flask

from app.config import Config
from app.core.extensions import cors, db, migrate
from app.core.responses import register_error_handlers


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    import_module("app.models")

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])

    register_error_handlers(app)
    register_blueprints(app)

    return app


def register_blueprints(app):
    from app.modules.dashboard.routes import dashboard_bp
    from app.modules.inventory.routes import inventory_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
```

Why this works:

- `create_app()` keeps startup predictable.
- `import_module("app.models")` makes sure models are loaded before migrations inspect metadata.
- Blueprints keep each feature module separate.
- Extensions are created outside the app, then initialized inside the factory.

## `app/config/`

Configuration belongs here.

### `app/config/settings.py`

Example:

```python
import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
```

Use config classes for values that change between local development, staging, and production.

## `app/core/`

`core/` is for app-wide infrastructure. It should not belong to one feature.

### `app/core/extensions.py`

Stores extension objects.

Example:

```python
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
```

Why this works:

- Models can import `db` without creating the Flask app.
- The app factory can initialize the extensions later.

### `app/core/exceptions.py`

Stores application exceptions.

Example:

```python
class AppError(Exception):
    status_code = 400

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class ValidationError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404
```

### `app/core/responses.py`

Stores shared error handling and response behavior.

Example:

```python
from flask import jsonify, render_template, request

from app.core.exceptions import AppError


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": error.message}), error.status_code

        return render_template("errors/error.html", message=error.message), error.status_code
```

### `app/core/auth/`

Stores authentication and authorization helpers.

Example files:

```text
decorators.py      route decorators like require_permission()
current_user.py    helpers for reading the current user
client.py          external auth API client, if the app uses one
```

Routes should use auth decorators, not duplicate auth checks manually.

## `app/models/`

Models define database tables and relationships.

Models are shared by all modules. A model should not be hidden inside a feature module if another module might need the same table.

### `app/models/mixins.py`

Example:

```python
from app.core.extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )
```

### `app/models/product.py`

Example:

```python
from app.core.extensions import db
from app.models.mixins import TimestampMixin


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, server_default="active")
```

### `app/models/__init__.py`

Import models here so migrations and the app factory can discover them.

Example:

```python
from app.models.product import Product
from app.models.user import User
```

## `app/modules/`

Feature code lives here.

Each module is a vertical feature area. For example:

```text
modules/
  inventory/
    routes.py
    service.py
    repository.py
    schemas.py
```

The module owns the workflow, but the database models still live in `app/models/`.

## Example Module: `inventory`

This example shows the full pattern.

### `app/modules/inventory/__init__.py`

Usually empty. It marks the folder as a Python package.

```python
```

### `app/modules/inventory/routes.py`

Routes receive HTTP requests.

Routes should:

- read query parameters or form data,
- call the service layer,
- render a template or redirect,
- stay thin.

Example:

```python
from flask import Blueprint, redirect, render_template, request, url_for

from app.core.auth.decorators import require_permission
from app.modules.inventory.service import InventoryService


inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.get("")
@require_permission("inventory", "products")
def list_products():
    search = request.args.get("q", "").strip() or None
    products = InventoryService.list_products(search=search)
    return render_template("inventory/list.html", products=products, search=search or "")


@inventory_bp.post("")
@require_permission("inventory", "products")
def create_product():
    product = InventoryService.create_product(request.form)
    return redirect(url_for("inventory.detail_product", product_id=product["id"], created="1"))


@inventory_bp.get("/<int:product_id>")
@require_permission("inventory", "products")
def detail_product(product_id):
    product = InventoryService.get_product(product_id)
    return render_template("inventory/detail.html", product=product)
```

### `app/modules/inventory/service.py`

Services contain business rules.

Services should:

- validate input,
- decide what is allowed,
- call repositories,
- raise app exceptions,
- return simple data for routes.

Example:

```python
from app.core.exceptions import NotFoundError, ValidationError
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import product_detail, product_summary


PRODUCT_STATUSES = {"active", "inactive"}


class InventoryService:
    @staticmethod
    def list_products(search=None):
        products = InventoryRepository.list(search=search)
        return [product_summary(product) for product in products]

    @staticmethod
    def get_product(product_id):
        product = InventoryRepository.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")

        return product_detail(product)

    @staticmethod
    def create_product(form_data):
        sku = (form_data.get("sku") or "").strip().upper()
        name = (form_data.get("name") or "").strip()
        status = (form_data.get("status") or "active").strip()

        if not sku:
            raise ValidationError("SKU is required")
        if not name:
            raise ValidationError("Product name is required")
        if status not in PRODUCT_STATUSES:
            raise ValidationError("Product status is not valid")
        if InventoryRepository.get_by_sku(sku):
            raise ValidationError("SKU already exists")

        product = InventoryRepository.create(
            {
                "sku": sku,
                "name": name,
                "status": status,
            }
        )
        return product_detail(product)
```

### `app/modules/inventory/repository.py`

Repositories contain database access.

Repositories should:

- query models,
- create records,
- update records,
- delete records,
- commit transactions when this project's pattern expects it.

Example:

```python
from sqlalchemy import or_

from app.core.extensions import db
from app.models.product import Product


class InventoryRepository:
    @staticmethod
    def get_by_id(product_id):
        return Product.query.get(product_id)

    @staticmethod
    def get_by_sku(sku):
        return Product.query.filter(Product.sku == sku).first()

    @staticmethod
    def list(search=None):
        query = Product.query

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(or_(Product.sku.ilike(term), Product.name.ilike(term)))

        return query.order_by(Product.name.asc()).all()

    @staticmethod
    def create(product_data):
        product = Product(**product_data)
        db.session.add(product)
        db.session.commit()
        return product
```

### `app/modules/inventory/schemas.py`

Schemas convert model objects into plain dictionaries.

This keeps templates and JSON responses away from raw SQLAlchemy objects when a simple structure is better.

Example:

```python
def product_summary(product):
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "status": product.status,
    }


def product_detail(product):
    return {
        **product_summary(product),
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }
```

## `app/templates/`

Templates store HTML.

Use folders that match module names:

```text
templates/
  base.html
  inventory/
    list.html
    detail.html
```

### `app/templates/base.html`

The base layout should contain shared HTML:

- page shell,
- navigation,
- CSS links,
- JavaScript links,
- common blocks.

Example:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{% block title %}Internal App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">
  </head>
  <body>
    <nav>
      <a href="{{ url_for('dashboard.index') }}">Dashboard</a>
      <a href="{{ url_for('inventory.list_products') }}">Inventory</a>
    </nav>

    <main>
      {% block content %}{% endblock %}
    </main>

    <script src="{{ url_for('static', filename='js/app-auth.js') }}"></script>
  </body>
</html>
```

### `app/templates/inventory/list.html`

Example:

```html
{% extends "base.html" %}

{% block title %}Inventory{% endblock %}

{% block content %}
  <h1>Inventory</h1>

  <form method="get">
    <input name="q" value="{{ search }}" placeholder="Search products">
    <button type="submit">Search</button>
  </form>

  <ul>
    {% for product in products %}
      <li>
        <a href="{{ url_for('inventory.detail_product', product_id=product.id) }}">
          {{ product.sku }} - {{ product.name }}
        </a>
      </li>
    {% endfor %}
  </ul>
{% endblock %}
```

## `app/static/`

Static files are public assets served by Flask.

```text
static/
  css/
    app.css
  js/
    app-auth.js
  img/
    logo.webp
```

Use this folder for:

- CSS,
- JavaScript,
- images,
- favicons,
- small frontend assets.

Avoid putting Python files or private data here.

## `app/shared/`

`shared/` is for reusable code that is not app infrastructure and does not belong to one feature.

Use it for:

```text
constants/     values reused across modules
enums/         shared enum-like values
helpers/       small formatting or utility helpers
validators/    reusable validation functions
```

Example:

```python
ACTIVE_STATUSES = {"active", "inactive"}
```

Do not put feature-specific business logic in `shared/`. If only `inventory` uses it, keep it in `modules/inventory/`.

## `migrations/`

Use this for database migration files.

In this project, migrations include SQL files such as:

```text
migrations/
  alter_ticket_statuses.sql
  add_product_table.sql
```

Example:

```sql
create table products (
  id serial primary key,
  sku text not null unique,
  name text not null,
  status text not null default 'active',
  created_at timestamp not null default now(),
  updated_at timestamp not null default now()
);
```

## `seeds/`

Use this for initial data.

Examples:

```text
seeds/
  initial_roles.sql
  phase1_rbac.sql
```

Seed files are useful for:

- default roles,
- default permissions,
- required lookup data,
- local development bootstrap data.

## `docs/`

Use docs for long-term project knowledge.

Recommended files:

```text
docs/
  ARCHITECTURE.md
  FEATURES.md
  CHANGELOG.md
  PRE_PUSH_CHECKLIST.md
```

`guide.md` explains structure. `docs/` explains current product behavior and project history.

## How To Add A New Feature Module

Example: adding `inventory`.

### 1. Add the model

Create:

```text
app/models/product.py
```

Then import it in:

```text
app/models/__init__.py
```

### 2. Add the module folder

Create:

```text
app/modules/inventory/
  __init__.py
  routes.py
  service.py
  repository.py
  schemas.py
```

### 3. Add templates

Create:

```text
app/templates/inventory/
  list.html
  detail.html
```

### 4. Register the blueprint

Edit `app/__init__.py`:

```python
def register_blueprints(app):
    from app.modules.inventory.routes import inventory_bp

    app.register_blueprint(inventory_bp)
```

### 5. Add navigation

Edit `app/templates/base.html` and add a link to the module.

Example:

```html
<a href="{{ url_for('inventory.list_products') }}">Inventory</a>
```

If the app uses permission-aware navigation, also add the page/sub-page permissions to the database seed or admin page catalog.

### 6. Add migrations and seeds

Create migration SQL for new tables.

Create seed SQL if the feature needs default permissions or lookup data.

### 7. Test the flow

Check:

```text
GET /inventory
POST /inventory
GET /inventory/<id>
```

Verify:

- route receives request correctly,
- service validates form data,
- repository queries and commits correctly,
- schema returns expected fields,
- template renders expected data,
- permissions allow the correct users only.

## Request Flow Example

When a user opens `/inventory`, this is what happens:

```text
1. Browser sends GET /inventory
2. inventory.routes.list_products() handles the request
3. Route reads request.args["q"]
4. Route calls InventoryService.list_products(search=q)
5. Service calls InventoryRepository.list(search=q)
6. Repository queries Product
7. Service converts Product models with product_summary()
8. Route renders templates/inventory/list.html
9. Browser receives HTML
```

When a user submits the create form:

```text
1. Browser sends POST /inventory
2. inventory.routes.create_product() receives request.form
3. Route calls InventoryService.create_product(request.form)
4. Service validates sku, name, status, and duplicate SKU
5. Service calls InventoryRepository.create(product_data)
6. Repository creates Product and commits db.session
7. Service returns product_detail(product)
8. Route redirects to /inventory/<id>?created=1
```

## Layer Rules

Use these rules to keep the monolith clean.

### Routes

Routes can:

- read `request.args`,
- read `request.form`,
- call services,
- render templates,
- redirect,
- return JSON.

Routes should not:

- contain business rules,
- build complex database queries,
- commit database transactions directly,
- format large response objects manually.

### Services

Services can:

- validate input,
- enforce business rules,
- call repositories,
- combine data from multiple repositories,
- raise `ValidationError` or `NotFoundError`,
- choose schemas.

Services should not:

- import Flask `request`,
- render templates,
- know HTML details,
- contain raw SQL unless there is no better place.

### Repositories

Repositories can:

- query SQLAlchemy models,
- add records,
- update records,
- delete records,
- commit database changes.

Repositories should not:

- render templates,
- decide user-facing messages,
- contain request-specific logic,
- know about form fields unless the service passes them in.

### Schemas

Schemas can:

- convert model objects into dictionaries,
- select fields for list/detail views,
- normalize display values.

Schemas should not:

- query the database,
- commit changes,
- validate form input,
- read Flask request data.

### Models

Models can:

- define tables,
- define columns,
- define relationships,
- provide small model-level properties.

Models should not:

- know about routes,
- render templates,
- call services,
- contain page-specific behavior.

## Naming Conventions

Use consistent names:

```text
Blueprint name: inventory
URL prefix:     /inventory
Module folder:  app/modules/inventory/
Templates:      app/templates/inventory/
Model:          Product
Repository:     InventoryRepository
Service:        InventoryService
Schema:         product_summary(), product_detail()
```

Route endpoint names come from the blueprint and function name:

```python
url_for("inventory.list_products")
url_for("inventory.detail_product", product_id=product.id)
```

## Common Mistakes To Avoid

Avoid putting everything in `routes.py`.

Avoid importing `db` and committing from templates or route helpers.

Avoid making one large `service.py` for the whole app. Use one service file per feature module.

Avoid putting every helper in `shared/`. Shared code should be truly shared.

Avoid duplicating table definitions inside modules. Put SQLAlchemy models in `app/models/`.

Avoid skipping schemas for complex pages. Templates become easier to read when they receive simple dictionaries.

## Small Module Checklist

Use this checklist when adding a module:

```text
[ ] Model exists in app/models/
[ ] Model is imported in app/models/__init__.py
[ ] Module folder exists in app/modules/<feature>/
[ ] routes.py defines a Blueprint
[ ] routes.py calls service methods
[ ] service.py validates and applies business rules
[ ] repository.py owns database queries
[ ] schemas.py formats output data
[ ] Templates exist in app/templates/<feature>/
[ ] Blueprint is registered in app/__init__.py
[ ] Navigation is updated in base.html
[ ] Permissions are seeded or configured
[ ] Migration exists for new tables
[ ] Manual browser flow is tested
```

## Simple Mental Model

Think of the monolith like this:

```text
app/__init__.py starts the app.
core/ makes Flask, database, auth, and errors work.
models/ describes the database.
modules/ describes what users can do.
templates/ describes what users see.
static/ describes how the frontend looks and behaves.
shared/ holds small reusable pieces.
migrations/ changes the database.
seeds/ fills required starting data.
docs/ explains the product and architecture.
```

That is the whole structure. Keep each feature inside its module, keep shared infrastructure in `core/`, keep shared database tables in `models/`, and the monolith can grow without turning into one giant file.
