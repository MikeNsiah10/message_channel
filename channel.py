## channel.py - a simple message channel
##

from flask import Flask, request, jsonify
import json
import requests
import random
import datetime

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db

HUB_URL = 'https://temporary-server.de'
HUB_AUTHKEY = 'Crr-K3d-2N'
CHANNEL_AUTHKEY = '0987654321'
CHANNEL_NAME = "Sequence Guess Game"
CHANNEL_ENDPOINT = "http://vm954.rz.uni-osnabrueck.de/user123/channel_954.wsgi" # don't forget to adjust in the bottom of the file
CHANNEL_FILE = 'messages.json'


@app.cli.command('register')
def register_command():
    global CHANNEL_AUTHKEY, CHANNEL_NAME, CHANNEL_ENDPOINT

    print(f"Registering channel with name: {CHANNEL_NAME}, endpoint: {CHANNEL_ENDPOINT}, authkey: {CHANNEL_AUTHKEY}")

    # send a POST request to server /channels
    response = requests.post(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
                             data=json.dumps({
            "name": CHANNEL_NAME,
            "endpoint": CHANNEL_ENDPOINT,
            "authkey": CHANNEL_AUTHKEY}))
    if response.status_code != 200:
        print(f"Error creating channel: {response.status_code}, {response.text}")
        return



def check_authorization(request):
    global CHANNEL_AUTHKEY
    # check if Authorization header is present
    if 'Authorization' not in request.headers:
        return False
    # check if authorization header is valid
    if request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
        return False
    return True



@app.route('/health', methods=['GET'])
def health_check():
    global CHANNEL_NAME
    if not check_authorization(request):
        return "Invalid authorization", 400
    return jsonify({'name':CHANNEL_NAME}),  200

# GET: Return list of messages

# GET: Return list of messages
@app.route('/', methods=['GET'])
def home_page():
    if not check_authorization(request):
        return "Invalid authorization", 400
    # fetch channels from server
    return jsonify(read_messages())


def read_messages():
    global CHANNEL_FILE
    try:
        with open(CHANNEL_FILE, 'r') as f:
            try:
                messages = json.load(f)
            except json.decoder.JSONDecodeError:
                messages = []
    except FileNotFoundError:
        messages = []

    # Add the welcome message at the beginning 
    if not messages:
        welcome_message = {
            "content": "Welcome to the Number Sequence Guessing Game!\n\n"
                       "To play, simply guess the 4-digit sequence (0-9).\n"
                       "Type 'replay' to start a new game.\n\n"
                       "You have only 10 attempts,Enjoy the game!",
            "sender": "Mikkybot",
            "timestamp": datetime.datetime.now().isoformat()
        }
        messages.append(welcome_message)

    return messages



def save_messages(messages):
    global CHANNEL_FILE
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f)


#class SequenceGame
class NumberSequenceGame:
    def __init__(self):
        self.reset_game()
    #restart game   
    def reset_game(self):
        # Generate a 4 random sequence of numbers
        self.secret_sequence = ''.join(str(x) for x in random.sample(range(10), 4))
        self.num_attempts = 0
        self.game_over = False
        return """Welcome to the Number Sequence Guessing Game!\n\n"
                       To play, simply guess the 4-digit sequence (0-9).\n"
                        type 'replay' to start a new game.
                        you have only 10 attempts! Enjoy the game"""


    def check_guess(self, guess):
      if self.game_over:
         return "Game over! Please type 'replay' to play again."

      if not guess.isdigit() or len(guess) != 4:
         return "Invalid guess. Please enter a four-digit sequence."

      self.num_attempts += 1
    # Allow only 10 attempts
      if self.num_attempts > 10:
          self.game_over = True
          return f"Game over! You've exceeded the max number of attempts. Correct sequence was {self.secret_sequence}. Type 'replay' to play again."

    # Check if the guess matches the secret sequence
      if guess == self.secret_sequence:
         self.game_over = True
         return f"Congratulations! You guessed the correct sequence {guess} in {self.num_attempts} attempts. Type 'replay' to play again."
    
    # Feedback of digits in the correct position
      correct_positions = [i for i in range(4) if guess[i] == self.secret_sequence[i]]
      feedback = ['*' if i not in correct_positions else guess[i] for i in range(4)]
      return f"Guess: {' '.join(feedback)}. You have {len(correct_positions)} digit(s) in the correct position. Attempts remaining: {10 - self.num_attempts}"


#instantiate the NumberSequenceGame
sequence_game = NumberSequenceGame()


# POST: Send a message and receive bot response
@app.route('/', methods=['POST'])
def send_message():
    # fetch channels from server
    # check authorization header
    if not check_authorization(request):
        return "Invalid authorization", 400

    # check if message is present
    message = request.json
    if not message:
        return "No message", 400
    if not 'content' in message:
        return "No content", 400
    if not 'sender' in message:
        return "No sender", 400
    if not 'timestamp' in message:
        return "No timestamp", 400

    global sequence_game
    #check if content is replay and start the game
    if message['content'] == 'replay':
        response = sequence_game.reset_game()
        messages = read_messages()
        bot_message = {'content': response, 'sender': 'Mikkybot', 'timestamp': datetime.datetime.now().isoformat()}
        messages.append(bot_message)
        save_messages(messages)
        return jsonify({"bot_response": bot_message}), 200

    # add user message to messages
    user_message = {'content': message['content'], 'sender': message['sender'], 'timestamp': message['timestamp']}
    messages = read_messages()
    messages.append(user_message)

    # generate bot response
    bot_response = sequence_game.check_guess(message['content'])
    bot_message = {'content': bot_response, 'sender': 'Mikkybot', 'timestamp': datetime.datetime.now().isoformat()}
    messages.append(bot_message)

    # save messages
    save_messages(messages)

    return jsonify({"user_message": user_message, "bot_response": bot_message}), 200




# Start development web server
if __name__ == '__main__':
    app.run(port=5001, debug=True)
