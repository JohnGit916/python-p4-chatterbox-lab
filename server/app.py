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

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    
    if request.method == 'GET':
        messages = Message.query.all()
        if len(messages)> 0:
            res = make_response(
                sorted([message.to_dict() for message in messages], key=lambda x:x['created_at']),
                200
            )
            return res
        
    elif request.method == 'POST':
        data = request.get_json()
        newMessage = Message(
            username=data.get('username'),
            body=data.get('body')
        )
        
        db.session.add(newMessage)
        db.session.commit()

        res = make_response(newMessage.to_dict(), 201)

        return res
    
    return make_response({'Error': 'Messages not found'}, 404)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if request.method == 'PATCH':
        data = request.get_json()
        
        if message:
            for attr in data:
                setattr(message, attr, data.get(attr))

            db.session.add(message)
            db.session.commit()

            return message.to_dict(), 201
        else:
            return {'Error': 'Message not Found'}, 404
        
    elif request.method == 'DELETE':

        if message:
            db.session.delete(message)
            db.session.commit()

            return '', 204
        else:
            return {'Error': 'Message not Found'}, 404


if __name__ == '__main__':
    app.run(port=5555)