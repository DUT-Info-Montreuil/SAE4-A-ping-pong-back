from flask import Flask
from flask_cors import CORS
from joueur_routes import joueurs_bp
from equipe_route import equipes_bp
from match_route import matchs_bp
from equipement_tournoi_route import equipement_tournoi_bp
from tournoi_route import tournois_bp

app = Flask(__name__)
cors = CORS(app)


app.register_blueprint(joueurs_bp, url_prefix='/joueurs')
app.register_blueprint(equipes_bp, url_prefix='/equipes')
app.register_blueprint(matchs_bp, url_prefix='/matchs')
app.register_blueprint(equipement_tournoi_bp, url_prefix='/equipement')
app.register_blueprint(tournois_bp, url_prefix='/tournois')


@app.route('/')
def welcome_app():
    return 'Welcome to ping-pong tournament API.'


if __name__ == '__main__':
    app.run(debug=True)