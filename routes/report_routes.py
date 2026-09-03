from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from models import db, Product, SearchLog
from utils import role_required

reports_bp = Blueprint("reports", __name__, url_prefix="/relatorios")


@reports_bp.route("/")
@login_required
@role_required("gerente")
def index():
    # -----------------------------------------------------------------
    # 1) ESTOQUE BAIXO
    # -----------------------------------------------------------------
    # Reaproveitamos o método is_low_stock() que já existe no modelo Product.
    low_stock_products = [
        p for p in Product.query.order_by(Product.quantity).all() if p.is_low_stock()
    ]

    # -----------------------------------------------------------------
    # 2) PRODUTOS MAIS BUSCADOS
    # -----------------------------------------------------------------
    # Junta Product com SearchLog (JOIN), agrupa por produto (GROUP BY),
    # conta quantas vezes cada um aparece (COUNT), e ordena do mais para
    # o menos buscado. Isso responde: "quais produtos as pessoas mais
    # procuraram no sistema?"
    most_searched = (
        db.session.query(Product, func.count(SearchLog.id).label("total"))
        .join(SearchLog, SearchLog.product_id == Product.id)
        .group_by(Product.id)
        .order_by(func.count(SearchLog.id).desc())
        .limit(10)
        .all()
    )

    # -----------------------------------------------------------------
    # 3) BUSCAS SEM RESULTADO
    # -----------------------------------------------------------------
    # Lembra que, na Fase 5, quando uma busca não encontrava nada,
    # registrávamos um SearchLog com product_id=None? Aqui agrupamos
    # esses casos por termo buscado, para descobrir o que os funcionários
    # procuram e a loja ainda não tem cadastrado.
    not_found_searches = (
        db.session.query(SearchLog.search_term, func.count(SearchLog.id).label("total"))
        .filter(SearchLog.product_id.is_(None))
        .group_by(SearchLog.search_term)
        .order_by(func.count(SearchLog.id).desc())
        .limit(10)
        .all()
    )

    # -----------------------------------------------------------------
    # 4) OCUPAÇÃO POR LOCALIZAÇÃO
    # -----------------------------------------------------------------
    # Agrupa os produtos por corredor + depósito/área, contando quantos
    # produtos diferentes e quantas unidades no total existem em cada um.
    occupancy = (
        db.session.query(
            Product.aisle,
            Product.warehouse,
            func.count(Product.id).label("total_produtos"),
            func.sum(Product.quantity).label("total_unidades"),
        )
        .group_by(Product.aisle, Product.warehouse)
        .order_by(Product.aisle)
        .all()
    )

    return render_template(
        "reports/reports.html",
        low_stock_products=low_stock_products,
        most_searched=most_searched,
        not_found_searches=not_found_searches,
        occupancy=occupancy,
    )