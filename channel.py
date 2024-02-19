## channel.py - a simple message channel
##

from flask import Flask, request, render_template, jsonify
import json
import requests
import random
import re
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
CHANNEL_NAME = "MultiBot Hub"
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
@app.route('/', methods=['GET'])
def home_page():
    if not check_authorization(request):
        return "Invalid authorization", 400
    # fetch channels from server
    return jsonify(read_messages())


def read_messages():
    global CHANNEL_FILE
    try:
        f = open(CHANNEL_FILE, 'r')
    except FileNotFoundError:
        return []
    try:
        messages = json.load(f)
    except json.decoder.JSONDecodeError:
        messages = []
    f.close()
    return messages

def save_messages(messages):
    global CHANNEL_FILE
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f)



# Number Sequence Guessing Game
class NumberSequenceGame:
    def __init__(self):
        self.reset_game()
        

    def reset_game(self):
        # Generate a 4 random sequence of numbers
        self.secret_sequence = ''.join(str(x) for x in random.sample(range(10), 4))
        self.num_attempts = 0
        self.game_over = False
        return "Game resetted,please guess the 4 digit sequence(0-9)"

    def check_guess(self, guess):
        if self.game_over:
            return  "Game over! Please type 'reset'  to play again."

        self.num_attempts += 1

         # Check if the guess matches the secret sequence
        if guess == self.secret_sequence:
            self.game_over = True
            return  f"Congratulations! You guessed the correct sequence {guess} in {self.num_attempts} attempts.Type 'reset' to play again"
        
        
        # Check if the guess is a digit or a four-digit number
        elif len(guess) != 4:
            return  "Invalid guess. Please enter a four-digit sequence."

        else:
            # Find which digits are in the correct position
            correct_positions = [i for i in range(4) if guess[i] == self.secret_sequence[i]]
            feedback = ['*' if i not in correct_positions else guess[i] for i in range(4)]
            return  f"Guess: {' '.join(feedback)}. You have {len(correct_positions)} digit(s) in the correct position."

sequence_game = NumberSequenceGame()

# ELIZA-style Chatbot
def eliza_chatbot(message_content):
    """
    Simulate an ELIZA-style chatbot that responds to user messages.
    """
    # Check if the message matches the "sequence" pattern
    sequence_pattern = re.match(r'(\d+)', message_content, re.IGNORECASE)
    if sequence_pattern:
        return sequence_game.check_guess(sequence_pattern.group(1))

    # Check if the message matches any of the "calculate" patterns
    calculate_patterns = [
        (r'calculate (-?\d+) plus (-?\d+)', lambda x, y: int(x) + int(y)),
        (r'calculate (-?\d+) minus (-?\d+)', lambda x, y: int(x) - int(y)),
        (r'calculate (-?\d+) times (-?\d+)', lambda x, y: int(x) * int(y)),
        (r'calculate (-?\d+) divided by (-?\d+)', lambda x, y: (int(x) / int(y)) if int(y) != 0 else "Cannot divide by zero!")
    ]
    for pattern, operation in calculate_patterns:
        match = re.match(pattern, message_content, re.IGNORECASE)
        if match:
            return operation(match.group(1), match.group(2))
    # Basic responses based on patterns
    responses = {

      r'maths|mathematics': ["Sure.let's start with the basics,use keyword:calculate (int) plus|minus|times|divided by (int)"],  
      r'game':["Sure! Let's play the Number Sequence Game. Guess a 4-digit sequence of numbers(0-9)."],
      r'reset':[lambda:sequence_game.reset_game()],
      #general bot responses
      r'your name|who are you': ["I'm just a chatbot! You can call me Ruby"],
      r'Hello|Hi|Hey|Good morning|Good afternoon': ["Hello! How can I help you today?","Hi there! What brings you here?"],
      r'what can you do':["I can respond to text about Osnabrueck university and myself,tell jokes,do some basic maths and play a guess game"],
      r'favorite color|favorite food|favorite movie|favorite book|favorite music': [
        "I don't have personal preferences, but I'm curious to know about your favorites but maybe next time"],
      r'how are you': ["I'm  a chatbot, but thanks for asking!", "I don't have feelings, but I'm here to help!"],
      r'Ruby': ["Hello, what can I do for you today"],
      r'bye|goodbye|see you': ["Goodbye!have a great day", "See you later,Take care!", "Bye!"],
      r'weather': ["I'm not a weather bot, but you can check a weather website for the latest updates."],
      r'jokes': ["Sure,Why was the math book sad?Because it had too many problems!",
      "okay,How does a penguin build its house?Igloos it together!",
      " Ofcourse, What do you call a bear with no teeth? A gummy bear!",
      "Willingly,What do you call fake spaghetti? An impasta!",
      "with pleasure,Why did the golfer bring two pairs of pants? In case he got a hole in one!"],
      r'time': ["I don't wear a watch, for me it's always chatbot o'clock!"],
      r'how old are you': ["I don't age; I'm timeless!"],
      #osnabrueck university responses
      r'information|describe|say about|talk about': [
        "Our university, Osnabrück University, offers a wide range of academic programs and a vibrant campus life. How can I help you further?",
        "Osnabrück University is known for its diverse academic offerings and supportive community. What specific information are you looking for?"
      ],
      r'courses|discipline': [
        "We offer a variety of undergraduate and graduate programs|courses in fields such as Cognitive Science, Economics, and more.(visit Universität Osnabrück website for more info)",
        "Our courses cover a wide range of disciplines including Environmental Sciences, Linguistics, and more.(visit Universität Osnabrück website for more info)"
      ],
      r'specialized programs|interdisciplinary programs': [
        "Yes, we offer several specialized and interdisciplinary programs, such as Cognitive Sciences among others.(visit Universität Osnabrück website for more info)",
        "We have a variety of interdisciplinary options, including joint programs and specialized courses that integrate multiple disciplines.(visit Universität Osnabrück website for more info)"
      ],
      r'learning': [
        "Many of our courses are offered in a hybrid format, allowing students to attend classes in person or participate online.",
        "We understand the importance of flexibility, so we offer a variety of course delivery methods including hybrid, online, to accommodate different learning needs"
      ],
      r'duration|long' :["The duration of study is 6semesters for undergraduate and 4 semesters for masters"],
      r'thank you|thanks': [
        "You're welcome! If you have any more questions, feel free to ask.",
        "No problem at all. Let me know if there's anything else I can assist you with."
      ],
      r'sports' :["The university has several sporting clubs of which you can join based on your interest"],
      r'support|guidance':["Support services available to students, include counseling services, career guidance, and disability support."],
      r'deadline':["The deadline for Application can be found on the university website(visit Universität Osnabrück website for more info)"],
      r'financial aid|grants':["Yes,Students can apply for a wide range of financial and material support(visit Universität Osnabrück website for more info)"], 
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
    return """Unable to give response,if  game,enter an integer,
    if calculation,follow instructions for 'maths|mathematics'pattern,
    if text enter valid text(check syntax) to be matched,thanks"""


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

    # add user message to messages
    user_message = {'content': message['content'], 'sender': message['sender'], 'timestamp': message['timestamp']}
    messages = read_messages()
    messages.append(user_message)

    # generate chatbot response
    chatbot_response = {
        "content": eliza_chatbot(message['content']),
        "sender": "chatbot",
        "timestamp":datetime.datetime.now().isoformat()
    }
    messages.append(chatbot_response)

    # save messages
    save_messages(messages)

    return jsonify({"user_message": user_message, "bot_response": chatbot_response}), 200



# Start development web server
if __name__ == '__main__':
    app.run(port=5001, debug=True)
