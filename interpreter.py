# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 22:09:06 2018

@author: User
"""

#TODO
#test call, jump, branch, store functionality
#make sure the stack functions as specified
#when does type conversion of global, local, routine variables occur?

from memory import Memory
from helper import *
from frame import *
from math import *

class Interpreter():
    def __init__(self, file):        
        # represents story file/memory
        self.memory = Memory(file)

        # version number of z machine
        self.ver_num = self.memory.get_ver()
        
        # set of predetermined values and functions
        self.help = Helper(self.ver_num)
        
        # parts of the z machine not included in the story file
        # define the state of play to be saved
        # maybe converted to classes?
        pc = self.memory.get_pc()
        
        self.stack = []
        if self.ver_num in [1, 2]:
            first_frame = Frame(pc, [])
        elif self.ver_num in [3, 4]:
            first_frame = Frame3(pc, [], None)
        elif self.ver_num == 5:
            first_frame = Frame5(pc, [], None)
        elif self.ver_num == 6:
            localvars = self.memory.get_routine(pc)
            pc = self.memory.get_pc
            first_frame = Frame5(pc, localvars, None)
        self.stack.append(first_frame)
        self.cur_frame = first_frame

        # # start to execute instructions
        # # issue with dectets, abbrev?
        for i in range(25):
            self.cur_frame = self.stack[len(self.stack) - 1]
            # gets instr details 
            instr = self.memory.get_instr(self.cur_frame.get_pc())
            # updates program counter
            self.cur_frame.set_pc(self.memory.get_pc())
            # executes
            print('operands: ' + str(instr.operands))
            print('arguments: ' + str(instr.arguments))
            # print('pc: ' + str(self.cur_frame.get_pc()))
            # try:
            #     instr_function = getattr(self, instr.name)
            # except AttributeError:
            #     raise NotImplementedError("Class `{}` does not implement `{}`".format(self.__class__.__name__, instr.name))
            # # use * before an iterable to expand it before a function call
            # instr_function(*instr.arguments, *instr.operands)
            
# =============================================================================
# Get Methods
# =============================================================================
        
# Operations
# Reading and writing memory
    def push(self, a):
        self.cur_frame.push_routine_stack(a)
    
    def pop(self):
        return self.cur_frame.pop_routine_stack()

    def store(self, var, a):
        if var == 0:
            self.push(a)
        elif var in range(1, 16):
            self.cur_frame.set_localvar(a, var)
        elif var in range(16, 256):
            self.memory.set_gvar(var - 16, a)
            
    def load(self, result, var):
        if var == 0:        
            value = self.pop()
        elif var in range(1, 16):
            value = self.cur_frame.get_localvar(var)
        elif var in range(16, 256):
            value = self.memory.get_gvar(var - 16)
        
        self.store(result, value)

    def storew(self, baddr, n, a):
        self.memory.storew(baddr, n, a)

    def storeb(self, baddr, n, byte):
        self.memory.storeb(baddr, n, byte)

    def loadw(self, result, baddr, n):
        value = self.memory.loadw(baddr, n)
        assert (len(value == 2) and type(value[0]) == bytes), "Incorrect format of value in loadw"
        self.store(result, value)

    def loadb(self, result, baddr, n):
        value = self.memory.loadb(baddr, n)
        assert(len(value == 1) and type(value) == bytes), "Incorrect format of value in loadb"
        self.store(result, value)

    def pull(self, var):
        value = self.pop()
        self.store(var, value)
    
    def pull_b(self, result, baddr):
        pass

    def scan_table(self, result, is_reversed, offset, a, baddr, n, byte):
        value = self.memory.scan_table(a, baddr, n, byte)
        if value == 0:
            return 0
        else:
            self.store(result, value)
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2) 

    def copy_table(self, baddr1, baddr2, s):
        self.memory.copy_table(baddr1, baddr2, s)

    def push_stack(self, is_reversed, offset, a, baddr):
        pass

    def pull_stack(self, n, baddr):
        pass

# Arithmetic
    def add(self, result, a, b):
        self.store(result, a + b)
    
    def sub(self, result, a, b):
        self.store(result, a - b)
    
    def mul(self, result, a, b):
        self.store(result, a*b)
    
    def div(self, result, s, t):
        # s and t are signed numbers
        value = floor(s/t)
        self.store(result, value)

    def mod(self, result, s, t):
        value = s - t * floor(s/t)
        self.store(result, value)

    def inc(self, var):
        value = self.load(var)
        value += 1
        self.store(var, value)

    def dec(self, var):
        value = self.load(var)
        value -= 1
        self.store(var, value)

    def inc_jg(self, branch, var, s):
        # CHECK
        pass

    def dec_jl(self, branch, var, s):
        # CHECK
        pass

    def or_(self, result, a, b):
        value = a|b
        self.store(result, value)

    def and_(self, result, a, b):
        value = a&b
        self.store(result, value)

    def not_(self, result, a):
        # complement
        value = ~a 
        self.store(result, value)

    def log_shift(self, result, a, t):
        value = floor(a * 2**t)
        self.store(result, value)

    def art_shift(self, result, s, t):
        value = floor(s * 2**t)
        self.store(result, value)

# Comparisons and jumps
    def jz(self, is_reversed, offset, a):
        # branch if a is 0
        condition = (a == 0)
        if is_reversed:
            condition = not condition
        if condition:
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2)
    
    def je(self, is_reversed, offset, a, b1=None, b2=None, b3=None):
        if b1 == None and b2 == None and b3 == None:
            pass
        else:
            condition = (a == b1 or a == b2 or a == b3)
            if is_reversed:
                condition = not condition
            if condition:
                pc = self.cur_frame.get_pc()
                self.cur_frame.set_pc(pc + offset - 2)

    def jl(self, is_reversed, offset, s, t):
        condition = s < t
        if is_reversed:
            condition = not condition
        if condition:
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2)

    def jg(self, is_reversed, offset, s, t):
        condition = s > t
        if is_reversed:
            condition = not condition
        if condition:
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2)

    def jin(self, is_reversed, offset, obj, n):
        pass

    def test(self, is_reversed, offset, a, b):
        condition = a & b
        if is_reversed:
            condition = not condition
        if condition:
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2)

    def jump(self, s):
        self.cur_frame.set_pc(pc + s - 2)

# Call and return, throw and catch
    # Last character of function name refers to number of operands - 1:1, v:0-3, d:0-7
    # 2nd last char of func name refers to presence of result args - f:yes, p:no 
    def call(self, raddr, values=[], result=None, ret=None, n=None):
        # if raddr is 0, either it is the result or if result is already present, nothing happens
        assert (raddr != 0 and result == None), "Raddr should not be 0 if result argument is present"
        localvars = self.memory.get_routine(raddr)
        pc = self.memory.get_pc()
        # passes in operands into localvars
        if values != []:
            for i in range(len(values)):
                localvars[i] = values[i]
        if self.ver_num in [1, 2]:
            new_frame = Frame(pc, localvars, result)
        elif self.ver_num in [3, 4]:
            new_frame = Frame3(pc, localvars, ret, result)
        elif self.ver_num in [5, 6]:
            new_frame = Frame5(pc, localvars, ret, n, result)

        self.stack.append(new_frame)
        self.cur_frame = new_frame

    def call_f0(self, result, raddr):
        self.call(raddr, result=result, ret="function", n=0)

    def call_p0(self, raddr):
        self.call(raddr, ret="procedure", n=0)
    
    def call_f1(self, result, raddr, a1=None):
        values = []
        if a1 != None:
            values = [a1]
        self.call(raddr, values=values, result=result, ret="function", n=len(values))
        
    def call_p1(self, raddr, a1=None):
        values = []
        if a1 != None:
            values = [a1]
        self.call(raddr, values=values, ret="procedure", n=len(values))

    def call_fv(self, result, raddr, a1=None, a2=None, a3=None):
        values = [a1, a2, a3]
        values = [value for value in values if value != None]
        if self.ver_num in [1, 2]:
            self.call(raddr, values=values, result=result)
        else:
            self.call(raddr, values=values, result=result, ret="function", n=len(values))

    def call_pv(self, raddr, a1=None, a2=None, a3=None):
        values = [a1, a2, a3]
        values = [value for value in values if value != None]
        if self.ver_num in [1, 2]:
            self.call(raddr, values=values)
        else:
            self.call(raddr, values=values, ret="procedure", n=len(values))

    def call_fd(self, result, raddr, a1=None, a2=None, a3=None, a4=None, a5=None, a6=None, a7=None):
        values = [a1, a2, a3, a4, a5, a6, a7]
        values = [value for value in values if value != None]
        self.call(raddr, values=values, result=result, ret="function", n=len(values))

    def call_pd(self, raddr, a1=None, a2=None, a3=None, a4=None, a5=None, a6=None, a7=None):
        values = [a1, a2, a3, a4, a5, a6, a7]
        values = [value for value in values if value != None]
        self.call(raddr, values=values, ret="procedure", n=len(values))
    
    def ret(self, a):
        # Note that print_rtrue, ret_pulled, rfalse, rtrue, throw do a ret implicitly
        # returns a value to the previous frame to be stored in the result arg
        if self.ver_num in [3, 4, 5, 6]:
            ret = self.cur_frame.get_ret()
        assert (len(self.stack) != 1), "Stack should not be left empty on return instruction"
        self.stack.pop()
        self.cur_frame = self.stack[len(self.stack) - 1]
        result = self.cur_frame.get_result()
        # CHECK
        # if the routine was called as an interrupt, return the value a to the caller
        if ret == "function":
            self.store(result, a)

    def rtrue(self):
        self.ret(1)

    def rfalse(self):
        self.ret(0)
    
    def ret_pulled(self):
        a = self.pop()
        self.ret(a)

    def check_arg_count(self, is_reversed, offset, n):
        assert (len(self.stack) != 1), "check_arg_count instruction encountered on the main routine"
        values_passed = self.cur_frame.get_n()
        condition = (values_passed >= n)
        if is_reversed:
            condition = not condition
        if condition:
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2)

    def catch(self, result):
        # CHECK
        pass
    
    def throw(self):
        # CHECK
        pass

# Objects, attributes and their properties
    def get_sibling(self, result, is_reversed, offset, obj):
        pass

# =============================================================================
# End of Class
# =============================================================================

#testing code
# file_name = '/Users/kaizhe/Desktop/Telegram/ifbot/games/zork1.z5'
file_name = '/Users/kaizhe/Desktop/Telegram/ifbot/games/hhgg.z3'

#opens file in binary
file = open(file_name, "rb")

#need to write file in binary as well

#checks attributes of Memory
machine = Interpreter(file)

mem = machine.memory.get_memory()

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
