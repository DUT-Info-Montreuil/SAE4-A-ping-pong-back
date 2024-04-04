from bson import ObjectId
from flask import Blueprint, jsonify, request
from mongo_client import Mongo2Client

equipes_bp = Blueprint('equipes_bp', __name__)


db_equipe = Mongo2Client().db['equipe']

@equipes_bp.route('/', methods=['GET'])
def get_all_equipes():
    equipes = db_equipe.find()
    equipes_list = []
    for equipe in equipes:
        equipe['_id'] = str(equipe['_id'])
        equipes_list.append(equipe)
    return jsonify(equipes_list)


@equipes_bp.route('/<int:id_equipe>', methods=['GET'])
def get_equipe_by_id(id_equipe):
    equipe = db_equipe.find_one({'_id': ObjectId(id_equipe)})
    if equipe:
        equipe['_id'] = str(equipe['_id'])
        return jsonify(equipe)
    else:
        return jsonify({'erreur': f"l'équipe d'identifiant {id_equipe} n'existe pas."}), 404


@equipes_bp.route('/', methods=['POST'])
def add_equipes():
    data = request.get_json()
    insert_equipe = db_equipe.insert_one(data)
    if insert_equipe:
        return jsonify({"True": "La requete a bien été insérée"})
    else:
        return jsonify({"False": "Erreur lors de l'insertion"}), 404


@equipes_bp.route('/<int:id_equipe>', methods=['DELETE'])
def delete_equipe_by_id(id_equipe):
    delete_equipe = db_equipe.delete_one({'_id': ObjectId(id_equipe)})
    if delete_equipe:
        return jsonify({"True": "La suppression a bien été réalisée."})
    else:
        return jsonify({'False': 'Erreur lors de la suppression'}), 404


@equipes_bp.route('/<int:id_equipe>', methods=['PUT'])
def update_equipe_by_id(id_equipe):
    data = request.json
    update_equipe = db_equipe.update_one({'_id': ObjectId(id_equipe)}, {'$set': data})
    if update_equipe.modified_count > 0:
        return jsonify({"True": "La mise à jour a bien été réalisée."})
    else:
        return jsonify({'False': 'Erreur lors de la mise à jour'}), 404