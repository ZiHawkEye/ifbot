# testing code
from interpreter import *

path = '/Users/kaizhe/Desktop/Telegram/ifbot/games/'
file_name = path + 'zork1.z5'
# file_name = path + 'hhgg.z3'

# opens file in binary
file = open(file_name, "rb")

machine = Interpreter(file)

# =============================================================================
# #tests memory and its segments
# print(mem[6:8])
# print(machine.memory.get_byte_address(mem[6:8]))
# print(machine.memory.get_dynamic(), machine.memory.get_high(), machine.memory.get_static())
# =============================================================================

# =============================================================================
# #tests the get string function
# abbrev_add = machine.help.abbrev_add
# for i in range(60):
#     offset = i*2
#     abbrev_table_add = machine.memory.get_byte_address(mem[abbrev_add:abbrev_add + 2])
#     #print('abbrev_table_add ' + str(abbrev_table_add))
#     abbrev_string_location = machine.memory.get_word_address(mem[abbrev_table_add 
#                                                          + offset:abbrev_table_add
#                                                          + offset + 2])
#     #print('abbrev_string_location ' + str(abbrev_string_location))

#     abbrev_string = machine.memory.get_string(abbrev_string_location)
#     print(abbrev_string)
# =============================================================================

# #test the instruction encoding (memory.get_instr())
# pc_add = machine.program_counter
# for i in range(20):
#     print('pc_add', pc_add)
#     instr = machine.memory.get_instr(pc_add)
#     print('form, count, num, type, ops', instr)

# =============================================================================
# Unit tests
# =============================================================================

# Comparisons and jumps
pc = machine.cur_frame.get_pc()
machine.jz(False, 3, 0)
new_pc = machine.cur_frame.get_pc()
assert (pc + 1 == new_pc), "Error"
print("jz() success")

pc = machine.cur_frame.get_pc()
machine.je(False, 3, 1, 1)
new_pc = machine.cur_frame.get_pc()
assert (pc + 1 == new_pc), "Error"
print("je() success")

pc = machine.cur_frame.get_pc()
machine.jl(False, 3, 0, 1)
new_pc = machine.cur_frame.get_pc()
assert (pc + 1 == new_pc), "Error"
print("jl() success")

pc = machine.cur_frame.get_pc()
machine.jg(False, 3, 1, 0)
new_pc = machine.cur_frame.get_pc()
assert (pc + 1 == new_pc), "Error"
print("jg() success")

# dependent on story file
if file_name == path + 'zork1.z5':
    pc = machine.cur_frame.get_pc()
    machine.jin(False, 3, 180, 82)
    new_pc = machine.cur_frame.get_pc()
    assert (pc + 1 == new_pc), "Error"
    pc = machine.cur_frame.get_pc()
    machine.jin(False, 3, 4, 0)
    new_pc = machine.cur_frame.get_pc()
    assert (pc + 1 == new_pc), "Error"
    print("jin() success")

pc = machine.cur_frame.get_pc()
machine.test(False, 3, 13, 0)
new_pc = machine.cur_frame.get_pc()
assert (pc + 1 == new_pc), "Error"
print("test() success")

pc = machine.cur_frame.get_pc()
machine.jump(3)
new_pc = machine.cur_frame.get_pc()
assert (pc + 1 == new_pc), "Error"
print("jump() success")

# Objects
obj_var = machine.memory.get_obj(1)
flags = [value % 2 for value in range(32)]
parent = 1
sibling = 2
child = 3
properties_add = obj_var.properties_add

test_obj = Object(flags, parent, sibling, child, properties_add)
machine.memory.set_obj(1, test_obj)
test_obj = machine.memory.get_obj(1)
assert (test_obj.flags == flags and 
        test_obj.parent == parent and
        test_obj.sibling == sibling and
        test_obj.child == child and 
        test_obj.properties_add == properties_add), "Error with set_obj(), get_obj()"
print("set_obj(), get_obj() success")

pc = machine.cur_frame.get_pc()
# stores child in top of routine stack
machine.get_child(result=0, is_reversed=False, offset=3, obj=1)
child = machine.pop()
assert(child == test_obj.child), "Error in get_child(), child is " + str(child)
new_pc = machine.cur_frame.get_pc()
assert(pc + 1 == new_pc), "Error in branching"
print("get_child() success")

pc = machine.cur_frame.get_pc()
machine.get_sibling(result=0, is_reversed=False, offset=3, obj=1)
sibling = machine.pop()
assert(sibling == test_obj.sibling), "Error in get_sibling(), sibling is " + str(sibling)
new_pc = machine.cur_frame.get_pc()
assert(pc + 1 == new_pc), "Error in branching"
print("get_sibling() success")

machine.get_parent(result=0, obj=1)
parent = machine.pop()
assert(parent == test_obj.parent), "Error in get_parent(), parent is " + str(parent)
print("get_parent() success")

# dependent on story file
if file_name == path + 'zork1.z5':
    obj_var = machine.memory.get_obj(180)
    machine.remove_obj(180)
    parent_obj = machine.memory.get_obj(obj_var.parent)
    test_obj = machine.memory.get_obj(180)
    assert(parent_obj.child == obj_var.sibling), "Error"
    assert(test_obj.sibling == 0 and test_obj.parent == 0), "Error"
    print("remove_obj() success")

    machine.insert_obj(180, 82)
    obj1_var = machine.memory.get_obj(180)
    obj2_var = machine.memory.get_obj(82)
    assert(obj2_var.child == 180), "Error"
    assert(obj1_var.parent == 82), "Error"
    print("insert_obj() success")

machine.clear_attr(1, 0)
test_obj = machine.memory.get_obj(1)
assert(test_obj.flags[0] == 0), "Error"
print("clear_attr() success")

machine.set_attr(1, 0)
test_obj = machine.memory.get_obj(1)
assert(test_obj.flags[0] == 1), "Error"
print("set_attr() success")

pc = machine.cur_frame.get_pc()
machine.test_attr(is_reversed=False, offset=3, obj=1, attr=0)
test_obj = machine.memory.get_obj(1)
new_pc = machine.cur_frame.get_pc()
assert(test_obj.flags[0] == 1 and pc + 1 == new_pc), "Error"
print("test_attr() success")

# dependent on story file
if file_name == path + 'zork1.z5':
    machine.put_prop(obj=180, prop=31, a=42)
    obj1_var = machine.memory.get_obj(180)
    machine.get_prop(0, 180, 31)
    temp = machine.pop()
    assert(temp == 42), "Error"
    print("put_prop() success")

    # dependent on story file
    machine.get_prop(result=0, obj=180, prop=28)
    prop = machine.pop()
    assert(prop == 0x50), "Error"
    print("get_prop() success")

    # dependent on story file
    machine.get_prop_addr(result=0, obj=180, prop=28)
    prop_add = machine.pop()
    machine.get_prop_len(result=0, baddr=prop_add)
    prop = machine.pop()
    assert(prop == 1), "Error" 
    print("get_prop_addr success")

    # dependent on story file
    machine.get_next_prop(result=0, obj=180, prop=0)
    prop = machine.pop()
    assert(prop == 31), "Error"
    machine.get_next_prop(result=0, obj=180, prop=27)
    prop = machine.pop()
    assert(prop == 25), "Error"
    print("get_next_prop() success")

# Call 
# dependent on story file
if file_name == path + 'zork1.z5':
    machine.call(raddr=36174, values=[123], result=0, ret="function", n=1)
    frame = machine.stack[-1]
    assert(frame.get_localvar(1) == [0, 123] and
            frame.get_ret() == "function" and
            frame.get_pc() == 36174 + 3 and
            frame.get_result() == 0), "Error"
    print("call() success")

    # dependent on story file
    machine.ret(456)
    temp = machine.pop()
    frame = machine.stack[-1]
    assert(temp == 456 and
            len(machine.stack) == 1), "Error"
    print("ret() success")

# Reading and writing memory
machine.cur_frame.localvars = [0, 0, 0, 0]
machine.store(1, 19)
machine.load(0, 1)
temp = machine.pop()
assert (temp == 19), "Error with store()/load(), localvars"
machine.store(16, 1997)
machine.load(0, 16)
temp = machine.pop()
temp = temp if type(temp) == int else machine.memory.get_num(temp)
assert (temp == 1997), "Error with store()/load(), globalvars"
print("store(), load() success")

machine.storew(1, 0, 2018)
machine.loadw(0, 1, 0)
temp = machine.pop()
temp = machine.memory.get_num(temp)
assert(temp == 2018), "Error"
print("storew(), loadw() success")

machine.storeb(3, 0, 144)
machine.loadb(0, 3, 0)
temp = machine.pop()
assert(temp == 144), "Error"
print("storeb(), loadb() success")

# Arithmetic
machine.add(0, 1, 1)
temp = machine.pop()
assert(temp == 2), "Error"
print("add() success")

machine.sub(0, 4, 1)
temp = machine.pop()
assert(temp == 3), "Error"
print("sub() success")

machine.mul(0, 2, 2)
temp = machine.pop()
assert(temp == 4), "Error"
print("mul() success")

machine.div(0, 16, 3)
temp = machine.pop()
assert(temp == 5), "Error"
print("div() success")

machine.mod(0, 55, 7)
temp = machine.pop()
assert(temp == 6), "Error"
print("mod() success")

machine.add(0, 1, 5)
machine.inc(0)
temp = machine.pop()
assert(temp == 7), "Error"
print("inc() success")

machine.add(0, 4, 5)
machine.dec(0)
temp = machine.pop()
assert(temp == 8), "Error"
print("dec() success")

# Miscellaneous
add = machine.memory.get_obj(247).properties_add
data = machine.memory.memory[add:add + 10]
name = machine.memory.get_obj_name(add)
result = machine.memory.get_prop_addr(add, 0)
print(data)
print(result)
print(name)