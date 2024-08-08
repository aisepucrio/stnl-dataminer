import socket

def check_internet_connection(timeout=5):
    try:
        # Tenta se conectar ao servidor DNS do Google
        socket.setdefaulttimeout(timeout)
        host = socket.gethostbyname("8.8.8.8")  # Endereço IP do servidor DNS do Google
        s = socket.create_connection((host, 53), timeout)
        s.close()
        return True
    except OSError:
        return False

# Exemplo de uso
if check_internet_connection():
    print("Conectado à internet")
else:
    print("Sem conexão com a internet")
