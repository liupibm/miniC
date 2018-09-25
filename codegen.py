# esp is just a marker, or logical cursor, it does not restrict you from placing items at anywhere in the stack.
# Two really important invariants:
#  Consider Expr3 := Expr4 + Expr4 for example
#       (1) eax holds the value of the Expr just evaluated. Suppose the 2nd Expr4 is just evalauted, then eax holds its value
#       (2) the val of the Expr is pushed to the stack before any further eval, e.g., 1st Expr4 is pushed to stack before 2nd Expr4 is evaluated.               Interestingly, after the eval of 2nd Expr4 completes,   the val of 1st Expr4 is again on top of the stack!
#       (2) requires that all those temporarily introduced to the stack should be cleaned up! 

output_asm_file = None
label_id = -1
tab = "    "
stackwidth = 4


def x86inst(operator):
    if operator == '*':
        return 'imul'
    elif operator == '/':
        return 'idiv'
    elif operator == '+':
        return 'add'
    elif operator == '-':
        return 'sub' 
    elif operator == '<=':
        return 'setle'
    elif operator == '>=':
        return 'setge'
    elif operator == '<':
        return 'setl'
    elif operator == '>':
        return 'setg'
    elif operator == '!=':
        return 'setne'
    elif operator == '==':
        return 'sete'
    elif operator == '++':
        return "inc"
    elif operator == '--':
        return 'dec'
    else:
        pass
def setup_output_asm(source_file):
    global output_asm_file
    without_extenion = source_file.split('.')[0]
    asm_file_name = without_extenion + ".s"
    output_asm_file = open(asm_file_name, 'w')


def emit(code):
    global output_asm_file
    output_asm_file.write(code)


def new_label():
    global label_id
    label_id += 1
    label = 'L' + str(label_id)
    return label

def emit_label(label):
    output_asm_file.write(label + ":\n")

def emit_func_prologue(func_name, num_of_locals_not_parameters, label):
    output_asm_file.write(".global " + func_name + "\n") # global means we want other modules to see it
    output_asm_file.write(func_name + ":\n")
    output_asm_file.write(tab + "push ebp\n")
    output_asm_file.write(tab + "mov ebp, esp\n")
    output_asm_file.write(tab + "sub esp, " + str(num_of_locals_not_parameters * stackwidth) + "\n")
    output_asm_file.write(tab + "jmp " + label + "\n")




def emit_func_epilogue():
    output_asm_file.write(tab + "mov esp, ebp\n")
    output_asm_file.write(tab + "pop ebp\n")
    output_asm_file.write(tab + "ret\n") # there will be a matching 'call' instruction.
    # if you want to return value, simple: @return, mov the value to eax
