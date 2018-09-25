# miniC
This is just a hobby project: a compiler for C written in Python (<=600 lines of code).
The compiler supports the basic arithemtic computations, if-else, while loop, function definitions and calls (including the recursive functions).

It consists of the hand-crafted lexer, parser and code generator which produces the x86 (32 bits) assembly code. 

To try it:
python3 compiler.py
gcc -m32 loop.s -o loop
./loop

Note it works only in Linux (again it is just the hobby code). 

