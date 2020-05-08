from flask import Flask
from sqlalchemy import Column, String, Integer, create_engine, Date, Float
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from config import database_path


#Database Setup
'''for testing locally use 
 database_path = 'postgresql://postgres:12@127.0.0.1:5432/castingcampany'
 '''
#database_path = 'postgresql://postgres:12@127.0.0.1:5432/castingcampany'
db = SQLAlchemy()

#def create_app():
"""
    def create_app():
    is for the shell
    https://python-decompiler.com/article/2013-10/when-scattering-
    flask-models-runtimeerror-application-not-registered-on-db-w
"""
#    app = Flask("app")
#    setup_db(app)
#    db_create_all()
#    return app



def setup_db(app, database_path=database_path):
    '''binds a flask application and a SQLAlchemy service'''
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

def db_create_all():
    '''drops the database tables and starts fresh new records '''
    #db.drop_all()
    db_init_records()

def db_init_records():
    #initialize the database with some test records

    movie1 = (Movie(
        title='Xmovie',
        release_date=date.today()

    ))

    movie2 = (Movie(
        title='Ymovie',
        release_date=date.today()
    ))
    movie3 = (Movie(
        title='Zmovie',
        release_date=date.today()
    ))
    movie4 = (Movie(
        title='Nmovie',
        release_date=date.today()
    ))
    actor1 = (Actor(
        name='act1',
        gender='male',
        age=40
    ))
    actor2 = (Actor(
        name='act2',
        gender='female',
        age=20
    ))
    actor3 = (Actor(
        name='act3',
        gender='male',
        age=40
    ))
    actor4 = (Actor(
        name='act4',
        gender='male',
        age=40
    ))

    record1 = movies_actors_association.insert().values(
        movie_id = 1,
        actor_id = 2
    )
    record2 = movies_actors_association.insert().values(
        movie_id = 2,
        actor_id=3
    )
    record3 = movies_actors_association.insert().values(
        movie_id = 2,
        actor_id = 4
    )



    actor1.insert()
    actor2.insert()
    actor3.insert()
    actor4.insert()
    movie2.insert()
    movie3.insert()
    movie4.insert()
    movie1.insert()

    db.session.execute(record1)
    db.session.execute(record2)
    db.session.execute(record3)
    db.session.commit()
"""
You can create insert.py file with extra test records
insert into actors (name,gender,age) values('Hanna','Female',27);
insert into actors (name,gender,age) values('Kakash','male',37);
insert into actors (name,gender,age) values('Hayma','Female',20);
"""

# Models
#
movies_actors_association = db.Table('movies_actors', db.Model.metadata,
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id')),
    db.Column('actor_id', db.Integer, db.ForeignKey('actors.id'))

         )



# Actor



class Actor(db.Model):

    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    def __init__(self, name, gender, age):
        self.name = name
        self.gender = gender
        self.age = age

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # return all the model details as a dictionary
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age
        }
    def __repr__(self):
        return f'<Actor {self.id} {self.name}>'



#Movie

class Movie(db.Model):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(Date)


    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }


