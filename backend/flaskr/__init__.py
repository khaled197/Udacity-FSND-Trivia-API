import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    q_list = [q.format() for q in selection]
    current_questions = q_list[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route('/categories')
    def get_categories():

        cat = Category.query.order_by(Category.id).all()

        if len(cat) == 0:
            abort(404)

        cat_list = {c.id: c.type for c in cat}

        return jsonify({
                        'success': True,
                        'categories': cat_list,
                        'total_categories': len(cat_list)
        })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination
    at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''

    @app.route('/questions')
    def get_questions():

        abort_code, questions, categories, selection = None, None, None, None

        try:
            selection = Question.query.order_by(Question.id).all()
            questions = paginate_questions(request, selection)
            categories = Category.query.order_by(Category.id).all()
            cat_list = {c.id: c.type for c in categories}

            if len(questions) == 0:
                abort_code = 404
                raise Exception('not found')

        except Exception as e:
            print(sys.exc_info(), questions)
            if abort_code == 404:
                abort(404)
            abort(422)

        return jsonify({
                        'success': True,
                        'questions': questions,
                        'total_questions': len(selection),
                        'categories': cat_list,
                        'current_category': None
        })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        abort_code = None
        try:
            question = Question.query.filter_by(id=question_id).one_or_none()
            if question is None:
                abort_code = 404
                raise Exception('not found')

            question.delete()
        except Exception as e:
            print(sys.exc_info(), question)
            if abort_code == 404:
                abort(404)
            abort(422)

        return jsonify({
                        'success': True,
                        'deleted_id': question_id
        })

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    '''

    @app.route('/questions', methods=['POST'])
    def add_question():

        abort_code, question_id = None, None
        body = request.get_json()
        try:
            question = body['question']
            answer = body['answer']
            category = body['category']
            difficulty = body['difficulty']
            rating = body['rating']

            if question == "" or answer == "":
                abort_code = 400
                raise Exception('Bad request')

            new_question = Question(question, answer, category,
                                    difficulty, rating)

            new_question.insert()
            question_id = new_question.id

        except Exception as e:
            print(sys.exc_info(), body)
            if abort_code == 400:
                abort(400)
            else:
                abort(422)

        return jsonify({
                "success": True,
                "question_id": question_id
        })

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    @app.route('/questions/search', methods=['POST'])
    def search_questions():

        search_term, questions, selection = None, None, None
        try:
            search_term = request.get_json()['searchTerm']
            selection = Question.query.filter(Question.question.ilike(
                '%{}%'.format(search_term))).all()
            questions = paginate_questions(request, selection)

        except Exception as e:
            print(sys.exc_info())
            abort(422)

        return jsonify({
                        'success': True,
                        'total_questions': len(selection),
                        'questions': questions,
                        'current_category': None
        })

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    @app.route('/categories/<int:cat_id>/questions')
    def get_by_category(cat_id):

        abort_code = None

        try:
            category = Category.query.filter_by(id=cat_id).one_or_none()
            if category is None:
                abort_code = 404
                raise Exception('Resource Not Found')

            selection = Question.query.filter_by(category=cat_id).all()
            questions = paginate_questions(request, selection)

        except Exception as e:
            print(sys.exc_info())
            if abort_code == 404:
                abort(404)
            abort(422)

        return jsonify({
                        'success': True,
                        'questions': questions,
                        'total_questions': len(selection),
                        'current_category': cat_id
        })

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random question within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.

    '''

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        abort_code = None

        try:

            previous_questions = request.get_json()['previous_questions']
            current_category = request.get_json()['quiz_category']
            if previous_questions is None or current_category is None:
                abort_code = 400
                raise Exception('Bad Request')

            questions_list = None
            question = None
            if current_category['id'] == 0:
                questions_list = Question.query.all()
            else:
                questions_list = Question.query.filter_by(
                    category=current_category['id']).all()

            for q in questions_list:
                if q.id not in previous_questions:
                    question = q.format()
                    break
        except Exception as e:
            print(sys.exc_info(), request.get_json())
            if abort_code:
                abort(400)
            abort(422)

        return jsonify({
                        'success': True,
                        'question': question
        })

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 400,
            'success': False,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def bad_request(error):
        return jsonify({
            'error': 404,
            'success': False,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def bad_request(error):
        return jsonify({
            'error': 422,
            'success': False,
            'message': 'unprocessable'
        }), 422
    return app
