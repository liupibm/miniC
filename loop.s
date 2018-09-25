.intel_syntax noprefix
.section .text
L0:
    mov eax, 0
    mov [ebp-4], eax
    mov eax, 0
    mov [ebp-8], eax
L2:
    mov eax, [ebp-8]
    push eax
    mov eax, [ebp+8]
    mov ebx, eax
    pop eax
    cmp eax, ebx
    setl al
    movzx eax, al
    cmp eax, 0
    jz L1
L3:
    mov eax, [ebp-4]
    mov eax, [ebp-4]
    push eax
    mov eax, [ebp-8]
    push eax
    mov eax, 2
    mov ebx, eax
    pop eax
    imul ebx
    mov ebx, eax
    pop eax
    add eax, ebx
    mov [ebp-4], eax
    mov eax, [ebp-8]
    inc eax
    mov [ebp-8], eax
    jmp L2
L1:
    mov eax, [ebp-4]
    mov esp, ebp
    pop ebp
    ret
.global sumUp
sumUp:
    push ebp
    mov ebp, esp
    sub esp, 8
    jmp L0
.section .text
L4:
    lea eax, [sumUp]
    push eax
    jmp L5
L7:
    mov eax, 10
    push eax
    jmp L6
L5:
    jmp L7
L6:
    call [esp+4]
    add esp, 8
    mov [ebp-4], eax
    lea eax, [printf]
    push eax
    jmp L8
L10:
    mov eax, offset L11
.section .data
L11: .asciz "%d"
.section .text
    push eax
    jmp L9
L12:
    mov eax, [ebp-4]
    push eax
    jmp L10
L8:
    jmp L12
L9:
    call [esp+8]
    add esp, 12
    mov esp, ebp
    pop ebp
    ret
.global main
main:
    push ebp
    mov ebp, esp
    sub esp, 4
    jmp L4
