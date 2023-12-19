from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=["GET", "POST"])
def messages():
    if request.method == "GET":
        messages = Message.query.order_by(Message.created_at.asc()).all()
        messages_dict = [message.to_dict() for message in messages]
        return make_response(messages_dict, 200)
    elif request.method == "POST":
        #get_json() - convert the json to a list/dict
        json_data = request.get_json()
        new_message = Message(
            username=json_data["username"],
            body=json_data["body"],
        )
        db.session.add(new_message)
        db.session.commit()
        return make_response(new_message.to_dict(), 201)

@app.route('/messages/<int:id>', methods=["GET","PATCH", "DELETE"])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if message == None:
        body = {"message": "Message id not found. Please try again"}
        return make_response(body, 404)
    else:
        if request.method == "GET":
            return make_response(message.to_dict(), 200)
        elif request.method == "PATCH":
            json_data = request.get_json()
            for attr in json_data:
                setattr(message, attr, json_data.get(attr))
            db.session.add(message)
            db.session.commit()
            return make_response(message.to_dict(), 200)
        elif request.method == "DELETE":
            db.session.delete(message)
            db.session.commit()
            body = {
                "delete_successful": True,
                "message": "Message deleted"
            }
            return make_response(body, 200)


if __name__ == '__main__':
    app.run(port=5555)
