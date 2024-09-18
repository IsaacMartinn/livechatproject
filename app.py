from flask import Flask, request, jsonify, render_template,url_for,redirect,request
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
from controllers.calculations import attackValue, getRoboName, toAdd
from mistralai import Mistral
import requests
import random
import os


leetcode_questions = [{
    'title': 'Two Sum',
    'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
    'example': 'Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]',
    'output': 'Output explanation: Because nums[0] + nums[1] == 9, we return [0, 1].',
    'constraints': '2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9\nOnly one valid answer exists.',
    'difficulty': 'Easy'
}, {
    'title': 'Add Two Numbers',
    'description': 'You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.',
    'example': 'Input: l1 = [2,4,3], l2 = [5,6,4]\nOutput: [7,0,8]\nExplanation: 342 + 465 = 807.',
    'output': '[7,0,8]',
    'constraints': '1. The number of nodes in each linked list is in the range [1, 100].\n2. 0 <= Node.val <= 9\n3. It is guaranteed that the list represents a number that does not have leading zeros.',
    'difficulty': 'Medium'
}, {
    'title': 'Longest Substring Without Repeating Characters',
    'description': 'Given a string s, find the length of the longest substring without repeating characters.',
    'example': 'Input: s = "abcabcbb"\nOutput: 3',
    'output': 'Explanation: The answer is "abc", with the length of 3.',
    'constraints': '0 <= s.length <= 5 * 10^4\ns consists of English letters, digits, symbols, and spaces.',
    'difficulty': 'Medium'
}, {
    'title': 'Longest Palindromic Substring',
    'description': 'Given a string s, return the longest palindromic substring in s.',
    'example': 'Input: s = "babad"<br>Output: "bab"',
    'output': 'Output explanation: "aba" is also a valid answer.',
    'constraints': '1 <= s.length <= 1000<br>s consists of only digits and English letters.',
    'difficulty': 'Medium'
}]

random_int = random.randint(0,3)
question = leetcode_questions[random_int]

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route("/")
def home():
    try:
        submitted_question = False
        name = request.args.get("name")
        response = requests.get(url=f"https://alfa-leetcode-api.onrender.com/{name}")
        response.raise_for_status()

        data = response.json()
        picture = data['avatar']
        if request.method =='POST':
            submitted_question = True

            return render_template("index.html",question =question,num=random_int,profile_pic = picture,submitted_question=submitted_question )
        else:
            return render_template("index.html",question =question,num=random_int,profile_pic = picture,submitted_question=submitted_question)

    except Exception as e:
        print(str(e))
        return render_template("index.html",question =question,num=random_int,profile_pic = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png")


@app.route("/gettheScores", methods=['GET',"POST"])
def getScores():
    try:
        print("Scores begun")
        data = request.get_json("name")
        name = data["name"]
        # response = requests.get(url=f"https://alfa-leetcode-api.onrender.com/userProfile/{name}")
        response = requests.post(url="https://leetcode.com/graphql?submitStats=submitStatsGlobal", json={
            "query":'{ matchedUser(username: \"' + name + '\") { username profile { realName aboutMe userAvatar ranking starRating globalRanking reputation } submitStats: submitStatsGlobal { acSubmissionNum { difficulty count submissions } totalSubmissionNum { difficulty count submissions } } badges { name displayName icon } contributions { points questionCount testcaseCount } languageProblemCount { languageName problemsSolved } } }'
        })
        response.raise_for_status()
        data = response.json()
        count = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"][0]["count"]
        total_submission = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"][0]["submissions"]
        ranking = data['data']["matchedUser"]["profile"]["ranking"]
        print("Scores found")
        data = toAdd(count, total_submission, ranking)
        print(data)
        return jsonify({
            "data": data
        })

    except Exception as e:
        print(str(e))
        data = {
            "perc": 0,
            "solved": 0,
            "ranking": 0,
            "exc": str(e)
        }
        return jsonify({
            "data": data
        })  

@app.route("/backtolobby",methods=["POST"])
def recieve_data():
    ANSWER = request.form['answer']

    api_key = os.environ.get("MISTRAL_API")
    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)

    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"First tell me if i got the answer right with a yes or no then given the leetcode question titled,{question['title']}, and the question {question['description']} is this the right answer for the question? Answer: {ANSWER}. GIVE ME THE RIGHT ANSWER"
            },
        ]
    )
    response_text = chat_response.choices[0].message.content

    formatted_text = response_text.replace("\n", "   ")
    name = request.args.get("name")
    response = requests.get(url=f"https://alfa-leetcode-api.onrender.com/{name}")
    response.raise_for_status()
    data = response.json()
    picture = data['avatar']
    submitted_question = True
    answer_yes_or_no = formatted_text.split()[0]

    return render_template("index.html",
                           question =question,
                           num=random_int,
                           profile_pic = picture,
                           submitted_question=submitted_question,
                           answer=formatted_text,
                           answer_yes_or_no=answer_yes_or_no
                           )




    # return f"""
    # <h1>Answer</h1>
    # <p>{formatted_text}</p>
    # <a href="http://localhost:5173/boost">GET BOOST</a>
    # """







player1 = None
player2 = None

@socketio.on('connect')
def handle_connect():
    global player1, player2
    print(f'User Connected: {request.sid}')
    
    if player1 is None:
        player1 = request.sid
        print("P1")
        emit("YouAreOne", {"message": "You are player1"}, to=player1)
    
    elif player2 is None:
        player2 = request.sid
        print("P2")

def sendToGame():
    emit('sendTogame', {'message': 'Both are connected'}, broadcast=True)

@socketio.on("doTurn")
def handleTurn(data):
    if data["socketId"] == player2:
        newTurn = player1
    else:
        newTurn = player2

    if("data" in data):
        damage = attackValue(data["data"], data["scoreInfo"])
        return emit ("yourTurn", {"message": "Your turn", "damage": damage, "opp": data["myHealth"], "genData": data["me"]}, to=newTurn)
    
    print(f"Turn {newTurn}")
    emit("yourTurn", {"message": "your turn", "damage": 0, "opp": data["myHealth"], "genData": data["me"]["data"]["info"]}, to=newTurn)
    

@socketio.on("disconnect")
def disconnect():
    print("disconnedted")
    global player1, player2
    player1 = None
    player2 = None

@socketio.on("gameOver")
def gameOver(data):
    global player1, player2
    loser = data["id"]
    if(loser == player1):
        winner = "Player 2 WINS"
    else:
        winner = "Player 1 WINS"
    emit("winner", {'data': winner})

@socketio.on("sendOppInfo")
def sendOppInfo(data):
    global player1, player2
    if(player2 == None):
        return

    toreturn = data["info"]

    emit("getOpp", {"data": toreturn}, to=player1)
    sendToGame()

@app.route('/namebot', methods=['POST'])
def status():
    name = request.get_json()["name"]
    roboname = getRoboName(name)
    return jsonify({"success": True, "name": roboname}), 200

socketio.run(app, debug=True, port=8000, host='0.0.0.0')