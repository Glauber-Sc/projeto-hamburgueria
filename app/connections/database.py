from pony import orm

db = orm.Database()
db.bind(provider='postgres', user='postgres', password='1234', host='localhost', database='hamburgueria')

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
    offer = orm.Required(bool)
    category_id = orm.Optional(Category)
    items = orm.Set("OrderItem")


class Order(db.Entity):
    _table_ = "orders"

    id = orm.PrimaryKey(int, auto=True)
    status = orm.Required(bool)
    user_id = orm.Required(User)
    items = orm.Set("OrderItem")


class OrderItem(db.Entity):
    _table_ = "order_items"

    id = orm.PrimaryKey(int, auto=True) 
    order_id = orm.Required(Order)
    product_id = orm.Required(Product)
    quantity = orm.Required(int)
    

print("Generating mappings")  
db.generate_mapping(create_tables=True)
