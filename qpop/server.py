from __future__ import annotations

from dataclasses import dataclass, field
from email import parser as email_parser
import getpass
import poplib
import ssl
from typing import Generator


__all__ = [
    'Content',
    'ReceivedEmail',
    'Server',
]

def parse_msg_octet(value: bytes) -> tuple[int]:
    splitted = value.split()
    return tuple(int(s) for s in splitted)


def reconnect_on_error(n_retries: int = 1):

    def decorator(function):

        def wrapper(self, *args, **kwargs):
            try:
                result = function(self, *args, **kwargs)
            except (poplib.error_proto, ssl.SSLEOFError):
                for i in range(n_retries):
                    try:
                        self.connect()
                        result = function(self, *args, **kwargs)
                        return result
                    except (poplib.error_proto, ssl.SSLEOFError):
                        pass
            return result

        return wrapper

    return decorator


def create_and_connect(host, port, user, passwd, context=None) -> poplib.POP3_SSL:
    mailbox = poplib.POP3_SSL(host, port, context=context)
    # open debug switch to print debug information between client and pop3 server.
    # mailbox.set_debuglevel(1)
    # get pop3 server welcome message.
    pop3_server_welcome_msg = mailbox.getwelcome().decode('utf-8')
    # print(mailbox.getwelcome().decode('utf-8'))
    mailbox.user(user)
    mailbox.pass_(passwd)
    return mailbox


def response_is_ok(response: bytes) -> bool:
    return response.startswith(b'+OK')


@dataclass(kw_only=True)
class Content:

    content_type: str = field()
    payload: bytes = field(default=None)

    @classmethod
    def from_part(cls, part) -> Content:
        return cls(
            content_type=part.get_content_type(),
            payload=part.get_payload(decode=True),
        )


class ReceivedEmail:

    header_map = {
        'from': 'From',
        'to': 'To',
        'delivered_to': 'Delivered-To',
        'in_reply_to': 'In-Reply-To',
        'return_path': 'Return-Path',
        'date': 'Date',
        'subject': 'Subject',
    }

    def __init__(self, message: bytes):
        self._raw_message = message
        self._parse()

    def _parse(self):
        self._message_str = b'\r\n'.join(self._raw_message).decode('utf-8')
        self.message = email_parser.Parser().parsestr(self._message_str)
        # print(f'self.message.keys() = {self.message.keys()}')
        self.content = list(self.message.walk())

    def iterate_content_of_type(self, content_type: str) -> Generator[bytes, None, None]:  # [YieldType, SendType, ReturnType]
        for part in self.content:
            if part.get_content_type().startswith(content_type):
                yield part.get_payload(decode=True)

    def iterate_content_text_and_decode(self, content_type: str = 'text/') -> Generator[bytes, None, None]:  # [YieldType, SendType, ReturnType]:
        for body in self.iterate_content_of_type(content_type=content_type):
            yield body.decode()

    def iterate_content_text_plain(self) -> Generator[bytes, None, None]:  # [YieldType, SendType, ReturnType]:
        yield from self.iterate_content_text_and_decode(content_type='text/plain')

    def iterate_content_html(self) -> Generator[bytes, None, None]:  # [YieldType, SendType, ReturnType]:
        yield from self.iterate_content_text_and_decode(content_type='text/html')

    def iterate_content_image(self) -> Generator[bytes, None, None]:  # [YieldType, SendType, ReturnType]:
        yield from self.iterate_content_of_type(content_type='image/')

    def iterate_content_application(self) -> Generator[bytes, None, None]:  # [YieldType, SendType, ReturnType]:
        yield from self.iterate_content_of_type(content_type='application/')

    def get_header(self) -> dict:
        return {
            k: self.message.get(v)
            for k, v in self.header_map.items()
        }

    def get_data(self) -> list[Content]:
        return [
            Content.from_part(part) for part in self.content
        ]

    def get_plain_text(self) -> str:
        return '\n'.join(self.iterate_content_text_plain())


class Server:

    def __init__(self, host, port, user, passwd=None):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.context = ssl.create_default_context()
        self.mailbox = None
        self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        self.disconnect()
        passwd = self.passwd or getpass.getpass('Password:')
        self.mailbox = create_and_connect(self.host, self.port, self.user, passwd, context=self.context)

    @reconnect_on_error(n_retries=0)
    def disconnect(self):
        if self.mailbox is not None:
            try:
                self.mailbox.quit()
            finally:
                self.mailbox = None

    @reconnect_on_error(n_retries=1)
    def get_messages(self) -> list[tuple]:
        response, msg_list, xx = self.mailbox.list()
        if not response_is_ok(response):
            raise RuntimeError(f'Failed to retrieve messages list: {response}')
        return msg_list

    def iter_messages(self) -> Generator[tuple, None, None]:  # [YieldType, SendType, ReturnType]
        for msg in self.get_messages():
            yield parse_msg_octet(msg)

    @reconnect_on_error(n_retries=1)
    def retrieve_message(self, msg_id: int) -> list[bytes]:
        response, message, octets = self.mailbox.retr(msg_id)
        if not response_is_ok(response):
            raise RuntimeError(f'Failed to retrieve message: {response}')
        return message

    def retrieve_parse_message(self, msg_id: int) -> ReceivedEmail:
        message = self.retrieve_message(msg_id)
        return ReceivedEmail(message=message)


    @reconnect_on_error(n_retries=1)
    def retrieve_top(self, msg_id: int, how_much: int = 20) -> list[bytes]:
        response, message, octets = self.mailbox.top(msg_id, how_much)
        if not response_is_ok(response):
            raise RuntimeError(f'Failed to retrieve message: {response}')
        return message


def main():
    pass


if __name__ == '__main__':
    main()
