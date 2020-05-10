import os
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import  setup_db,db_create_all ,Movie ,Actor
import unittest
from config import bearer_tokens
import json
from datetime import date


#dict with Authorization key and Bearer token as values.
#to be used by test classes as Header

casting_assistant_auth_header = {
    'Authorization': bearer_tokens['Casting Assistant']
}

casting_director_auth_header = {
    'Authorization': bearer_tokens['Casting Director']
}

executive_producer_auth_header = {
    'Authorization': bearer_tokens['Executive Producer']
}

class capstonTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        # self.database_name="bookapp"
        self.client = self.app.test_client
        database_path = 'postgresql://postgres:12@127.0.0.1:5432/castingcampany'
        #database_path = os.environ['DATABASE_PATH']
        setup_db(self.app, database_path)
        #db_create_all()



    def tearDown(self):
        # executed after each test
        pass


    #===============Test actors endpoint===============


    def test_create_new_actor(self):
            """Test POST new actor."""
            json_create_actor = {
                'name': 'Johin',
                'age': 25,
                'gender':'male'
            }

            res = self.client().post('/actors', json=json_create_actor, headers=casting_director_auth_header)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['created'], 16)

    
    def test_error_401_new_actor(self):
        """Test POST new actor without Authorization"""
        json_create_actor = {
            'name': 'emma',
            'age': 21,
            'gender': 'female'
        }

        res = self.client().post('/actors', json=json_create_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'],'Authorization header is expected.')

    def test_error_422_create_new_actor(self):
        """Test Error POST new actor with missing records"""

        json_create_actor = {
            'age': 19
        }

        res = self.client().post('/actors', json=json_create_actor, headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'name can not be blank')


    def test_get_all_actors(self):
        """Test GET all actors."""
        res = self.client().get('/actors?page=1',headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actors']) > 0)

    def test_error_401_get_all_actors(self):
        """Test GET all actors w/o Authorization."""
        res = self.client().get('/actors?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected.')

    def test_error_404_get_actors(self):
        """Test Error GET all actors."""
        res = self.client().get('/actors?page=1125125125', headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'no actors found in database.')

    def test_edit_actor(self):
        """Test PATCH existing actors"""
        json_edit_actor = {
            'age': 45
        }
        res = self.client().patch('/actors/7', json=json_edit_actor, headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actor']) > 0)

    def test_error_400_edit_actor(self):
        """Test PATCH with non json body"""

        res = self.client().patch('/actors/123412', headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'request does not contain a valid JSON body.')

    def test_error_404_edit_actor(self):
        """Test PATCH with non valid id"""
        json_edit_actor = {
            'updated_age': 90
        }
        res = self.client().patch('/actors/786', json=json_edit_actor,
                                  headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'requested actor id not found')

    def test_error_401_delete_actor(self):
        """Test DELETE existing actor without Authorization"""
        res = self.client().delete('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected.')

    def test_error_403_delete_actor(self):
        """Test DELETE existing actor with missing permissions"""
        res = self.client().delete('/actors/1', headers=casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Permission not found.')



    def test_delete_actor(self):
        """successful Test DELETE existing actor"""
        res = self.client().delete('/actors/8', headers = casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['delete'], 8)

    def test_error_404_delete_actor(self):
        """Test DELETE non existing actor"""
        res = self.client().delete('/actors/898', headers = casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'] ,'no actor with this id found')



    #===============Test movies endpoint===============

    def test_create_new_movie(self):
        """Test successful POST new movie."""

        json_new_movie = {
            'title': 'the proposal',
            'release_date': date.today()
        }

        res = self.client().post('/movies', json=json_new_movie, headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['created'], 10)

    def test_error_422_create_new_movie(self):
        """Test Error POST new movie."""

        json_create_movie = {
            'release_date': date.today()
        }

        res = self.client().post('/movies', json=json_create_movie, headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'title can not be blank')

    def test_get_all_movies(self):
        """Test GET all movies."""
        res = self.client().get('/movies?page=1', headers=casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['movies']) > 0)

    def test_error_401_get_all_movies(self):
        """Test GET all movies without Authorization."""
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected.')

    def test_error_401_delete_movie(self):
        """Test DELETE existing movie without Authorization"""
        res = self.client().delete('/movies/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected.')

    def test_error_403_delete_movie(self):
        """Test DELETE existing movie with wrong permissions"""
        res = self.client().delete('/movies/8', headers=casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Permission not found.')

    def test_delete_movie(self):
        """Test DELETE existing movie"""
        res = self.client().delete('/movies/7', headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['delete'], 7)

    def test_error_404_delete_movie(self):
        """Test DELETE non existing movie"""
        res = self.client().delete('/movies/8887', headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'no movies found in database')

    if __name__ == "__main__":
        unittest.main()

