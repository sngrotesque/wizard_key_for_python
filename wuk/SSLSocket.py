import socket
import ssl

class BaseSSLSocket:
    def __init__(self,
                family    :int = socket.AF_INET,
                sock_type :int = socket.SOCK_STREAM,
                proto     :int = socket.IPPROTO_TCP,
                cert_path :str = 'server.crt',
                key_path  :str = 'server.key'
                ):
        self.family   = family
        self.type     = sock_type
        self.proto    = proto
        self.certPath = cert_path
        self.keyPath  = key_path
    
    def init_ssl(self):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ssl_ctx.load_cert_chain(certfile = self.certPath, keyfile = self.keyPath)
        return ssl_ctx

# openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key
class SSLSocketServer(BaseSSLSocket):
    def __init__(self,
                laddr :str, lport :int,
                family    :int = socket.AF_INET,
                sock_type :int = socket.SOCK_STREAM,
                proto     :int = socket.IPPROTO_TCP,
                cert_path :str = 'server.crt',
                key_path  :str = 'server.key'
                ):
        super().__init__(family   = family,
                        sock_type = sock_type,
                        proto     = proto,
                        cert_path = cert_path,
                        key_path  = key_path)

        self.laddr = laddr
        self.lport = lport

        self.fd      :socket.socket  = None
        self.ssl_ctx :ssl.SSLContext = None

    def init(self, backlog :int = 5):
        self.fd = socket.socket(self.family, self.type, self.proto)
        self.fd.bind((self.laddr, self.lport))
        self.fd.listen(backlog)

        self.ssl_ctx = self.init_ssl()

    def accept(self):
        client_fd, client_addrinfo = self.fd.accept()
        # 不需要特地对client_fd做任何操作，因为它已经关闭
        ssl_fd = self.ssl_ctx.wrap_socket(client_fd, server_side = True)
        return ssl_fd, client_addrinfo

    def handler(self, backlog :int = 5):
        self.init(backlog)

        ssl_fd, caddr = self.accept()

        print(f'client connected: {caddr}')

        ssl_fd.send(b'hello!\n')

        ssl_fd.close()


