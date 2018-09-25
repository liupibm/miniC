from codegen import *
from lexer import *
#TODO  codegen: if-else, while

globals = [] # (name, isFunc)
locals = [] # (name: isParam)




#rule for everybody: once you are done, bring the next token in


# what are supported: if/else, while(){}, sequences, basic arithematic computations, func def/calls.
# what are not supported: do-while, for loop, arrays, advanced arithematic computations

def is_local(var_name):
    for pair in locals:
        if pair[0] == var_name:
            return True
    return False

def is_global(var_name):
    for pair in globals:
        if pair[0] == var_name:
            return True
    return False


# feel free to add more library functions you want to call here
def setup_global_functions():
    global globals
    globals.append(("printf", True)) 
    globals.append(("malloc", True)) 
    globals.append(("free", True)) 


def num_of_locals_not_parameters():
    num_of_locals = 0
    for pair in locals:
        if not pair[1]:
            num_of_locals += 1
    return num_of_locals

def compute_offset(var_name):
    index_para = 0
    index_pure_local = 0
     
    for pair in locals:
        if pair[0] == var_name:
            if pair[1]:
                return (index_para+2)*stackwidth
            else:
                return -1*(index_pure_local+1)*stackwidth
        if pair[1]:
            index_para += 1
        else:
            index_pure_local += 1

    assert (var_name == None), "code gen error: no locals with the name {} found!".format(var_name) 

def offset_to_str(offset):
    if offset < 0:
        return str(offset)
    elif offset >0:
        return "+"+str(offset)
    else:
        return "" # add nothing



# Func = int ID(ID*) S
# note: S must start with { in this BNF.
def func(func_name):
    global  locals
    global globals
    locals.clear()
    emit('.section .text\n')
    globals.append((func_name, True))
    next() # ) or arg0's type
    if token() != ')': # token: arg0's type
        next() # arg0
        locals.append((token(), True))
        next() # token: ',' or ')'
        while token() == ",":
            next()
            next()
            locals.append((token(), True))
            next()

    assert (token() == ')'),"parsing error: expect ')'"
    next() # token: '{' or ';'

    #emit_func_prologue(func_name)
    label = new_label() # replaced the prologue emitting with this placeholder label
    emit_label(label)

    assert (token() == '{'), "parsing error: expect '{'. For simplicity, we support func def, but don't support func decl. "
    stmt(token())
    emit_func_epilogue()

    emit_func_prologue(func_name, num_of_locals_not_parameters(),label) # we want to preserve regions for locals. Need the #num info
                                                                        # alternatively, you can do an extra pass to compute #num


# S=if... | while...| int x=...|x=y+z...|S:S|{S}
def stmt(start_token):
    if start_token == "{":
        next()
        while token() != '}': # collection of stmts
            stmt(token())
        assert (token() == '}'),"parsing error: expect '}'" # after parsing the stmt, we should see the closing }
        next()
    elif start_token == "int" or start_token == "char":
        #do expr() first, then notice to assign to local
        next() # token: var
        var_name = token()
        locals.append((var_name, False))

        next()
        if token() == "=":
            next()
            expr(token())
            offset = compute_offset(var_name)
            emit(tab+ "mov [ebp" + offset_to_str(offset) + "], eax\n")
        assert (token() == ';'),"parsing error: expect ';'"
        next()
    elif start_token == "if":
        branch(start_token)
    elif start_token == "while":
        loop(start_token)
    elif start_token == "return":
        # moving val to eax is enough, 'ret' will take care of the rest
        next()
        expr(token())
        # val is automatically in eax
        assert (token() == ';'),"parsing error: expect ';'"
        next()
    else: # Expr
        #core part!
        expr(start_token)
        assert (token() == ';'),"parsing error: expect ';'"
        next()

def loop(start_token):
    assert (start_token == 'while'),"parsing error: expect 'while'"
    next()
    assert (token() == '('),"parsing error: expect '('"
    next()
    end_label = new_label()
    check_label = new_label()
    emit_label(check_label)
    expr(token())
    emit(tab + "cmp eax, 0\n")
    emit(tab + "jz {}\n".format(end_label))
    assert (token() == ')'),"parsing error: expect ')'"
    next()
    body_label = new_label()
    emit_label(body_label) 
    stmt(token())
    emit(tab + "jmp {}\n".format(check_label))
    emit_label(end_label) 

def branch(start_token):
    assert (start_token == 'if'),"parsing error: expect 'if'"
    next()
    assert (token() == '('),"parsing error: expect '('"
    next()
    expr(token())
    else_label = new_label()
    emit(tab+"cmp eax, 0\n")
    emit(tab+ "jz {} \n".format(else_label))
    assert (token() == ')'),"parsing error: expect ')'"
    next()
    if_label = new_label()
    emit_label(if_label)
    stmt(token())
    emit(tab+ "jmp {} \n".format(end_label))

    emit_label(else_label) # always generate else label. Worst case: else body is empty, so what?
    if token() == "else":
        next()
        stmt(token())

    end_label = new_label()
    emit_label(end_label)



# E= Expr1
# Expr1 = Expr2 '=' Expr2
# Expr2 = Expr3 && Expr3
# Expr3 = Expr4 <=Expr4
# Expr4 = Expr5 + Expr5
# Expr5= -Expr5 | Atom| Atom++
# Atom = ID | ID(...) | ID[...] , or alternatively, Atom=ID | CALL | ID[...], CALL = ID(E*)
# for those sharing the same prefix, you can handle the prefix first and delay the path choosing.

def expr(start_token):
    expr1(start_token)

def expr5(start_token): #unary
    if start_token == '-':
        next()
        expr5(token())
        emit(tab+"neg eax\n")
    else:
        atom(start_token)
        cur_token = token()
        if cur_token == "++" or cur_token == "--":
            next()
            inst = x86inst(cur_token) 
            emit(tab + inst + " eax\n")
            offset_to_ebp = compute_offset(start_token)
            emit(tab+ "mov [ebp" + offset_to_str(offset_to_ebp) + "], eax\n")

def expr4point5(start_token): # fix embarassing bug: 5+4*3-> 27!, due to that + is at the same precedence level as *.
    expr5(start_token)
    cur = token() # if the following is not exeecuted, the result is in eax, no push needed
    while cur == '*' or cur == '/':
        emit(tab+"push eax\n")
        next()
        expr5(token())
        emit(tab+"mov ebx, eax\n")
        emit(tab+"pop eax\n") # give seat eax to big brother!
        inst = x86inst(cur) 
        emit(tab+"{0} ebx\n".format(inst)) # hoping that we do not need the edx:eax extension. eax is big enough to hold the result
        cur = token()

def expr4(start_token): # expr5+expr5
    expr4point5(start_token)
    cur = token()
    while cur == "+" or cur == '-':
        emit(tab+"push eax\n")
        next()
        expr4point5(token())
        emit(tab+"mov ebx, eax\n")
        emit(tab+"pop eax\n")
        inst = x86inst(cur) 
        emit(tab+"{0} eax, ebx\n".format(inst)) 
        cur = token()

def expr3(start_token): # expr4<=expr4
    expr4(start_token)
    cur = token()
    if cur == '<=' or cur == '>=' or cur == '<' or cur == '>' or cur == '!=' or cur == '==':
        emit(tab+"push eax\n")
        next()
        expr4(token())
        emit(tab+"mov ebx, eax\n")
        emit(tab+"pop eax\n")
        inst = x86inst(cur) 
        emit(tab+"cmp eax, ebx\n")
        emit(tab+inst+" al\n") # setxx only takes 8bit as argument! stingy!
        emit(tab+"movzx eax, al\n")
        
# need to achieve the short circuit semantics.
def expr2(start_token): #expr3 && expr3
    expr3(start_token)
    cur = token()
    if cur == '||' or cur == '&&': # otherwise, end here
        bypass2nd = new_label()
        # short circuit:
        emit(tab+"cmp eax, 0\n")
        if cur == '||': # ignore 2nd, total=eax=1st
            emit(tab+"jnz " + bypass2nd + "\n")
        else:
            emit(tab+"jz " + bypass2nd + "\n")

        next()
        expr3(token())
        #ignore 1st, total=eax=2nd
        emit_label(bypass2nd)



def expr1(start_token): # expr2 = expr2
    expr2(start_token)
    if token() == '=': # otherwise, end here
        var_name = start_token
        next()
        expr2(token())
        offset_to_ebp = compute_offset(var_name)
        emit(tab+ "mov [ebp" + offset_to_str(offset_to_ebp) + "], eax\n")


#TODO global variable, where is it defined?
def atom(start_token):
    name = start_token
    tokenT = tokentype()
    if tokenT== TOKEN_NUM:
        emit(tab+'mov eax, {}\n'.format(token()))
    elif tokenT == TOKEN_STRING:
        label = new_label()
        emit(tab+ 'mov eax, offset ' + label +  '\n')
        emit('.section .data\n') 
        emit(label + ": .asciz " + token() + "\n")
        emit(".section .text\n")
    elif tokenT == TOKEN_IDENTIFIER:
        if is_local(name):
            offset_to_ebp = compute_offset(name)
            emit(tab+ "mov eax, [ebp" + offset_to_str(offset_to_ebp) + "]\n")
        elif is_global(name):
            emit(tab+"lea eax, [{}]\n".format(name))

    next()
    cur = token()
    if cur == "(":
        call(name, token())

    elif cur == "[":
        pass # to be handled later



def call(name, start_token): # a bit tricky
    emit(tab+"push eax\n") # push func addr
    next()
    start_label= new_label()
    end_label = new_label()
    arg_num = 0
    if token() != ')':
        emit(tab+"jmp {}\n".format(start_label))

        cur_label = new_label()
        emit_label(cur_label) 
        expr(token())
        emit(tab+"push eax\n")
        arg_num += 1
        emit(tab+"jmp {}\n".format(end_label))
        prev_label = cur_label
        while token() == ",":
            next()
            cur_label = new_label()
            emit_label(cur_label) 
            expr(token())
            emit(tab+"push eax\n")
            arg_num += 1
            emit(tab+"jmp {}\n".format(prev_label))
            prev_label = cur_label
   
        emit_label(start_label) 
        emit(tab+"jmp {}\n".format(prev_label))

        emit_label(end_label)

    # call and pop 
    emit(tab+"call [esp+{}]\n".format(str(arg_num*stackwidth)))
    emit(tab+"add esp, " + str((arg_num+1)*stackwidth) + "\n")  # pop args and func addr
    # the ret will be in eax if any, see 'ret' instruction!
    assert (token() == ')'),"parsing error: expect ')'"
    next()


def top_level(source_file):
    lexer_init(source_file)
    setup_output_asm(source_file)
    setup_global_functions() 
    emit(".intel_syntax noprefix\n")

    next() # should be type

    while tokentype() != TOKEN_EOF:
        name_func_or_var = next() # func/var ID

        next()
        cur = token()
        if cur == "(": # i do not care how much you look ahead to decide the path
            func(name_func_or_var)
        elif cur == "=": # global initialization
            pass

top_level("loop.c")
