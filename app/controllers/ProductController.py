from flask import Request
from cerberus import Validator
from flask_jwt_extended import get_jwt_identity
from app.connections.database import User

class ProductController:
    def store(request: Request, filename: str):
        form = request.form
               
        schema = {
            'name': {'type': 'string', 'required': True},
            'price': {'type': 'number', 'required': True},
            'category_id': {'type': 'number', 'required': True},
            'offer': {'type': 'boolean', 'required': True},            
        }
        validator = Validator(schema)
        is_valid = validator.validate(request.form)
                
        if not is_valid:
            return { "error": "Make sure you inputted the correct body" }, 400
        
        return { "message": "ok" }
        # userId = get_jwt_identity()
        # user = User.get(id=userId)
        # print(user)
        
        return { "message": "Okay" }