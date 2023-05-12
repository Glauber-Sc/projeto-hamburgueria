from os import remove, path
from flask import Request, jsonify
from cerberus import Validator
from flask_jwt_extended import get_jwt_identity
from app.connections.database import User, Product, Category, Order, OrderItem
from pony import orm

def extractID(product):
    return product['id']

class OrderController:
    @orm.db_session
    def store(request: Request):        
        schema = {
            'products': {'type': 'list', 'required': True},            
        }
        validator = Validator(schema)
        is_valid = validator.validate(request.json)
                
        if not is_valid:
            return { "error": "Make sure you inputted the correct body" }, 400
                
        userId = get_jwt_identity()
        user = User.get(id=userId)

        productsBody = request.json['products']
        productsMap = map(extractID, productsBody)
        productsIds = list(productsMap)
        products = list()
        order_products = list();

        order = Order(
            user_id=userId,
            status=True
        )

        for id in productsIds:
            product_query_result = orm.select(p for p in Product if p.id == id).first()
            if not product_query_result: continue

            product = product_query_result.to_dict()
            product_body = list(filter(lambda productBody: productBody['id'] == product['id'], productsBody))[0]

            product_category_query = orm.select(c for c in Category if c.id == product['category_id']).first()
            if not product_category_query: continue
            product_category = product_category_query.to_dict()
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product['id'],
                quantity=product_body['quantity']
            )
            orm.commit()

            product['category'] = { "name": product_category['name'] }
            product['quantity'] = product_body['quantity']

            products.append(product)
        
        for product in products:
            url = f'http://localhost:5000/product-images/{product["path"]}'

            new_product = {
                "id": product['id'],
                "name": product['name'],
                "price": product['price'],
                "category": product['category']['name'],
                "url": url,
                "quantity": product['quantity']
            }

            order_products.append(new_product)

        order = {
            "user": {
                "id": user.id,
                "name": user.name
            },
            "products": order_products,
            "status": "Pedido realizado"
        }

        orm.commit()

        return order, 201
     
    @orm.db_session
    def index(request: Request):
        productsFound = orm.select(p for p in Product)[:]
        products = [t.to_dict() for t in productsFound]         

        return jsonify(products)
    
    @orm.db_session
    def update(request: Request, product_id: int, filename: str):
        file_path = 'uploads/products/' + filename
        schema = {
            'name': {'type': 'string', 'required': True},     
            'price': {'type': 'string', 'required': True},   
            'category_id': {'type': 'string', 'required': True},
            'offer': {'type': 'string', 'required': True},     
        }

        validator = Validator(schema)
        is_valid = validator.validate(request.form)
                
        if not is_valid:
            if path.exists(file_path): remove(file_path)
            return { "error": "Make sure you inputted the correct body" }, 400
        
        product_name, product_price = request.form['name'], request.form['price']
        product_category_id, product_offer = request.form['category_id'], request.form['offer']

        category = Category.get(id=product_category_id);        
        userId = get_jwt_identity()
        user = User.get(id=userId)

        product = orm.select(p for p in Product if p.id == product_id).first()

        old_file_path = 'uploads/products/' + product.path

        if not product:
            return { "error": "Make sure your product id is correct" }, 401

        if not user.admin:
            if path.exists(file_path): remove(file_path)
            return { "error": "You are not authorized to perform this action" }, 401

        product.name = product_name
        product.path = filename
        product.price = product_price
        product.offer = True if product_offer == 'true' else False
        product.category_id = category

        orm.commit();

        if path.exists(old_file_path): remove(old_file_path)

        return {}, 200