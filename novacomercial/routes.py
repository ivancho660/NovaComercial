
from flask import Blueprint, flash, redirect, render_template, request, url_for
from .repositories import ProductRepository, SaleRepository
from .services import ProductService, SaleService, ValidationError
from .product_api import (
    get_products_from_service,
    ProductServiceUnavailable
)

bp = Blueprint("main", __name__)

products = ProductRepository()
sales = SaleRepository()

product_service = ProductService(products)
sale_service = SaleService(products, sales)


def money(cents):
    return f"${cents / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@bp.app_context_processor
def inject_helpers():
    return {"money": money}


@bp.get("/")
def dashboard():
    inventory = products.inventory_summary()
    sale_summary = sales.summary()
    recent_sales = sales.list_all()[:5]

    return render_template(
        "dashboard.html",
        inventory=inventory,
        sale_summary=sale_summary,
        recent_sales=recent_sales,
        products_count=products.count()
    )


@bp.get("/products")
def product_list():
    service_available = True

    try:
        product_list_data = get_products_from_service()
    except ProductServiceUnavailable as error:
        flash(str(error), "error")
        product_list_data = None
        service_available = False

    return render_template(
        "products.html",
        products=product_list_data,
        service_available=service_available
    )

@bp.route("/products/new", methods=["GET", "POST"])
def product_new():
    if request.method == "POST":
        try:
            product_service.create(request.form)
            flash("Producto registrado correctamente.", "success")
            return redirect(url_for("main.product_list"))

        except ValidationError as error:
            flash(str(error), "error")

    return render_template("product_form.html", product=None)


@bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id):
    product = products.get(product_id)

    if product is None:
        flash("El producto solicitado no existe.", "error")
        return redirect(url_for("main.product_list"))

    if request.method == "POST":
        try:
            product_service.update(product_id, request.form)
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("main.product_list"))

        except ValidationError as error:
            flash(str(error), "error")

    return render_template("product_form.html", product=product)


@bp.get("/sales")
def sale_list():
    return render_template("sales.html", sales=sales.list_all())


@bp.route("/sales/new", methods=["GET", "POST"])
def sale_new():
    if request.method == "POST":
        try:
            sale_id = sale_service.create(request.form)
            flash(
                f"Venta #{sale_id} registrada. El inventario fue actualizado.",
                "success"
            )
            return redirect(url_for("main.sale_list"))

        except ValidationError as error:
            flash(str(error), "error")

    try:
        product_list_data = get_products_from_service()
        service_available = True

    except ProductServiceUnavailable as error:
        flash(str(error), "error")
        product_list_data = []
        service_available = False

    return render_template(
        "sale_form.html",
        products=product_list_data,
        service_available=service_available
    )
