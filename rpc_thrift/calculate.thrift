include 'base.thrift'

service Calculate extends base.BasicService{
    i32 calculate(1:base.Work w) throws (1: base.InvalidOperation e)
}