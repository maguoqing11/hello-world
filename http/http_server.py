'''
http server v2.0
io 并发处理
基本的request解析
使用类封装
'''
from socket import *
from select import select

# 将具体HTTP server功能封装
class HTTPserver:
    def __init__(self,server_addr,static_dir):
        self.server_addr = server_addr
        self.static_dir = static_dir
        self.create_socket()
        self.bind()
        self.rlist = []
        self.wlist = []
        self.xlist = []

    #创建套接字
    def create_socket(self):
        self.sockfd =socket()
        self.sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    def bind(self):
        self.sockfd.bind(self.server_addr)
        self.ip = self.server_addr[0]
        self.port = self.server_addr[1]

    def handle(self,connfd):
        request = connfd.recv(4096)
        print(request)
        if not request:
            self.rlist.remove(connfd)
            connfd.close()
            return

        #请求解析
        request_line = request.splitlines()[0]
        info = request_line.decode().split(' ')[1]
        print(connfd.getpeername(),':',info)

        if info == '/' or info[-5:] == '.html':
            self.get_html(connfd,info)
        else:
            self.get_data(connfd, info)
        self.rlist.remove(connfd)
        connfd.close()

    def get_data(self,connfd,info):
        responseHeaders = 'HTTP/1.1 200 Ok\r\n'
        responseHeaders = '\r\n'
        responseBody = '<h1>Waiting httpser 3.0<>h1\r\n'
        response = responseHeaders + responseBody
        connfd.send(response.encode())

    #处理网页
    def get_html(self,connfd,info):
        if info == '/':
            filename = self.static_dir + '/index.html'
        else:
            filename = self.static_dir + info
        try:
            fd = open(filename)
        except Exception:
            responseHeaders = 'HTTP/1.1 404 Not Found\r\n'
            responseHeaders += '\r\n'
            responseBody = '<h1>Sorry,Not Found the Page<h1>\r\n'
        else:
            responseHeaders = 'HTTP/1.1 200 Ok\r\n'
            responseHeaders += '\r\n'
            responseBody = fd.read()
        finally:
            response = responseHeaders + responseBody
            connfd.send(response.encode())


    def serve_forever(self):
        self.sockfd.listen(5)
        print('listen the port %d'%self.port)
        self.rlist.append(self.sockfd)

        while True:
            rs,ws,xs = select(self.rlist,self.wlist,self.xlist)
            for r in rs:
                if r is self.sockfd:
                    connfd,addr = r.accept()
                    print('connet from:',addr)
                    self.rlist.append(connfd)
                else:
                    #处理客户端请求
                    self.handle(r)

#如何使用http server 类
if __name__ == '__main__':
    #用户地址，用户内容
    server_addr = ('0.0.0.0',11111)
    static_dir = './static_dir'#网页存放地址
    httpd = HTTPserver(server_addr,static_dir)#生成对象
    httpd.serve_forever()#启动服务