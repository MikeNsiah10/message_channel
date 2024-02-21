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
CHANNEL_NAME = "Sequence Guest Game"
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

#implement a guessing game
class GuessingGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        # Generate a 4 random sequence of numbers
        self.secret_sequence = ''.join(str(x) for x in random.sample(range(10), 4))
        self.num_attempts = 0
        self.game_over = False
        return "Game resetted! guess the random number generated(1,20)."

    def guess(self, guess):
        if self.game_over:
            return "Game over! Type new guess to start a new game."
        elif guess == self.number_to_guess:
            self.game_over = True
            return "Congratulations! You guessed correctly."
        elif guess < self.number_to_guess:
            return "Too low! Try again."
        else:
            return "Too high! Try again."
#create an instance of the class
game = GuessingGame()
       

# ELIZA-style Chatbot
def eliza_chatbot(message_content):
    """
    Simulate an ELIZA-style chatbot that responds to user messages.
    """
    # Basic responses based on patterns
    responses = {
      r'calculate (\d+) plus (\d+)':  [lambda x, y: str(int(x) + int(y))],
      r'calculate (\d+) minus (\d+)': [lambda x, y: str(int(x) - int(y))],
      r'calculate (\d+) times (\d+)': [lambda x, y: str(int(x) * int(y))],
      r'calculate (\d+) divided by (\d+)': [lambda x, y: str(int(x) / int(y)) if int(y) != 0 else "Cannot divide by zero!"], 
      r'game':["okay, try to guess the number generated(1,20),Let's go"],
      r'(\d+)': [lambda x: game.guess(int(x))],
      r'new guess': [lambda: game.reset_game()],
      r'how are you': ["I'm just a bot, but thanks for asking!", "I don't have feelings, but I'm here to help!"],
      r'your name|who are you': ["I'm just a chatbot! You can call me Ruby"],
      r'Hello|Hi|Hey|Good morning|Good afternoon': [
        "Hello! How can I help you today?",
        "Hi there! What brings you here?"],
      r'what can you do':["I can respond to text about Osnabrueck university and myself,tell jokes,do some basic maths and play a guess game"],
      r'maths': ["okay.let's start with the basics(add,substract,multiply,divide)"],
      r'Tell me something interesting': [
        "Did you know that Osnabrück is known, particularly for its role in the Peace of Westphalia treaty(1648)which ended 30years War in Europe?",
        "Osnabrück is home to the University of Osnabrück(1974) which contributes to the city's vibrant academic and cultural life",
        "The city is home to several museums and art galleries, example is The Felix-Nussbaum-Haus"],
   
      r'favorite color|favorite food|favorite movie|favorite book|favorite music': [
        "I don't have personal preferences, but I'm curious to know about your favorites but maybe next time"],
      r'how are you': ["I'm  a chatbot, but thanks for asking!", "I don't have feelings, but I'm here to help!"],
      r'Ruby': ["Hello, what can I do for you today"],
      r'bye|goodbye|see you': ["Goodbye!have a great day", "See you later,Take care!", "Bye!"],
      r'weather': ["I'm not a weather bot, but you can check a weather website for the latest updates."],
      r'jokes': ["Sure,Why was the math book sad?Because it had too many problems!",
      "okay,How does a penguin build its house?Igloos it together!"],
      r'time': ["I don't wear a watch, for me it's always chatbot o'clock!"],
      r'how old are you': ["I don't age; I'm timeless!"],
      r'information about the university': [
        "Our university, Osnabrück University, offers a wide range of academic programs and a vibrant campus life. How can I help you further?",
        "Osnabrück University is known for its diverse academic offerings and supportive community. What specific information are you looking for?"
      ],
      r'what courses are offered': [
        "We offer a variety of undergraduate and graduate programs in fields such as Cognitive Science, Economics, and more.(visit Universität Osnabrück website for more info)",
        "Our courses cover a wide range of disciplines including Environmental Sciences, Linguistics, and more.(visit Universität Osnabrück website for more info)"
      ],
      r' any specialized programs|any interdisciplinary programs': [
        "Yes, we offer several specialized and interdisciplinary programs, such as Cognitive Sciences among others.(visit Universität Osnabrück website for more info)",
        "We have a variety of interdisciplinary options, including joint programs and specialized courses that integrate multiple disciplines.(visit Universität Osnabrück website for more info)"
      ],
      r'mode of learning': [
        "Many of our courses are offered in a hybrid format, allowing students to attend classes in person or participate online.",
        "We understand the importance of flexibility, so we offer a variety of course delivery methods including hybrid, online, to accommodate different learning needs"
      ],
      r'duration of study' :["The duration of study is 6semesters for undergraduate and 4 semesters for masters"],
      r'thank you|thanks|thank you for the help': [
        "You're welcome! If you have any more questions, feel free to ask.",
        "No problem at all. Let me know if there's anything else I can assist you with."
      ],
      r'sports' :["The university has several sporting clubs of which you can join based on your interest"],
      r'support|guidance':["Support services available to students, include counseling services, career guidance, and disability support."],
      r'application deadline':["The deadline for Application can be found on the university website(visit Universität Osnabrück website for more info)"],
      r'financial aid|scholarship':["Yes,Students can apply for a wide range of financial and material support(visit Universität Osnabrück website for more info)"], 
      r'career opportunity':["The university shows different ways to find the right employer in Germany .(visit Universität Osnabrück website for more info)"],

    
 }

     
    # Check for pattern matches
    for pattern, responses_list in responses.items():
        match = re.search(pattern, message_content, re.IGNORECASE)
        if match:
            response = random.choice(responses_list)
             # if the response is a function
            if callable(response): 
                 # call the function with the matched groups as arguments
                return response(*match.groups()) 
            else:
                 # if the response is not a function, return it as is
                return response 

    # Default response if no match is found
    return "I'm not sure how to respond to that. Can you please elaborate or rephrase?"

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
