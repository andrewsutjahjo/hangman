import pytest
import os

from hangmanapi import hangman_api


@pytest.fixture
def client():
    hangman_api.app.config['TESTING'] = True
    client = hangman_api.app.test_client()

    yield client


def set_test_sess(sess):
    sess['user_id'] = 'bar'
    sess['attempts_remaining'] = 5
    sess['word_to_guess'] = '3dhubs'
    sess['guessed_letters'] = []
    sess['score'] = 0
    sess['word_state'] = '______'


def test_healthcheck(client):
    rv = client.get('/health_check')
    assert rv.status_code == 200
    assert bool(rv.data) is True


def test_start_session(client):
    rv = client.get('/start_session/foo')
    json_data = rv.get_json()
    assert json_data['user_id'] == 'foo'


def test_start_new_game(client):
    """It should decrement the attempts remaining and add the letter to the guessed letter list"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
        sess['word_state'] = None
    rv = client.get('/start_new_game')
    json_data = rv.get_json()

    assert json_data['attempts_remaining'] == 5
    assert json_data['user_id'] == 'bar'
    assert json_data['word_state']


def test_guess_letter_unknown_user(client):
    """It should return an unknown user message"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
        sess['user_id'] = None
    rv = client.get('/guess_letter/3')
    json_data = rv.get_json()

    assert json_data['attempts_remaining'] == 5
    assert json_data['guessed_letters'] == []
    assert json_data['score'] == 0
    assert json_data['word_state'] == '______'
    assert json_data['message'] == "401 Unknown user"


def test_guess_letter_no_letter(client):
    """It should return a message to add a guessed letter"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
    rv = client.get('/guess_letter')
    json_data = rv.get_json()
    assert json_data['attempts_remaining'] == 5
    assert json_data['guessed_letters'] == []
    assert json_data['score'] == 0
    assert json_data['word_state'] == '______'
    assert json_data['message'] == "No guessed letters"


def test_guess_letter_non_alphanum(client):
    """It should return a message asking for alphanumeric characters"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
    rv = client.get('/guess_letter/~')
    json_data = rv.get_json()
    assert json_data['attempts_remaining'] == 5
    assert json_data['guessed_letters'] == []
    assert json_data['score'] == 0
    assert json_data['word_state'] == '______'
    assert json_data['message'] == "Please only fill in letters or numbers"


def test_guess_letter_correct(client):
    """It should add the letter to the guessed letter list and return an updated word_state"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
    rv = client.get('/guess_letter/3')
    json_data = rv.get_json()

    assert json_data['attempts_remaining'] == 5
    assert json_data['guessed_letters'] == ['3']
    assert json_data['score'] == 0
    assert json_data['word_state'] == '3_____'


def test_guess_letter_incorrect(client):
    """It should decrement the attempts remaining and add the letter to the guessed letter list"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
    rv = client.get('/guess_letter/a')
    json_data = rv.get_json()

    assert json_data['attempts_remaining'] == 4
    assert json_data['guessed_letters'] == ['a']
    assert json_data['score'] == 0
    assert json_data['word_state'] == '______'


def test_guess_letter_lose(client):
    """It should tell the user they have lost when there are no attempts remaining and decrement their score"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
        sess['attempts_remaining'] = 1
        sess['score'] = 50
    rv = client.get('/guess_letter/a')
    json_data = rv.get_json()

    assert json_data['attempts_remaining'] == 0
    assert json_data['guessed_letters'] == ['a']
    assert json_data['score'] == 30
    assert json_data['word_state'] == '______'
    assert json_data['message'] == "You didn't guess the word. The word was 3dhubs"


def test_guess_letter_win(client):
    """It should tell the user they have won and increment their score"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
        sess['attempts_remaining'] = 1
        sess['score'] = 50
        sess['guessed_letters'] = ['3', 'd', 'h', 'u', 'b']


    rv = client.get('/guess_letter/s')
    json_data = rv.get_json()

    assert json_data['attempts_remaining'] == 1
    assert json_data['guessed_letters'] == ['3','d','h','u','b','s']
    assert json_data['score'] == 55
    assert json_data['word_state'] == '3dhubs'
    assert json_data['message'] == "You win! You now have 55 points"


def test_guess_word_win(client):
    """It should tell the user they have won and increment their score"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
        sess['attempts_remaining'] = 1
        sess['score'] = 50
        sess['guessed_letters'] = ['3', 'd', 'h', 'u']
        sess['word_state'] = '3dhu__'

    rv = client.get('/guess_letter/3dhubs')
    json_data = rv.get_json()

    assert json_data['attempts_remaining'] == 1
    assert json_data['guessed_letters'] == ['3','d','h','u']
    assert json_data['score'] == 60
    assert json_data['word_state'] == '3dhu__'
    assert json_data['message'] == "The word is 3dhubs! You've won 10 points. Save score, Continue, or Restart?"


def test_save_high_score(client):
    """It should tell the user they have won and increment their score"""
    with client.session_transaction() as sess:
        set_test_sess(sess)
        sess['attempts_remaining'] = 1
        sess['score'] = 50
        sess['guessed_letters'] = ['3', 'd', 'h', 'u']
        sess['word_state'] = '3dhu__'
    rv = client.get('/save_high_score')
    json_data = rv.get_json()
    os.remove("./logs/high_scores")

    assert json_data == [['Andrew', 9001], ['bar', 50]]
    with client.session_transaction() as sess_after:
        assert not sess_after

