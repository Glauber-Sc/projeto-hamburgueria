import bcrypt
from cerberus import Validator
from pony import orm
from flask import Request
from app.connections.database import User

class UserController:
    
    @orm.db_session
    def store(request: Request):
        schema = {
            'name': { 'type': 'string', 'required': True },
            'email': { 'type': 'string', 'required': True },
            'password': { 'type': 'string', 'required': True, 'valuesrules': { 'min': 6 } }
        }
        validator = Validator(schema)
        is_valid = validator.validate(request.json)
        
        if not is_valid:
            return { "error": "Missing body fields in request" }, 400

        userData = request.json

        userExists = User.get(email=userData['email'])
        if (userExists):
            return { "error": "User already exists" }, 409
        
        pw_bytes = userData['password'].encode('utf-8')
        print(pw_bytes)
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(pw_bytes, salt)
        hashed_password = str(hash)[2:-1]

        user = User(
            name=userData['name'],
            email=userData['email'],
            password_hash=hashed_password,
            admin=False          
        )
        orm.commit()

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "admin": user.admin
        }, 201
