from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Objeto "db" é a ponte entre nossos modelos Python e o banco SQLite.
# Ele é inicializado (conectado à aplicação) dentro do app.py.
db = SQLAlchemy()


class User(db.Model, UserMixin):
    """Representa um usuário do sistema: vendedor, repositor ou gerente."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Perfil do usuário: "vendedor", "repositor" ou "gerente".
    # Usamos uma string simples em vez de uma tabela separada de perfis
    # porque, para um protótipo de TCC, isso mantém o código mais direto
    # sem perder a clareza.
    role = db.Column(db.String(20), nullable=False, default="vendedor")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento: um usuário pode ter registrado várias movimentações.
    # "backref" cria automaticamente um atributo "user" dentro de Movement,
    # para acessarmos o usuário a partir de uma movimentação também.
    movements = db.relationship("Movement", backref="user", lazy=True)

    def set_password(self, plain_password):
        self.password_hash = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.password_hash, plain_password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Product(db.Model):
    """Representa um brinquedo cadastrado na loja."""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    # SKU = código de referência único do produto. "unique=True" impede
    # que dois produtos sejam cadastrados com o mesmo código por engano.
    sku = db.Column(db.String(30), unique=True, nullable=False)

    category = db.Column(db.String(60), nullable=False)

    # Localização física, dividida em campos separados (mais fácil de
    # filtrar e exibir do que um único campo de texto livre).
    aisle = db.Column(db.String(30), nullable=False)      # Corredor
    shelf = db.Column(db.String(30), nullable=False)      # Prateleira
    section = db.Column(db.String(60), nullable=True)     # Seção (ex.: "Meninas")
    warehouse = db.Column(db.String(60), nullable=False, default="Loja")  # Depósito/área

    quantity = db.Column(db.Integer, nullable=False, default=0)

    # Nome do arquivo da foto (se houver). A foto em si fica salva em
    # static/uploads/, e aqui guardamos só o nome do arquivo.
    photo_filename = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos: um produto pode ter várias movimentações e
    # aparecer em vários registros de busca.
    movements = db.relationship(
        "Movement", backref="product", lazy=True, cascade="all, delete-orphan"
    )
    search_logs = db.relationship(
        "SearchLog", backref="product", lazy=True, cascade="all, delete-orphan"
    )

    def location_display(self):
        """Monta um texto amigável com a localização completa do produto."""
        partes = [f"Corredor {self.aisle}", f"Prateleira {self.shelf}"]
        if self.section:
            partes.append(f"Seção {self.section}")
        partes.append(self.warehouse)
        return " • ".join(partes)

    def is_low_stock(self, threshold=5):
        """Verifica se o produto está com estoque baixo."""
        return self.quantity <= threshold

    def __repr__(self):
        return f"<Product {self.sku} - {self.name}>"


class Movement(db.Model):
    """Registra uma movimentação de estoque: entrada, saída ou transferência."""

    __tablename__ = "movements"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Tipo: "entrada", "saida" ou "transferencia".
    movement_type = db.Column(db.String(20), nullable=False)

    quantity_change = db.Column(db.Integer, nullable=False)

    # Guardamos a quantidade ANTES e DEPOIS da movimentação, para que o
    # histórico seja auditável (dá pra ver a evolução exata do estoque).
    previous_quantity = db.Column(db.Integer, nullable=False)
    new_quantity = db.Column(db.Integer, nullable=False)

    # Localização antes/depois — usado principalmente em transferências.
    previous_location = db.Column(db.String(150), nullable=True)
    new_location = db.Column(db.String(150), nullable=True)

    notes = db.Column(db.String(255), nullable=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Movement {self.movement_type} - Produto {self.product_id}>"


class SearchLog(db.Model):
    """Registra cada busca realizada, para o relatório de produtos mais buscados."""

    __tablename__ = "search_logs"

    id = db.Column(db.Integer, primary_key=True)

    # Pode ser nulo se a busca não encontrou nenhum produto correspondente.
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    search_term = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SearchLog '{self.search_term}'>"