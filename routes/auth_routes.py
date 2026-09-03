from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User

# "auth" é o nome interno deste blueprint, usado em url_for("auth.login"), por exemplo.
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Se o usuário já estiver logado, não faz sentido mostrar a tela de login de novo.
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Bem-vindo(a), {user.name}!", "success")

            # Se o usuário tentou acessar uma página protegida antes de logar,
            # o Flask-Login guarda esse destino em "next" — assim, depois do
            # login, ele volta exatamente para onde queria ir.
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))