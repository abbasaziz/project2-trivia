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
        database_path = 'postgresql://{}:{}@{}/{}'.format("postgres", "root", "localhost:5432", "trivia_test")
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
    
    def test_get_categories_success(self):
        # Test to get results from a categories endpoint
        res = self.client().get('/categories')
        # Transforming the server response into JSON data 
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    # to GET the categories when category_id isn't there
    def test_get_categories_404(self):
        # Trying to get an erronous high value which actually doesn't exist
        res = self.client().get('/categories/400000')
        # Transforming the server response into JSON data 
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    # Making a test for GET request on questions endpoint
    def test_get_questions_success(self):
        # For getting results from that endpoint
        res = self.client().get('/questions')
        # Transforming the server response into JSON data 
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    # Making a test for GET request error on questions endpoint when pagination value is set on a random high number
    def test_get_questions_404(self):
        # Error test for GET request when pagination has a high value
        res = self.client().get('/questions?page=6420000')
        # Transforming the server response into JSON data 
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    # Implementing a test to make sure that the functionality to retrieve questions by category works
    def test_get_category_questions_success(self):
        # Getting basic category results from a category that is confirmed to
        # exist
        res = self.client().get('/categories/1/questions')
        # Transforming the server response into JSON data 
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    # Implementing test to analyze error condition and what happens when an unreal category is passed to endpoint
    def test_get_category_questions_404(self):
        # Trying to get output from endpoint
        res = self.client().get('/categories/23400000/questions')
        # Transforming the server response into JSON data 
        data = json.loads(res.data)
        # To ensure that the data passes error tests
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    # DELETE Tests
    # --------------------------------------------------------------------------
    # Implementing test of delete functionality from DELETE endpoint

    def test_delete_question_success(self):
        # Implementing a sample question
        dummy_question = Question(question='What came first, chicken or the egg?',
                                  answer='The omellette',
                                  difficulty=1,
                                  category=1)

        # Inserting sample question to SQL database
        dummy_question.insert()

        # Retrieving the ID from newly inserted question
        dummy_question_id = dummy_question.id

        # Trying to remove sample question
        res = self.client().delete('/questions/{}'.format(dummy_question_id))
        # Transforming the server response into JSON data 
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(dummy_question_id))

    # Implementing a test to check if the correct error form is shown when we pass an unexpected DELETE request
    def test_delete_question_422(self):
        # Trying to delete a non-existent question with an error request
        res = self.client().delete('/questions/78900000')
        # Transforming data into JSON
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unable to process request')

    # POST Tests
    # ----------------------------------------------------------------------
    # Implementing a test to ensure that adding a question works correctly

    def test_create_question_success(self):
        # Implementing sample question data to add
        dummy_question_data = {
            'question': 'What happens after death?',
            'answer': '1244155',
            'difficulty': 1,
            'category': 1
            }

        # Trying to create question with sample question data
        res = self.client().post('/questions', json=dummy_question_data)
        # Transforming data into JSON
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # Implementing a test to find out what happens when we insert a question with missing data
    def test_create_question_422(self):
        # Implementing sample question data to add
        dummy_question_data = {
            'question': 'What happens after death?',
            'answer': '1244155',
        #   'difficulty': 1,
            'category': 1
            }

        # Trying to post a question with sample question data
        res = self.client().post('/questions', json=dummy_question_data)
        # Transforming data into JSON
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unable to process request')

    # Implementing a test to ensure searching works correctly
    def test_search_questions_found(self):
        # Establishing a very basic new search
        new_search = {'search_term': 'country'}

        # Performing search with search term
        res = self.client().post('/questions/search', json=new_search)
        # Transforming data into JSON
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    # Implementing a test to ensure searching works if no results are found
    def test_search_questions_404(self):
        # Establishing a very basic bogus search
        bogus_search = {'search_term': ''}

        # Trying to search with search term
        res = self.client().post('/questions/search', json=bogus_search)
        # Transforming data into JSON
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    # Implementing a test to ensure playing a quiz works properly
    def test_play_quiz_success(self):
        # Implementing sample round data
        dummy_round_data = {
            'previous_questions': [],
            'quiz_category': {'type': 'Entertainment',
                              'id': 5}
        }

        # Starting new quiz round by invoking endpoint
        res = self.client().post('/quiz', json=dummy_round_data)
        # Transforming data into JSON
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # Implementing test to check what happens when 'quiz' endpoint experiences
    # 404
    def test_play_quiz_422(self):
        dummy_round_data = {
            #    'previous_questions': [],
            'quiz_category': {'type': 'Entertainment',
                              'id': 5}
        }

        # Trying to start new quiz round
        res = self.client().post('/quiz', json=dummy_round_data)
        # Transforming data into JSON
        data = json.loads(res.data)

        # To ensure that the data passes tests
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unable to process request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()