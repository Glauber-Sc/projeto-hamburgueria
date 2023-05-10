import bcrypt
import jwt
import datetime
from cerberus import Validator
from pony import orm
from app.connections.database import User
from flask import Request

class SessionController:
    @orm.db_session
    def store(request: Request):        
        schema = {
            'email': {'type': 'string', 'required': True},
            'password': {'type': 'string', 'required': True},
        }
        validator = Validator(schema)
        is_valid = validator.validate(request.json)
                
        if not is_valid:
            return { "error": "Make sure your password or email are correct" }, 401
        
        email = request.json['email']
        password = request.json['password']
        
        user = User.get(email=email)
        if not user:
            return { "error": "Make sure your password or email are correct" }, 401
        
        user_pw_bytes = user.password_hash.encode('utf-8')
        req_pw_bytes = password.encode('utf-8')
        
        check = bcrypt.checkpw(password=req_pw_bytes, hashed_password=user_pw_bytes)
        if not check:
            return { "error": "Make sure your password or email are correct" }, 401

        token_payload = { "id": user.id, "name": user.name }
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        secret = "1234"

        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "admin": user.admin,
            "token": jwt.encode({
                "exp": expires,
                "payload": token_payload,
                "sub": user.id
            }, key=secret, algorithm="HS256")
        }, 200