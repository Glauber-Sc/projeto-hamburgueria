from os import remove, path
from flask import Request, jsonify
from cerberus import Validator
from flask_jwt_extended import get_jwt_identity
from app.connections.database import User, Product, Category
from pony import orm

class ProductController:
    @orm.db_session
    def store(request: Request, filename: str):
        file_path = 'uploads/products/' + filename
        form = request.form
               
        schema = {
            'name': {'type': 'string', 'required': True},
            'price': {'type': 'string', 'required': True},
            'category_id': {'type': 'string', 'required': True},
            'offer': {'type': 'string', 'required': True},            
        }
        validator = Validator(schema)
        is_valid = validator.validate(form)
                
        if not is_valid:
            if path.exists(file_path): remove(file_path)
            return { "error": "Make sure you inputted the correct body" }, 400
                
        userId = get_jwt_identity()
        user = User.get(id=userId)
        
        if not user.admin:
            if path.exists(file_path): remove(file_path)
            return { "error": "You are not allowed to do this" }, 401
        
        category = Category.get(id=form['category_id']);        
 
        product_name, product_price, product_offer = form['name'], form['price'], form['offer']

        product = Product(
            name=product_name,
            price=product_price,
            path=filename,
            offer=product_offer
        )
        product.category = category

        orm.commit();

        return jsonify(product.to_dict()), 201
    
    @orm.db_session
    def index(request: Request):
        productsFound = orm.select(p for p in Product)[:]
        products = [t.to_dict() for t in productsFound]         

        return jsonify(products)