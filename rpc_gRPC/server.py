import time
from concurrent import futures

import grpc

from rpc_gRPC import base_pb2_grpc
from rpc_gRPC import base_pb2


# 实现被调用的方法的具体代码
class DemoService(base_pb2_grpc.DemoServicer):

    def __init__(self):
        self.city_subject_db = {
            'beijing': ['烤鸭', '糖葫芦', '糕点', '圆明园', '长城'],
            'shanghai': ['明珠', '浦东', '上海交大', '中山大学'],
            'tianjin': ['麻花', '传销', '摩天轮', '世纪钟'],
        }
        self.answers = [x for x in range(30)]

    def Calculate(self, request, context):
        if request.op == base_pb2.Work.ADD:
            result = request.num1 + request.num2
            return base_pb2.Result(val=result)
        elif request.op == base_pb2.Work.SUBTRACT:
            result = request.num1 - request.num2
            return base_pb2.Result(val=result)
        elif request.op == base_pb2.Work.MULTIPLY:
            result = request.num1 * request.num2
            return base_pb2.Result(val=result)
        elif request.op == base_pb2.Work.DIVIDE:
            if request.num2 == 0:
                # 设置响应状态码和描述字符， 返回异常
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('cannot divide by 0')
                return base_pb2.Result
            else:
                result = request.num1 // request.num2
                return base_pb2.Result(val=result)
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('invalid operation')
            return base_pb2.Result()

    def GetSubjects(self, request, context):
        city = request.name
        subject = self.city_subject_db.get(city)
        for ret in subject:
            yield base_pb2.Subject(name=ret)

    def Accumulate(self, request_iterator, context):
        sum = 0
        for request in request_iterator:
            sum += request.val
        return base_pb2.Sum(val=sum)

    def GuessNumber(self, request_iterator, context):
        for request in request_iterator:
            if request.val in self.answers:
                yield base_pb2.Answer(val=request.val, desc='猜对了')
            else:
                yield base_pb2.Answer(val=request.val, desc='猜错了')


# 开启服务器
def service():
    # 创建服务器对象
    service = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 注册实现服务方法到服务器
    base_pb2_grpc.add_DemoServicer_to_server(DemoService(), service)
    # 为服务器设置地址
    service.add_insecure_port('127.0.0.1:8888')
    # 开启服务器
    print('服务器开启')
    service.start()
    # 关闭服务器
    try:
        time.sleep(1000)
    except KeyboardInterrupt:
        service.stop(0)


if __name__ == '__main__':
    service()
