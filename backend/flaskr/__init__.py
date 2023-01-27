from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    
    @app.after_request
    def add_access_control(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'ContentType,Authorization, True')



        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,PUT,DELETE,UPDATE,OPTIONS')

        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    

    @app.route("/categories", methods=["GET"])
    def get_categories():

        
        # Retrieve all categories in the database and order them by their type
        categories = Category.query.order_by(Category.type).all()


        # If there are no categories in the database, return a 404 error
        if not categories:
            abort(404)


        # Return all categories in a JSON format with success status
        return jsonify(
            {
                "success": True, 
                "categories": {category.id: category.type for category in categories}
            }
        )


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
    @app.route('/questions', methods=['GET'])
    def get_questions():
        all_questions = Question.query.order_by(Question.id).all()
        page = request.args.get('page', 1, type=int)
        
        
        # Creating start and end points based on static variable QUESTIONS_PER_PAGE 
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        
        
        # In order to apply pagination to each question group
        questions = [question.format() for question in all_questions]
        paginated_questions = questions[start:end]

        categories = Category.query.order_by(Category.type).all()

        
        if len(paginated_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(all_questions),
            'categories': {category.id: category.type
                           for category in categories},
            'current_category': None
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id: int):
       
        # Get the question from the database using the question_id passed in the URL
        question = Question.query.get(question_id)
        
        # If the question is not found, return a 404 error message
        if question is None:
            return jsonify({
                "success": False, 
                "error": f"Question {question_id} not found"}), 404


        # If the question is found, delete it from the database
        question.delete()


        # Return a success message with the deleted question's ID
        return jsonify({
            "success": True, 
            "deleted": question_id
        })


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        # Get data from the request body in JSON format
        body = request.get_json()

        # Extracting the necessary information from the request
        difficulty = body.get('difficulty')
        answer = body.get('answer')
        question = body.get('question')
        category = body.get('category')

        # Check if all the required fields are present
        if not (question and answer and difficulty and category):
            abort(422)

        try:
            # Create a new Question object with the data
            new_question = Question(question=question,
                                    answer=answer,
                                    difficulty=difficulty,
                                    category=category)

            # Insert the new question into the database
            new_question.insert()

            # Return a JSON object with success message and created question id
            return jsonify({
                'success': True,
                'created': new_question.id
            })

        except BaseException:
            # Handle any errors that may occur
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


    @app.route("/questions/search", methods=["POST"])
    def search_questions():

        # Retrieve the search term from the request data
        data = request.get_json()
        search_term = data.get("searchTerm")

    
        # If the search term is missing, return a bad request error
        if not search_term:
            return jsonify({
                            "success": False, 
                            "error": "Missing searchTerm parameter in your query."
                            }), 400
        
        
        # Use the filter method to search for questions that contain the search term
        search_results = (
            Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
        )
        

        # If no matching questions are found, return a not found error        
        if not search_results:
            return jsonify({
                "success": False, 
                "error": "We couldn't find any matching questions on our databse"
            }), 404
        
 
        # Otherwise, return the search results as a JSON response, including success status, questions, total_questions, and current_category
        return jsonify(
            {
                "success": True,
                "questions": [question.format() for question in search_results],
                "total_questions": len(search_results),
                "current_category": None,
            }
        )

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        # This route is used to get all the questions that belong to a specific category based on the category_id passed in the url


        # Get all questions that match the category_id
        questions = Question.query.filter(Question.category == category_id).all()


        # If no questions are found for the given category_id, return a 404 error
        if len(questions) == 0:
            abort(404)


        # Return a json object containing success status, list of questions, total number of questions, and the current category id
        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'total_questions': len(questions),
            'current_category': category_id
        })

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
    @app.route("/quiz", methods=["POST"])
    def play_quiz():
        
        try:
            # Retrieve data from the request body
            data = request.get_json()
            
            
            
            # Ensure the required data is present in the request
            if not all(key in data for key in ("quiz_category", "previous_questions")):
                return jsonify({
                    "success": False, 
                    "error": "Missing required parameters"
                }), 422
            


            # Assign the data to variables
            quiz_category = data.get("quiz_category")
            previous_questions = data.get("previous_questions")
            
            
            
            # Determine the questions to be used based on the category and previous questions
            if quiz_category["type"] == "click":
                available_questions = Question.query.filter(
                    Question.id.notin_(previous_questions)
                ).all()
            
            else:
                available_questions = Question.query.filter_by(
                    category=quiz_category["id"]
                ).filter(
                    Question.id.notin_(previous_questions)
                ).all()
            


            # Select a random question from the available questions
            if available_questions:
                new_question = random.choice(available_questions).format()
            else:
                new_question = None
            


            # Return a JSON response with the success status and the new question
            return jsonify({
                "success": True, 
                "question": new_question
            })
        

        # Handle any exceptions that may occur
        except BaseException:
            return jsonify({
                "success": False, 
                "error": "Unable to process the request"
            }), 422

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request',
        }), 400

    @app.errorhandler(422)
    def unable_to_process(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unable to process request'
        }), 422

    @app.errorhandler(500)
    def unable_to_process(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource Not Found'
        }), 404

    return app