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
    category = orm.Optional(Category)

    
db.generate_mapping(create_tables=True)
