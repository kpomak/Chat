from datetime import datetime

from pony.orm import Required, Optional, Database, Set, set_sql_debug, db_session
from config import DEBUG


class Storage:
    db = Database()

    class Client(db.Entity):
        _table_ = "client"
        username = Required(str, unique=True)
        info = Optional(str)
        is_active = Required(bool, default=True)

        history = Set(lambda: Storage.ClientHistory)
        contacts = Set(lambda: Storage.ContactsList, reverse="client_id")
        user = Optional(
            lambda: Storage.ContactsList,
        )

    class ClientHistory(db.Entity):
        _table_ = "clients history"
        entry_date = Required(datetime)
        ip_address = Required(str)
        port = Required(int)

        user_id = Required(lambda: Storage.Client)

    class ContactsList(db.Entity):
        _table_ = "contacts list"
        owner_id = Required(lambda: Storage.Client)
        client_id = Required(lambda: Storage.Client)

    def __init__(self):
        self.db.bind(provider="sqlite", filename="../db.sqlite3", create_db=True)
        set_sql_debug(DEBUG)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def add_user(self, username, info=""):
        client = self.Client(username=username, info=info)

    @db_session
    def get_userlist(self):
        users = self.Client.select(lambda client: client.is_active == True)
        return [user.username for user in users]


if __name__ == "__main__":
    server_db = Storage()
    """
    GET CONNECTION FROM THE LOCAL POOL
    PRAGMA foreign_keys = false
    BEGIN IMMEDIATE TRANSACTION

    CREATE TABLE "client" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "username" TEXT UNIQUE NOT NULL,
    "info" TEXT NOT NULL,
    "is_active" BOOLEAN NOT NULL
    )

    CREATE TABLE "clients history" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "entry_date" DATETIME NOT NULL,
    "ip_address" TEXT NOT NULL,
    "port" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL REFERENCES "client" ("id") ON DELETE CASCADE
    )

    CREATE INDEX "idx_clients history__user_id" ON "clients history" ("user_id")
    CREATE TABLE "contacts list" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "owner_id" INTEGER NOT NULL REFERENCES "client" ("id"),
    "client_id" INTEGER NOT NULL REFERENCES "client" ("id") ON DELETE CASCADE
    )

    CREATE INDEX "idx_contacts list__client_id" ON "contacts list" ("client_id")
    CREATE INDEX "idx_contacts list__owner_id" ON "contacts list" ("owner_id")
    COMMIT
    PRAGMA foreign_keys = true
    CLOSE CONNECTION
    """

    server_db.add_user(username="Fransis")

    """
    GET NEW CONNECTION
    BEGIN IMMEDIATE TRANSACTION
    INSERT INTO "client" ("username", "info", "is_active") VALUES (?, ?, ?)
    ['Fransis', '', True]
    COMMIT
    RELEASE CONNECTION
    """

    print(server_db.get_userlist())  # ['Fransis']

    """
    GET CONNECTION FROM THE LOCAL POOL
    SWITCH TO AUTOCOMMIT MODE
    SELECT "client"."id", "client"."username", "client"."info", "client"."is_active"
    FROM "client" "client"
    WHERE "client"."is_active" = 1
    RELEASE CONNECTION
    """
