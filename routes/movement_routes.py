from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db, Product, Movement
from utils import role_required

movements_bp = Blueprint("movements", __name__)


@movements_bp.route("/produtos/<int:product_id>/movimentar", methods=["GET", "POST"])
@login_required
@role_required("gerente", "repositor")
def register(product_id):
    """Registra uma entrada, saída ou transferência para um produto específico."""
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        movement_type = request.form.get("movement_type")
        errors = []

        if movement_type not in ("entrada", "saida", "transferencia"):
            errors.append("Selecione um tipo de movimentação válido.")
            return render_template("movements/form.html", product=product)

        previous_quantity = product.quantity
        new_quantity = previous_quantity
        quantity_change = 0
        previous_location = None

        # --- Entrada ou Saída: mexe na QUANTIDADE ---
        if movement_type in ("entrada", "saida"):
            quantity_raw = request.form.get("quantity", "").strip()
            try:
                quantity = int(quantity_raw)
                if quantity <= 0:
                    errors.append("A quantidade deve ser maior que zero.")
            except ValueError:
                errors.append("A quantidade deve ser um número inteiro.")
                quantity = 0

            if movement_type == "entrada":
                quantity_change = quantity
                new_quantity = previous_quantity + quantity
            else:  # saida
                if quantity > previous_quantity:
                    errors.append(
                        f"Não é possível registrar saída de {quantity} unidades: "
                        f"só há {previous_quantity} em estoque."
                    )
                quantity_change = -quantity
                new_quantity = previous_quantity - quantity

        # --- Transferência: mexe na LOCALIZAÇÃO ---
        else:
            new_aisle = request.form.get("aisle", "").strip()
            new_shelf = request.form.get("shelf", "").strip()
            new_section = request.form.get("section", "").strip() or None
            new_warehouse = request.form.get("warehouse", "").strip() or "Loja"

            if not new_aisle or not new_shelf:
                errors.append("Informe corredor e prateleira de destino para a transferência.")
            else:
                previous_location = product.location_display()

        if errors:
            for erro in errors:
                flash(erro, "danger")
            return render_template("movements/form.html", product=product)

        # Cria o registro de movimentação (o histórico permanente)
        movement = Movement(
            product_id=product.id,
            user_id=current_user.id,
            movement_type=movement_type,
            quantity_change=quantity_change,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            previous_location=previous_location,
            notes=request.form.get("notes", "").strip() or None,
        )

        # Aplica a mudança de fato no produto
        product.quantity = new_quantity

        if movement_type == "transferencia":
            product.aisle = new_aisle
            product.shelf = new_shelf
            product.section = new_section
            product.warehouse = new_warehouse
            movement.new_location = product.location_display()

        db.session.add(movement)
        db.session.commit()

        flash(f"Movimentação de {movement_type} registrada com sucesso para '{product.name}'.", "success")
        return redirect(url_for("products.detail", product_id=product.id))

    return render_template("movements/form.html", product=product)


@movements_bp.route("/movimentacoes")
@login_required
def list_movements():
    """Histórico geral das últimas movimentações registradas no sistema."""
    movements = Movement.query.order_by(Movement.timestamp.desc()).limit(100).all()
    return render_template("movements/list.html", movements=movements)