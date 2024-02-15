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
from models import db, User, Planets, People, FavoritesPlanets, FavoritePeople
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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


#Get a list of all the people in the database.
@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    serialized_people = list(map(lambda item: item.serialize(), people))
    return jsonify({'msg': 'Ok', 'results': serialized_people}), 200


#Get one single person's information.
@app.route('/people/<int:people_id>', methods=['GET'])
def get_particular_people(people_id):
    people = People.query.get(people_id)
    serialized_people = people.serialize()
    return jsonify({'msg': 'Ok', 'results': serialized_people}), 200


#Get a list of all the planets in the database.
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    serialized_planets = list(map(lambda item: item.serialize(), planets))
    return jsonify({'msg': 'Ok', 'results': serialized_planets}), 200


#Get one single planet's information.
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_particular_planet(planet_id):
    planet = Planets.query.get(planet_id)
    serialzed_planet = planet.serialize()
    return jsonify({'msg': 'Ok', 'results': serialzed_planet}), 200


#Get a list of all the blog post users.
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    serialized_users = list(map(lambda item: item.serialize(), users))
    return jsonify({'msg' : 'Ok', 'results' : serialized_users}), 200


#Get all the planets favorites that belong to the current user.
@app.route('/favoritesPlanets/user/<int:user_id>', methods=['GET'])
def get_favorites_planets(user_id):
    user = User.query.get(user_id)
    if user is None:
        return ({'msg': 'The user with id {} does not exist'.format(user_id)}), 404
    favorites_planets = db.session.query(FavoritesPlanets, Planets).join(Planets).filter(FavoritesPlanets.user_id == user_id).all()
    serialized_favorites_planets = []
    for favorite_item, planet_item in favorites_planets:
        serialized_favorites_planets.append({'planet': planet_item.serialize()})
    return({'msg': 'ok', 'planets_favorites': serialized_favorites_planets, 'user': user.serialize()}), 200


#Get all the people favorites that belong to the current user.
@app.route('/favoritePeople/user/<int:user_id>', methods=['GET'])
def get_favorite_people(user_id):
    user = User.query.get(user_id)
    if user is None:
        return ({'msg': 'The user with id {} does not exist'.format(user_id)}), 404
    favorite_people = db.session.query(FavoritePeople, People).join(People).filter(FavoritePeople.user_id == user_id).all()
    serialized_favorite_people = []
    for favorite_item, people_item in favorite_people:
        serialized_favorite_people.append({'person': people_item.serialize()})
    return({'msg': 'ok', 'people_favorite': serialized_favorite_people, 'user': user.serialize()}), 200


#Get all the favorites that belong to the current user.
@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_all_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return ({'msg': 'The user with id {} does not exist'.format(user_id)}), 404
    favorite_people = db.session.query(FavoritePeople, People).join(People).filter(FavoritePeople.user_id == user_id).all()
    print(favorite_people)
    serialized_favorites = []
    for favorite_item, people_item in favorite_people:
        serialized_favorites.append({'person': people_item.serialize()})
    favorites_planets = db.session.query(FavoritesPlanets, Planets).join(Planets).filter(FavoritesPlanets.user_id == user_id).all()
    for favorite_item, planet_item in favorites_planets:
        serialized_favorites.append({'planet': planet_item.serialize()})
    return({'msg': 'Ok', 'results': serialized_favorites, 'user': user.serialize()}), 200


# Add a new favorite planet to the current user with the planet id = planet_id
@app.route('/favorite/planet/<int:planet_id>/user/<int:user_id>', methods=['POST'])
def add_favorite_planet(planet_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return ({'msg': 'The user with id {} does not exist'.format(user_id)}), 404
    planet = Planets.query.get(planet_id)
    if planet is None:
        return({'msg': 'The planet with id {} does not exist'.format(planet_id)}), 404
    existing_favorite = db.session.query(FavoritesPlanets).filter((FavoritesPlanets.planet_id == planet_id) & (FavoritesPlanets.user_id == user_id)).all()
    if existing_favorite:
        return({'msg': 'The planet with id {} is already a favorite for the user with id {}'.format(planet_id, user_id)})
    favorite_planet = FavoritesPlanets(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite_planet)
    db.session.commit()
    return({'msg': 'The planet with id {} has been correctly added to the favorites of the user with id {}'.format(planet_id, user_id)})


#Add new favorite people to the current user with the people id = people_id
@app.route('/favorite/people/<int:people_id>/user/<int:user_id>', methods=['POST'])
def add_favorite_person(people_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return ({'msg': 'The user with id {} does not exist'.format(user_id)}), 404
    person = People.query.get(people_id)
    if person is None:
        return({'msg': 'The person with id {} does not exist'.format(people_id)}), 404
    existing_favorite = db.session.query(FavoritePeople).filter((FavoritePeople.people_id == people_id) & (FavoritePeople.user_id == user_id)).all()
    if existing_favorite:
        return({'msg': 'The person with id {} is already a favorite for the user with id {}'.format(people_id, user_id)})
    favorite_person = FavoritePeople(user_id=user_id, people_id=people_id)
    db.session.add(favorite_person)
    db.session.commit()
    return({'msg': 'The person with id {} has been correctly added to the favorites of the user with id {}'.format(people_id, user_id)})


# Delete a favorite planet with the id = planet_id
@app.route('/favorite/planet/<int:planet_id>/user/<int:user_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return ({'msg': 'The user with id {} does not exist'.format(user_id)}), 404
    planet = Planets.query.get(planet_id)
    if planet is None:
        return({'msg': 'The planet with id {} does not exist'.format(planet_id)}), 404
    favorite_planet_to_delete = db.session.query(FavoritesPlanets).filter((FavoritesPlanets.planet_id == planet_id) & (FavoritesPlanets.user_id == user_id)).first()
    if favorite_planet_to_delete is None:
        return({'msg': 'The planet with id {} is not a favorite for the user with id {}'.format(planet_id, user_id)})
    
    db.session.delete(favorite_planet_to_delete)
    db.session.commit()

    return ({'msg': 'The planet with id {} has been correctly deleted from the favorites of the user with id {}'.format(planet_id, user_id)})


# Delete a favorite person with the id = planet_id
@app.route('/favorite/people/<int:people_id>/user/<int:user_id>', methods=['DELETE'])
def delete_favorite_person(people_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return ({'msg': 'The user with id {} does not exist'.format(user_id)}), 404
    person = People.query.get(people_id)
    if person is None:
        return({'msg': 'The person with id {} does not exist'.format(people_id)}), 404
    favorite_person_to_delete = db.session.query(FavoritePeople).filter((FavoritePeople.people_id == people_id) & (FavoritePeople.user_id == user_id)).first()
    if favorite_person_to_delete is None:
        return({'msg': 'The person with id {} is not a favorite for the user with id {}'.format(people_id, user_id)})
    
    db.session.delete(favorite_person_to_delete)
    db.session.commit()

    return ({'msg': 'The person with id {} has been correctly deleted from the favorites of the user with id {}'.format(people_id, user_id)})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
