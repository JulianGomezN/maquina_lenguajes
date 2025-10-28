### Formatos de Instrucción (64 bits)

## Formatos de Instrucción (64 bits)

Para simplificar la implementación, se definen **cinco formatos fijos** de 64 bits:

#### Formato OP (Solo Opcode)
Usado en `PARAR`, `NOP`.
```
 63    48 47                    0
┌────────┬──────────────────────┐
│ OPCODE │         0            │
│16 bits │      48 bits         │
└────────┴──────────────────────┘
```

#### Formato R (Registro Único)
Usado en `INC R`, `DEC R`, `NOT R`.
```
 63    48 47  44 43             0
┌────────┬─────┬─────────────────┐
│ OPCODE │ RD  │        0        │
│16 bits │4bits│     44 bits     │
└────────┴─────┴─────────────────┘
```

#### Formato RR (Registro-Registro)
Usado en `ADD R, R'`, `SUB R, R'`.
```
 63    48 47           8 7   4 3   0
┌────────┬─────────────┬─────┬─────┐
│ OPCODE │      0      │ RD  │ RS  │
│16 bits │   40 bits   │4bits│4bits│
└────────┴─────────────┴─────┴─────┘
```

#### Formato RI (Registro-Inmediato)
Usado en `LOADV R, v`, `ADDV R, v`.
```
 63    48 47  44 43             0
┌────────┬─────┬─────────────────┐
│ OPCODE │ RD  │   INMEDIATO     │
│16 bits │4bits│    44 bits      │
└────────┴─────┴─────────────────┘
```

#### Formato I (Solo Inmediato)  
Usado en `JMP k`, `SHOWIO addr`.
```
 63    48 47             0
┌────────┬─────────────────┐
│ OPCODE │   INMEDIATO     │
│16 bits │    48 bits      │
└────────┴─────────────────┘
```

---



## Conjunto de Instrucciones (ISA)

### Control de Flujo

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0000 | PARAR | Termina la ejecución del programa |
| 0x0001 | NOP | No operación (sin efecto) |
| 0x0090 | JMP k | Salto incondicional a dirección k |
| 0x0091 | JEQ k | Salto si Z=1 (resultado igual a cero) |
| 0x0092 | JNE k | Salto si Z=0 (resultado no igual a cero) |
| 0x0093 | JMI k | Salto si N=1 (resultado negativo) |
| 0x0094 | JPL k | Salto si N=0 (resultado positivo) |

### Aritmética

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0010 | ADD Rd, Rs | Rd = Rd + Rs |
| 0x0011 | SUB Rd, Rs | Rd = Rd - Rs |
| 0x0012 | MULS Rd, Rs | Rd = Rd × Rs (con signo) |
| 0x0013 | MUL Rd, Rs | Rd = Rd × Rs (sin signo) |
| 0x0014 | DIV Rd, Rs | Rd = Rd ÷ Rs |
| 0x0020 | ADDV Rd, v | Rd = Rd + v (valor inmediato) |
| 0x0021 | SUBV Rd, v | Rd = Rd - v (valor inmediato) |
| 0x0030 | INC Rd | Rd = Rd + 1 |
| 0x0031 | DEC Rd | Rd = Rd - 1 |

### Lógicas y Bits

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0040 | NOT Rd | Rd = ~Rd (inversión de bits) |
| 0x0041 | AND Rd, Rs | Rd = Rd & Rs |
| 0x0042 | ANDV Rd, v | Rd = Rd & v |
| 0x0043 | OR Rd, Rs | Rd = Rd \| Rs |
| 0x0044 | ORV Rd, v | Rd = Rd \| v |
| 0x0045 | XOR Rd, Rs | Rd = Rd ^ Rs |
| 0x0046 | XORV Rd, v | Rd = Rd ^ v |
| 0x0050 | SHL Rd | Shift left lógico |
| 0x0051 | SHR Rd | Shift right lógico |

### Memoria y Datos

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0060 | LOAD Rd, addr | Rd = Memoria[addr] |
| 0x0061 | LOADV Rd, v | Rd = v (cargar valor inmediato) |
| 0x0062 | STORE Rd, Rs | Memoria[Rs] = Rd |
| 0x0063 | STOREV Rd, addr | Memoria[addr] = Rd |
| 0x0064 | CLEAR Rd | Rd = 0 |
| 0x0070 | CMP Rd, Rs | Comparar Rd con Rs (8 bytes, actualiza flags) |
| 0x0071 | CMPV Rd, v | Comparar Rd con valor inmediato (8 bytes) |
| 0x0830 | CMP1 Rd, Rs | Comparar Rd con Rs (1 byte) |
| 0x0831 | CMP2 Rd, Rs | Comparar Rd con Rs (2 bytes) |
| 0x0832 | CMP4 Rd, Rs | Comparar Rd con Rs (4 bytes) |
| 0x0833 | CMP8 Rd, Rs | Comparar Rd con Rs (8 bytes) |
| 0x0840 | CMPV1 Rd, v | Comparar Rd con valor inmediato (1 byte) |
| 0x0841 | CMPV2 Rd, v | Comparar Rd con valor inmediato (2 bytes) |
| 0x0842 | CMPV4 Rd, v | Comparar Rd con valor inmediato (4 bytes) |
| 0x0843 | CMPV8 Rd, v | Comparar Rd con valor inmediato (8 bytes) |

### Entrada/Salida

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x00A0 | SVIO Rd, addr | IO[addr] = Rd |
| 0x00A1 | LOADIO Rd, addr | Rd = IO[addr] |
| 0x00A2 | SHOWIO addr | Mostrar valor en IO[addr] |
| 0x00A3 | CLRIO | Limpiar dispositivos de entrada |
| 0x00A4 | RESETIO | Resetear sistema de E/S |

### Aritmética con Tamaños Específicos (ALU)

#### Operaciones de 1 Byte
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0100 | ADD1 Rd, Rs | Rd = Rd + Rs (1 byte, con signo) |
| 0x0101 | SUB1 Rd, Rs | Rd = Rd - Rs (1 byte, con signo) |
| 0x0102 | MUL1 Rd, Rs | Rd = Rd × Rs (1 byte, sin signo) |
| 0x0103 | MULS1 Rd, Rs | Rd = Rd × Rs (1 byte, con signo) |
| 0x0104 | DIV1 Rd, Rs | Rd = Rd ÷ Rs (1 byte, con signo) |
| 0x0110 | ADDV1 Rd, v | Rd = Rd + v (1 byte, valor inmediato) |
| 0x0111 | SUBV1 Rd, v | Rd = Rd - v (1 byte, valor inmediato) |

#### Operaciones de 2 Bytes
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0200 | ADD2 Rd, Rs | Rd = Rd + Rs (2 bytes, con signo) |
| 0x0201 | SUB2 Rd, Rs | Rd = Rd - Rs (2 bytes, con signo) |
| 0x0202 | MUL2 Rd, Rs | Rd = Rd × Rs (2 bytes, sin signo) |
| 0x0203 | MULS2 Rd, Rs | Rd = Rd × Rs (2 bytes, con signo) |
| 0x0204 | DIV2 Rd, Rs | Rd = Rd ÷ Rs (2 bytes, con signo) |
| 0x0210 | ADDV2 Rd, v | Rd = Rd + v (2 bytes, valor inmediato) |
| 0x0211 | SUBV2 Rd, v | Rd = Rd - v (2 bytes, valor inmediato) |

#### Operaciones de 4 Bytes
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0300 | ADD4 Rd, Rs | Rd = Rd + Rs (4 bytes, con signo) |
| 0x0301 | SUB4 Rd, Rs | Rd = Rd - Rs (4 bytes, con signo) |
| 0x0302 | MUL4 Rd, Rs | Rd = Rd × Rs (4 bytes, sin signo) |
| 0x0303 | MULS4 Rd, Rs | Rd = Rd × Rs (4 bytes, con signo) |
| 0x0304 | DIV4 Rd, Rs | Rd = Rd ÷ Rs (4 bytes, con signo) |
| 0x0310 | ADDV4 Rd, v | Rd = Rd + v (4 bytes, valor inmediato) |
| 0x0311 | SUBV4 Rd, v | Rd = Rd - v (4 bytes, valor inmediato) |

### Operaciones de 8 Bytes
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0300 | ADD8 Rd, Rs | Rd = Rd + Rs (4 bytes, con signo) |
| 0x0301 | SUB8 Rd, Rs | Rd = Rd - Rs (4 bytes, con signo) |
| 0x0302 | MUL8 Rd, Rs | Rd = Rd × Rs (4 bytes, sin signo) |
| 0x0303 | MULS8 Rd, Rs | Rd = Rd × Rs (4 bytes, con signo) |
| 0x0304 | DIV8 Rd, Rs | Rd = Rd ÷ Rs (4 bytes, con signo) |
| 0x0310 | ADDV8 Rd, v | Rd = Rd + v (4 bytes, valor inmediato) |
| 0x0311 | SUBV8 Rd, v | Rd = Rd - v (4 bytes, valor inmediato) |

### Transferencia de Datos (MOV)

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0400 | MOV1 Rd, Rs | Rd = Rs (1 byte) |
| 0x0401 | MOV2 Rd, Rs | Rd = Rs (2 bytes) |
| 0x0402 | MOV4 Rd, Rs | Rd = Rs (4 bytes) |
| 0x0403 | MOV8 Rd, Rs | Rd = Rs (8 bytes) |
| 0x0410 | MOVV1 Rd, v | Rd = v (1 byte, valor inmediato) |
| 0x0411 | MOVV2 Rd, v | Rd = v (2 bytes, valor inmediato) |
| 0x0412 | MOVV4 Rd, v | Rd = v (4 bytes, valor inmediato) |
| 0x0413 | MOVV8 Rd, v | Rd = v (8 bytes, valor inmediato) |

### Carga de Memoria (LOAD)

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0500 | LOAD1 Rd, addr | Rd = Memoria[addr] (1 byte) |
| 0x0501 | LOAD2 Rd, addr | Rd = Memoria[addr] (2 bytes) |
| 0x0502 | LOAD4 Rd, addr | Rd = Memoria[addr] (4 bytes) |
| 0x0503 | LOAD8 Rd, addr | Rd = Memoria[addr] (8 bytes) |
| 0x0510 | LOADR1 Rd, Rs | Rd = Memoria[Rs] (1 byte, indirecto) |
| 0x0511 | LOADR2 Rd, Rs | Rd = Memoria[Rs] (2 bytes, indirecto) |
| 0x0512 | LOADR4 Rd, Rs | Rd = Memoria[Rs] (4 bytes, indirecto) |
| 0x0513 | LOADR8 Rd, Rs | Rd = Memoria[Rs] (8 bytes, indirecto) |

### Almacenamiento en Memoria (STORE)

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0600 | STORE1 Rd, addr | Memoria[addr] = Rd (1 byte) |
| 0x0601 | STORE2 Rd, addr | Memoria[addr] = Rd (2 bytes) |
| 0x0602 | STORE4 Rd, addr | Memoria[addr] = Rd (4 bytes) |
| 0x0603 | STORE8 Rd, addr | Memoria[addr] = Rd (8 bytes) |
| 0x0610 | STORER1 Rd, Rs | Memoria[Rs] = Rd (1 byte, indirecto) |
| 0x0611 | STORER2 Rd, Rs | Memoria[Rs] = Rd (2 bytes, indirecto) |
| 0x0612 | STORER4 Rd, Rs | Memoria[Rs] = Rd (4 bytes, indirecto) |
| 0x0613 | STORER8 Rd, Rs | Memoria[Rs] = Rd (8 bytes, indirecto) |

### Punto Flotante (FPU)

#### Operaciones de 4 Bytes (Float)
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0700 | FADD4 Rd, Rs | Rd = Rd + Rs (float, 4 bytes) |
| 0x0701 | FSUB4 Rd, Rs | Rd = Rd - Rs (float, 4 bytes) |
| 0x0702 | FMUL4 Rd, Rs | Rd = Rd × Rs (float, 4 bytes) |
| 0x0703 | FDIV4 Rd, Rs | Rd = Rd ÷ Rs (float, 4 bytes) |
| 0x0720 | FSQRT4 Rd | Rd = √Rd (float, 4 bytes) |
| 0x0722 | FSIN4 Rd | Rd = sin(Rd) (float, 4 bytes) |
| 0x0723 | FCOS4 Rd | Rd = cos(Rd) (float, 4 bytes) |

#### Operaciones de 8 Bytes (Double)
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0710 | FADD8 Rd, Rs | Rd = Rd + Rs (double, 8 bytes) |
| 0x0711 | FSUB8 Rd, Rs | Rd = Rd - Rs (double, 8 bytes) |
| 0x0712 | FMUL8 Rd, Rs | Rd = Rd × Rs (double, 8 bytes) |
| 0x0713 | FDIV8 Rd, Rs | Rd = Rd ÷ Rs (double, 8 bytes) |
| 0x0721 | FSQRT8 Rd | Rd = √Rd (double, 8 bytes) |
| 0x0724 | FSIN8 Rd | Rd = sin(Rd) (double, 8 bytes) |
| 0x0725 | FCOS8 Rd | Rd = cos(Rd) (double, 8 bytes) |

### Operaciones de Pila (Stack)

#### Control de Subrutinas
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0800 | RET | Retorna de subrutina (pop dirección de retorno) |

#### Operaciones de Pila por Tamaño
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0810 | POP1 Rd | Rd = Stack[SP-1] (pop 1 byte) |
| 0x0811 | POP2 Rd | Rd = Stack[SP-2] (pop 2 bytes) |
| 0x0812 | POP4 Rd | Rd = Stack[SP-4] (pop 4 bytes) |
| 0x0813 | POP8 Rd | Rd = Stack[SP-8] (pop 8 bytes) |
| 0x0820 | PUSH1 Rd | Stack[SP] = Rd (push 1 byte) |
| 0x0821 | PUSH2 Rd | Stack[SP] = Rd (push 2 bytes) |
| 0x0822 | PUSH4 Rd | Stack[SP] = Rd (push 4 bytes) |
| 0x0823 | PUSH8 Rd | Stack[SP] = Rd (push 8 bytes) |