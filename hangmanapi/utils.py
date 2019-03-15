# Creates the word state of a word based on the letters that have been guessed
def create_word_state(word_to_guess, guessed_letters):
    word_state = list('_' * len(word_to_guess))
    for idx, letter in enumerate(word_to_guess):
        if letter in guessed_letters:
            word_state[idx] = letter
    return ''.join(word_state)


# Creates the json to be returned to the client
def create_json_return(session, message):

    return {'attempts_remaining': session['attempts_remaining'],
            'guessed_letters': list(session['guessed_letters']),
            'message': message,
            'score': session['score'],
            'user_id': session['user_id'],
            'word_state': session['word_state']
            }


# Gets points won based on attempts and if it's a guess
def get_points_won(attempts, word_state=''):
    if attempts == 0:
        return -20

    points = attempts *5
    multiplier = max(word_state.count('_'), 1)

    return points * multiplier


# Update points based on attempts
def update_points(session, points_to_add):
    session['score'] += points_to_add
    if session['score'] < 0:
        session['score'] = 0
