# hangman
small hangman game

Currently contains the backend API of a hangman game, built on the Flask framework.

#Startup:
Ensure you have an environment with python 3.6
Preferably run this in a conda environment.

configure `hangmanapi/config.yml` to point to where you want your logs to be

To run the code locally, ensure you install the requirements by running the following commande in tne root folder

`make prepare`

Optionally you can run the tests with

`make test`

to run the backend usethe use

`make api-up`


#Playing the game

Currently there is only an API to run the game. 
It is functional and to check if it is up, use a browser and go to:

`localhost:5000/health_check`

The endpoints available are:
 - `localhost:5000/health_check` : See if the API is up
 - `localhost:5000/start_session/<user_id>` : start a session of games, linked to a user_id
 - `localhost:5000/check_session` : check if you've started a session
 - `localhost:5000/start_new_game` : Starts a new game
 - `localhost:5000/guess_letter/<string>` : Guess if a letter is in the word. You can also use this to guess the entire word
 - `localhost:5000/save_high_score` : Saves the score you've accumulated in a session, then resets your session, and returns the high score list
 
The flow the frontend should follow is:
 - start a session
 - start a game
 - guess letters until you get the whole word
 - start another game
 - once you're happy with your score: save_high_score
 
#Further steps:
Build a front end that doesn't rely on the user entering their commands and guesses in the address bar

dockerize both the back end and front end. Use docker compose to automatically let them communicate with each other

Add extend function to get words from a db.  
 
      


