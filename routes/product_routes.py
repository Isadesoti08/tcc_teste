import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename

from models import db, Product
from utils import role_required

products_bp = Blueprint("products", __name__, url_prefix="/produtos")


def _allowed_file(filename):
    """Verifica se a extensão do arquivo enviado é uma imagem permitida."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def _save_photo(photo, sku):
    """Salva a foto enviada em static/uploads/ e devolve o nome do arquivo salvo."""
    filename = secure_filename(f"{sku}_{photo.filename}")
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    photo.save(filepath)
    return filename


def _validar_dados(form, product_id_atual=None):
    """
    Valida os dados enviados pelo formulário de produto.
    Devolve uma lista de mensagens de erro (vazia se estiver tudo certo).
    """
    errors = []

    if not form.get("name", "").strip():
        errors.append("O nome do produto é obrigatório.")

    sku = form.get("sku", "").strip().upper()
    if not sku:
        errors.append("O código SKU é obrigatório.")
    else:
        existente = Product.query.filter_by(sku=sku).first()
        if existente and existente.id != product_id_atual:
            errors.append(f"Já existe um produto cadastrado com o SKU '{sku}'.")

    if not form.get("category", "").strip():
        errors.append("A categoria é obrigatória.")

    if not form.get("aisle", "").strip():
        errors.append("O corredor é obrigatório.")

    if not form.get("shelf", "").strip():
        errors.append("A prateleira é obrigatória.")

    quantity_raw = form.get("quantity", "").strip()
    try:
        quantity = int(quantity_raw)
        if quantity < 0:
            errors.append("A quantidade não pode ser negativa.")
    except ValueError:
        errors.append("A quantidade deve ser um número inteiro.")

    return errors


@products_bp.route("/")
@login_required
def list_products():
    """Lista todos os produtos cadastrados, ordenados por nome."""
    products = Product.query.order_by(Product.name).all()
    return render_template("products/list.html", products=products)


@products_bp.route("/<int:product_id>")
@login_required
def detail(product_id):
    """Mostra os detalhes completos de um único produto."""
    product = Product.query.get_or_404(product_id)
    return render_template("products/detail.html", product=product)


@products_bp.route("/novo", methods=["GET", "POST"])
@login_required
@role_required("gerente")
def create():
    """Formulário de cadastro de um novo produto."""
    if request.method == "POST":
        errors = _validar_dados(request.form)

        if errors:
            for erro in errors:
                flash(erro, "danger")
            return render_template("products/form.html", product=None, form_data=request.form)

        product = Product(
            name=request.form.get("name").strip(),
            sku=request.form.get("sku").strip().upper(),
            category=request.form.get("category").strip(),
            aisle=request.form.get("aisle").strip(),
            shelf=request.form.get("shelf").strip(),
            section=request.form.get("section", "").strip() or None,
            warehouse=request.form.get("warehouse", "").strip() or "Loja",
            quantity=int(request.form.get("quantity")),
        )

        photo = request.files.get("photo")
        if photo and photo.filename:
            if _allowed_file(photo.filename):
                product.photo_filename = _save_photo(photo, product.sku)
            else:
                flash("Formato de imagem não permitido. Use PNG, JPG, JPEG ou GIF.", "warning")

        db.session.add(product)
        db.session.commit()
        flash(f"Produto '{product.name}' cadastrado com sucesso!", "success")
        return redirect(url_for("products.list_products"))

    return render_template("products/form.html", product=None, form_data=None)


@products_bp.route("/<int:product_id>/editar", methods=["GET", "POST"])
@login_required
@role_required("gerente")
def edit(product_id):
    """Formulário de edição de um produto existente."""
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        errors = _validar_dados(request.form, product_id_atual=product.id)

        if errors:
            for erro in errors:
                flash(erro, "danger")
            return render_template("products/form.html", product=product, form_data=request.form)

        product.name = request.form.get("name").strip()
        product.sku = request.form.get("sku").strip().upper()
        product.category = request.form.get("category").strip()
        product.aisle = request.form.get("aisle").strip()
        product.shelf = request.form.get("shelf").strip()
        product.section = request.form.get("section", "").strip() or None
        product.warehouse = request.form.get("warehouse", "").strip() or "Loja"
        product.quantity = int(request.form.get("quantity"))

        photo = request.files.get("photo")
        if photo and photo.filename:
            if _allowed_file(photo.filename):
                product.photo_filename = _save_photo(photo, product.sku)
            else:
                flash("Formato de imagem não permitido. Use PNG, JPG, JPEG ou GIF.", "warning")

        db.session.commit()
        flash(f"Produto '{product.name}' atualizado com sucesso!", "success")
        return redirect(url_for("products.list_products"))

    return render_template("products/form.html", product=product, form_data=None)


@products_bp.route("/<int:product_id>/excluir", methods=["POST"])
@login_required
@role_required("gerente")
def delete(product_id):
    """Exclui um produto do sistema."""
    product = Product.query.get_or_404(product_id)
    nome = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f"Produto '{nome}' excluído com sucesso.", "info")
    return redirect(url_for("products.list_products"))