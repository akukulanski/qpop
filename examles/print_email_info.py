from email.header import decode_header
from email.utils import parseaddr

# The Subject of the message or the name contained in the Email is encoded string
# , which must decode for it to display properly, this function just provide the feature.
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
       value = value.decode(charset)
    return value

# check email content string encoding charset.
def guess_charset(msg):
    # get charset from message object.
    charset = msg.get_charset()
    # if can not get charset
    if charset is None:
       # get message header content-type value and retrieve the charset from the value.
       content_type = msg.get('Content-Type', '').lower()
       pos = content_type.find('charset=')
       if pos >= 0:
          charset = content_type[pos + 8:].strip()
    return charset

# variable indent_number is used to decide number of indent of each level in the mail multiple bory part.
def print_email_info(msg, indent_number=0):
    if indent_number == 0:
       # loop to retrieve from, to, subject from email header.
       for header in ['From', 'To', 'Subject']:
           # get header value
           value = msg.get(header, '')
           if value:
              # for subject header.
              if header == 'Subject':
                 # decode the subject value
                 value = decode_str(value)
              # for from and to header.
              else:
                 # parse email address
                 hdr, addr = parseaddr(value)
                 # decode the name value.
                 name = decode_str(hdr)
                 value = u'%s <%s>' % (name, addr)
           print('%s%s: %s' % (' ' * indent_number, header, value))
    # if message has multiple part.
    if (msg.is_multipart()):
       # get multiple parts from message body.
       parts = msg.get_payload()
       # loop for each part
       for n, part in enumerate(parts):
           print('%spart %s' % (' ' * indent_number, n))
           print('%s--------------------' % (' ' * indent_number))
           # print multiple part information by invoke print_email_info function recursively.
           print_email_info(part, indent_number + 1)
    # if not multiple part.
    else:
        # get message content mime type
        content_type = msg.get_content_type()
        # if plain text or html content type.
        if content_type=='text/plain' or content_type=='text/html':
           # get email content
           content = msg.get_payload(decode=True)
           # get content string charset
           charset = guess_charset(msg)
           # decode the content with charset if provided.
           if charset:
              content = content.decode(charset)
           print('%sText: %s' % (' ' * indent_number, content + '...'))
        else:
           print('%sAttachment: %s' % (' ' * indent_number, content_type))



def main():
    import os
    from qpop.server import Server, parse_msg_octet

    host = os.getenv('POP_HOST')
    port = os.getenv('POP_PORT')
    user = os.getenv('POP_USER')
    passwd = os.getenv('POP_PASS')

    server = Server(host, port, user, passwd)
    msg_id, msg_octets = parse_msg_octet(server.get_messages()[0])
    print(f'Message ID: {msg_id}')
    first_message = server.retrieve_parse_message(msg_id)
    print_email_info(first_message.message)


if __name__ == '__main__':
    main()
