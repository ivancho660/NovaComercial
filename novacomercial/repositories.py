from .db import get_db


class ProductRepository:
    """Encapsula las consultas SQL relacionadas con productos."""
    def list_all(self):
        return get_db().execute("SELECT * FROM products ORDER BY name COLLATE NOCASE").fetchall()

    def get(self, product_id):
        return get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    def create(self, name, category, price_cents, stock):
        db = get_db()
        cursor = db.execute(
            "INSERT INTO products (name, category, price_cents, stock) VALUES (?, ?, ?, ?)",
            (name, category, price_cents, stock),
        )
        db.commit()
        return cursor.lastrowid

    def update(self, product_id, name, category, price_cents, stock):
        db = get_db()
        cursor = db.execute(
            "UPDATE products SET name=?, category=?, price_cents=?, stock=? WHERE id=?",
            (name, category, price_cents, stock, product_id),
        )
        db.commit()
        return cursor.rowcount > 0

    def count(self):
        return get_db().execute("SELECT COUNT(*) FROM products").fetchone()[0]

    def inventory_summary(self):
        row = get_db().execute(
            "SELECT COALESCE(SUM(stock),0) AS units, COALESCE(SUM(stock * price_cents),0) AS value FROM products"
        ).fetchone()
        return dict(row)


class SaleRepository:
    """Encapsula el historial y persistencia transaccional de ventas."""
    def list_all(self):
        db = get_db()
        sales = db.execute("SELECT * FROM sales ORDER BY id DESC").fetchall()
        result = []
        for sale in sales:
            items = db.execute(
                "SELECT * FROM sale_items WHERE sale_id=? ORDER BY id", (sale["id"],)
            ).fetchall()
            result.append({"sale": sale, "items": items})
        return result

    def summary(self):
        db = get_db()
        row = db.execute("SELECT COUNT(*) AS count, COALESCE(SUM(total_cents),0) AS total FROM sales").fetchone()
        return dict(row)
