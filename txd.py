def txd(memory):
    pc = memory.get_pc()
    instr = memory.get_instr(pc)
    new_pc = memory.get_pc()
    data = memory.memory[pc:new_pc]
    data = ', '.join(['{0:02x}'.format(byte) for byte in data])

    # operands
    operands = instr.operands
    types = instr.types
    op_types = instr.op_types
    for j in range(len(operands)):
        op = memory.get_num(operands[j])
        typ = types[j]
        opt = op_types[j]
        if opt in ["s", "t"]:
            op = memory.get_num(op, signed=True)
        if typ == 2 or opt == "var":
            if op == 0:
                operands[j] = "SP"
            elif op in range(1, 16):
                operands[j] = "L" + str('{0:02x}'.format(op - 1))
            elif op in range(16, 256):
                operands[j] = "G" + str('{0:02x}'.format(op - 16))
        elif instr.name in ["jump"]:
            address = new_pc + op - 2
            operands[j] = str('{0:02x}'.format(address))
        elif opt == "baddr":
            op = memory.get_byte_address(op)
            operands[j] = str('{0:02x}'.format(op))
        elif opt == "raddr":
            op = memory.get_packed_address(op, is_routine_call=True)
            operands[j] = str('{0:02x}'.format(op))
        elif opt == "saddr":
            op = memory.get_packed_address(op, is_print_paddr=True)
            operands[j] = str('{0:02x}'.format(op))
        else:
            try:
                operands[j] = '#' + str('{0:02x}'.format(op))
            except:
                print(instr.name, str(operands))
    args = instr.args
    for key in args:
        if key == "string":
            pass
        elif key == "result":
            arg = args[key]
            if arg == 0:
                args[key] = "SP"
            elif arg in range(1, 16):
                args[key] = "L" + str('{0:02x}'.format(arg - 1))
            elif arg in range(16, 256):
                args[key] = "G" + str('{0:02x}'.format(arg - 16))
        elif key == "offset":
            arg = args[key]
            if arg == 0:
                args[key] = "rfalse"
            elif arg == 1:
                args[key] = "rtrue"
            else:
                address = new_pc + arg - 2
                args[key] = str('{0:02x}'.format(address))
        elif key == "is_reversed":
            if args[key]:
                args[key] = "false"
            else:
                args[key] = "true"
    values = list(args.values())
    values = " -> " + ', '.join(values) if values != [] else ''
    entry = '{0:02x}'.format(pc) + ': ' + '{0:<35}'.format(data) + '{0:<20}'.format(instr.name) + ', '.join(operands) + values
    print(entry)

from interpreter import *

path = '/Users/kaizhe/Desktop/Telegram/ifbot/games/'
file_name = path + 'zork1.z5'
# file_name = path + 'hhgg.z3'

# opens file in binary
file = open(file_name, "rb")

machine = Interpreter(file)

memory = machine.memory

address = int(input("Routine address: "))

localvars = memory.get_routine(address)
str_localvars = ', '.join(['{0:04x}'.format(memory.get_num(var)) for var in localvars])
print("Routine {}, {} locals ({})".format('{0:02x}'.format(address), str(len(localvars)), str_localvars))

for i in range(70):
    txd(memory)
