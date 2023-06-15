import socket
import os
import mimetypes

#Configurações
SERVER_ADRESS = "192.168.2.103"
SERVER_PORT = 30000
HEADER_HTTP_200 = 'HTTP/1.1 200 OK\r\nContent-Type: ; charset: utf-8\r\n\r\n'
HEADER_HTTP_404 = 'HTTP/1.1 404 \r\nContent-Type: ; charset: utf-8\r\n\r\n'
HEADER_HTTP_200_DOWNLOAD = 'HTTP/1.1 200 OK\r\nContent-Disposition: attachment;'
BASE_PATH = r"C:\Users\gusta\Codes\Server\Arquivos/"
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def list_files(directory):
    try:
        files = os.listdir(directory)
        links = []
        for file in files:
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                link = f'<a href="{file}">{file}</a>'
                links.append(link)
            elif os.path.isdir(file_path):
                link = f'<a href="{file}/">{file}/</a>'
                links.append(link)
        return "<br>".join(links)
    except:
        return False
    
def getPath(message):
    path = str(message[message.find('GET /')+5:message.find(' HTTP/1.1')])

    if path[-1:] == '/':
        path = path[:-1]
    #print("O caminho é: '" + path +"'")
    
    return path

def getFileName(path): 
    paths = path.split("/")
    file_name = ''.join(paths[-1:])
    return file_name

def handleClient(client_socket, client_adress):
    print("[NOVA CONEXÃO]", client_adress, "Conectado")
    request = client_socket.recv(1024).decode()
    path = getPath(request)
    #print("Caminho: "+ BASE_PATH + path)

    # Se for /HEADER deve responder com o cabeçalho HTTP
    if path == "HEADER":
        content = "<br>" + request            
        #print (content)
        response = HEADER_HTTP_200 + content
        client_socket.send(response.encode('utf-8'))        
    
    # Se for diretório
    elif os.path.isdir(BASE_PATH + path):             
        content = list_files(BASE_PATH + path)                
        
        if content == False:
            response = HEADER_HTTP_404 + '<br> O recurso pedido não existe!'
            client_socket.send(response.encode('utf-8'))
        else:        
            response = HEADER_HTTP_200 + content
            client_socket.send(response.encode('utf-8'))           
    
    # Se for arquivo
    else: 
        if os.path.isfile(BASE_PATH + path) == False:
            response = HEADER_HTTP_404 + '<br> O recurso pedido não existe!'
            client_socket.send(response.encode('utf-8'))
        else:    
            try:
                with open(BASE_PATH + path, 'rb') as file:                
                    content = file.read()
            except:            
                response = HEADER_HTTP_404 + '<br> Erro ao abrir o arquivo.'
                client_socket.send(response)

            content_type, _ = mimetypes.guess_type(BASE_PATH + path)
            
            if content_type is None:
                content_type = 'application/octet-stream'  # Tipo de conteúdo desconhecido
            
            file_name = getFileName(path)                    
            content_lenght = format(len(content))
            response_headers = HEADER_HTTP_200_DOWNLOAD + f' filename="{file_name}"\nContent-Length: {content_lenght}\n'
            response = response_headers.encode('utf-8') + b'\n' + content
            
            client_socket.send(response)
        
    client_socket.close()
    print("[ENCERRANDO A CONEXÃO] Conexão encerrada!")

def start():
    server_socket.bind((SERVER_ADRESS, SERVER_PORT))
    server_socket.listen()

    print("[OUVINDO] Servidor está ouvindo em ", SERVER_ADRESS, ':', SERVER_PORT)

    while True:
        client_socket, client_adress = server_socket.accept()        
        handleClient(client_socket, client_adress)       

print("[INICIANDO] O servidor está iniciando")
start()
