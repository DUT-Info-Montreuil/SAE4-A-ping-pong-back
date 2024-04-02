from bson import ObjectId
from flask import Blueprint, jsonify, request
from mongo_client import Mongo2Client
import random

matchs_bp = Blueprint('matchs_bp', __name__)


def conversion_objectid_en_string(matchs):
    matchs_list = []
    for match in matchs:
        match_copy = match.copy()
        match_copy['_id'] = str(match['_id'])
        matchs_list.append(match_copy)
    return matchs_list


@matchs_bp.route('/', methods=['GET'])
def get_all_matchs():
    with Mongo2Client() as mongo_client:
        db_match = mongo_client.db['match']
        matchs = db_match.find()
        match_list = conversion_objectid_en_string(matchs)
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


@matchs_bp.route('/<string:id_match>', methods=['DELETE'])
def delete_match_by_id(id_match):
    with Mongo2Client() as mongo_client:
        db_match = mongo_client.db['match']
        delete_match = db_match.delete_one({'_id': ObjectId(id_match)})

        if delete_match:
            return jsonify({"True": "La suppression a bien été réalisée."})
        else:
            return jsonify({'False': 'Erreur lors de la suppression'}), 404


@matchs_bp.route('/<string:id_match>', methods=['PUT'])
def update_match_by_id(id_match):
    data = request.json

    with Mongo2Client() as mongo_client:
        db_match = mongo_client.db['match']
        update_match = db_match.update_one({'_id': ObjectId(id_match)}, {'$set': data})

        if update_match.modified_count > 0:
            return jsonify({"True": "La mise à jour a bien été réalisée."})
        else:
            return jsonify({'False': 'Erreur lors de la mise à jour'}), 404


@matchs_bp.route('/random_match', methods=['POST'])
def create_random_matches():
    data = request.json

    joueurs_tournoi = data.get('joueurs', [])
    equipement = data.get('equipement')
    duree_tournoi = int(data.get('dureeTournoi'))

    if len(joueurs_tournoi) == 0:
        return jsonify({"error": "Aucun joueur(s) assigné pour un match."}), 400

    if len(joueurs_tournoi) % 2 != 0:
        return jsonify({"error": "Nombre impair de joueurs."}), 400

    if not equipement:
        return jsonify({"error": "Équipement non fourni."}), 400

    if equipement['table']['quantite'] < duree_tournoi / 5:
        return jsonify({"error": "Nombre de tables insuffisant pour la durée du tournoi."}), 400

    if equipement['fillet']['quantite'] < duree_tournoi / 5:
        return jsonify({"error": "Nombre de filets insuffisant pour la durée du tournoi."}), 400

    if equipement['marqueur']['quantite'] < 1:
        return jsonify({"error": "Nombre de marqueurs insuffisant pour la durée du tournoi."}), 400

    if equipement['balle']['quantite'] < 1:
        return jsonify({"error": "Nombre de balles insuffisant pour la durée du tournoi."}), 400

    random.shuffle(joueurs_tournoi)

    liste_matchs = []
    for i in range(0, len(joueurs_tournoi), 2):
        if i + 1 < len(joueurs_tournoi):
            match = {
                'joueur_1': joueurs_tournoi[i],
                'joueur_2': joueurs_tournoi[i + 1],
                'duree': 5,
                'resultat': 0
            }
            liste_matchs.append(match)

    with Mongo2Client() as mongo_client:
        db_match = mongo_client.db['match']
        insert_matchs = db_match.insert_many(liste_matchs)

        if insert_matchs:
            matchs_inserer = db_match.find({'_id': {'$in': insert_matchs.inserted_ids}})
            matchs = conversion_objectid_en_string([match for match in matchs_inserer])
            return jsonify({"success": "Les matchs ont été créés avec succès.", "matchs": matchs})
        else:
            return jsonify({"error": "Erreur lors de la création des matchs."}), 500
