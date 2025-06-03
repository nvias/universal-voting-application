from flask import Flask, render_template, request, jsonify, make_response, redirect
import json
import random
import os
from datetime import datetime

app = Flask(__name__, template_folder="./site")

# Default route
@app.route('/')
def home():
    return "."


def generate_unique_id(existing_ids):
    while True:
        rand_id = str(random.randint(100000, 999999))
        if rand_id not in existing_ids:
            return rand_id

# creating a new voting session POST
#payload: {"name":"name","teams":[{"team 1":[{question "1":0}]}],"questions":["auestion 1"]}

@app.route('/create_voting', methods=['POST', "GET"]) 
def create_voting():
    try:
        data = request.get_json()

        if not data or 'teams' not in data or 'questions' not in data:
            return jsonify({'error': 'Invalid request format'}), 400

        # Load existing voting sessions
        if os.path.exists("./database/votes.json"):
            with open("./database/votes.json", 'r', encoding='utf-8') as f:
                db = json.load(f)
        else:
            db = {}

        # Create a new voting session with a unique ID
        unique_id = generate_unique_id(db.keys())
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db[unique_id] = {
            'unique_id': unique_id,
            'started': False,
            'name': data["name"],
            'teams': data['teams'],
            'questions': data['questions'],
            'created_at': created_at
        }

        # Save the new voting session
        with open("./database/votes.json", 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4, ensure_ascii=False)

        return jsonify({
            'message': 'Voting pool saved',
            'id': unique_id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# all voting sessions
@app.route('/get_votings', methods=['GET'])
def get_votings():
    if os.path.exists("./database/votes.json"):
        with open("./database/votes.json", 'r', encoding='utf-8') as f:
            db = json.load(f)
            return jsonify(db)

# voting session by ID
@app.route('/get_voting/<votingid>', methods=['GET'])
def get_voting(votingid):
    if os.path.exists("./database/votes.json"):
        with open("./database/votes.json", 'r', encoding='utf-8') as f:
            db = json.load(f)
            voting = db[votingid]
            return jsonify(voting)

# processes login form, saves in cookies
# form: name=nvias&pass=nvias jednoduzse predelas na json 
@app.route('/admin', methods=['POST', "GET"]) 
def process_login():
    data = request.form.to_dict(flat=False)
    print(data["name"][0])
    resp = make_response(render_template('admin.html'))
    resp.set_cookie('login', str(data["name"][0]), httponly=False)
    resp.set_cookie('password', str(data["pass"][0]), httponly=False)
    return resp

# Start voting
# no payload
@app.route('/start_voting/<voting_id>', methods=['POST'])
def start_voting(voting_id):
    if os.path.exists("./database/votes.json"):
        with open("./database/votes.json", 'r', encoding='utf-8') as f:
            db = json.load(f)
    votings = db

    if voting_id in votings:
        votings[voting_id]["started"] = True
        print(voting_id)

        with open("./database/votes.json", 'w') as file:
            json.dump(votings, file, indent=4)

        return jsonify({"message": f"Voting {voting_id} has started!"})
    else:
        return jsonify({"error": "Voting not found"}), 404

# admin login page
@app.route('/login')
def admin_login():
    return render_template('login.html')

# qr code page
@app.route('/presentation/<id>')
def projected_site(id):
    print("qr id")
    return render_template('qr.html')

# voting page for users
@app.route('/hlasovani/<voteid>')
def voting_site_menu(voteid):
    return render_template('voting.html')


if __name__ == '__main__':
    app.run(host="192.168.2.18")
