from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from models import db, Product, SearchLog

search_bp = Blueprint("search", __name__)


@search_bp.route("/busca")
@login_required
def search():
    """
    Busca produtos por nome, SKU ou categoria (busca parcial, sem
    diferenciar maiúsculas/minúsculas), e registra a busca no SearchLog
    para alimentar o relatório de produtos mais buscados (Fase 7).
    """
    query = request.args.get("q", "").strip()
    results = []

    if query:
        termo = f"%{query}%"

        # ilike = "LIKE" que ignora maiúsculas/minúsculas.
        # O "%" antes e depois do termo permite encontrar a palavra
        # em qualquer posição do texto (busca parcial).
        results = (
            Product.query.filter(
                db.or_(
                    Product.name.ilike(termo),
                    Product.sku.ilike(termo),
                    Product.category.ilike(termo),
                )
            )
            .order_by(Product.name)
            .all()
        )

        if results:
            # Registramos uma busca por PRODUTO ENCONTRADO. Isso permite,
            # na Fase 7, sabermos quantas vezes cada produto específico
            # apareceu como resultado de uma busca.
            for product in results:
                db.session.add(
                    SearchLog(
                        search_term=query,
                        product_id=product.id,
                        user_id=current_user.id,
                    )
                )
        else:
            # Nenhum resultado: registramos mesmo assim, com product_id
            # vazio, para sabermos o que as pessoas procuram e não encontram
            # (informação valiosa para decidir o que passar a estocar).
            db.session.add(
                SearchLog(
                    search_term=query,
                    product_id=None,
                    user_id=current_user.id,
                )
            )

        db.session.commit()

    return render_template("search/search.html", query=query, results=results)