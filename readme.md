# qpop

A simple POP3 wrapper to retrieve email content already parsed.

## Usage

```python
from qpop.server import Server, parse_msg_octet
# host = # To be completed
# port = # To be completed
# user = # To be completed
# passwd = # To be completed (If None, the password will be requested at login)
server = Server(host, port, user, passwd)

# Get list of messages
messages = server.get_messages()
n_messages = len(messages)
print(f'Messages found: {n_messages}')

# Read first message
msg_id, msg_octets = parse_msg_octet(messages[0])
print(f'Message ID: {msg_id}')
first_message = server.retrieve_parse_message(msg_id)

# Print header
print(f'Header:\n{first_message.get_header()}')

# Print plain text
print(f'Text:\n{first_message.get_plain_text()}')

# Print html
for html_data in first_message.iterate_content_html():
    print(html_data + '\n')

```

## Example in cli

Read messages list, print how many messages were read, and print header and text of the first one:

```bash
export POP_HOST=  # COMPLETE THIS
export POP_PORT=  # COMPLETE THIS
export POP_USER=  # COMPLETE THIS
export POP_PASS=  # Optional. If not set, it will be asked for when logging into the server with getpass()

# Read one email; Print header and text
PYTHONPATH=. python3 examles/print_header_text.py

# Read one email; Print info
PYTHONPATH=. python3 examles/print_email_info.py
```
