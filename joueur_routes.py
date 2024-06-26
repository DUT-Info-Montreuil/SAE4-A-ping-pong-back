import csv
import io

from flask import Blueprint, jsonify, request
from flask_expects_json import expects_json
from mongo_client import Mongo2Client
from bson import ObjectId

joueurs_bp = Blueprint('joueur_bp', __name__)

joueur_schema = {
    'type': 'object',
    'properties': {
        'nom': {'type': 'string'},
        'prenom': {'type': 'string'},
        'categorie': {
            'type': 'object',
            'properties': {
                'age': {'type': 'integer'},
                'niveau': {'type': 'string'}
            },
            'required': ['age', 'niveau']
        },
        'sexe': {'type': 'string'},
        'point': {'type': 'integer'}
    },
    'required': ['nom', 'prenom', 'categorie', 'sexe', 'point']
}

db_joueur = Mongo2Client().db['joueur']


@joueurs_bp.route('/', methods=['GET'])
def get_all_joueurs():
    joueurs = db_joueur.find()
    joueurs_list = []
    for joueur in joueurs:
        joueur['_id'] = str(joueur['_id'])
        joueurs_list.append(joueur)
    return jsonify(joueurs_list)


@joueurs_bp.route('/<string:id_joueur>', methods=['GET'])
def get_joueur_by_id(id_joueur):
    joueur = db_joueur.find_one({'_id': ObjectId(id_joueur)})
    if joueur:
        joueur['_id'] = str(joueur['_id'])
        return jsonify(joueur)
    else:
        return jsonify({'erreur': f"le joueur d'identifiant {id_joueur} n'existe pas."}), 404


@joueurs_bp.route('/add', methods=['POST'])
@expects_json(joueur_schema)
def add_joueur():
    data = request.json
    insert_joueur = db_joueur.insert_one(data)
    if insert_joueur:
        return jsonify({"message": "La requete a bien été insérée"})
    else:
        return jsonify({"message": "Erreur lors de l'insertion"}), 404


@joueurs_bp.route('/<string:id_joueur>', methods=['DELETE'])
def delete_joueur_by_id(id_joueur):
    delete_joueur = db_joueur.delete_one({'_id': ObjectId(id_joueur)})
    if delete_joueur:
        return jsonify({"message": "La suppression a bien été réalisée."})
    else:
        return jsonify({'message': 'Erreur lors de la suppression'}), 404


@joueurs_bp.route('/<string:id_joueur>', methods=['PUT'])
def update_joueur_by_id(id_joueur):
    data = request.json

    update_joueur = db_joueur.update_one({'_id': ObjectId(id_joueur)}, {'$set': data})

    if update_joueur.modified_count > 0:
        return jsonify({"message": "La mise à jour a bien été réalisée."})
    else:
        return jsonify({'message': 'Erreur lors de la mise à jour'}), 404


@joueurs_bp.route('/add_fichier', methods=['POST'])
def add_joueurs_fichier():
    print("Fichier reçu:", "fichier" in request.files)
    fichier = request.files['fichier']

    if not fichier:
        return jsonify({"succès": False, "message": "Aucun fichier fourni"}), 400
    try:
        if not fichier.filename.endswith('.csv'):
            return jsonify({"succès": False, "message": "Le fichier n'est pas un CSV"}), 400

        fichier.seek(0)
        joueurs = []
        for row in csv.DictReader(io.StringIO(fichier.read().decode('utf-8'))):
            categorie = {'age': row['Age'], 'niveau': row['Niveau']}
            try:
                points = int(row['Points'])
            except ValueError:
                points = 0
            joueur = {
                'nom': row['Nom'],
                'prenom': row['Prénom'],
                'sexe': row['Sexe'],
                'categorie': categorie,
                'point': points
            }
            joueurs.append(joueur)

    except Exception as e:
        return jsonify({"succès": False, "message": "Erreur lors de la lecture du fichier", "erreur": str(e)}), 400

    try:
        if joueurs:
            resultat = db_joueur.insert_many(joueurs)
            ids_insertion = [str(id_) for id_ in resultat.inserted_ids]
            return jsonify({"succès": True, "ids_insertion": ids_insertion}), 201
        else:
            return jsonify({"succès": False, "message": "Le fichier CSV est vide"}), 400
    except Exception as e:
        return jsonify({"succès": False, "message": "Erreur lors de l'insertion des joueurs", "erreur": str(e)}), 500


@joueurs_bp.route('/', methods=['GET'])
def get_joueurs_filtre():
    niveau = request.args.get('niveau', 'Mixte')

    query = {}

    if niveau != 'Mixte':
        query['categorie.niveau'] = niveau

    joueurs = db_joueur.find(query)
    joueurs_list = []
    for joueur in joueurs:
        joueur['_id'] = str(joueur['_id'])
        joueurs_list.append(joueur)
    return jsonify(joueurs_list)
