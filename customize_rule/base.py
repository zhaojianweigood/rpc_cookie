import struct
import socket

from io import BytesIO


class DivException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'error: {}'.format(self.message)


class MethodProtocol(object):
    def __init__(self, connection):
        self.conn = connection

    def read_all(self, size):

        if isinstance(self.conn, BytesIO):
            buff = self.conn.read(size)
            return buff
        else:
            have = 0
            buff = b''
            while have < size:
                chunk = self.conn.recv(size - have)
                buff += chunk
                l = len(chunk)
                have += l
                if l == 0:
                    raise EOFError()
            return buff

    def get_method_name(self):
        method = self.read_all(4)
        len_ = struct.unpack('!I', method)[0]
        method_name = self.read_all(len_)
        return method_name.decode()


class Division(object):
    """结构为四个字节函数名， 函数名，参数总长度，
    1个字节， 参数1， 1  个字节参数2"""


    def encode_args(self, num1, num2):
        """编码传入参数"""
        func_name = 'division'
        buff = struct.pack('!I', len(func_name))
        buff += func_name.encode()

        buff_2 = struct.pack('!B', 4)
        buff_2 += struct.pack('!i', num1)
        if num2 != 2:
            buff_2 += struct.pack('!B', 4)
            buff_2 += struct.pack('!i', num2)

        buff += struct.pack('!I', len(buff_2))
        buff += buff_2
        return buff

    def read_all(self, size):
        """读取解析"""
        if isinstance(self.conn, BytesIO):
            buff = self.conn.read(size)
            return buff
        else:
            have = 0
            buff = b''
            while have < size:
                chunk = self.conn.recv(size - have)
                buff += chunk
                l = len(chunk)
                have += l
                if l == 0:
                    raise EOFError()
            return buff

    def decode_args(self, connection):
        """解码参数"""
        # 文件名不在这读取
        self.conn = connection
        all_len = self.read_all(4)
        all_len = struct.unpack('!I', all_len)[0]
        one_params_len = self.read_all(1)
        one_params_len = struct.unpack('!B', one_params_len)[0]
        one_params = self.read_all(one_params_len)
        one_params = struct.unpack('!i', one_params)[0]

        if (1 + one_params_len) >= all_len:
            return {
                'num1': one_params
            }
        two_params_len = self.read_all(1)
        two_params_len = struct.unpack('!B', two_params_len)[0]
        two_params = self.read_all(two_params_len)
        two_params = struct.unpack('!i', two_params)[0]
        return {
            'num1': one_params,
            'num2': two_params,
        }

    def encode_result(self, result):
        """编码结果， 结果1， 1个字节标识，加4个字节浮点数
            结果2， 1个字节标识， 4个字节字符串长度 ， 字符串错误原因"""
        if isinstance(result, float):
            buff = struct.pack('!B', 1)
            buff += struct.pack('!f', result)
            return buff
        else:
            buff = struct.pack('!B', 2)

            buff += struct.pack('!I', len(result))
            buff += result.encode()
            return buff

    def decode_result(self, connection):
        """解码结果"""
        self.conn = connection
        head_ = self.read_all(1)
        head_ = struct.unpack('!B', head_)[0]
        if head_ == 1:
            number = self.read_all(4)

            return '%.2f' % struct.unpack('!f', number)[0]
        else:
            one_params = self.read_all(4)
            one_len = struct.unpack('!I', one_params)[0]
            return self.read_all(one_len).decode()


class ClientServer(object):
    """客户端的服务器"""
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def client(self):
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect((self.host, self.port))
        return sk


class ServiceServer(object):
    """服务端的服务器"""
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def server(self):
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sk.bind((self.host, self.port))
        return sk


class Server(object):
    """封装的服务端运行，可以把服务器初始化， 方法解析类，放在init里面
    另外，对于结果的处理可以使用map状态积或者类方法调用，这里只是单纯的实现功能"""
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port

    def sever(self):
        conn = ServiceServer(self.host, self.port)
        self.conn = conn.server()
        self.conn.listen(100)
        print('开启监听')
        while True:
            sub_server, sub_dirr = self.conn.accept()
            print('建立链接')
            try:
                while True:
                    method_proto = MethodProtocol(sub_server)
                    name = method_proto.get_method_name()
                    division = Division()
                    args = division.decode_args(sub_server)
                    # 此处应该调用外部处理函数， 这里内部实现了
                    num1 = args.get('num1')
                    num2 = args.get('num2')
                    if num2 is not None and int(num2) == 0:
                        err = DivException('error_1')
                        buff = division.encode_result(err.message)
                        sub_server.sendall(buff)
                    else:
                        if not num2:
                            num2 = 2
                        float = int(num1) / int(num2)
                        buff = division.encode_result(float)
                        sub_server.sendall(buff)

            except EOFError:
                print('链接结束')


class Client(object):
    """封装的客户端运行，可以把客户端链接放在init里面保持长连接"""
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port

    def client(self, num1, num2=2):
        division = Division()
        buff = division.encode_args(num1, num2)
        conn = ClientServer(self.host, self.port)
        self.conn = conn.client()
        self.conn.sendall(buff)
        try:
            result = division.decode_result(self.conn)
        except DivException as e:
            result = e.message
        else:
            result = result

        return result


if __name__ == '__main__':
    # 构造数据
    division = Division()
    # buff_ = division.encode_args(100, 4)
    buff_ = division.encode_result(22.0)
    conn = BytesIO()
    conn.write(buff_)
    # 指针回到最初
    conn.seek(0)

    # 解析数据
    # method_proto = MethodProtocol(conn)
    # name = method_proto.get_method_name()
    # print(name, "##")

    # args = division.decode_args(conn)
    args = division.decode_result(conn)
    print(args)
