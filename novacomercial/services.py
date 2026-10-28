from .db import get_db
from .repositories import ProductRepository, SaleRepository


class ValidationError(ValueError):
    pass


def parse_product_form(form):
    name = form.get("name", "").strip()
    category = form.get("category", "").strip()
    price_text = form.get("price", "").strip().replace(",", ".")
    stock_text = form.get("stock", "").strip()
    if not name or not category:
        raise ValidationError("El nombre y la categoría son obligatorios.")
    try:
        price_float = float(price_text)
        if not price_float >= 0 or price_float == float("inf"):
            raise ValueError
        price_cents = round(price_float * 100)
    except (ValueError, TypeError):
        raise ValidationError("El precio debe ser un número válido igual o mayor que cero.")
    try:
        if not stock_text or any(c in stock_text for c in ".,-"):
            raise ValueError
        stock = int(stock_text)
        if stock < 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValidationError("La cantidad disponible debe ser un entero igual o mayor que cero.")
    return name, category, price_cents, stock


class ProductService:
    def __init__(self, repository=None):
        self.repository = repository or ProductRepository()

    def create(self, form):
        return self.repository.create(*parse_product_form(form))

    def update(self, product_id, form):
        values = parse_product_form(form)
        if not self.repository.update(product_id, *values):
            raise ValidationError("El producto no existe.")


class SaleService:
    def __init__(self, product_repository=None, sale_repository=None):
        self.products = product_repository or ProductRepository()
        self.sales = sale_repository or SaleRepository()

    def create(self, form):
        # Convierte los campos repetidos product_id / quantity en líneas de venta.
        product_ids = form.getlist("product_id")
        quantities = form.getlist("quantity")
        if not product_ids or len(product_ids) != len(quantities):
            raise ValidationError("Agrega al menos un producto con una cantidad válida.")
        lines = {}
        for raw_id, raw_qty in zip(product_ids, quantities):
            if not raw_id and not raw_qty:
                continue
            try:
                product_id, quantity = int(raw_id), int(raw_qty)
                if product_id <= 0 or quantity <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValidationError("Selecciona un producto y una cantidad entera mayor que cero.")
            lines[product_id] = lines.get(product_id, 0) + quantity
        if not lines:
            raise ValidationError("Agrega al menos un producto a la venta.")

        db = get_db()
        try:
            db.execute("BEGIN IMMEDIATE")
            total = 0
            prepared = []
            for product_id, quantity in lines.items():
                product = db.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
                if product is None:
                    raise ValidationError("Uno de los productos seleccionados ya no existe.")
                if quantity > product["stock"]:
                    raise ValidationError(
                        f'Inventario insuficiente para "{product["name"]}". Disponible: {product["stock"]}; solicitado: {quantity}.'
                    )
                subtotal = product["price_cents"] * quantity
                total += subtotal
                prepared.append((product, quantity, subtotal))

            cursor = db.execute("INSERT INTO sales (total_cents) VALUES (?)", (total,))
            sale_id = cursor.lastrowid
            for product, quantity, subtotal in prepared:
                updated = db.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
                    (quantity, product["id"], quantity),
                )
                if updated.rowcount != 1:
                    raise ValidationError(f'Inventario insuficiente para "{product["name"]}".')
                db.execute(
                    "INSERT INTO sale_items (sale_id, product_id, product_name, quantity, unit_price_cents, subtotal_cents) VALUES (?, ?, ?, ?, ?, ?)",
                    (sale_id, product["id"], product["name"], quantity, product["price_cents"], subtotal),
                )
            db.commit()
            return sale_id
        except Exception:
            db.rollback()
            raise
