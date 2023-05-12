from app.utils.hashFilename import hashFilename
from flask import Flask, request, send_from_directory
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, jwt_required
from werkzeug.utils import secure_filename
from app.controllers.ProductController import ProductController
from app.controllers.SessionController import SessionController
from app.controllers.CategoryController import CategoryController
from app.controllers.UserController import UserController
from app.controllers.OrderController import OrderController

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JWT_SECRET_KEY'] = '1234'

jwt = JWTManager(app)

#   IMAGES

@app.route('/category-images/<path:filename>', methods=['GET'])
def serve_category_images(filename):
    return send_from_directory(f"uploads/categories", filename)

@app.route('/product-images/<path:filename>', methods=['GET'])
def serve_product_images(filename):
    return send_from_directory(f"uploads/products", filename)

#   USERS AND SESSION

@app.route('/sessions', methods=['POST'])
@cross_origin()
def authenticate_users():
    return SessionController.store(request)

@app.route('/users', methods=['POST'])
@cross_origin()
def create_user():  
    return UserController.store(request)

#   PRODUCTS

@app.route('/products', methods=['POST'])
@cross_origin()
@jwt_required()
def create_product():
    f = request.files['file']
    filename = secure_filename(f.filename)
    hashed_filename = hashFilename(filename) + filename    
    f.save(dst=f"uploads/products/{hashed_filename}")
    
    return ProductController.store(request, filename=hashed_filename)

@app.route('/products', methods=['GET'])
@cross_origin()
@jwt_required()
def get_products():
    return ProductController.index(request)

@app.route('/products/<int:id>', methods=['PUT'])
@cross_origin()
@jwt_required()
def update_product(id):
    f = request.files['file']
    filename = secure_filename(f.filename)
    hashed_filename = hashFilename(filename) + filename    
    f.save(dst=f"uploads/products/{hashed_filename}")

    return ProductController.update(request, id, filename=hashed_filename)

#   CATEGORIES

@app.route('/categories', methods=['POST'])
@cross_origin()
@jwt_required()
def create_category():
    f = request.files['file']
    filename = secure_filename(f.filename)
    hashed_filename = hashFilename(filename) + filename    
    f.save(dst=f"uploads/categories/{hashed_filename}")

    return CategoryController.store(request, filename=hashed_filename)

@app.route('/categories', methods=['GET'])
@cross_origin()
@jwt_required()
def get_categories():
    return CategoryController.index(request)

@app.route('/categories/<int:id>', methods=['PUT'])
@cross_origin()
@jwt_required()
def update_category(id):
    f = request.files['file']
    filename = secure_filename(f.filename)
    hashed_filename = hashFilename(filename) + filename    
    f.save(dst=f"uploads/categories/{hashed_filename}")

    return CategoryController.update(request, id, filename=hashed_filename)

#   ORDERS

@app.route('/orders', methods=['POST'])
@cross_origin()
@jwt_required()
def create_order():
    return OrderController.store(request)

# @app.route('/orders/<int:id>', methods=['PUT'])
# def update_order(id):
#     return OrderController().update(request, id)

@app.route('/orders', methods=['GET'])
@cross_origin()
@jwt_required()
def get_orders():
    return OrderController.index(request)

if __name__ == '__main__':
    app.run()
