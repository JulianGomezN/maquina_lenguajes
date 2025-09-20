# Simulador de Computador – Arquitectura y Codificación

## Resumen de decisiones de diseño

- **Tamaño de palabra:** 64 bits  
- **Direccionamiento:** por byte  
- **Bus de direcciones:** 44 bits (compatible con las instrucciones que reservan 44 bits para direcciones/inmediatos)  
- **Endianess:** Little-endian  
- **Registros generales:** R01 … R15 (codificación de 4 bits)  
- **Flags:** Z (zero), N (negative), C (carry), V (overflow)  
- **Instrucciones y datos:** ocupan una palabra de 64 bits (fetch en 8 bytes)  

---

## Formatos de instrucción (64 bits)

Para simplificar la implementación, se definen cinco formatos fijos de 64 bits:

### Formato RR (registro–registro)

Usado en operaciones tipo `ADD R, R'`, `AND R, R'`.

Bits 63..48 : OPCODE (16 bits)
Bits 47..4 : Reservado (44 bits)
Bits 7..4 : RD (registro destino)
Bits 3..0 : RS (registro fuente)

---

### Formato RI (registro–inmediato, 44 bits)

Usado en `ADDV R, v`, `JMP k`, `LOAD R, M`.

Bits 63..48 : OPCODE (16 bits)
Bits 47..44 : RD (4 bits)
Bits 43..0 : Inmediato / Dirección (44 bits)

---

### Formato R (registro único)

Usado en `INC R`, `DEC R`, `CLR R`.

Bits 63..48 : OPCODE (16 bits)
Bits 47..44 : RD (4 bits)
Bits 43..0 : Reservado / 0 (44 bits)

---

### Formato OP (solo opcode)  

Usado en `PARAR`, `NOP`.

Bits 63..48 : OPCODE (16 bits)
Bits 47..0 : 0

---

### Formato LARGEIMM (reservado)

Pensado para futuros inmediatos mayores, no se usa inicialmente.

---

## Tabla de opcodes (16 bits, propuesta)

### Control

| Opcode | Instrucción |
|--------|-------------|
| 0x0000 | PARAR |
| 0x0001 | NOP |

### Aritmética (RR)

| Opcode | Instrucción |
|--------|-------------|
| 0x0010 | ADD R, R' |
| 0x0011 | SUB R, R' |
| 0x0012 | MULS R, R' (signed) |
| 0x0013 | MUL R, R' (unsigned) |
| 0x0014 | DIV R, R' |

### Aritmética (RI)

| Opcode | Instrucción |
|--------|-------------|
| 0x0020 | ADDV R, v |
| 0x0021 | SUBV R, v |

### Increment/Decrement (R)

| Opcode | Instrucción |
|--------|-------------|
| 0x0030 | INC R |
| 0x0031 | DEC R |

### Lógicas

| Opcode | Instrucción |
|--------|-------------|
| 0x0040 | NOT R |
| 0x0041 | AND R, R' |
| 0x0042 | ANDV R, v |
| 0x0043 | OR R, R' |
| 0x0044 | ORV R, v |
| 0x0045 | XOR R, R' |
| 0x0046 | XORV R, v |

### Shifts

| Opcode | Instrucción |
|--------|-------------|
| 0x0050 | SHI R (signed left) |
| 0x0051 | SHD R (signed right) |
| 0x0052 | USHI R (unsigned left) |
| 0x0053 | USHD R (unsigned right) |

### Memoria / Load / Store

| Opcode | Instrucción |
|--------|-------------|
| 0x0060 | LOAD R, M |
| 0x0061 | LOADV R, v |
| 0x0062 | LOADR R, R' |
| 0x0063 | SV M, R |
| 0x0064 | CLR R |

### Comparación y flags

| Opcode | Instrucción |
|--------|-------------|
| 0x0070 | CMP R, R' |
| 0x0071 | CMPV R, v |

### Manipulación de flags

| Opcode | Instrucción |
|--------|-------------|
| 0x0080 | CZF (clear Z) |
| 0x0081 | SZF (set Z) |
| 0x0082 | CNF (clear N) |
| 0x0083 | SNF (set N) |
| 0x0084 | CCF (clear C) |
| 0x0085 | SCF (set C) |
| 0x0086 | CDF (clear V) |
| 0x0087 | SDF (set V) |

### Saltos (RI)

| Opcode | Instrucción |
|--------|-------------|
| 0x0090 | JMP k |
| 0x0091 | JMPC k (si Z == 1) |
| 0x0092 | JMPNC k (si Z == 0) |
| 0x0093 | JMPNEG k (si N == 1) |
| 0x0094 | JMPPOS k (si N == 0) |
| 0x0095 | JMPCMY k (si C == 1) |
| 0x0096 | JMPCMN k (si C == 0) |
| 0x0097 | JMPOMY k (overflow xor negative) |
| 0x0098 | JMPOMN k (negación) |

### I/O (Memory-Mapped)

| Opcode | Instrucción |
|--------|-------------|
| 0x00A0 | SVIO M, R |
| 0x00A1 | LOADIO R, M |
| 0x00A2 | SHOWIO M |
| 0x00A3 | CLRIIO |
| 0x00A4 | CLROIO |

---

## Reglas de codificación y ejemplos

### Ejemplo RI – `LOAD R05, 0x0000ABCD1234`

- OPCODE = `0x0060`  
- RD = `0x04` (R05)  
- Dirección = `0x0000ABCD1234`  

Codificación (64 bits):  

Bits 63..48 = `0x0060`
Bits 47..44 = `0x4`
Bits 43..0 = `0x0000ABCD1234`

En código:

```c
instr = (0x0060 << 48) | (0x4 << 44) | 0x0000ABCD1234;
```

Ejemplo RR – `ADD R02, R03`

OPCODE = 0x0010

RD = `0x01` (R02)

RS = `0x02` (R03)

Codificación:

```c
instr = (0x0010 << 48) | (0x1 << 44) | (0x2);
```

Ejemplo OP – `PARAR`

OPCODE = 0x0000

Instrucción = opcode en los 16 bits más altos, resto en cero.