const i32 INTCONSTANT = 1234
const map<string, string> MAPCONSTANT = {'hello': 'thrift', 'idcast': 'python'}

enum Opertation {
    ADD,
    SUBTRACT,
    MULTIPLY,
}


struct Work{
    1: i32 num1=0
    2: i32 num2,
    3: Opertation op,
    4: optional string comment,
}

exception InvalidOperation{
    1: i32 whatOp,
    2: string why,
}

service BasicService{
    double divide(1:i32 num1, 2:i32 num2) throws (1:InvalidOperation e)
    oneway void ping()
}