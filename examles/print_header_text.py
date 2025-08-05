def main():
    import os
    from qpop.server import Server, parse_msg_octet

    host = os.getenv('POP_HOST')
    port = os.getenv('POP_PORT')
    user = os.getenv('POP_USER')
    passwd = os.getenv('POP_PASS')

    server = Server(host, port, user, passwd)

    # Get messages and show how many were received
    messages = server.get_messages()
    n_messages = len(messages)
    print(f'Messages found: {n_messages}')

    # Read first message, print header and plain text
    msg_id, msg_octets = parse_msg_octet(messages[0])
    print(f'Message ID: {msg_id}')
    first_message = server.retrieve_parse_message(msg_id)
    print(f'Header:\n{first_message.get_header()}\n'
          f'Text:\n{first_message.get_plain_text()}')


if __name__ == '__main__':
    main()
