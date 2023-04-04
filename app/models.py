from datetime import datetime

from pony.orm import Required, Optional, Database, Set, set_sql_debug
from config import DEBUG

db = Database()


class Client(db.Entity):
    username = Required(str)
    info = Optional(str)

    history = Set("ClientHistory")
    contacts = Set("ContactsList", reverse="client_id")
    user = Optional("ContactsList")


class ClientHistory(db.Entity):
    entry_date = Required(datetime)
    ip_address = Required(str)

    user_id = Required(Client)


class ContactsList(db.Entity):
    owner_id = Required(Client)
    client_id = Required(Client)


db.bind(provider="sqlite", filename="db.sqlite3", create_db=True)
set_sql_debug(DEBUG)
db.generate_mapping(create_tables=True)
