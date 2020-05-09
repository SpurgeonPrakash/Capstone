import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db,db_create_all ,Movie ,Actor
from auth import AuthError, requires_auth

ACTOR_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    #comment setup_db(app) when running tests
    setup_db(app)
    #to create the test records when running python3 manage.py db upgrade
    #db_create_all()
    CORS(app)

    ''' CORS. Allow '*' for origins   '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    #to return the exact error msg
    def get_custom_error_message(error, default_error):

        try:
            # Return message contained in error
            return error.description['message']
        except:
            # if not found, return given default text
            return default_error


    def paginate_actors(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * ACTOR_PER_PAGE
        end = start + ACTOR_PER_PAGE
        all_actors = [actor.format() for actor in selection]
        actors = all_actors[start:end]

        return actors

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''GET /movies  endpoint '''
    @app.route('/movies', methods=['GET'])
    @requires_auth('get:actorsAndmovies')
    def get_movies(jwt):
        movies = Movie.query.all()
        # if there is movies
        if movies:
            return jsonify({
                'success': True,
                'movies': [movie.format() for movie in movies]
            }), 200
        # if no movies
        abort(404, {'message': 'no movies found in database.'})


    '''GET /actors  endpoint '''

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actorsAndmovies')
    def get_actors(jwt):
        actors = Actor.query.all()
        actors_paginated = paginate_actors(request, actors)
        # if there is actors
        if actors_paginated:
            return jsonify({
                'success': True,
                'actors':actors_paginated
            }), 200
        # if no actors
        abort(404, {'message': 'no actors found in database.'})

    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(jwt,id):
        if not id:
            abort(400)
        actors = Actor.query.filter(Actor.id == id).one_or_none()
        if not actors:
            abort(404, {'message': 'no actor with this id found'})
        actors.delete()
        return jsonify({
            "success": True,
            "delete": id
        }), 200

    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(jwt,id):
        if not id:
            abort(400, {'message': 'no movie with this id found'})
        movies = Movie.query.filter(Movie.id == id).one_or_none()
        if not movies:
            abort(404, {'message': 'no movies found in database'})
        movies.delete()
        return jsonify({
            "success": True,
            "delete": id
        }), 200

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actor')
    def create_actor(jwt):
        body = request.get_json()
        if not body:
            abort(400, {'message': 'request does not contain a valid JSON body.'})

        name = body.get('name')
        age=body.get('age')
        gender=body.get('gender')
        if not name:
            abort(400,  {'message': 'name can not be blank'})

        if not age:
             abort(400, {'message': 'age can not be blank'})

        if not gender:
            abort(400, {'message': 'gender can not be blank'})

        try:
            new_actor = Actor(name=name, age=age, gender=gender)
            new_actor.insert()
            allactors = Actor.query.order_by(Actor.id).all()
            actors=paginate_actors(request , allactors)
            return jsonify({
                'success': True,
                'created': new_actor.id,
                'actors': actors,
                'total_actors': len(actors)
            })
        except BaseException:
            abort(422,{'message': 'something went wrong with prossing request '})
    '''curl -iX POST http://127.0.0.1:5000/movies -H "Content-Type:application/json"  -d '{"title":"home alon" , "release_date":"2020-5-1" }'''
    '''curl -iX GET http://127.0.0.1:5000/movies  -H "Authorization: Bearer <token>"'''


    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movie')
    def create_movie(jwt):
        body = request.get_json()
        if not body:
            abort(400, {'message': 'request does not contain a valid JSON body.'})

        title = body.get('title')
        release_date = body.get('release_date')
        if not title:
            abort(400 , {'message': 'title can not be blank'})

        if not release_date:
            abort(400, {'message': 'release_date can not be blank'})

        try:
            new_movie = Movie(title=title, release_date=release_date)
            new_movie.insert()
            allmovies = Movie.query.order_by(Movie.id).all()
            movies =[movie.format() for movie in allmovies]

            return jsonify({
                'success': True,
                'created': new_movie.id,
                'movies': movies,
                'total_movies': len(movies)
            })
        except BaseException:
            abort(422 ,{'message': 'something went wrong with prossing request'})

    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth('patch:actor')
    def update_actor(jwt,id):
        body = request.get_json()
        if not id:
            abort(400, {'message': 'please append an actor id to the request url.'})

        if not body:
            abort(400, {'message': 'request does not contain a valid JSON body.'})

        actor = Actor.query.filter(Actor.id == id).one_or_none()
        if not actor:
            abort(404, {'message': 'requested actor id not found'})

        updated_name = body.get('updated_name')
        updated_age = body.get('updated_age')
        updated_gender = body.get('updated_gender')

        # Depending on which fields are available, make accorisbonding updates
        if updated_name:
            actor.name =updated_name
        if updated_age:
            actor.age = updated_age
        if updated_gender:
            actor.gender = updated_gender
        actor.update()

        return jsonify({
            'success': True,
            'actor': [actor.format()]
        })
    '''
    curl -iX PATCH http://127.0.0.1:5000/movies/7 -H "Content-Type:application/json"  -d '{"updated_title":"home alone 2" }'
    '''
    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth('patch:movie')
    def update_movie(jwt,id):
        body = request.get_json()
        print("your body is", body)
        if not body:
            abort(400, {'message': 'request does not contain a valid JSON body.'})

        updated_title = body.get('updated_title')
        updated_release_date = body.get('updated_release_date')
        movie = Movie.query.filter(Movie.id == id).one_or_none()
        print("req. mov is", movie)
        if not movie:
            abort(404, {'message': 'requested movie id not found'})
        # Depending on which fields are available, make accorisbonding updates
        if updated_title:
            movie.title = updated_title
        print("updated_title", updated_title)

        if updated_release_date:
            movie.release_date = updated_release_date
        movie.update()

        return jsonify({
            'success': True,
            'movie': [movie.format()]
        })






    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": get_custom_error_message(error,"resource not found")
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": get_custom_error_message(error,"unprocessable")
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message":get_custom_error_message(error, "bad request")
        }), 400

    @app.errorhandler(405)
    def method_not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": get_custom_error_message(error,"method not allowed")
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": get_custom_error_message(error, "internal server error")
        }), 500

    @app.errorhandler(AuthError)
    def authentification_failed(AuthError):
        return jsonify({
            "success": False,
            "code":AuthError.error['code'],
            "error": AuthError.status_code,
            "message": AuthError.error['description']
        }), AuthError.status_code


    return app





app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

