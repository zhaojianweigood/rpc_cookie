## 安装， 简单只需要安装依赖包即可
```
pip install grpcio-tools
```
## 生成接口定义文件
> -I 搜索proto文件中被导入文件的目录，指定include寻找目录， 即使没有include也要指明
> --python_out 定义的数据类型文件 生成目录
> --grpc_python_out 定义的服务文件  生成目录
```
python -m grpc_tools.protoc -I. --python_out=.. --grpc_python_out=.. base.proto

```
###服务模式为
> 非流式
> 客户端流式
> 服务端流式
> 客户端和服务端皆流式