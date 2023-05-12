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
            url = f'http://localhost:3000/product-images/{product["path"]}'

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
        ordersFound = orm.select(o for o in Order)[:]
        orders = [t.to_dict() for t in ordersFound]

        return jsonify(orders)

    @orm.db_session
    def update(request: Request, order_id: str):
        schema = {
            'status': {'type': 'boolean', 'required': True},    
        }

        validator = Validator(schema)
        is_valid = validator.validate(request.json)
                
        if not is_valid:
            return { "error": "Make sure you inputted the correct body" }, 400
        
        userId = get_jwt_identity()
        user = User.get(id=userId)
        new_status = request.json['status']

        if not user.admin:
            return { "error": "You are not authorized to perform this action" }, 401

        order = orm.select(o for o in Order if o.id == order_id).first()

        if not order:
            return { "error": "Make sure your order id is correct" }, 400

        order.status = new_status == True

        orm.commit();        

        return { "message": "Status updated successfully" }, 200