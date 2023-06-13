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
        
        category = Category(name=categoryName, path=filename)
        orm.commit()
        
        return {
            "id": category.id,
            "path": category.path
        }

    @orm.db_session
    def index(request: Request):
        categoriesFound = orm.select(c for c in Category)[:]
        categories = list()

        for category in categoriesFound:
            category_dict = category.to_dict()
            category_dict['url'] = f'http://10.0.9.5:3000/category-images/{category_dict["path"]}'
            categories.append(category_dict)

        return jsonify(categories)

    @orm.db_session
    def update(request: Request, category_id: int, filename: str):
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

        category = orm.select(c for c in Category if c.id == category_id).first()
        old_file_path = 'uploads/categories/' + category.path
        category_name = request.form['name']     

        if not category:
            return { "error": "Make sure your category id is correct" }, 401

        if not user.admin:
            if path.exists(file_path): remove(file_path)
            return { "error": "You are not authorized to perform this action" }, 401

        category.name = category_name
        category.path = filename
        orm.commit()

        if path.exists(old_file_path): remove(old_file_path)

        return {}, 200

    @orm.db_session
    def delete(request: Request, category_id: int):
        category = orm.select(c for c in Category if c.id == category_id).first()

        if not category:
            return {"error": "Make sure your category id is correct"}, 401

        userId = get_jwt_identity()
        user = User.get(id=userId)

        if not user.admin:
            return {"error": "You are not authorized to perform this action"}, 401

        file_path = 'uploads/categories/' + category.path

        if path.exists(file_path):
            remove(file_path)

        category.delete()
        orm.commit()

        return {}, 200