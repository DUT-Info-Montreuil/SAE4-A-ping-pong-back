from bson import ObjectId
from flask import Blueprint, jsonify, request
from mongo_client import Mongo2Client

matchs_bp = Blueprint('matchs_bp', __name__)


@matchs_bp.route('/', methods=['GET'])
def get_all_matchs():
    with Mongo2Client() as mongo_client:
        db_match = mongo_client.db['match']
        matchs = db_match.find()
        match_list = []
        for match in matchs:
            match['_id'] = str(match['_id'])
            match_list.append(match)
        return jsonify(match_list)


@matchs_bp.route('/<string:id_match>', methods=['GET'])
def get_match_by_id(id_match):
    with Mongo2Client() as mongo_client:
        db_match = mongo_client.db['match']
        match = db_match.find_one({'_id': ObjectId(id_match)})
        if match:
            match['_id'] = str(match['_id'])
            return jsonify(match)
        else:
            return jsonify({'erreur': f"le match d'identifiant {id_match} n'existe pas."}), 404


@matchs_bp.route('/', methods=['POST'])
def add_match():
    data = request.get_json()
    with Mongo2Client() as mongo_client:
        db_joueur = mongo_client.db['match']
        insert_joueur = db_joueur.insert_one(data)
        if insert_joueur:
            return jsonify({"True": "La requete a bien été insérée"})
        else:
            return jsonify({"False": "Erreur lors de l'insertion"}), 404


@matchs_bp.route('/<int:id_match>', methods=['DELETE'])
def delete_match_by_id(id_match):
    with Mongo2Client() as mongo_client:
        db_match = mongo_client.db['match']
        delete_match = db_match.delete_one({'_id': ObjectId(id_match)})

        if delete_match:
            return jsonify({"True": "La suppression a bien été réalisée."})
        else:
            return jsonify({'False': 'Erreur lors de la suppression'}), 404


@matchs_bp.route('/<int:id_match>', methods=['PUT'])
def update_match_by_id(id_match):
    data = request.json

    with Mongo2Client() as mongo_client:
        db_match = mongo_client.db['match']
        update_match = db_match.update_one({'_id': ObjectId(id_match)}, {'$set': data})

        if update_match.modified_count > 0:
            return jsonify({"True": "La mise à jour a bien été réalisée."})
        else:
            return jsonify({'False': 'Erreur lors de la mise à jour'}), 404

