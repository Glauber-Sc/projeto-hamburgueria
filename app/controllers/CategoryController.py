from os import remove, path
from flask import Request, jsonify
from cerberus import Validator
from flask_jwt_extended import get_jwt_identity
from app.connections.database import User, Category
from pony import orm

class CategoryController:
    @orm.db_session
    def store(request: Request, filename: str):
        file_path = 'uploads/categories/' + filename
        schema = {
            'name': {'type': 'string', 'required': True}      
        }

        validator = Validator(schema)
        is_valid = validator.validate(request.form)
                
        if not is_valid:
            if path.exists(file_path): remove(file_path)
            return { "error": "Make sure you inputted the correct body" }, 400
                
        userId = get_jwt_identity()
        user = User.get(id=userId)   
        categoryName = request.form['name']     

        if not user.admin:
            if path.exists(file_path): remove(file_path)
            return { "error": "You are not authorized to perform this action" }, 401

        categoryExists = orm.select(c for c in Category if c.name == categoryName).first()
        if categoryExists:
            if path.exists(file_path): remove(file_path)
            return { "error": "Category already exists" }, 400
        
        category = Category(name=categoryName, path=filename);
        orm.commit();
        
        return {
            "id": category.id,
            "path": category.path
        }

    @orm.db_session
    def index(request: Request):
        categoriesFound = orm.select(c for c in Category)[:]
        categories = [t.to_dict() for t in categoriesFound]         

        return jsonify(categories)
