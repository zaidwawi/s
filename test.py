import os
import unittest
import json

from app import APP
from models import setup_db, Movie, Actor

CASTING_ASSISTANT = os.environ["ASSISTANT"]
CASTING_DIRECTOR = os.environ["DIRECTOR"]
EXECUTIVE_PRODUCER = os.environ["PRODUCER"]


class CastingAgencyTest(unittest.TestCase):
    def setUp(self):
        self.app = APP
        self.client = self.app.test_client
        self.test_movie = {
            "title": "Jhone Smith",
            "release_date": "15-12-2021",
        }
        self.test_actor = {
            "name": "odai slaiti",
            "age": 35,
            "gender": "male"
        }
        self.database_path = os.environ["DATABASE_URL"]

        setup_db(self.app, self.database_path)


    def post_actor(self, token):
        response = self.client().post(
            "/actors",
            json=self.test_actor,
            headers={"Authorization": f"Bearer {token}"},
        )
        return response

    def post_movie(self, token):
        response = self.client().post(
            "/movies",
            json=self.test_movie,
            headers={"Authorization": f"Bearer {token}"},
        )
        return response

    def patch_actor(self, actor_id, token):
        response = self.client().patch(
            f"/actors/{actor_id}",
            json={
                "name": "Tom Hanks",
                "age": "30",
                "gender": "male"
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        return response

    def patch_movie(self, movie_id, token):
        response = self.client().patch(
            f"/movies/{movie_id}",
            json={
                "title": "Wanted",
                "release_date": "2020-12-20"
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        return response

    def delete_actor(self, actor_id, token):
        response = self.client().delete(
            f"/actors/{actor_id}", headers={"Authorization": f"Bearer {token}"}
        )
        return response

    def delete_movie(self, movie_id, token):
        response = self.client().delete(
            f"/movies/{movie_id}", headers={"Authorization": f"Bearer {token}"}
        )
        return response


    def test_get_all_movies(self):
        response = self.client().get(
            "/movies",
            headers={"Authorization": f"Bearer {EXECUTIVE_PRODUCER}"}
        )
        data = json.loads(response.data)
        self.assertEqual(data["success"], True)
        self.assertEqual(response.status_code, 200)

    def test_get_movie_by_id(self):
        response = self.client().get(
            "/movies/1",
            headers={
                "Authorization": f"Bearer {EXECUTIVE_PRODUCER}"
            }
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])


    def test_404_get_movie_by_id(self): 
        response = self.client().get(
            f"/movies/{2345}",
            headers={"Authorization": f"Bearer {EXECUTIVE_PRODUCER}"}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_post_movie(self):
        response = self.post_movie(EXECUTIVE_PRODUCER)
        data = json.loads(response.data)
        movie = data["created_movie"]
        self.assertEqual(data["success"], True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(movie, movie)

        self.delete_movie(movie["id"], EXECUTIVE_PRODUCER)

    def test_401_post_movie(self):
        response = self.post_movie(CASTING_ASSISTANT)
        data = json.loads(response.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(response.status_code, 401)

    def test_patch_movie(self):
        post_movie = self.post_movie(EXECUTIVE_PRODUCER)
        movie = json.loads(post_movie.data)["created_movie"]

        response = self.patch_movie(movie["id"], EXECUTIVE_PRODUCER)
        data = json.loads(response.data)

        self.assertEqual(data["success"], True)
        self.assertNotEqual(movie, data["patched_movie"])

        self.delete_movie(movie["id"], EXECUTIVE_PRODUCER)

    def test_404_patch_movie(self):
        response = self.patch_movie(1234, EXECUTIVE_PRODUCER)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_delete_movie(self):
        post_movie = self.post_movie(EXECUTIVE_PRODUCER)
        movie = json.loads(post_movie.data)

        response = self.delete_actor(
            movie["created_movie"]["id"],
            EXECUTIVE_PRODUCER
            )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_delete_movie(self):
        response = self.delete_movie(5134, EXECUTIVE_PRODUCER)
        data = json.loads(response.data)
        self.assertEqual(data["success"], False)


    def test_get_all_actors(self):
        response = self.client().get(  
            "/actors",
            headers={
                "Authorization": f"Bearer {EXECUTIVE_PRODUCER}" 
                }
        )
        data = json.loads(response.data)
        self.assertEqual(data["success"], True)
        self.assertEqual(response.status_code, 200) 

    def test_get_actor_by_id(self): 
        post_actor = self.post_actor(EXECUTIVE_PRODUCER)
        actor = json.loads(post_actor.data)["created_actor"]
        actor_id = actor["id"]

        response = self.client().get(
            f"/actors/{actor_id}", 
            headers={"Authorization": f"Bearer {EXECUTIVE_PRODUCER}"}, 
        )
        data = json.loads(response.data)

        self.assertEqual(data["success"], True)
        self.assertEqual(data["actor"], actor)

        self.delete_actor(actor_id, EXECUTIVE_PRODUCER)

    def test_404_get_actor_by_id(self): 
        response = self.client().get(
            f"/actors/{2345}",
            headers={
                "Authorization": f"Bearer {EXECUTIVE_PRODUCER}"
                }
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_post_actor(self):
        response = self.post_actor(EXECUTIVE_PRODUCER) 
        data = json.loads(response.data)
        actor = data["created_actor"] 
        self.assertEqual(data["success"], True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(actor, actor)

        self.delete_actor(actor["id"], EXECUTIVE_PRODUCER)

    def test_401_post_actor(self):
        response = self.post_actor(CASTING_ASSISTANT) 
        data = json.loads(response.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(response.status_code, 401)

    def test_patch_actor(self): 
        post_actor = self.post_actor(EXECUTIVE_PRODUCER) 
        actor = json.loads(post_actor.data)["created_actor"]

        response = self.patch_actor(actor["id"], EXECUTIVE_PRODUCER)
        data = json.loads(response.data)

        self.assertEqual(data["success"], True)
        self.assertNotEqual(actor, data["patched_actor"])

        self.delete_actor(actor["id"], EXECUTIVE_PRODUCER)

    def test_404_patch_actor(self): 
        response = self.patch_actor(1234, EXECUTIVE_PRODUCER)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_delete_actor(self):  
        post_actor = self.post_actor(EXECUTIVE_PRODUCER)
        actor = json.loads(post_actor.data)

        response = self.delete_actor(
            actor["created_actor"]["id"],
            EXECUTIVE_PRODUCER
            )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_delete_actor(self): 
        response = self.delete_actor(5134, EXECUTIVE_PRODUCER)
        data = json.loads(response.data)
        self.assertEqual(data["success"], False)




if __name__ == "__main__":
    unittest.main()
