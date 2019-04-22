# -*- coding: utf-8 -*-

import sys

from thrift.protocol import TCompactProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

sys.path.append('gen-py')

from calculate import Calculate
from base.ttypes import InvalidOperation, Opertation


class CalculateHandler(Calculate.Iface):
    def ping(self):
        print('ping')

    def divide(self, num1, num2):
        if num2 == 0:
            raise InvalidOperation(num2, 'cannot divide by 0')

        return num1 / num2

    def calculate(self, w):
        if w.op == Opertation.ADD:
            return w.num1 + w.num2
        elif w.op == Opertation.SUBTRACT:
            return w.num1 - w.num2
        elif w.op == Opertation.MULTIPLY:
            return w.num1 * w.num2
        else:
            raise InvalidOperation(w.op, 'Invalid operation')


if __name__ == '__main__':

    # 调用处理工具
    handler = CalculateHandler()
    processor = Calculate.Processor(handler)

    # 构建传输工具
    transport = TSocket.TServerSocket('127.0.0.1', 8888)
    tfactory = TTransport.TBufferedTransportFactory()

    # 消息协议工具-选用的密集高效率的二进制编码
    pfactory = TCompactProtocol.TCompactProtocolFactory()

    # 构建服务器对象
    server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)

    # 开启服务器
    print('服务器开启')
    server.serve()
