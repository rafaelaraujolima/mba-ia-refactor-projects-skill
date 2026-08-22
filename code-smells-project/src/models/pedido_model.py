from src.models.db import get_db


def _fetch_itens_por_pedido(db, pedido_ids):
    """Busca itens + nomes de produto em lote para uma lista de pedidos, em vez de uma
    query por item por pedido (playbook #9 — corrige o N+1 do relatório de auditoria)."""
    if not pedido_ids:
        return {}

    placeholders = ",".join("?" * len(pedido_ids))
    itens = db.execute(
        f"SELECT * FROM itens_pedido WHERE pedido_id IN ({placeholders})", pedido_ids
    ).fetchall()

    produto_ids = {item["produto_id"] for item in itens}
    produtos_by_id = {}
    if produto_ids:
        placeholders_produtos = ",".join("?" * len(produto_ids))
        produtos_by_id = {
            row["id"]: row["nome"]
            for row in db.execute(
                f"SELECT id, nome FROM produtos WHERE id IN ({placeholders_produtos})",
                list(produto_ids),
            ).fetchall()
        }

    itens_by_pedido = {}
    for item in itens:
        itens_by_pedido.setdefault(item["pedido_id"], []).append(
            {
                "produto_id": item["produto_id"],
                "produto_nome": produtos_by_id.get(item["produto_id"], "Desconhecido"),
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"],
            }
        )
    return itens_by_pedido


def list_pedidos(usuario_id=None):
    """Função única para listar pedidos (com ou sem filtro por usuário), substituindo as
    duas funções quase idênticas get_pedidos_usuario/get_todos_pedidos da versão original
    (playbook #10 — corrige o finding HIGH de lógica duplicada)."""
    db = get_db()
    if usuario_id is not None:
        rows = db.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM pedidos").fetchall()

    pedido_ids = [row["id"] for row in rows]
    itens_by_pedido = _fetch_itens_por_pedido(db, pedido_ids)

    return [
        {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": itens_by_pedido.get(row["id"], []),
        }
        for row in rows
    ]


def create(usuario_id, itens):
    db = get_db()

    produto_ids = [item["produto_id"] for item in itens]
    placeholders = ",".join("?" * len(produto_ids))
    produtos = {
        row["id"]: row
        for row in db.execute(
            f"SELECT * FROM produtos WHERE id IN ({placeholders})", produto_ids
        ).fetchall()
    }

    total = 0
    for item in itens:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]

    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        produto = produtos[item["produto_id"]]
        db.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
            "VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def update_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
