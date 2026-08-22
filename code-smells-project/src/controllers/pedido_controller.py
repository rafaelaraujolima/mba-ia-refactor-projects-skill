import logging

from flask import jsonify, request

from src.models import pedido_model

logger = logging.getLogger(__name__)


def criar_pedido():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    resultado = pedido_model.create(usuario_id, itens)
    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

    logger.info("Pedido %s criado para usuario %s", resultado["pedido_id"], usuario_id)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_model.list_pedidos(usuario_id=usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    pedidos = pedido_model.list_pedidos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json()
    novo_status = dados.get("status", "") if dados else ""

    if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
        return jsonify({"erro": "Status inválido"}), 400

    pedido_model.update_status(pedido_id, novo_status)

    if novo_status == "aprovado":
        logger.info("Pedido %s aprovado — preparar envio", pedido_id)
    if novo_status == "cancelado":
        logger.info("Pedido %s cancelado — devolver estoque", pedido_id)

    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
