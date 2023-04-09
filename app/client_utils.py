from http import HTTPStatus
from log import LoggerProxy

proxy = LoggerProxy("client")
logger = proxy.get_logger()


class MessageHandler:
    def parse_message(self, message):
        logger.info(f"Parsing messagefrom server: {message}")

        if message["action"] == "login":
            return message["username_status"]

        if message["action"] == "get_users":
            return f'Active users:\n{{"\n".join(message["alert"])}}'

        if message["action"] == "message" and message["user_id"] == self.username:
            self.db.add_message(message["user_login"], message["body"], message["time"])
            return f"{message['body']}"

        if message["action"] in ("get_contacts", "del_contact", "add_contact"):
            self.db.update_contacts(message["alert"])
            return f'Active users:\n{{"\n".join(message["alert"])}}'

        if message["action"] == "status code":
            if message["response"] < 400:
                return f'{message["response"]}: {message["alert"]}'
            return f'{message["response"]}: {message["error"]}'
