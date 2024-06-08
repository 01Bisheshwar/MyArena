from flask import Flask, request, jsonify
from flask_cors import CORS 
import pymongo 
  
# Replace your URL here. Don't forget to replace the password. 
connection_url = 'mongodb+srv://Players:9f0ZRG7msSjmeLOb@bisheshwargames.ur3vhyp.mongodb.net/?retryWrites=true&w=majority&appName=BisheshwarGames'
app = Flask(__name__) 
client = pymongo.MongoClient(connection_url) 

# Specify the database you are using
db = client.get_database('MyArena')  # Replace 'your_database_name' with the actual name of your database

@app.route('/check_user', methods=['POST'])
def check_user():
    data = request.get_json()
    username = data.get('username')
    if username:
        user = db.leaderboard.find_one({"username": username})
        if user:
            return jsonify({"exists": True}), 200
        else:
            return jsonify({"exists": False}), 200
    return jsonify({"error": "Missing username"}), 400

@app.route('/insert_user', methods=['POST'])
def insert_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    highscore = data.get('highscore', 0)  # Default highscore to 0 if not provided
    if username and password:
        # Check if the username already exists
        if db.leaderboard.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 400
        else:
            # Insert the username and password into the MongoDB database
            db.leaderboard.insert_one({"username": username, "password": password, "highscore": highscore})
            return jsonify({"success": True}), 201
    return jsonify({"error": "Missing username or password"}), 400

@app.route('/check_credentials', methods=['POST'])
def check_credentials():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username and password:
        user = db.leaderboard.find_one({"username": username, "password": password})
        if user:
            return jsonify({"valid": True}), 200
        else:
            return jsonify({"valid": False}), 200
    return jsonify({"error": "Missing username or password"}), 400

@app.route('/check_highscore', methods=['POST'])
def check_highscore():
    data = request.get_json()
    username = data.get('username')
    if username:
        user = db.leaderboard.find_one({"username": username})
        if user:
            highscore = user.get('highscore', 0)
            return jsonify({"highscore": highscore}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    return jsonify({"error": "Missing username"}), 400

@app.route('/update_highscore', methods=['POST'])
def update_highscore():
    data = request.get_json()
    username = data.get('username')
    new_score = data.get('score')
    if username and new_score is not None:
        user = db.leaderboard.find_one({"username": username})
        if user:
            current_highscore = user.get('highscore', 0)
            if new_score > current_highscore:
                db.leaderboard.update_one({"username": username}, {"$set": {"highscore": new_score}})
                return jsonify({"updated": True}), 200
            else:
                return jsonify({"updated": False, "message": "New score is not higher than current highscore"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    return jsonify({"error": "Missing username or score"}), 400

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    # Retrieve all users and their highscores
    users = list(db.leaderboard.find({}, {"_id": 0, "username": 1, "highscore": 1}))
    
    # Sort users by highscore in descending order
    sorted_users = sorted(users, key=lambda x: x['highscore'], reverse=True)
    
    return jsonify({"leaderboard": sorted_users}), 200
    
if __name__ == '__main__':
    app.run(debug=True)
