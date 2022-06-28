import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):

    page = request.args.get('page', 1, type=int)
    print(page)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/trivia/*": {"origins": "*"}})
   
    CORS(app)
    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=['GET'])
    # @cross_origin()
    def get_categories():

        categories = Category.query.order_by('id').all()
        print(len(categories))
        category_list = {i.id: i.type for i in categories}

        if len(categories) == 0:
            abort(404)

        return jsonify({

            'categories': category_list
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
# how to change the page number and get notified if no more data

    @ app.route('/questions', methods=['GET'])
    # @cross_origin()
    def get_questions():

        questions = Question.query.order_by('id').all()
        total_questions = [question.format() for question in questions]
        questions = paginate_questions(request, questions)
        categories = Category.query.order_by('id').all()
        current_categories = {i.id: i.type for i in categories}

        if len(total_questions) == 0:
            abort(404)

        elif len(questions) == 0:
            abort(422)
        else:
            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(total_questions),
                'categories': current_categories,
                'currentCategory': None
            }) 
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @ app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_specific_question(question_id):

        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if question is None:
            abort(404)

        question.delete()

        return get_questions()
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @ app.route('/questions/add', methods=['POST'])
    def create_question():

        body = request.get_json()
        print(body)
        try:
            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_category = body.get('category', None)
            new_difficulty = body.get('difficulty', None)
            if not new_question or not new_answer:
                abort(422)
            else:
                category_item = Category.query.filter(
                    Category.id == int(new_category)).one_or_none()
                category_id = category_item.id

                question_data = Question(
                    question=new_question.capitalize(), answer=new_answer.capitalize(), category=category_id, difficulty=new_difficulty)

                question_data.insert()
                return jsonify({
                    "success": True
                })
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @ app.route('/questions/search', methods=['POST'])
    def search_question():

        search_input = request.get_json().get('searchTerm', '')
        print(search_input)

        try:
            total_questions = Question.query.filter(
                Question.question.ilike('%{}%'.format(search_input))).all()
            if not search_input or not total_questions:
                abort(422)
            else:
                questions = paginate_questions(request, total_questions)
                return jsonify({
                    'success': True,
                    'questions': questions,
                    'totalQuestions': len(total_questions),
                    'currentCategory': None,
                    'searchWord': search_input
                })
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def category_questions(category_id):
        try:

            current_category = Category.query.filter(
                Category.id == category_id).one()
            total_questions = Question.query.filter(
                Question.category == category_id).all()

            questions = paginate_questions(
                request, total_questions)

            return jsonify({
                'questions': questions,
                'totalQuestions': len(total_questions),
                'currentCategory': current_category.type
            })
        except:
            abort(500)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quizz():
        body = request.get_json()
        previous_question = body['previous_questions']
        quiz_category = body.get('quiz_category')
        print(quiz_category['id'])
        print(type(quiz_category['id']))
        print(int(quiz_category['id']))
        categories = Category.query.all()
        if int(quiz_category['id']) != 0:
            if len(previous_question) > 0:
                question_collections = Question.query.filter(
                    Question.id.notin_(previous_question), (Question.category == quiz_category['id'])).all()

            else:
                question_collections = Question.query.filter(
                    Question.category == quiz_category['id']).all()

        # elif int(quiz_category['id']) not in [i.id for i in categories]:
        #     abort(404)

        else:
            if len(previous_question) > 0:
                question_collections = Question.query.filter(
                    Question.id.notin_(previous_question)).all()
            else:
                question_collections = Question.query.all()

        # print(question_collections)
        try:
            question_list = [i.format() for i in question_collections]
            # question_list will have empty sequence if it runs out
            random_question = random.choice(question_list)
            print(random_question)

            return jsonify({
                "success": True,
                "question": random_question
            })

        except:
            return jsonify({
                "success": True,
                "question": None
            })
        #     print('there are no more questions')
        # abort(404)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @ app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404,
                     "message": "resource not found"}),
            404,
        )

    @ app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422,
                     "message": "unprocessable"}),
            422,
        )

    @ app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @ app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405,
                     "message": "method not allowed"}),
            405,
        )

    @ app.errorhandler(500)
    def server_error(error):

        return (
            jsonify({"success": False, "error": 500,
                     "message": "Internal Server Error"}),
            500,
        )

    return app

