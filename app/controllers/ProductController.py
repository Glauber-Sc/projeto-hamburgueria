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
            'description': {'type': 'string', 'required': True},
        }
        validator = Validator(schema)
        is_valid = validator.validate(form)

        if not is_valid:
            if path.exists(file_path):
                remove(file_path)
            return {"error": "Make sure you inputted the correct body"}, 400

        userId = get_jwt_identity()
        user = User.get(id=userId)

        if not user.admin:
            if path.exists(file_path):
                remove(file_path)
            return {"error": "You are not allowed to do this"}, 401

        category = Category.get(id=form['category_id'])

        product_name, product_price, product_description = form['name'], form['price'], form['description']

        product = Product(
            name=product_name,
            price=product_price,
            path=filename,
            description=product_description

        )
        product.category_id = category

        orm.commit()

        return jsonify(product.to_dict()), 201

    @orm.db_session
    def index(request: Request):
        productsFound = orm.select(p for p in Product)[:]
        products = list()

        for product in productsFound:
            product_dict = product.to_dict()
            product_dict['url'] = f'http://localhost:3000/product-images/{product_dict["path"]}'
            products.append(product_dict)

        return jsonify(products)

    @orm.db_session
    def update(request: Request, product_id: int, filename: str):
        file_path = 'uploads/products/' + filename
        schema = {
            'name': {'type': 'string', 'required': True},
            'price': {'type': 'string', 'required': True},
            'category_id': {'type': 'string', 'required': True},
            'description': {'type': 'string', 'required': True},
            'offer': {'type': 'string', 'required': True},
            'file': {'type': 'string', 'required': False},
        }

        validator = Validator(schema)
        is_valid = validator.validate(request.form)

        if not is_valid:
            if path.exists(file_path):
                remove(file_path)
            return {"error": "Make sure you inputted the correct body"}, 400

        product_name, product_price = request.form['name'], request.form['price']
        product_category_id, product_offer  = request.form['category_id'], request.form['offer']
        product_description = request.form['description']

        category = Category.get(id=product_category_id)
        userId = get_jwt_identity()
        user = User.get(id=userId)

        product = orm.select(p for p in Product if p.id == product_id).first()

        old_file_path = 'uploads/products/' + product.path

        if not product:
            return {"error": "Make sure your product id is correct"}, 401

        if not user.admin:
            if path.exists(file_path):
                remove(file_path)
            return {"error": "You are not authorized to perform this action"}, 401

        product.name = product_name
        product.path = filename
        product.price = product_price
        product.description = product_description
        product.offer = True if product_offer == 'true' else False
        product.category_id = category

        orm.commit()

        if path.exists(old_file_path):
            remove(old_file_path)

        return {}, 200




    @orm.db_session
    def delete(product_id: int):
        product = orm.select(p for p in Product if p.id == product_id).first()

        if not product:
            return {"error": "Make sure your product id is correct"}, 401

        old_file_path = 'delete/products/' + product.path

        if path.exists(old_file_path):
            remove(old_file_path)

        product.delete()
        orm.commit()

        return {}, 200
