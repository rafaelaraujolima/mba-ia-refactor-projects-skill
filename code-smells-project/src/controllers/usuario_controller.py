from flask import jsonify, request

from src.models import usuario_model


def listar_usuarios():
    usuarios = usuario_model.get_all()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.get_by_id(usuario_id)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True}), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404


def criar_usuario():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    usuario_id = usuario_model.create(nome, email, senha)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201
