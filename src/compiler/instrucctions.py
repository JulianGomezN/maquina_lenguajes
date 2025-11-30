INSTRUCTION_SET = {
    # Control básico
    'PARAR':  {'opcode': 0x0000, 'format': 'OP', 'requiresAddress': False},
    'NOP':    {'opcode': 0x0001, 'format': 'OP', 'requiresAddress': False},

    # Aritmética básica (8 bytes)
    'ADD':  {'opcode': 0x0010, 'format': 'RR', 'requiresAddress': False},
    'SUB':  {'opcode': 0x0011, 'format': 'RR', 'requiresAddress': False},
    'MULS': {'opcode': 0x0012, 'format': 'RR', 'requiresAddress': False},
    'MUL':  {'opcode': 0x0013, 'format': 'RR', 'requiresAddress': False},
    'DIV':  {'opcode': 0x0014, 'format': 'RR', 'requiresAddress': False},
    'MOD' :  {'opcode': 0x0015, 'format': 'RR', 'requiresAddress': False},
    'ADDV': {'opcode': 0x0020, 'format': 'RI', 'requiresAddress': False},
    'SUBV': {'opcode': 0x0021, 'format': 'RI', 'requiresAddress': False},
    'INC':  {'opcode': 0x0030, 'format': 'R',  'requiresAddress': False},
    'DEC':  {'opcode': 0x0031, 'format': 'R',  'requiresAddress': False},

    # Lógicas
    'NOT':  {'opcode': 0x0040, 'format': 'R',  'requiresAddress': False},
    'AND':  {'opcode': 0x0041, 'format': 'RR', 'requiresAddress': False},
    # size-suffixed logical (accept codegen using AND8/OR8)
    'AND8': {'opcode': 0x0041, 'format': 'RR', 'requiresAddress': False},
    'ANDV': {'opcode': 0x0042, 'format': 'RI', 'requiresAddress': False},
    'OR':   {'opcode': 0x0043, 'format': 'RR', 'requiresAddress': False},
    'OR8':  {'opcode': 0x0043, 'format': 'RR', 'requiresAddress': False},
    'ORV':  {'opcode': 0x0044, 'format': 'RI', 'requiresAddress': False},
    'XOR':  {'opcode': 0x0045, 'format': 'RR', 'requiresAddress': False},
    'XORV': {'opcode': 0x0046, 'format': 'RI', 'requiresAddress': False},

    # Shifts
    'SHL': {'opcode': 0x0050, 'format': 'RR', 'requiresAddress': False},
    'SHR': {'opcode': 0x0051, 'format': 'RR', 'requiresAddress': False},
    'SAL': {'opcode': 0x0052, 'format': 'RR', 'requiresAddress': False},
    'SAR': {'opcode': 0x0053, 'format': 'RR', 'requiresAddress': False},

    # Memoria básica
    'LOAD':   {'opcode': 0x0060, 'format': 'RI', 'requiresAddress': False},
    'LOADV':  {'opcode': 0x0061, 'format': 'RI', 'requiresAddress': False},
    'STORE':  {'opcode': 0x0062, 'format': 'RI', 'requiresAddress': False},
    'STOREV': {'opcode': 0x0063, 'format': 'RI', 'requiresAddress': False},
    'CLEAR':  {'opcode': 0x0064, 'format': 'R',  'requiresAddress': False},

    # Comparación
    'CMP':  {'opcode': 0x0070, 'format': 'RR', 'requiresAddress': False},
    'CMPV': {'opcode': 0x0071, 'format': 'RI', 'requiresAddress': False},

    # Flags
    'CLRZ': {'opcode': 0x0080, 'format': 'OP', 'requiresAddress': False},
    'CLRN': {'opcode': 0x0081, 'format': 'OP', 'requiresAddress': False},
    'CLRC': {'opcode': 0x0082, 'format': 'OP', 'requiresAddress': False},
    'CLRV': {'opcode': 0x0083, 'format': 'OP', 'requiresAddress': False},
    'SETZ': {'opcode': 0x0084, 'format': 'OP', 'requiresAddress': False},
    'SETN': {'opcode': 0x0085, 'format': 'OP', 'requiresAddress': False},
    'SETC': {'opcode': 0x0086, 'format': 'OP', 'requiresAddress': False},
    'SETV': {'opcode': 0x0087, 'format': 'OP', 'requiresAddress': False},

    # Saltos (requieren dirección)
    'JMP': {'opcode': 0x0090, 'format': 'I', 'requiresAddress': True},
    'JEQ': {'opcode': 0x0091, 'format': 'I', 'requiresAddress': True},
    'JNE': {'opcode': 0x0092, 'format': 'I', 'requiresAddress': True},
    'JLT': {'opcode': 0x0093, 'format': 'I', 'requiresAddress': True},
    'JGE': {'opcode': 0x0094, 'format': 'I', 'requiresAddress': True},
    'JCS': {'opcode': 0x0095, 'format': 'I', 'requiresAddress': True},
    'JCC': {'opcode': 0x0096, 'format': 'I', 'requiresAddress': True},
    'JMI': {'opcode': 0x0097, 'format': 'I', 'requiresAddress': True},
    'JPL': {'opcode': 0x0098, 'format': 'I', 'requiresAddress': True},

    # I/O
    'SVIO':   {'opcode': 0x00A0, 'format': 'RI', 'requiresAddress': False},
    'LOADIO': {'opcode': 0x00A1, 'format': 'RI', 'requiresAddress': False},
    #'SHOWIO': {'opcode': 0x00A2, 'format': 'I',  'requiresAddress': False},
    #'CLRIO':  {'opcode': 0x00A3, 'format': 'I',  'requiresAddress': False},
    #'RESETIO':{'opcode': 0x00A4, 'format': 'OP', 'requiresAddress': False},

    # Aritmética 1 byte
    'ADD1':  {'opcode': 0x0100, 'format': 'RR', 'requiresAddress': False},
    'SUB1':  {'opcode': 0x0101, 'format': 'RR', 'requiresAddress': False},
    'MUL1':  {'opcode': 0x0102, 'format': 'RR', 'requiresAddress': False},
    'MULS1': {'opcode': 0x0103, 'format': 'RR', 'requiresAddress': False},
    'DIV1':  {'opcode': 0x0104, 'format': 'RR', 'requiresAddress': False},
    'MOD1':  {'opcode': 0x0105, 'format': 'RR', 'requiresAddress': False},
    'ADDV1': {'opcode': 0x0110, 'format': 'RI', 'requiresAddress': False},
    'SUBV1': {'opcode': 0x0111, 'format': 'RI', 'requiresAddress': False},

    # Aritmética 2 bytes
    'ADD2':  {'opcode': 0x0200, 'format': 'RR', 'requiresAddress': False},
    'SUB2':  {'opcode': 0x0201, 'format': 'RR', 'requiresAddress': False},
    'MUL2':  {'opcode': 0x0202, 'format': 'RR', 'requiresAddress': False},
    'MULS2': {'opcode': 0x0203, 'format': 'RR', 'requiresAddress': False},
    'DIV2':  {'opcode': 0x0204, 'format': 'RR', 'requiresAddress': False},
    'MOD2':  {'opcode': 0x0205, 'format': 'RR', 'requiresAddress': False},
    'ADDV2': {'opcode': 0x0210, 'format': 'RI', 'requiresAddress': False},
    'SUBV2': {'opcode': 0x0211, 'format': 'RI', 'requiresAddress': False},

    # Aritmética 4 bytes
    'ADD4':  {'opcode': 0x0300, 'format': 'RR', 'requiresAddress': False},
    'SUB4':  {'opcode': 0x0301, 'format': 'RR', 'requiresAddress': False},
    'MUL4':  {'opcode': 0x0302, 'format': 'RR', 'requiresAddress': False},
    'MULS4': {'opcode': 0x0303, 'format': 'RR', 'requiresAddress': False},
    'DIV4':  {'opcode': 0x0304, 'format': 'RR', 'requiresAddress': False},
    'MOD4':  {'opcode': 0x0305, 'format': 'RR', 'requiresAddress': False},
    'ADDV4': {'opcode': 0x0310, 'format': 'RI', 'requiresAddress': False},
    'SUBV4': {'opcode': 0x0311, 'format': 'RI', 'requiresAddress': False},

    # Aritmética 8 bytes
    'ADD8':  {'opcode': 0x0312, 'format': 'RR', 'requiresAddress': False},
    'SUB8':  {'opcode': 0x0313, 'format': 'RR', 'requiresAddress': False},
    'MUL8':  {'opcode': 0x0314, 'format': 'RR', 'requiresAddress': False},
    'MULS8': {'opcode': 0x0315, 'format': 'RR', 'requiresAddress': False},
    'DIV8':  {'opcode': 0x0316, 'format': 'RR', 'requiresAddress': False},
    'MOD8':  {'opcode': 0x0319, 'format': 'RR', 'requiresAddress': False},
    'ADDV8': {'opcode': 0x0317, 'format': 'RI', 'requiresAddress': False},
    'SUBV8': {'opcode': 0x0318, 'format': 'RI', 'requiresAddress': False},

    # MOV
    'MOV1':  {'opcode': 0x0400, 'format': 'RR', 'requiresAddress': False},
    'MOV2':  {'opcode': 0x0401, 'format': 'RR', 'requiresAddress': False},
    'MOV4':  {'opcode': 0x0402, 'format': 'RR', 'requiresAddress': False},
    'MOV8':  {'opcode': 0x0403, 'format': 'RR', 'requiresAddress': False},
    'MOVV1': {'opcode': 0x0410, 'format': 'RI', 'requiresAddress': False},
    'MOVV2': {'opcode': 0x0411, 'format': 'RI', 'requiresAddress': False},
    'MOVV4': {'opcode': 0x0412, 'format': 'RI', 'requiresAddress': False},
    'MOVV8': {'opcode': 0x0413, 'format': 'RI', 'requiresAddress': False},

    # LOADR
    'LOADR1': {'opcode': 0x0510, 'format': 'RR', 'requiresAddress': False},
    'LOADR2': {'opcode': 0x0511, 'format': 'RR', 'requiresAddress': False},
    'LOADR4': {'opcode': 0x0512, 'format': 'RR', 'requiresAddress': False},
    'LOADR8': {'opcode': 0x0513, 'format': 'RR', 'requiresAddress': False},

    # STORE
    'STORE1': {'opcode': 0x0600, 'format': 'RI', 'requiresAddress': False},
    'STORE2': {'opcode': 0x0601, 'format': 'RI', 'requiresAddress': False},
    'STORE4': {'opcode': 0x0602, 'format': 'RI', 'requiresAddress': False},
    'STORE8': {'opcode': 0x0603, 'format': 'RI', 'requiresAddress': False},
    'STORER1':{'opcode': 0x0610, 'format': 'RR', 'requiresAddress': False},
    'STORER2':{'opcode': 0x0611, 'format': 'RR', 'requiresAddress': False},
    'STORER4':{'opcode': 0x0612, 'format': 'RR', 'requiresAddress': False},
    'STORER8':{'opcode': 0x0613, 'format': 'RR', 'requiresAddress': False},

    # FPU 4 bytes
    'FADD4': {'opcode': 0x0700, 'format': 'RR', 'requiresAddress': False},
    'FSUB4': {'opcode': 0x0701, 'format': 'RR', 'requiresAddress': False},
    'FMUL4': {'opcode': 0x0702, 'format': 'RR', 'requiresAddress': False},
    'FDIV4': {'opcode': 0x0703, 'format': 'RR', 'requiresAddress': False},
    'FSQRT4':{'opcode': 0x0720, 'format': 'R',  'requiresAddress': False},
    'FSIN4': {'opcode': 0x0722, 'format': 'R',  'requiresAddress': False},
    'FCOS4': {'opcode': 0x0723, 'format': 'R',  'requiresAddress': False},

    # FPU 8 bytes
    'FADD8': {'opcode': 0x0710, 'format': 'RR', 'requiresAddress': False},
    'FSUB8': {'opcode': 0x0711, 'format': 'RR', 'requiresAddress': False},
    'FMUL8': {'opcode': 0x0712, 'format': 'RR', 'requiresAddress': False},
    'FDIV8': {'opcode': 0x0713, 'format': 'RR', 'requiresAddress': False},
    'FSQRT8':{'opcode': 0x0721, 'format': 'R',  'requiresAddress': False},
    'FSIN8': {'opcode': 0x0724, 'format': 'R',  'requiresAddress': False},
    'FCOS8': {'opcode': 0x0725, 'format': 'R',  'requiresAddress': False},

    # Stack
    'RET':  {'opcode': 0x0800, 'format': 'OP', 'requiresAddress': False},
    'CALL': {'opcode': 0x0099, 'format': 'I',  'requiresAddress': True},
    'POP1': {'opcode': 0x0810, 'format': 'R',  'requiresAddress': False},
    'POP2': {'opcode': 0x0811, 'format': 'R',  'requiresAddress': False},
    'POP4': {'opcode': 0x0812, 'format': 'R',  'requiresAddress': False},
    'POP8': {'opcode': 0x0813, 'format': 'R',  'requiresAddress': False},
    'POP': {'opcode': 0x0813, 'format': 'R',  'requiresAddress': False},
    'PUSH1':{'opcode': 0x0820, 'format': 'R',  'requiresAddress': False},
    'PUSH2':{'opcode': 0x0821, 'format': 'R',  'requiresAddress': False},
    'PUSH4':{'opcode': 0x0822, 'format': 'R',  'requiresAddress': False},
    'PUSH8':{'opcode': 0x0823, 'format': 'R',  'requiresAddress': False},
    'PUSH':{'opcode': 0x0823, 'format': 'R',  'requiresAddress': False},

}


### USED FOR disassembler


IS_INV = {
    # Control básico
    0x0000: {'mnemonic': 'PARAR', 'format': 'OP'},
    0x0001: {'mnemonic': 'NOP',   'format': 'OP'},

    # Aritmética básica (8 bytes)
    0x0010: {'mnemonic': 'ADD',  'format': 'RR'},
    0x0011: {'mnemonic': 'SUB',  'format': 'RR'},
    0x0012: {'mnemonic': 'MULS', 'format': 'RR'},
    0x0013: {'mnemonic': 'MUL',  'format': 'RR'},
    0x0014: {'mnemonic': 'DIV',  'format': 'RR'},
    0x0020: {'mnemonic': 'ADDV', 'format': 'RI'},
    0x0021: {'mnemonic': 'SUBV', 'format': 'RI'},
    0x0030: {'mnemonic': 'INC',  'format': 'R'},
    0x0031: {'mnemonic': 'DEC',  'format': 'R'},

    # Lógicas
    0x0040: {'mnemonic': 'NOT',  'format': 'R'},
    0x0041: {'mnemonic': 'AND',  'format': 'RR'},
    0x0042: {'mnemonic': 'ANDV', 'format': 'RI'},
    0x0043: {'mnemonic': 'OR',   'format': 'RR'},
    0x0044: {'mnemonic': 'ORV',  'format': 'RI'},
    0x0045: {'mnemonic': 'XOR',  'format': 'RR'},
    0x0046: {'mnemonic': 'XORV', 'format': 'RI'},

    # Shifts
    0x0050: {'mnemonic': 'SHL', 'format': 'RR'},
    0x0051: {'mnemonic': 'SHR', 'format': 'RR'},
    0x0052: {'mnemonic': 'SAL', 'format': 'RR'},
    0x0053: {'mnemonic': 'SAR', 'format': 'RR'},

    # Memoria básica
    0x0060: {'mnemonic': 'LOAD',   'format': 'RI'},
    0x0061: {'mnemonic': 'LOADV',  'format': 'RI'},
    0x0062: {'mnemonic': 'STORE',  'format': 'RI'},
    0x0063: {'mnemonic': 'STOREV', 'format': 'RI'},
    0x0064: {'mnemonic': 'CLEAR',  'format': 'R'},

    # Comparación
    0x0070: {'mnemonic': 'CMP',  'format': 'RR'},
    0x0071: {'mnemonic': 'CMPV', 'format': 'RI'},

    # Flags
    0x0080: {'mnemonic': 'CLRZ', 'format': 'OP'},
    0x0081: {'mnemonic': 'CLRN', 'format': 'OP'},
    0x0082: {'mnemonic': 'CLRC', 'format': 'OP'},
    0x0083: {'mnemonic': 'CLRV', 'format': 'OP'},
    0x0084: {'mnemonic': 'SETZ', 'format': 'OP'},
    0x0085: {'mnemonic': 'SETN', 'format': 'OP'},
    0x0086: {'mnemonic': 'SETC', 'format': 'OP'},
    0x0087: {'mnemonic': 'SETV', 'format': 'OP'},

    # Saltos
    0x0090: {'mnemonic': 'JMP', 'format': 'I'},
    0x0091: {'mnemonic': 'JEQ', 'format': 'I'},
    0x0092: {'mnemonic': 'JNE', 'format': 'I'},
    0x0093: {'mnemonic': 'JLT', 'format': 'I'},
    0x0094: {'mnemonic': 'JGE', 'format': 'I'},
    0x0095: {'mnemonic': 'JCS', 'format': 'I'},
    0x0096: {'mnemonic': 'JCC', 'format': 'I'},
    0x0097: {'mnemonic': 'JMI', 'format': 'I'},
    0x0098: {'mnemonic': 'JPL', 'format': 'I'},
    0x0099: {'mnemonic': 'CALL', 'format': 'I'},

    # I/O
    0x00A0: {'mnemonic': 'SVIO',   'format': 'RI'},
    0x00A1: {'mnemonic': 'LOADIO', 'format': 'RI'},

    # Aritmética 1 byte
    0x0100: {'mnemonic': 'ADD1',  'format': 'RR'},
    0x0101: {'mnemonic': 'SUB1',  'format': 'RR'},
    0x0102: {'mnemonic': 'MUL1',  'format': 'RR'},
    0x0103: {'mnemonic': 'MULS1', 'format': 'RR'},
    0x0104: {'mnemonic': 'DIV1',  'format': 'RR'},
    0x0105: {'mnemonic': 'MOD1',  'format': 'RR'},
    0x0110: {'mnemonic': 'ADDV1', 'format': 'RI'},
    0x0111: {'mnemonic': 'SUBV1', 'format': 'RI'},

    # Aritmética 2 bytes
    0x0200: {'mnemonic': 'ADD2',  'format': 'RR'},
    0x0201: {'mnemonic': 'SUB2',  'format': 'RR'},
    0x0202: {'mnemonic': 'MUL2',  'format': 'RR'},
    0x0203: {'mnemonic': 'MULS2', 'format': 'RR'},
    0x0204: {'mnemonic': 'DIV2',  'format': 'RR'},
    0x0205: {'mnemonic': 'MOD2',  'format': 'RR'},
    0x0210: {'mnemonic': 'ADDV2', 'format': 'RI'},
    0x0211: {'mnemonic': 'SUBV2', 'format': 'RI'},

    # Aritmética 4 bytes
    0x0300: {'mnemonic': 'ADD4',  'format': 'RR'},
    0x0301: {'mnemonic': 'SUB4',  'format': 'RR'},
    0x0302: {'mnemonic': 'MUL4',  'format': 'RR'},
    0x0303: {'mnemonic': 'MULS4', 'format': 'RR'},
    0x0304: {'mnemonic': 'DIV4',  'format': 'RR'},
    0x0305: {'mnemonic': 'MOD4',  'format': 'RR'},
    0x0310: {'mnemonic': 'ADDV4', 'format': 'RI'},
    0x0311: {'mnemonic': 'SUBV4', 'format': 'RI'},

    # Aritmética 8 bytes
    0x0312: {'mnemonic': 'ADD8',  'format': 'RR'},
    0x0313: {'mnemonic': 'SUB8',  'format': 'RR'},
    0x0314: {'mnemonic': 'MUL8',  'format': 'RR'},
    0x0315: {'mnemonic': 'MULS8', 'format': 'RR'},
    0x0316: {'mnemonic': 'DIV8',  'format': 'RR'},
    0x0319: {'mnemonic': 'MOD8',  'format': 'RR'},
    0x0317: {'mnemonic': 'ADDV8', 'format': 'RI'},
    0x0318: {'mnemonic': 'SUBV8', 'format': 'RI'},

    # MOV
    0x0400: {'mnemonic': 'MOV1',  'format': 'RR'},
    0x0401: {'mnemonic': 'MOV2',  'format': 'RR'},
    0x0402: {'mnemonic': 'MOV4',  'format': 'RR'},
    0x0403: {'mnemonic': 'MOV8',  'format': 'RR'},
    0x0410: {'mnemonic': 'MOVV1', 'format': 'RI'},
    0x0411: {'mnemonic': 'MOVV2', 'format': 'RI'},
    0x0412: {'mnemonic': 'MOVV4', 'format': 'RI'},
    0x0413: {'mnemonic': 'MOVV8', 'format': 'RI'},

    # LOADR
    0x0510: {'mnemonic': 'LOADR1', 'format': 'RR'},
    0x0511: {'mnemonic': 'LOADR2', 'format': 'RR'},
    0x0512: {'mnemonic': 'LOADR4', 'format': 'RR'},
    0x0513: {'mnemonic': 'LOADR8', 'format': 'RR'},

    # STORE y STORER
    0x0600: {'mnemonic': 'STORE1', 'format': 'RI'},
    0x0601: {'mnemonic': 'STORE2', 'format': 'RI'},
    0x0602: {'mnemonic': 'STORE4', 'format': 'RI'},
    0x0603: {'mnemonic': 'STORE8', 'format': 'RI'},
    0x0610: {'mnemonic': 'STORER1', 'format': 'RR'},
    0x0611: {'mnemonic': 'STORER2', 'format': 'RR'},
    0x0612: {'mnemonic': 'STORER4', 'format': 'RR'},
    0x0613: {'mnemonic': 'STORER8', 'format': 'RR'},

    # FPU 4 bytes
    0x0700: {'mnemonic': 'FADD4', 'format': 'RR'},
    0x0701: {'mnemonic': 'FSUB4', 'format': 'RR'},
    0x0702: {'mnemonic': 'FMUL4', 'format': 'RR'},
    0x0703: {'mnemonic': 'FDIV4', 'format': 'RR'},
    0x0720: {'mnemonic': 'FSQRT4','format': 'R'},
    0x0722: {'mnemonic': 'FSIN4', 'format': 'R'},
    0x0723: {'mnemonic': 'FCOS4', 'format': 'R'},

    # FPU 8 bytes
    0x0710: {'mnemonic': 'FADD8', 'format': 'RR'},
    0x0711: {'mnemonic': 'FSUB8', 'format': 'RR'},
    0x0712: {'mnemonic': 'FMUL8', 'format': 'RR'},
    0x0713: {'mnemonic': 'FDIV8', 'format': 'RR'},
    0x0721: {'mnemonic': 'FSQRT8','format': 'R'},
    0x0724: {'mnemonic': 'FSIN8', 'format': 'R'},
    0x0725: {'mnemonic': 'FCOS8', 'format': 'R'},

    # Stack
    0x0800: {'mnemonic': 'RET', 'format': 'OP'},
    0x0810: {'mnemonic': 'POP1', 'format': 'R'},
    0x0811: {'mnemonic': 'POP2', 'format': 'R'},
    0x0812: {'mnemonic': 'POP4', 'format': 'R'},
    0x0813: {'mnemonic': 'POP8', 'format': 'R'},
    0x0820: {'mnemonic': 'PUSH1','format': 'R'},
    0x0821: {'mnemonic': 'PUSH2','format': 'R'},
    0x0822: {'mnemonic': 'PUSH4','format': 'R'},
    0x0823: {'mnemonic': 'PUSH8','format': 'R'},
}
