import logging

from flask import jsonify, request

from src.models import produto_model

logger = logging.getLogger(__name__)


def listar_produtos():
    produtos = produto_model.get_all()
    logger.info("Listando %d produtos", len(produtos))
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(produto_id):
    produto = produto_model.get_by_id(produto_id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    preco_min = float(preco_min) if preco_min else None
    preco_max = float(preco_max) if preco_max else None

    resultados = produto_model.search(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def criar_produto():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    payload, erro = produto_model.validate_payload(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    produto_id = produto_model.create(**payload)
    logger.info("Produto criado com ID: %s", produto_id)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(produto_id):
    existente = produto_model.get_by_id(produto_id)
    if not existente:
        return jsonify({"erro": "Produto não encontrado"}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    payload, erro = produto_model.validate_payload(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    produto_model.update(produto_id, **payload)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(produto_id):
    produto = produto_model.get_by_id(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto_model.delete(produto_id)
    logger.info("Produto %s deletado", produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
