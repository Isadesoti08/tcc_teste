from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import create_app
from models import db, User, Product, Movement, SearchLog

app = create_app()

with app.app_context():
    # Apaga todas as tabelas existentes e recria do zero. Use isso à
    # vontade durante o desenvolvimento — é o que permite "resetar" o
    # banco sempre que quiser testar algo do início.
    db.drop_all()
    db.create_all()

    # ---------------------------------------------------------------
    # USUÁRIOS DE EXEMPLO
    # ---------------------------------------------------------------
    usuarios = [
        User(
            name="Isabella Desoti",
            username="gerente",
            password_hash=generate_password_hash("gerente123"),
            role="gerente",
        ),
        User(
            name="Camila da Conceição",
            username="repositor",
            password_hash=generate_password_hash("repositor123"),
            role="repositor",
        ),
        User(
            name="Khetlyn Fernanda",
            username="vendedor",
            password_hash=generate_password_hash("vendedor123"),
            role="vendedor",
        ),
    ]
    db.session.add_all(usuarios)
    db.session.commit()  # Salva agora para que os usuários já tenham um "id".

    gerente, repositor, vendedor = usuarios

    # ---------------------------------------------------------------
    # PRODUTOS DE EXEMPLO (brinquedos)
    # ---------------------------------------------------------------
    produtos = [
        Product(name="Boneca Fashion Bela", sku="BON-001", category="Bonecos",
                aisle="3", shelf="B2", section="Meninas", warehouse="Loja", quantity=12),
        Product(name="Boneco Herói Max Power", sku="BON-002", category="Bonecos",
                aisle="3", shelf="B3", section="Meninos", warehouse="Loja", quantity=8),
        Product(name="Boneco de Ação Ranger Cósmico", sku="BON-003", category="Bonecos",
                aisle="3", shelf="B4", section="Meninos", warehouse="Loja", quantity=14),
        Product(name="Boneca Bebê Reborn Realista", sku="BON-004", category="Bonecos",
                aisle="F", shelf="F2", section=None, warehouse="Depósito Central", quantity=3),

        Product(name="Urso de Pelúcia Grandão", sku="PEL-001", category="Pelúcias",
                aisle="4", shelf="A1", section="Bebês", warehouse="Loja", quantity=20),
        Product(name="Cachorro de Pelúcia Soneca", sku="PEL-002", category="Pelúcias",
                aisle="4", shelf="A2", section="Bebês", warehouse="Loja", quantity=4),
        Product(name="Pelúcia Coelhinho Fofinho", sku="PEL-003", category="Pelúcias",
                aisle="4", shelf="A3", section="Bebês", warehouse="Loja", quantity=6),

        Product(name="Jogo Banco Imobiliário", sku="JOG-001", category="Jogos de Tabuleiro",
                aisle="5", shelf="C1", section=None, warehouse="Loja", quantity=15),
        Product(name="Jogo Detetive Mistério", sku="JOG-002", category="Jogos de Tabuleiro",
                aisle="5", shelf="C2", section=None, warehouse="Loja", quantity=3),
        Product(name="Quebra-Cabeça 500 Peças Paisagem", sku="JOG-003", category="Jogos de Tabuleiro",
                aisle="5", shelf="C3", section=None, warehouse="Loja", quantity=10),
        Product(name="Jogo de Cartas Uno Clássico", sku="JOG-004", category="Jogos de Tabuleiro",
                aisle="5", shelf="C4", section=None, warehouse="Loja", quantity=22),

        Product(name="Carrinho Controle Remoto Speedster", sku="VEI-001", category="Veículos",
                aisle="2", shelf="D1", section=None, warehouse="Loja", quantity=7),
        Product(name="Caminhão de Bombeiro Miniatura", sku="VEI-002", category="Veículos",
                aisle="2", shelf="D2", section=None, warehouse="Loja", quantity=18),
        Product(name="Pista de Corrida Looping", sku="VEI-003", category="Veículos",
                aisle="2", shelf="D3", section=None, warehouse="Loja", quantity=5),
        Product(name="Helicóptero de Brinquedo com Luz", sku="VEI-004", category="Veículos",
                aisle="2", shelf="D4", section=None, warehouse="Loja", quantity=11),
        Product(name="Patinete Infantil 3 Rodas", sku="VEI-005", category="Veículos",
                aisle="F", shelf="F1", section=None, warehouse="Depósito Central", quantity=6),

        Product(name="Kit Blocos de Montar 500 Peças", sku="EDU-001", category="Educativos",
                aisle="1", shelf="E1", section=None, warehouse="Loja", quantity=25),
        Product(name="Quebra-Cabeça Alfabeto Ilustrado", sku="EDU-002", category="Educativos",
                aisle="1", shelf="E2", section=None, warehouse="Loja", quantity=9),
        Product(name="Microscópio Infantil Cientista Jr.", sku="EDU-003", category="Educativos",
                aisle="1", shelf="E3", section=None, warehouse="Loja", quantity=2),
        Product(name="Kit Massinha de Modelar Colorida", sku="EDU-004", category="Educativos",
                aisle="1", shelf="E4", section=None, warehouse="Loja", quantity=30),
    ]
    db.session.add_all(produtos)
    db.session.commit()

    # ---------------------------------------------------------------
    # MOVIMENTAÇÕES DE EXEMPLO
    # ---------------------------------------------------------------
    agora = datetime.utcnow()

    boneco_max = next(p for p in produtos if p.sku == "BON-002")
    pelucia_soneca = next(p for p in produtos if p.sku == "PEL-002")
    jogo_detetive = next(p for p in produtos if p.sku == "JOG-002")
    patinete = next(p for p in produtos if p.sku == "VEI-005")

    movimentacoes = [
        Movement(
            product_id=boneco_max.id, user_id=repositor.id, movement_type="entrada",
            quantity_change=10, previous_quantity=0, new_quantity=10,
            new_location=boneco_max.location_display(),
            notes="Reposição inicial de estoque.",
            timestamp=agora - timedelta(days=5),
        ),
        Movement(
            product_id=boneco_max.id, user_id=vendedor.id, movement_type="saida",
            quantity_change=-2, previous_quantity=10, new_quantity=8,
            notes="Venda no caixa 2.",
            timestamp=agora - timedelta(days=3),
        ),
        Movement(
            product_id=pelucia_soneca.id, user_id=repositor.id, movement_type="saida",
            quantity_change=-6, previous_quantity=10, new_quantity=4,
            notes="Alta procura no fim de semana.",
            timestamp=agora - timedelta(days=2),
        ),
        Movement(
            product_id=jogo_detetive.id, user_id=repositor.id, movement_type="saida",
            quantity_change=-7, previous_quantity=10, new_quantity=3,
            notes="Promoção de jogos de tabuleiro.",
            timestamp=agora - timedelta(days=1),
        ),
        Movement(
            product_id=patinete.id, user_id=repositor.id, movement_type="transferencia",
            quantity_change=0, previous_quantity=6, new_quantity=6,
            previous_location="Loja • Corredor 2 • Prateleira D5",
            new_location=patinete.location_display(),
            notes="Produto movido da loja para o depósito central por excesso de espaço ocupado.",
            timestamp=agora - timedelta(hours=6),
        ),
    ]
    db.session.add_all(movimentacoes)

    # ---------------------------------------------------------------
    # BUSCAS DE EXEMPLO (para o relatório de produtos mais buscados)
    # ---------------------------------------------------------------
    buscas = [
        SearchLog(product_id=boneco_max.id, user_id=vendedor.id, search_term="max power",
                   timestamp=agora - timedelta(days=4)),
        SearchLog(product_id=boneco_max.id, user_id=vendedor.id, search_term="BON-002",
                   timestamp=agora - timedelta(days=2)),
        SearchLog(product_id=pelucia_soneca.id, user_id=vendedor.id, search_term="pelúcia cachorro",
                   timestamp=agora - timedelta(days=2)),
        SearchLog(product_id=jogo_detetive.id, user_id=vendedor.id, search_term="detetive",
                   timestamp=agora - timedelta(days=1)),
        SearchLog(product_id=jogo_detetive.id, user_id=vendedor.id, search_term="jogo mistério",
                   timestamp=agora - timedelta(hours=10)),
        SearchLog(product_id=None, user_id=vendedor.id, search_term="lego star wars",
                   timestamp=agora - timedelta(hours=3)),
    ]
    db.session.add_all(buscas)
    db.session.commit()

    print("✅ Banco de dados criado e populado com sucesso!")
    print(f"   → {len(usuarios)} usuários criados")
    print(f"   → {len(produtos)} produtos criados")
    print(f"   → {len(movimentacoes)} movimentações registradas")
    print(f"   → {len(buscas)} buscas registradas")