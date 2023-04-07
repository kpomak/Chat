from datetime import datetime

from pony.orm import Required, Optional, Database, Set, set_sql_debug, db_session
from config import DEBUG, DEFAULT_PORT


class Storage:
    db = Database()

    class Client(db.Entity):
        _table_ = "client"
        username = Required(str, unique=True)
        info = Optional(str)
        is_active = Required(bool, default=True)

        history = Set(lambda: Storage.ClientHistory)
        contacts = Set(lambda: Storage.ContactsList, reverse="client_id")
        client = Optional(
            lambda: Storage.ContactsList,
        )

    class ClientHistory(db.Entity):
        _table_ = "clients history"
        client_id = Required(lambda: Storage.Client)
        entry_date = Required(datetime)
        ip_address = Required(str)
        port = Required(int)

    class ContactsList(db.Entity):
        _table_ = "contacts list"
        owner_id = Required(lambda: Storage.Client)
        contact_id = Required(lambda: Storage.Client)

    def __init__(self):
        self.db.bind(provider="sqlite", filename="../db.sqlite3", create_db=True)
        set_sql_debug(DEBUG)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def activate_client(self, username, *args, info="", **kwargs):
        client = self.Client.select(lambda client: client.username == username).get()
        if not client:
            client = self.Client(username=username, info=info)
            client.flush()
        elif not client.is_active:
            client.is_active = True
        self.add_history(client)

    @db_session
    def add_history(self, client, **kwargs):
        event = self.ClientHistory(
            client_id=client.id,
            entry_date=datetime.now(),
            ip_address=kwargs.get("ip_address") or "n/a",
            port=kwargs.get("port") or DEFAULT_PORT,
        )

    @db_session
    def deactivate_client(self, username):
        client = self.Client.select(lambda client: client.username == username).get()
        client.is_active = False

    @db_session
    def get_contacts(self, username):
        pass


if __name__ == "__main__":
    server_db = Storage()
    server_db.activate_user("Marvl")
