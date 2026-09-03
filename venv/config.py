import os

# Caminho absoluto da pasta onde este arquivo está localizado.
# Usamos isso para montar caminhos de forma segura, independente
# de onde o projeto for executado.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configurações gerais do sistema Locate Toy."""

    # Chave secreta usada pelo Flask para proteger sessões e formulários.
    # SUBSTITUA o valor abaixo pela chave que você gerou no passo 1.2.
    SECRET_KEY = "b39852eb381beb2b8d103246001396a8"

    # Caminho do banco de dados SQLite. Ele ficará dentro da pasta "instance",
    # que o Flask trata de forma especial (não deve ser versionada no Git).
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR, "instance", "locate_toy.db"
    )

    # Desativa um recurso do SQLAlchemy que fica avisando sobre mudanças
    # nos objetos (não precisamos dele e ele consome memória à toa).
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pasta onde as fotos dos produtos enviadas pelo usuário serão salvas.
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

    # Extensões de imagem permitidas no upload de fotos de produtos.
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # Limite padrão para considerar "estoque baixo" (RF05 do escopo).
    # Pode ser ajustado por produto futuramente; por enquanto é um valor global.
    LOW_STOCK_THRESHOLD = 5