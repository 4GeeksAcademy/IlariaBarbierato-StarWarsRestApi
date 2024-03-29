from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    #Table structure
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    #Information that it is shown when there is a print
    def __repr__(self):
        return 'User with id {} and email {}'.format(self.id, self.email)

    #Converts from Class to Object 
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    __tablename__ = "planets"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True)
    population = db.Column(db.Integer)
    climate = db.Column(db.String(30))
    diameter = db.Column(db.Float)

    def __repr__(self):
        return 'Planet with id {} and name {}'.format(self.id, self.name)
 
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "climate": self.climate,
            "diameter": self.diameter
        }

class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True)
    birth_year = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    height = db.Column(db.Float)
    eye_color = db.Column(db.String(15))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    planet_relationship = db.relationship(Planets)

    def __repr__(self):
        return 'Character with id {} and name {}'.format(self.id, self.name)
 
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "eye_color": self.eye_color,
            "planet_id": self.planet_id
        }

class FavoritesPlanets(db.Model):
    __tablename__ = "favorites_planets"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user_relationship = db.relationship(User)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable = False)
    planet_relationship = db.relationship(Planets)

    def __repr__(self):
        return 'User with id {} and favorite planet with id {}'.format(self.user_id, self.planet_id)
 
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id
        }

class FavoritePeople(db.Model):
    __tablename__ = "favorite_people"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user_relationship = db.relationship(User)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable = False)
    people_relationship = db.relationship(People)

    def __repr__(self):
        return 'User with id {} and favorite person with id {}'.format(self.user_id, self.people_id)
 
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "person_id": self.people_id
        }