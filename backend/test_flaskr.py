import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','123','localhost:5432',  self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']) > 0)

    def test_fail_categories(self):
        res = self.client().get("/category?page=15")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])

    def test_questions_with_invalid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_delete_question(self):
        res = self.client().delete("/questions/15")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'] > 0)

    def test_delete_invalid_question_id(self):
        res = self.client().delete("/questions/1000000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_add_valid_question(self):
        res = self.client().post("/questions/add",
                                 json={"question": "Who is the president of USA", "answer": "Biden", "difficulty": 1, "category": "4"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_add_invalid_question(self):
        res = self.client().post("/questions/add",
                                 json={"question": "", "answer": "Biden", "difficulty": 1, "category": "History"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_term(self):
        res = self.client().post("/questions/search",
                                 json={"searchTerm": "What"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_invalid_search_term(self):
        res = self.client().post("/questions/search",
                                 json={"searchTerm": "%$"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertTrue(data['message'],  "resource not found")

    def test_questions_from_assigend_category(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['totalQuestions'])

    def test_questions_from_invalid_category(self):
        res = self.client().get("/categories/1000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data["message"], "Internal Server Error")

    def test_valid_random_quizz(self):
        res = self.client().post(
            "/quizzes", json={"previous_questions": [19], "quiz_category": {"type": "Art", "id": "2"}})
        data = json.loads(res.data)
        print(data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question']['id'] != 19)

    def test_fail_random_quizz(self):
        res = self.client().post(
            "/quizzes", json={"previous_questions": [], "quiz_category": {"type": "", "id": "10"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertTrue(data['message'], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()