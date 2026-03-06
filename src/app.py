"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Users, Planets, Characters, Favorites_characters
from sqlalchemy import select
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# BEGIN


# POST - Agregar un usuario nuevo
@app.route('/adduser', methods=['POST'])
def add_user():

    body = request.get_json()

    if not body:
        return jsonify({"msg": "Debe enviar un JSON"}), 400

    if 'user_name' not in body:
        return "El nombre debe ser enviado", 400

    if body['user_name'] == "":
        return "El nombre no puede ser vacio", 400

    user = Users(
        user_name=body['user_name'], first_name=body['first_name'], last_name=body['last_name'],
        email=body['email'], password=body['password'], suscription_day=body['suscription_day']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize()), 200


# DELETE Eliminar un usuario
@app.route('/users/<int:users_id>', methods=['DELETE'])
def delete_user(users_id):
    users = db.session.get(Users, users_id)

    if users is None:
        return "No se encontro el usuario", 400

    response_body = {
        "msg": "Usuario eliminado correctamente" + users.user_name
    }

    db.session.delete(users)
    db.session.commit()

    return jsonify(response_body), 200


# GET mostrar todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():

    all_users = db.session.execute(select(Users)).scalars().all()
    results = list(map(lambda users: users.serialize(), all_users))

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(results), 200


# GET mostrar un unico usuario
@app.route('/users/<int:users_id>', methods=['GET'])
def get_user(users_id):
    users = db.session.get(Users, users_id)

    # Validación: si no existe el usuario
    if not users:
        return jsonify({
            "error": "Personaje no encontrado",
            "character_id": users_id
        }), 404

    return jsonify(users.serialize()), 200


# GET mostrar el primer usuario
@app.route('/primero', methods=['GET'])
def get_first():
    users = Users.query.first()

    return jsonify(users.serialize()), 200


# GET mostrar todos los personajes
@app.route('/characters', methods=['GET'])
def get_characters():

    all_characters = db.session.execute(select(Characters)).scalars().all()
    results = list(
        map(lambda characters: characters.serialize(), all_characters))

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(results), 200


# GET - mostrar un unico personaje
@app.route('/characters/<int:characters_id>', methods=['GET'])
def get_character(characters_id):

    characters = db.session.get(Characters, characters_id)

    # Validación: si no existe el personaje
    if not characters:
        return jsonify({
            "error": "Personaje no encontrado",
            "character_id": characters_id
        }), 404

    return jsonify(characters.serialize()), 200


# POST - Agregar Personaje Favorito
@app.route('/favorite/character/', methods=['POST'])
def add_favorite_character():
    data = request.get_json()

    # Validación: necesita user_id y planet_id
    if not data or not all(key in data for key in ['user_id', 'characters_id']):
        return jsonify({"error": "Faltan user_id y characters_id"}), 400

    # Verificar que existan user y planet
    user = Users.query.get(data['user_id'])
    character_id = Characters.query.get(data['characters_id'])

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if not character_id:
        return jsonify({"error": "Personaje no encontrado"}), 404

    # Verificar si ya es favorito
    existing_fav = Favorites_characters.query.filter_by(
        user_id=data['user_id'],
        character_id=data['characters_id']
    ).first()

    if existing_fav:
        return jsonify({"error": "Ya es favorito"}), 400

    try:
        # Crear favorito
        favorite = Favorites_characters(
            user_id=data['user_id'],
            characters_id=data['characters_id']
        )

        db.session.add(favorite)
        db.session.commit()

        return jsonify({
            "message": "Personaje favorito agregado",
            "favorite": favorite.serialize()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al agregar favorito"}), 500


# GET mostrar todos los planetas
@app.route('/planets', methods=['GET'])
def get_planets():

    all_planets = db.session.execute(select(Planets)).scalars().all()
    results = list(map(lambda planets: planets.serialize(), all_planets))

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(results), 200


# GET mostrar un unico planeta
@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet(planets_id):
    planets = db.session.get(Planets, planets_id)

    # Validación: si no existe el usuario
    if not planets:
        return jsonify({
            "error": "Planeta no encontrado",
            "planets_id": planets_id
        }), 404

    return jsonify(planets.serialize()), 200


# END
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
