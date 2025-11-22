# Definicion de formato
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

Ocupa dos palabras

```
 63    48 47  44 43             0
┌────────┬─────┬─────────────────┐
│ OPCODE │ RD  │                 │
│16 bits │4bits│                 │
└────────┴─────┴─────────────────┘
 ┌──────────────────────────────┐
     INMEDIATO 64 bits
 └──────────────────────────────┘
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

# Tabla de instrucciones

Listado de los opcodes, su mnemónico y formato.

| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
|     `0x0000` | PARAR     |    OP   | Detiene la CPU    |
|     `0x0001` | NOP       |    OP   | No hace nada      |
| `0x0010` | ADD | RR | Suma (8 bytes) |
| `0x0011` | SUB | RR | Resta (8 bytes) |
| `0x0012` | MULS | RR | Multiplicación (signed, 8 bytes) |
| `0x0013` | MUL | RR | Multiplicación (unsigned, 8 bytes) |
| `0x0014` | DIV | RR | División (8 bytes) |
| `0x0020` | ADDV | RI | Suma con inmediato (8 bytes) |
| `0x0021` | SUBV | RI | Resta con inmediato (8 bytes) |
| `0x0030` | INC | R | Incrementar registro |
| `0x0031` | DEC | R | Decrementar registro |
| `0x0064` | CLR | R | Poner registro a cero |
| `0x0040` | NOT | R | Negación bit a bit |
| `0x0041` | AND | RR | AND registro, registro |
| `0x0042` | ANDV | RI | AND con inmediato |
| `0x0043` | OR | RR | OR registro, registro |
| `0x0044` | ORV | RI | OR con inmediato |
| `0x0045` | XOR | RR | XOR registro, registro |
| `0x0046` | XORV | RI | XOR con inmediato |
| `0x0050` | SHI | R | Shift left (usar RD como fuente) |
| `0x0051` | SHD | R | Shift right aritmético (signed) |
| `0x0052` | USHI | R | Shift left (unsigned) |
| `0x0053` | USHD | R | Shift right lógico (unsigned) |
| `0x0060` | LOAD | RI | LOAD R, M (desde dirección inmediata) |
| `0x0061` | LOADV | RI | Cargar valor inmediato en R |
| `0x0062` | LOADR | RR | LOAD R, [R'] (dirección en registro) |
| `0x0063` | STOREV | RI | STORE M, R (dirección inmediata) |
| `0x0070` | CMP | RR | Comparar R, R' (8 bytes) |
| `0x0071` | CMPV | RI | Comparar R, inmediato (8 bytes) |
| `0x0080` | CLR.Z | OP | Flags: Z = 0 |
| `0x0081` | SET.Z | OP | Flags: Z = 1 |
| `0x0082` | CLR.N | OP | Flags: N = 0 |
| `0x0083` | SET.N | OP | Flags: N = 1 |
| `0x0084` | CLR.C | OP | Flags: C = 0 |
| `0x0085` | SET.C | OP | Flags: C = 1 |
| `0x0086` | CLR.V | OP | Flags: V = 0 |
| `0x0087` | SET.V | OP | Flags: V = 1 |
| `0x0090` | JMP | RI | Jump (incondicional) — formato I/RI (inmediato = destino) |
| `0x0091` | JEQ | RI | Jump if Z == 1 |
| `0x0092` | JNE | RI | Jump if Z == 0 |
| `0x0093` | JN | RI | Jump if N == 1 |
| `0x0094` | JNN | RI | Jump if N == 0 |
| `0x0095` | JC | RI | Jump if C == 1 |
| `0x0096` | JNC | RI | Jump if C == 0 |
| `0x0097` | JLT | RI | Jump if (V ^ N) == 1 (signed less) |
| `0x0098` | JGE | RI | Jump if (V ^ N) == 0 (signed >=) |
| `0x0099` | CALL | RI | Llamada a subrutina (push return addr, pc = imm) |
| `0x00A0` | SVIO | RI | Escribir a IO: IO[imm] = R(rd) (escribe 1 byte desde R) |
| `0x00A1` | LOADIO | RI | Leer desde IO → R(rd) |
| `0x00A2` | SHOWIO | RI | (usado en tests) Mostrar IO / efecto dependiente del IOSystem |
| `0x00A3` | ? | OP | Reserva / no usada en `execute()` (según mapa) |
| `0x00A4` | ? | OP | Reserva / no usada en `execute()` (según mapa) |
---

## Instrucciones con sufijo de tamaño (1 byte)
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0100` | ADD1 | RR |
| `0x0101` | SUB1 | RR |
| `0x0102` | MUL1 | RR |
| `0x0103` | MULS1 | RR |
| `0x0104` | DIV1 | RR |
| `0x0110` | ADDV1 | RI |
| `0x0111` | SUBV1 | RI |

## Instrucciones con sufijo de tamaño (2 bytes)
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0200` | ADD2 | RR |
| `0x0201` | SUB2 | RR |
| `0x0202` | MUL2 | RR |
| `0x0203` | MULS2 | RR |
| `0x0204` | DIV2 | RR |
| `0x0210` | ADDV2 | RI |
| `0x0211` | SUBV2 | RI |

## Instrucciones con sufijo de tamaño (4 bytes)
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0300` | ADD4 | RR |
| `0x0301` | SUB4 | RR |
| `0x0302` | MUL4 | RR |
| `0x0303` | MULS4 | RR |
| `0x0304` | DIV4 | RR |
| `0x0310` | ADDV4 | RI |
| `0x0311` | SUBV4 | RI |

## Instrucciones con sufijo de tamaño (8 bytes)
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0312` | ADD8 | RR |
| `0x0313` | SUB8 | RR |
| `0x0314` | MUL8 | RR |
| `0x0315` | MULS8 | RR |
| `0x0316` | DIV8 | RR |
| `0x0317` | ADDV8 | RI |
| `0x0318` | SUBV8 | RI |

---

## MOV / MOVV
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0400` | MOV1 | RR |
| `0x0401` | MOV2 | RR |
| `0x0402` | MOV4 | RR |
| `0x0403` | MOV8 | RR |
| `0x0410` | MOVV1 | RI |
| `0x0411` | MOVV2 | RI |
| `0x0412` | MOVV4 | RI |
| `0x0413` | MOVV8 | RI |

## LOAD / LOADR
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0500` | LOAD1 | RI |
| `0x0501` | LOAD2 | RI |
| `0x0502` | LOAD4 | RI |
| `0x0503` | LOAD8 | RI |
| `0x0510` | LOADR1 | RR |
| `0x0511` | LOADR2 | RR |
| `0x0512` | LOADR4 | RR |
| `0x0513` | LOADR8 | RR |

## STORE / STORER
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0600` | STORE1 | RI |
| `0x0601` | STORE2 | RI |
| `0x0602` | STORE4 | RI |
| `0x0603` | STORE8 | RI |
| `0x0610` | STORER1 | RR |
| `0x0611` | STORER2 | RR |
| `0x0612` | STORER4 | RR |
| `0x0613` | STORER8 | RR |

---

## FPU
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0700` | FADD4 | RR |
| `0x0701` | FSUB4 | RR |
| `0x0702` | FMUL4 | RR |
| `0x0703` | FDIV4 | RR |
| `0x0710` | FADD8 | RR |
| `0x0711` | FSUB8 | RR |
| `0x0712` | FMUL8 | RR |
| `0x0713` | FDIV8 | RR |
| `0x0720` | FSQRT4 | R |
| `0x0721` | FSQRT8 | R |
| `0x0722` | FSIN4 | R |
| `0x0723` | FCOS4 | R |
| `0x0724` | FSIN8 | R |
| `0x0725` | FCOS8 | R |
| `0x0726` | INTFLOAT4 | R |
| `0x0727` | INTFLOAT8 | R |

---

## Stack / PUSH / POP
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0800` | RET | OP |
| `0x0810` | POP1 | R |
| `0x0811` | POP2 | R |
| `0x0812` | POP4 | R |
| `0x0813` | POP8 | R |
| `0x0820` | PUSH1 | R |
| `0x0821` | PUSH2 | R |
| `0x0822` | PUSH4 | R |
| `0x0823` | PUSH8 | R |

## CMP size-specific
| Hex (16-bit) | Mnemónico | Formato | Descripción breve |
| -----------: | :-------- | :-----: | :---------------- |
| `0x0830` | CMP1 | RR |
| `0x0831` | CMP2 | RR |
| `0x0832` | CMP4 | RR |
| `0x0833` | CMP8 | RR |
| `0x0840` | CMPV1 | RI |
| `0x0841` | CMPV2 | RI |
| `0x0842` | CMPV4 | RI |
| `0x0843` | CMPV8 | RI |