from pony import orm

db = orm.Database()
db.bind(provider='postgres', user='postgres', password='1234', host='localhost', database='postgres')

class User(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    email = orm.Required(str)
    password_hash = orm.Required(str)
    admin = orm.Required(bool)


class Product(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    price = orm.Required(str)
    path = orm.Required(str)
    offer = orm.Required(bool)
    
db.generate_mapping(create_tables=True)