import logging
import yaml
from logging import handlers
from flask import Flask, session
from flask_restful import Resource, Api, reqparse
from hangmanapi import utils
import flask_restful.inputs
import colorama
import random
import pickle
from operator import itemgetter

with open('config.yml') as f:
    config = yaml.safe_load(f)

main_logger = logging.getLogger('hangman.error')
main_logger.setLevel(logging.DEBUG)  # Remove this when in production
if len(main_logger.handlers) > 0:
    main_logger.handlers[0].setLevel(logging.INFO)  # terminal handler

file_logging_format = logging.Formatter(
    "[{asctime}|" + "{levelname}]" +
    " - {message}", style='{'
    )

file_logging_handler = handlers.WatchedFileHandler(
    config['storage_path'] + '/logs/hangman_api_log_watchedfile'
    )

file_logging_handler.setLevel(logging.DEBUG)
file_logging_handler.setFormatter(file_logging_format)

main_logger.addHandler(file_logging_handler)

app = Flask(__name__)
api = Api(app)

# Use session to save status of game
app.secret_key = '3d_hubs'
app.config['SESSION_TYPE'] = 'filesystem'


class ContextAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return ("{0} {1}".format(self.extra['context'], msg), kwargs)


class HealthCheck(Resource):
    def get(self):
        return True


class StartSession(Resource):
    """Initializes a new session with a user. returns user_id and score"""
    def get(self, user_id):
        # Clear the session first
        session.clear()
        session['user_id'] = user_id
        session['score'] = 0

        return{'user_id': user_id, 'score': 0}


class CheckSession(Resource):
    """Checks if a session is initialized. Returns a dict with the user_id"""
    def get(self):
        user_id = session.get('user_id', None)
        if not user_id:
            return {'user_id': None}

        return {'user_id': user_id}


class StartNewGame(Resource):
    """Starts a new game. Returns dict with user_id, word_state, guessed_letters, attempts_remaining, score"""
    def get(self):

        user_id = session.get('user_id', None)
        if not user_id:
            return {'user_id': None}
        score = session.get('score', 0)

        word_to_guess = self.get_new_word()

        session['attempts_remaining'] = 5
        session['word_to_guess'] = word_to_guess
        session['guessed_letters'] = []
        session['score'] = score
        session['word_state'] = utils.create_word_state(word_to_guess, [])
        main_logger.debug(session)
        return utils.create_json_return(session, 'Ready to play?')

    """Gets a new word for a new game. Currently hardcoded to 6 values, but can be extended to read from disk/DB"""
    def get_new_word(self):
        word_list = ['3dhubs', 'marvin', 'print', 'filament', 'order', 'layer']

        return random.choice(word_list).lower()


class GuessLetter(Resource):

    def __init__(self):
        self.user_id = session.get('user_id', None)

        self.guessed_letters = session.get('guessed_letters', None)

        self.word_to_guess = session.get('word_to_guess', None)

    """Lets user guess if a letter is in the word.
    Updates session, and returns dict with user_id, word_state, guessed_letters, attempts_remaining, score"""
    def get(self, input_str=None):
        if not self.user_id:
            return utils.create_json_return(session, "401 Unknown user")
        if input_str is None:
            return utils.create_json_return(session, "No guessed letters")
        if self.word_to_guess is None:
            return utils.create_json_return(session, "No word to guess")

        input_str = input_str.lower()

        # check for correct alphanumeric here
        # Improvement: check for unicode accents like 'é'
        if input_str.isalnum() is False:
            return utils.create_json_return(session, "Please only fill in letters or numbers")

        if len(input_str) == 1:
            return self.guess_single_letter(input_str)

        elif len(input_str) == len(session['word_to_guess']):
            return self.guess_whole_word(input_str)
        else:
            return utils.create_json_return(session, "Either choose one letter or guess the word")

    # Logic for guessing a single letter in a word
    def guess_single_letter(self, input_letter):
        if input_letter in self.guessed_letters:
            return utils.create_json_return(session,
                                            "You've already guessed this letter, I'd use your attempt for something you haven't guessed yet.")
        self.guessed_letters.append(input_letter)
        session['guessed_letters'] = self.guessed_letters

        if input_letter in self.word_to_guess:
            session['word_state'] = utils.create_word_state(self.word_to_guess, self.guessed_letters)
            if '_' not in session['word_state']:
                points_to_add = utils.get_points_won(session['attempts_remaining'])
                utils.update_points(session, points_to_add)
                return utils.create_json_return(session,
                                                "You win! You now have {} points".format(session.get('score', 0)))

            return utils.create_json_return(session, "Correct")

        session['attempts_remaining'] -= 1
        if session['attempts_remaining'] == 0:
            points_to_add = utils.get_points_won(session['attempts_remaining'])
            utils.update_points(session, points_to_add)
            return utils.create_json_return(session, "You didn't guess the word. The word was {}".format(self.word_to_guess))

        return utils.create_json_return(session, "'{}' is not in the word".format(input_letter))

    # Logic for guessing a whole word at once
    def guess_whole_word(self, input_str):
        if input_str == self.word_to_guess:
            points_to_add = utils.get_points_won(session['attempts_remaining'], session['word_state'])

            utils.update_points(session, points_to_add)
            return utils.create_json_return(session,
                                            "The word is {}! You've won {} points. Save score, Continue, or Restart?".format(
                                                self.word_to_guess, points_to_add))

        session['attempts_remaining'] -= session['attempts_remaining']
        if session['attempts_remaining'] == 0:
            utils.update_points(session)
            return utils.create_json_return(session,
                                            "You didn't guess the word. The word was {}".format(self.word_to_guess))

        return utils.create_json_return(session, "you're guessing the word to be {}".format(input_str))


class SaveHighScore(Resource):
    """Saves your high score to disk and resets your session"""

    def __init__(self):
        self.user_id = session.get('user_id', None)
        self.score = session.get('score', None)

    def get(self):
        session.clear()

        high_score_path = config['storage_path'] + '/logs/high_scores'
        try:
            with open(high_score_path, 'rb') as fp:
                high_score_list = pickle.load(fp)
        except:
            high_score_list = [('Andrew', 9001)]

        if self.user_id is not None:
            high_score_list.append((self.user_id, self.score))

        high_score_list = sorted(high_score_list, key=itemgetter(1), reverse=True)[:10]

        with open(high_score_path, 'wb') as wp:
            pickle.dump(high_score_list, wp)

        return high_score_list


api.add_resource(HealthCheck, '/health_check')
api.add_resource(CheckSession, '/check_session')
api.add_resource(StartSession, '/start_session/<string:user_id>')
api.add_resource(StartNewGame, '/start_new_game')
api.add_resource(GuessLetter, '/guess_letter', '/guess_letter/<string:input_str>' )
api.add_resource(SaveHighScore, '/save_high_score')