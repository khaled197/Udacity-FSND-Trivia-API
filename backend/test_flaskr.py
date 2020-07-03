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
        self.database_path = "postgres://postgres:passwort@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()
        #
        self.question = {
            "question": "Gump, what is your sole purpose in this army?",
            "answer": "To do whatever you tell me drill sergeant",
            "category": 2,
            "difficulty": 3
        }

        self.another_question = {
            "question": "Gump, Are you stupid?",
            "answer": "No",
            "category": 2,
            "difficulty": 3

        }
        self.invalid_question = {
            "question": "",
            "answer": "",
            "category": 2,
            "difficulty": 3
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])

    # def test_404_get_categories(self):
    #     res = self.client().get('/categories')
    #     data = json.loads(res.data)
    #
    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data['success'], False)


    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], None)

    def test_404_get_questions(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # def test_delete_question(self):
    #     res = self.client().delete('questions/6')
    #     data = json.loads(res.data)
    #
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['deleted'], 6)
    #     self.assertEqual(data['success'], True)

    def test_404_delete_question(self):
        res = self.client().delete('questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


    def test_post_question(self):
        res = self.client().post('/questions', json =  self.question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_post_question(self):
        res = self.client().post('/questions', json =  self.question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_400_post_question(self):
        res = self.client().post('/questions', json =  self.invalid_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_search_questions_without_results(self):
        res = self.client().post('questions/search', json = {"searchTerm": "Noquestionfound"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_questions_with_results(self):
        res = self.client().post('questions/search', json = {"searchTerm": "who"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)


    def test_get_by_categories(self):
        category = 1
        res = self.client().get('/categories/{}/questions'.format(str(category)))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], category)
        self.assertIsInstance(data['questions'], list)


    def test_404_get_by_categories(self):
        category = 100
        res = self.client().get('/categories/{}/questions'.format(str(category)))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_play_quizz(self):
        category = 1
        previous_questions = [1,2]
        question = Question.query.filter(Question.category == category).first()
        res =self.client().post('/quizzes', json = {'quizCategory': category, 'previousQuestions': previous_questions})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertNotIn(data['question']['id'], previous_questions)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
