from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/MyArena"  # Use the correct database name
mongo = PyMongo(app)

@app.route('/check_user', methods=['POST'])
def check_user():
    data = request.get_json()
    username = data.get('username')
    if username:
        user = mongo.db.leaderboard.find_one({"username": username})
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
    highscore = data.get('highscore')
    if username and password:
        # Check if the username already exists
        if mongo.db.leaderboard.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 400
        else:
            # Insert the username and password into the MongoDB database
            mongo.db.leaderboard.insert_one({"username": username, "password": password, "highscore":highscore})
            return jsonify({"success": True}), 201
    return jsonify({"error": "Missing username or password"}), 400

@app.route('/check_credentials', methods=['POST'])
def check_credentials():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username and password:
        user = mongo.db.leaderboard.find_one({"username": username, "password": password})
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
        user = mongo.db.leaderboard.find_one({"username": username})
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
        user = mongo.db.leaderboard.find_one({"username": username})
        if user:
            current_highscore = user.get('highscore', 0)
            if new_score > current_highscore:
                mongo.db.leaderboard.update_one({"username": username}, {"$set": {"highscore": new_score}})
                return jsonify({"updated": True}), 200
            else:
                return jsonify({"updated": False, "message": "New score is not higher than current highscore"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    return jsonify({"error": "Missing username or score"}), 400

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    # Retrieve all users and their highscores
    users = list(mongo.db.leaderboard.find({}, {"_id": 0, "username": 1, "highscore": 1}))
    
    # Sort users by highscore in descending order
    sorted_users = sorted(users, key=lambda x: x['highscore'], reverse=True)
    
    return jsonify({"leaderboard": sorted_users}), 200
    
if __name__ == '__main__':
    app.run(debug=True)
