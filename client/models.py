from datetime import datetime

from pony.orm import Required, Database, set_sql_debug, db_session

from config.settigs import DEBUG, DB_FILE_NAME


class ClientDBase:
    db = Database()

    class Contacts(db.Entity):
        username = Required(str, unique=True)
        deleted = Required(bool, default=False)

    class Messages(db.Entity):
        contact = Required(str)
        message = Required(str)
        date = Required(datetime)
        recieved = Required(bool)
        deleted = Required(bool, default=False)

    def __init__(self, name):
        self.db.bind(
            provider="sqlite", filename=f"../{name}.{DB_FILE_NAME}", create_db=True
        )
        set_sql_debug(DEBUG)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def add_message(self, contact_username, message, time, recieved=True):
        store = self.Messages(
            contact=contact_username,
            message=message,
            date=datetime.fromtimestamp(time),
            recieved=recieved,
        )

    @db_session
    def update_contacts(self, users_list):
        for contact in self.Contacts.select():
            if contact.username not in users_list:
                contact.deleted = True

        contacts = {user.username: user.deleted for user in self.Contacts.select()}
        for username in users_list:
            if username in contacts:
                if contacts[username] == True:
                    user = self.Contacts.select(
                        lambda contact: contact.username == username
                    ).get()
                    user.deleted = False
            else:
                contact = self.Contacts(username=username)

    @db_session
    def update_messages(self):
        deleted_users = [
            user.username
            for user in self.Contacts.select(lambda contact: contact.deleted == True)
        ]
        for message in self.Messages.select(
            lambda mes: mes.contact in deleted_users and mes.deleted == False
        ):
            message.deleted = True

    @db_session
    def get_contacts(self):
        return [
            contact.username
            for contact in self.Contacts.select()
            if contact.deleted == False
        ]

    @db_session
    def get_messages(self):
        return self.Messages.select(lambda message: message.deleted == False)[:]


if __name__ == "__main__":
    client_db = ClientDBase("pony")
    client_db.update_contacts(["Alina", "Oleg"])
    client_db.add_message("Alina", "hello", 1680951955.02192)
    client_db.add_message("Oleg", "world", 1680951955.02192)
    client_db.update_contacts(["Alina"])
    client_db.update_messages()
    print(client_db.get_contacts())
    print(client_db.get_messages()[0].message)
