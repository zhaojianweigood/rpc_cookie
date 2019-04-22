import random

import grpc

from rpc_gRPC import base_pb2_grpc
from rpc_gRPC import base_pb2


def invoke_calculate(stub):
    """非流式"""
    work = base_pb2.Work()
    work.num1 = 100
    work.num2 = 20
    # 加
    work.op = base_pb2.Work.ADD
    result = stub.Calculate(work)
    print('100+20={}'.format(result.val))
    # 减
    work.op = base_pb2.Work.SUBTRACT
    result = stub.Calculate(work)
    print('100-20={}'.format(result.val))
    # 乘法
    work.op = base_pb2.Work.MULTIPLY
    result = stub.Calculate(work)
    print('100*20={}'.format(result.val))
    # 除法
    work.op = base_pb2.Work.DIVIDE
    result = stub.Calculate(work)
    print('100//20={}'.format(result.val))

    # 除数为0
    work.num2 = 0
    try:
        result = stub.Calculate(work)
        print('100//20={}'.format(result.val))
    except grpc.RpcError as e:
        print('code:{}, des{}'.format(e.code(), e.details()))

    print('-' * 30 + '以上为非流式测试' + '—' * 30)


def invoke_get_subject(stub):
    """客户端流式"""
    city = base_pb2.City(name='beijing')
    subjects = stub.GetSubjects(city)

    for index, subject in enumerate(subjects):
        print('第{}个:{}'.format(index+1, subject.name))
    print('-' * 30 + '以上为客户端流式测试' + '—' * 30)


def invoke_accumulate(stub):
    def delta_iterator():
        """迭代器"""
        for _ in range(3):
            num = random.randint(10, 100)
            print('发送num:{}'.format(num))
            yield base_pb2.Delta(val=num)

    sum = stub.Accumulate(delta_iterator())
    print('和为{}'.format(sum.val))
    print('-' * 30 + '以上为服务端流式测试' + '—' * 30)


def invoke_guess_number(stub):
    def delta_iterator():
        """迭代器"""
        for _ in range(5):
            num = random.randint(10, 100)
            print('发送num:{}'.format(num))
            yield base_pb2.Number(val=num)
    answers = stub.GuessNumber(delta_iterator())
    for answer in answers:
        print('{}:{}'.format(answer.val, answer.desc))
    print('-' * 30 + '以上为服务端和客户端皆流式测试' + '—' * 30)


def run():
    with grpc.insecure_channel('127.0.0.1:8888') as channel:
        # 创建客户端对象
        stub = base_pb2_grpc.DemoStub(channel)
        invoke_calculate(stub)
        invoke_get_subject(stub)
        invoke_accumulate(stub)
        invoke_guess_number(stub)


if __name__ == '__main__':
    run()
