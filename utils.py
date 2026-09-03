from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def role_required(*allowed_roles):
    """
    Decorator que restringe o acesso a uma rota de acordo com o perfil
    do usuário logado (vendedor, repositor ou gerente).

    Deve ser usado SEMPRE junto com @login_required, e sempre depois dele:

        @app.route("/produtos/novo")
        @login_required
        @role_required("gerente")
        def novo_produto():
            ...

    Se o usuário logado não tiver um dos perfis permitidos, ele é
    redirecionado ao dashboard com uma mensagem de aviso, em vez de
    ver uma página de erro assustadora.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if current_user.role not in allowed_roles:
                flash("Você não tem permissão para acessar esta página.", "danger")
                return redirect(url_for("dashboard"))
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator