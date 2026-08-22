from src.models.db import get_db

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]


def get_all():
    db = get_db()
    rows = db.execute("SELECT * FROM produtos").fetchall()
    return [dict(row) for row in rows]


def get_by_id(produto_id):
    db = get_db()
    row = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return dict(row) if row else None


def search(termo=None, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []

    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def create(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def update(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()


def delete(produto_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def validate_payload(dados):
    """Validação compartilhada por criar_produto e atualizar_produto (playbook #10 —
    elimina a duplicação de validação apontada no finding MEDIUM do relatório de auditoria)."""
    if "nome" not in dados:
        return None, "Nome é obrigatório"
    if "preco" not in dados:
        return None, "Preço é obrigatório"
    if "estoque" not in dados:
        return None, "Estoque é obrigatório"

    nome = dados["nome"]
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        return None, "Preço não pode ser negativo"
    if estoque < 0:
        return None, "Estoque não pode ser negativo"
    if len(nome) < 2:
        return None, "Nome muito curto"
    if len(nome) > 200:
        return None, "Nome muito longo"
    if categoria not in CATEGORIAS_VALIDAS:
        return None, f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}"

    return {
        "nome": nome,
        "descricao": dados.get("descricao", ""),
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }, None
