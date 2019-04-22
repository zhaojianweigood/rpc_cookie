# -*- coding: utf-8 -*-
import sys
from thrift.protocol import TCompactProtocol
from thrift.transport import TSocket, TTransport

sys.path.append('gen-py')

from calculate import Calculate
from base.ttypes import InvalidOperation, Work, Opertation


def main():
    # 传输层
    transport = TSocket.TSocket('127.0.0.1', 8888)
    transport = TTransport.TBufferedTransport(transport)

    # 消息协议
    protocal = TCompactProtocol.TCompactProtocol(transport)

    client = Calculate.Client(protocal)

    # 进行具体调用
    # 打开
    transport.open()
    client.ping()
    print('调用了ping')
    result = client.divide(100, 50)
    print('100/50= {}'.format(result))
    try:
        result = client.divide(100, 0)
    except InvalidOperation as e:
        print(e.why, '-',  e.whatOp)

    work = Work(num1=100, num2=20, op=Opertation.SUBTRACT)
    result = client.calculate(work)
    print('100-20={}'.format(result))

    # 关闭
    transport.close()

if __name__ == '__main__':
    main()
