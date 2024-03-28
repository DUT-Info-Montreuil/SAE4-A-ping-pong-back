from bson import ObjectId
from flask import Blueprint, jsonify, request
from mongo_client import Mongo2Client
import random

tournois_bp = Blueprint('tournoi_bp', __name__)


@tournois_bp.route('/', methods=['GET'])
def get_all_tournois():
    with Mongo2Client() as mongo_client:
        db_tournoi = mongo_client.db['tournoi']
        tournois = db_tournoi.find()
        tournoi_list = []
        for tournoi in tournois:
            tournoi['_id'] = str(tournoi['_id'])
            tournoi_list.append(tournoi)
        return jsonify(tournoi_list)


@tournois_bp.route('/', methods=['POST'])
def add_tournoi():
    tournoi_data = request.json
    with Mongo2Client() as mongo_client:
        db_tournoi = mongo_client.db['tournoi']
        insert_tournoi = db_tournoi.insert_one(tournoi_data)
        if insert_tournoi:
            return jsonify({"message": "Tournoi ajouter avec succès."})
        else:
            return jsonify({"message": "Le tournoi n'a pas été ajouter."})


@tournois_bp.route('/<string:id_tournoi>', methods=['GET'])
def get_tournoi_by_id(id_tournoi):
    with Mongo2Client() as mongo_client:
        db_tournoi = mongo_client.db['tournoi']
        tournoi = db_tournoi.find_one({'_id': ObjectId(id_tournoi)})
        if tournoi:
            tournoi['_id'] = str(tournoi['_id'])
            return jsonify(tournoi)
        else:
            return jsonify({'message': 'Tournoi non trouvé'}), 404


@tournois_bp.route('/<string:id_tournoi>', methods=['PUT'])
def update_tournoi_by_id(id_tournoi):
    tournoi_data = request.json

    with Mongo2Client() as mongo_client:

        db_tournoi = mongo_client.db['tournoi']

        update_tournoi = db_tournoi.update_one({'_id': ObjectId(id_tournoi)}, {'$set': tournoi_data})

        if update_tournoi.modified_count > 0:
            return jsonify({"message": "Tournoi mis à jour avec succès."})
        else:
            return jsonify({'message': 'Erreur lors de la mise à jour du tournoi'}), 404


@tournois_bp.route('/<string:id_tournoi>', methods=['DELETE'])
def delete_tournoi_by_id(id_tournoi):
    with Mongo2Client() as mongo_client:

        db_tournoi = mongo_client.db['tournoi']

        delete_tournoi = db_tournoi.delete_one({'_id': ObjectId(id_tournoi)})
        if delete_tournoi.deleted_count > 0:
            return jsonify({"message": "Le tournoi a été supprimé avec succès."})
        else:
            return jsonify({'message': 'Erreur lors de la suppression du tournoi'}), 404


@tournois_bp.route('/randomiser_match', methods=['PUT'])
def randomiser_match():
    data_tournoi = request.json

    with Mongo2Client() as mongo_client:
        db_tournoi = mongo_client.db['tournoi']
        matchs = data_tournoi.get('match', [])
        random.shuffle(matchs)
        data_tournoi['match'] = matchs
        update = db_tournoi.update_one({'_id': ObjectId(data_tournoi['_id'])}, {'$set': data_tournoi})

        if update.modified_count > 0:
            return jsonify({"messsage": "Les matchs ont bien été randomiser"})
        else:
            return jsonify({"messsage": "Erreur lors de la requete"}), 40