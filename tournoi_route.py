from bson import ObjectId
from flask import Blueprint, jsonify, request
from mongo_client import Mongo2Client

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


@tournois_bp.route('/<string:id_tournoi>/match/<string:id_match>', methods=['PUT'])
def update_score_match_tournoi(id_tournoi, id_match):
    score_data = request.json
    scoreJ1 = score_data.get('scoreJ1')
    scoreJ2 = score_data.get('scoreJ2')

    with Mongo2Client() as mongo_client:
        db_tournoi = mongo_client.db['tournoi']
        tournoi = db_tournoi.find_one({'_id': ObjectId(id_tournoi)})
        if not tournoi:
            return jsonify({'message': 'Tournoi non trouvé'}), 404

        matchs = tournoi.get('matchs', [])
        updated_match = None
        for match in matchs:
            if str(match.get('_id')) == id_match:
                match['scoreJ1'] = scoreJ1
                match['scoreJ2'] = scoreJ2
                updated_match = match

        if updated_match:
            db_tournoi.update_one({'_id': ObjectId(id_tournoi), 'matchs._id': updated_match['_id']}, {'$set': {'matchs.$': updated_match}})
            return jsonify({"message": "Score du match mis à jour avec succès."})
        else:
            return jsonify({'message': 'Match non trouvé'}), 404


@tournois_bp.route('/<string:id_tournoi>/match/<string:id_match>/fin', methods=['PUT'])
def finir_match_tournoi(id_tournoi, id_match):
    score_data = request.json
    scoreJ1 = score_data.get('scoreJ1')
    scoreJ2 = score_data.get('scoreJ2')

    with Mongo2Client() as mongo_client:
        db_tournoi = mongo_client.db['tournoi']
        db_joueur = mongo_client.db['joueur']
        tournoi = db_tournoi.find_one({'_id': ObjectId(id_tournoi)})
        if not tournoi:
            return jsonify({'message': 'Tournoi non trouvé.'}), 404

        matchs = tournoi.get('matchs', [])
        updated_match = None
        for match in matchs:
            if str(match.get('_id')) == id_match:
                match['scoreJ1'] = scoreJ1
                match['scoreJ2'] = scoreJ2
                match['resultat'] = 1

                if scoreJ1 > scoreJ2:
                    match['vainqueur'] = match['joueur_1']
                else:
                    match['vainqueur'] = match['joueur_2']

                updated_match = match

        if updated_match:
            db_tournoi.update_one({'_id': ObjectId(id_tournoi), 'matchs._id': updated_match['_id']}, {'$set': {'matchs.$': updated_match}})

            joueur_1 = updated_match.get('joueur_1', {})
            joueur_2 = updated_match.get('joueur_2', {})
            joueur_1_score_actuel = joueur_1.get('point')
            joueur_2_score_actuel = joueur_2.get('point')

            db_tournoi.update_one({'_id': ObjectId(id_tournoi), 'joueurs._id': ObjectId(joueur_1['_id'])}, {'$inc': {'joueurs.$.point': joueur_1_score_actuel + scoreJ1}})
            db_joueur.update_one({'_id': ObjectId(joueur_1['_id'])}, {'$inc': {'point': joueur_1_score_actuel + scoreJ1}})
            db_tournoi.update_one({'_id': ObjectId(id_tournoi), 'joueurs._id': ObjectId(joueur_2['_id'])}, {'$inc': {'joueurs.$.point': joueur_2_score_actuel + scoreJ2}})
            db_joueur.update_one({'_id': ObjectId(joueur_2['_id'])}, {'$inc': {'point': joueur_2_score_actuel + scoreJ2}})

            return jsonify({"message": "Match terminé avec succès."})
        else:
            return jsonify({'message': f"Match avec l'id {id_match} non trouvé"}), 404