from src.models.db import get_db

# Faixas de desconto nomeadas — substitui os literais soltos (10000, 5000, 1000, 0.1, 0.05,
# 0.02) da versão original (playbook #13 — corrige o finding LOW de números mágicos).
DISCOUNT_TIERS = [(10_000, 0.10), (5_000, 0.05), (1_000, 0.02)]


def _calcular_desconto(faturamento):
    for limite, percentual in DISCOUNT_TIERS:
        if faturamento > limite:
            return faturamento * percentual
    return 0


def vendas():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT SUM(total) FROM pedidos").fetchone()[0] or 0
    pendentes = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'").fetchone()[0]
    aprovados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'").fetchone()[0]
    cancelados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'"
    ).fetchone()[0]

    desconto = _calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
