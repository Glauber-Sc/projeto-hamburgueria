import pytz
from pony import orm
from datetime import datetime

db = orm.Database()
db.bind(provider='postgres', user='hamburgueria', password='m2o3f4b5', host='34.95.194.132', database='hamburgueria')

class User(db.Entity):
    _table_ = "users"

    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    email = orm.Required(str)
    password_hash = orm.Required(str)
    admin = orm.Required(bool)

    orders = orm.Set("Order")


class Category(db.Entity):
    _table_ = "categories"

    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    path = orm.Optional(str)
    products = orm.Set("Product")


class Product(db.Entity):
    _table_ = "products"

    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    price = orm.Required(str)
    path = orm.Optional(str)
    offer = orm.Optional(bool)
    category_id = orm.Optional(Category)
    description = orm.Optional(str)  # Novo atributo
    items = orm.Set("OrderItem")


class Order(db.Entity):
    _table_ = "orders"

    id = orm.PrimaryKey(int, auto=True)
    status = orm.Optional(str, default="Pedido realizado")
    user_id = orm.Required(User)
    items = orm.Set("OrderItem")
    createdAt = orm.Required(datetime, default=datetime.now(pytz.timezone('America/Sao_Paulo')))


class OrderItem(db.Entity):
    _table_ = "order_items"

    id = orm.PrimaryKey(int, auto=True) 
    order_id = orm.Required(Order)
    product_id = orm.Required(Product)
    quantity = orm.Required(int)
    

print("Generating mappings")  
db.generate_mapping(create_tables=True)
