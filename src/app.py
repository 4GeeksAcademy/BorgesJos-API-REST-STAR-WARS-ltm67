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
from models import db, User, Users, Planets, Characters, Favorites_characters, Favorites_planets
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

    response_body = {
        "msg": "Usuario agregado correctamente" + user.user_name
    }

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
@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    data = request.get_json()
    user_id = data.get("user_id", 1)
    user = Users.query.get(user_id)

    if user is None:
        return jsonify({"Error": "Usuario no encontrado"}), 400

    character = Characters.query.get(character_id)
    if character is None:
        return jsonify({"Error": "Personaje no encontrado"}), 400

    exist_character = Favorites_characters.query.filter_by(
        user_id=user_id, characters_id=character_id
    ).first()

    if exist_character:
        return jsonify({"Error": "Personaje ya existe en favoritos"}), 400

    favorite_character = Favorites_characters(
        user_id=user_id, characters_id=character_id
    )

    db.session.add(favorite_character)
    db.session.commit()

    return jsonify({
        "mensaje": "Se añadió favorito",
        "favorites_characters": favorite_character.serialize()
    }), 201


# DELETE - Borrar Personaje Favorito
@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    data = request.get_json()
    user_id = data.get("user_id")

    favorite = Favorites_characters.query.filter_by(
        user_id=user_id,
        characters_id=character_id
    ).first()

    if not favorite:
        return jsonify({"Error": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"mensaje": "Favorito eliminado"}), 200


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


# POST - Agregar Planeta Favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get("user_id", 1)
    user = Users.query.get(user_id)

    if user is None:
        return jsonify({"Error": "Usuario no encontrado"}), 400

    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"Error": "Planeta no encontrado"}), 400

    exist_planet = Favorites_planets.query.filter_by(
        user_id=user_id, planet_id=planet_id
    ).first()

    if exist_planet:
        return jsonify({"Error": "Planeta ya existe en favoritos"}), 400

    favorite_planet = Favorites_planets(
        user_id=user_id, planet_id=planet_id
    )

    db.session.add(favorite_planet)
    db.session.commit()

    return jsonify({
        "mensaje": "Se añadió favorito",
        "favorites_planets": favorite_planet.serialize()
    }), 201


# DELETE - Borrar Planeta Favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get("user_id")

    favorite = Favorites_planets.query.filter_by(
        user_id=user_id,
        planet_id=planet_id
    ).first()

    if not favorite:
        return jsonify({"Error": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"mensaje": "Favorito eliminado"}), 200


# END
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
