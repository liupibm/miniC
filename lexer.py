cur_token = None
cur_ch = None
buffer = []
cur_f = None
TOKEN_EOF = -1
TOKEN_NUM = 0
TOKEN_IDENTIFIER = 1
TOKEN_STRING = 2
TOKEN_CHAR = 3
TOKEN_OPERATOR = 4
TOKEN_OTHER=5

cur_token_type = -1

def tokentype():
    global cur_token_type
    return cur_token_type
def token():
    global cur_token
    return cur_token


def buffer_to_string(buffer):
    return ''.join(buffer)

def next(): # assumption: my first char is always fetched by the last token, who does not know when to stop
    global buffer
    global cur_ch
    global cur_token_type
    global cur_f
    global cur_token
    buffer.clear()



    while cur_ch and cur_ch.isspace():
        cur_ch = cur_f.read(1)

    if not cur_ch:# EOF
        cur_token_type = TOKEN_EOF
        cur_token = None
        return cur_token

    if cur_ch.isalpha(): # identifiers
        buffer.append(cur_ch)
        cur_ch = cur_f.read(1)
        while cur_ch and (cur_ch.isalnum() or cur_ch == '_'): # note _
            buffer.append(cur_ch)
            cur_ch = cur_f.read(1)
        cur_token_type = TOKEN_IDENTIFIER
        cur_token = buffer_to_string(buffer)
        return cur_token

    if cur_ch.isnumeric(): # number
        buffer.append(cur_ch)
        cur_ch = cur_f.read(1)
        while cur_ch and cur_ch.isnumeric(): # note _
            buffer.append(cur_ch)
            cur_ch = cur_f.read(1)
        cur_token_type = TOKEN_NUM
        cur_token = buffer_to_string(buffer)
        return cur_token

    if cur_ch == '\'' or cur_ch == '\"': # string and chars
        endstring = cur_ch
        buffer.append(cur_ch)
        cur_ch = cur_f.read(1)

        while cur_ch and cur_ch != endstring:
            buffer.append(cur_ch)
            if cur_ch == '\\':
                buffer.append(cur_f.read(1)) # secretly eat next \t then act as if nothing happened
            cur_ch = cur_f.read(1)
        if cur_ch and cur_ch == endstring: # do not forget the endstring
            buffer.append(cur_ch)
            cur_ch = cur_f.read(1)
        if endstring == '\'':
            cur_token_type = TOKEN_CHAR
        else:
            cur_token_type = TOKEN_STRING
        cur_token = buffer_to_string(buffer)
        return cur_token

    if cur_ch: # operators
        if cur_ch == '+' or cur_ch == '-' or cur_ch== '*' or cur_ch== '/' or cur_ch == '<' or cur_ch == '>' or cur_ch== '=' or cur_ch== '&' or cur_ch == '|':
            buffer.append(cur_ch)
            lastseen = cur_ch
            cur_ch = cur_f.read(1)
            if cur_ch and (cur_ch == lastseen or cur_ch == '='):# cool, found my buddy
                buffer.append(cur_ch)
                cur_ch = cur_f.read(1)
            cur_token_type = TOKEN_OPERATOR
            cur_token = buffer_to_string(buffer)
            return cur_token

        if cur_ch and cur_ch == '!':
            buffer.append(cur_ch)
            cur_ch = cur_f.read(1)
            if cur_ch and cur_ch == '=':
                buffer.append(cur_ch)
                cur_ch = cur_f.read(1)
            cur_token_type = TOKEN_OPERATOR
            cur_token = buffer_to_string(buffer)
            return cur_token
        else:
            buffer.append(cur_ch)
            cur_ch = cur_f.read(1)
            cur_token_type = TOKEN_OTHER
            cur_token = buffer_to_string(buffer)
            return cur_token



def lexer_init(file_path): # lexer_init('basic.c')
    # Test Driver:
    global cur_f
    global cur_ch

    cur_f = open(file_path)
    cur_ch = cur_f.read(1) # ensure the assumption of next: first char already in ch



# test:
# lexer_init("basic.c")
# while True:
#     token = next()
#     if token != None:
#         print(token, cur_token_type)
#     else:
#         break
