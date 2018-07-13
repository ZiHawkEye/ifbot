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
pc = machine.cur_frame.get_pc()
machine.jin(False, 3, 180, 82)
new_pc = machine.cur_frame.get_pc()
assert (pc + 1 == new_pc), "Error"
print("jin() success")

pc = machine.cur_frame.get_pc()
machine.test(False, 3, 1, 1)
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
flags = [0 for value in range(32)]
parent = 0
sibling = 0
child = 0
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
machine.get_child(result=0, is_reversed=True, offset=3, obj=1)
child = machine.pop()
assert(child == 0), "Error in get_child(), child is " + str(child)
new_pc = machine.cur_frame.get_pc()
assert(pc + 1 == new_pc), "Error in branching"
print("get_child() success")

pc = machine.cur_frame.get_pc()
machine.get_sibling(result=0, is_reversed=True, offset=3, obj=1)
sibling = machine.pop()
assert(sibling == 0), "Error in get_sibling(), sibling is " + str(sibling)
new_pc = machine.cur_frame.get_pc()
assert(pc + 1 == new_pc), "Error in branching"
print("get_sibling() success")

machine.get_parent(result=0, obj=1)
parent = machine.pop()
assert(parent == 0), "Error in get_parent(), parent is " + str(parent)
print("get_parent() success")

machine.remove_obj(2)
test_obj = machine.memory.get_obj(2)
assert(test_obj.sibling == 0 and test_obj.parent == 0), "Error"
print("remove_obj() success")

machine.insert_obj(1, 2)
obj1_var = machine.memory.get_obj(1)
obj2_var = machine.memory.get_obj(2)
assert(obj2_var.child == 1), "Error"
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
machine.put_prop(obj=1, prop=16, a=42)
obj1_var = machine.memory.get_obj(1)
properties = machine.memory.get_properties(obj1_var.properties_add)
assert(properties[16][0] == 42), "Error"
print("put_prop() success")

# dependent on story file
machine.get_prop(result=0, obj=1, prop=16)
prop = machine.pop()
assert(prop[0] == 42), "Error"
print("get_prop() success")

# dependent on story file
machine.get_prop_addr(result=0, obj=1, prop=16)
prop_add = machine.pop()
machine.loadb(result=0, baddr=prop_add, n=1)
prop = machine.pop()
assert(prop == 42), "Error" 
print("get_prop_addr success")

# dependent on story file
machine.get_next_prop(result=0, obj=1, prop=0)
prop = machine.pop()
assert(prop == 18), "Error"
machine.get_next_prop(result=0, obj=1, prop=18)
prop = machine.pop()
assert(prop == 16), "Error"
print("get_next_prop() success")

