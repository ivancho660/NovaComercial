
from pathlib import Path
import os
import sqlite3
import threading
import time

from flask import Flask, jsonify


def create_product_app():
    app = Flask(__name__)

    database = Path(
        os.environ.get(
            "NOVACOMERCIAL_DATABASE",
            str(
                Path(__file__).resolve().parent.parent
                / "instance"
                / "novacomercial.db"
            )
        )
    )

    @app.get("/health")
    def health():
        return jsonify({
            "service": "product-service",
            "status": "running",
            "thread": threading.current_thread().name
        }), 200

    @app.get("/api/products")
    def list_products():
        start_time = time.perf_counter()
        thread_name = threading.current_thread().name

        connection = None

        try:
            connection = sqlite3.connect(
                str(database),
                timeout=10
            )
            connection.row_factory = sqlite3.Row

            products = connection.execute(
                """
                SELECT id, name, category, price_cents, stock
                FROM products
                ORDER BY name COLLATE NOCASE
                """
            ).fetchall()

            elapsed = round(
                (time.perf_counter() - start_time) * 1000,
                2
            )

            app.logger.info(
                "Solicitud atendida | Hilo: %s | Productos: %s | Tiempo: %s ms",
                thread_name,
                len(products),
                elapsed
            )

            return jsonify({
                "service": "product-service",
                "thread": thread_name,
                "total_products": len(products),
                "response_time_ms": elapsed,
                "products": [dict(product) for product in products]
            }), 200

        except sqlite3.Error:
            app.logger.exception(
                "Error consultando los productos"
            )

            return jsonify({
                "error": "No fue posible consultar los productos"
            }), 500

        finally:
            if connection is not None:
                connection.close()

    return app


app = create_product_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
        threaded=True
    )
