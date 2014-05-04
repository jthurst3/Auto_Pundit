# punditry_app.py
# runs Automated Punditry program with Flask
# J. Hassler Thurston
# Personal website
# 3 May 2014

from datetime import timedelta
from flask import Flask, request, jsonify, abort, make_response, current_app
from functools import update_wrapper
import punditry_main

# from http://librelist.com/browser/flask/2012/6/7/execute-at-flask-initialization/#a0b5c59832f372f69be6f6e2af4ae4f9
def create_app():
     app = Flask(__name__)
     def preprocess():
     	punditry_main.preprocess()
     preprocess()

     return app

# for debugging

app = create_app()

# from http://flask.pocoo.org/snippets/56/
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        f.required_methods = ['OPTIONS']
        return update_wrapper(wrapped_function, f)
    return decorator

# error handling
# responses modified from http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify( { 'error': 'no JSON' } ), 400)
@app.errorhandler(405)
def not_allowed(error):
    return make_response(jsonify( { 'error': 'Method not allowed' } ), 405)
@app.errorhandler(500)
def internal_error(error):
	return make_response(jsonify( { 'error': 'Internal server error' } ), 500)


# For finishing sentences, JSON requests should be in this form:
# {
# 	'grams': the "n" in ngrams,
# 	'pundit': the name of the pundit,
# 	'starttext': beginning of a sentence that the pundit finishes
# }

@app.route('/finish_sentence', methods = ['POST'])
@crossdomain(origin='*', headers='Content-Type') # TODO: update origin so that it only accepts hasslerthurston.com
def complete_sentence():
	# check to see if JSON exists
	if not request.json:
		abort(400)
	# check to see if JSON is in the right format
	if not checkJSONFinishSentence(request.json):
		abort(400)

	# if it is, define a variable to keep track of whether the computations ran successfully
	successful = True
	# and check to see if it initialized correctly
	# if not punditry_main.successfulInit:
	# 	print 'no successful initialization'
	# 	successful = False
	# if everything went well, return a JSON to the correct URL
	if successful:
		sentence = punditry_main.complete_sentence(request.json['grams'], request.json['pundit'], request.json['starttext'])
		return jsonify({'sentence': sentence})
	else: abort(500)

# For responding to what someone else says, JSON requests should be in this form:
# {
# 	'grams': the "n" in ngrams,
# 	'pundit': the name of the pundit,
# 	'responsetext': sentence that the pundit must respond to
# }

@app.route('/respond_to_pundit', methods = ['POST'])
@crossdomain(origin='*', headers='Content-Type') # TODO: update origin so that it only accepts hasslerthurston.com
def respond():
	# check to see if JSON exists
	if not request.json:
		abort(400)
	# check to see if JSON is in the right format
	if not checkJSONRespondToSentence(request.json):
		abort(400)

	# if it is, define a variable to keep track of whether the computations ran successfully
	successful = True
	# and check to see if it initialized correctly
	# if not punditry_main.successfulInit:
	# 	print 'no successful initialization'
	# 	successful = False
	# if everything went well, return a JSON to the correct URL
	if successful:
		sentence = punditry_main.respond(request.json['grams'], request.json['pundit'], request.json['responsetext'])
		return jsonify({'sentence': sentence})
	else: abort(500)


# A list of pundits that our application can handle
allowed_pundits = ['Limbaugh', 'Bloomberg']

# checks to see if JSON from client is in the correct format (for finishing sentences)
def checkJSONFinishSentence(json):
	# rows, columns, and moves fields must exist
	if not 'grams' in request.json or not 'pundit' in request.json or not 'starttext' in request.json:
		return False
	# gram must be an integer
	if not isinstance(request.json['grams'], int):
		return False
	# grams must be between 1 and 6
	if request.json['grams'] < 1 or request.json['grams'] > 6:
		return False
	# pundit must be a string
	if not isinstance(request.json['pundit'], str) and not isinstance(request.json['pundit'], unicode):
		return False
	# pundit must exist in our database
	if not request.json['pundit'] in allowed_pundits:
		return False
	# starttext must be a list of words
	if not isinstance(request.json['starttext'], list):
		return False
	if not all((isinstance(word, str) or isinstance(word, unicode)) for word in request.json['starttext']):
		return False
	# if all this is satisfied, JSON is in the correct format
	return True

# checks to see if JSON from client is in the correct format (for responding to pundits)
def checkJSONRespondToSentence(json):
	# rows, columns, and moves fields must exist
	if not 'grams' in request.json or not 'pundit' in request.json or not 'responsetext' in request.json:
		return False
	# gram must be an integer
	if not isinstance(request.json['grams'], int):
		return False
	# grams must be between 1 and 6
	if request.json['grams'] < 1 or request.json['grams'] > 6:
		return False
	# pundit must be a string
	if not isinstance(request.json['pundit'], str) and not isinstance(request.json['pundit'], unicode):
		return False
	# pundit must exist in our database
	if not request.json['pundit'] in allowed_pundits:
		return False
	# responsetext must be a list of words
	if not isinstance(request.json['responsetext'], list):
		return False
	if not all((isinstance(word, str) or isinstance(word, unicode)) for word in request.json['responsetext']):
		return False
	# if all this is satisfied, JSON is in the correct format
	return True

if __name__ == '__main__':
	# MAKE SURE TO NOT HAVE debug=True WHEN PUSHING TO PRODUCTION
	app.run(debug=True)





