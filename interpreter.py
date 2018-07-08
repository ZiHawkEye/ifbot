# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 22:09:06 2018

@author: User
"""

#TODO
#consider adding functionality similar to ztools
#need some way to monitor the state of the game
#test object functionality
#when to use get_int and get_num?
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

        # start to execute instructions
        # issue with dectets, abbrev?
        for i in range(200):
            # current state of interpreter?
            self.cur_frame = self.stack[len(self.stack) - 1]
            # gets instr details 
            instr = self.memory.get_instr(self.cur_frame.get_pc())
            # converts unsigned numbers to variable numbers
            operands = instr.operands
            types = instr.types
            for i in range(len(operands)):
                # checks if operand is an unsigned variable num - for instructions that may take it either variable or unsigned operands
                if types[i] == 2:
                    var = operands[i]
                    # moves value from variable to top of routine stack
                    self.load(0, operands[i])
                    # pops routine stack
                    temp = self.pop()
                    # converts to unsigned int
                    operands[i] = temp if type(temp) == int else self.memory.get_num(temp)
                    assert (operands[i] < 2 ** 16), "Unsigned variables are 16 bit, not " + str(operands[i])
                    print("op: " + str(operands[i]) + " var: " + str(var))

            # updates program counter 
            # this ensures that the program counter is not affected by the execution of instructions except for call instructions
            self.cur_frame.set_pc(self.memory.get_pc())
            # executes
            print('ops: ' + str(instr.operands) + " args: " + str(instr.arguments))
            try:
                instr_function = getattr(self, instr.name)
            except AttributeError:
                raise NotImplementedError("Class `{}` does not implement `{}`".format(self.__class__.__name__, instr.name))
            # use * before an iterable to expand it before a function call
            instr_function(*instr.arguments, *instr.operands)
            
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
        assert (var in range(0, 256)), "Incorrect value of var " + str(var) + " in store"
        if var == 0:
            self.push(a)
        elif var in range(1, 16):
            self.cur_frame.set_localvar(a, var)
        elif var in range(16, 256):
            self.memory.set_gvar(var - 16, a)
            
    def load(self, result, var):
        assert (var in range(0, 256)), "Incorrect value of var " + str(var) + " in load"
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
        assert (len(value) == 2 and type(value[0]) == bytes), "Incorrect format of value in loadw"
        self.store(result, value)

    def loadb(self, result, baddr, n):
        value = self.memory.loadb(baddr, n)
        assert(len(value) == 1 and type(value) == bytes), "Incorrect format of value in loadb"
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
            condition = a in [b1, b2, b3]
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
        pc = self.cur_frame.get_pc()
        self.cur_frame.set_pc(pc + s - 2)

# Call and return, throw and catch
    # Last character of function name refers to number of operands - 1:1, v:0-3, d:0-7
    # 2nd last char of func name refers to presence of result args - f:yes, p:no 
    def call(self, raddr, values=[], result=None, ret=None, n=None):
        # if raddr is 0, either it is the result or if result is already present, nothing happens
        assert ((raddr == 0 and result == None) or (raddr != 0)), "Raddr should not be 0 if result argument is present"
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
        # result arg is stored in the frame to be popped during call(), else the main routine would require a result arg
        if self.ver_num in [3, 4, 5, 6]:
            ret = self.cur_frame.get_ret()
        assert (len(self.stack) != 1), "Stack should not be left empty on return instruction"
        result = self.cur_frame.get_result()
        self.stack.pop()
        self.cur_frame = self.stack[len(self.stack) - 1]
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
# Note: Reading in the obj may change the program counter due to the get_string() function but
# Any changes in the memory's program counter should not affect the frame program counter
    def get_sibling(self, result, is_reversed, offset, obj):
        # obj refers to a legal obj number
        # Gets the object of type Object 
        obj_var = self.memory.get_obj(obj)
        # sibling is a legal obj number
        # sibling should be value 0 if it doesnt exist
        sibling = obj_var.sibling
        self.store(result, sibling)
        condition = sibling != 0
        if is_reversed:
            condition = not condition
        if condition:
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2)

    def get_child(self, result, is_reversed, offset, obj):
        # obj refers to a legal obj number
        # Gets the object of type Object 
        obj_var = self.memory.get_obj(obj)
        # child is a legal obj number 
        # child should be value 0 if it doesnt exist
        child = obj_var.child
        self.store(result, child)
        condition = child != 0
        if is_reversed:
            condition = not condition
        if condition:
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2)

    def get_parent(self, result, is_reversed, offset, obj):
        # obj refers to a legal obj number
        # Gets the object of type Object
        obj_var = self.memory.get_obj(obj)
        # parent is a legal obj number
        # parent should be value 0 if it doesnt exist
        parent = obj_var.parent
        self.store(result, parent)
        condition = parent != 0
        if is_reversed:
            condition = not condition
        if condition:
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2)    

    def remove_obj(self, obj):
        # the current obj is set to have no parents and siblings
        # its children remain unchanged - all its children move with it
        # no other objects should reference obj and the sibling chain should be closed
        # Gets the object of type Object
        obj_var = self.memory.get_obj(obj)
        parent = self.memory.get_obj(obj_var.parent)
        if parent.child != obj:
            # Gets the first sibling
            cur_sibling = self.memory.get_obj(parent.child)
            sibling_num = parent.child
            # iterates through siblings until the sibling before the current obj is found
            while cur_sibling.sibling != obj and cur_sibling.sibling != 0:
                sibling_num = cur_sibling.sibling
                cur_sibling = self.memory.get_obj(cur_sibling.sibling)
            sibling_before = cur_sibling
            # close the sibling chain
            sibling_before.sibling = obj_var.sibling
        else:
            parent.child = obj_var.sibling
        # obj has no parents and siblings
        obj_var.parent = 0
        obj_var.sibling = 0
        # encodes changes
        self.memory.set_obj(obj_var.parent, parent)
        self.memory.set_obj(sibling_num, sibling_before)
        self.memory.set_obj(obj, obj_var)

    def insert_obj(self, obj1, obj2):
        # Remove obj1 from its current position in the tree 
        self.remove_obj(obj1)
        # Insert it as the 1st child of obj2
        obj1_var = self.memory.get_obj(obj1)
        obj2_var = self.memory.get_obj(obj2)
        obj1_var.sibling = obj2_var.child
        obj2_var.child = obj1
        # Encode changes
        self.memory.set_obj(obj1, obj1_var)
        self.memory.set_obj(obj2, obj2_var)

    def test_attr(self, is_reversed, offset, obj, attr):
        # Branch if object has attribute
        obj_var = self.memory.get_obj(obj)
        # attributes are numbered from 1 onwards
        condition = obj_var.flags[attr - 1] == 1
        if is_reversed:
            condition = not condition
        if condition:
            pc = self.cur_frame.get_pc()
            self.cur_frame.set_pc(pc + offset - 2)

    def set_attr(self, obj, attr):
        obj_var = self.memory.get_obj(obj)
        # attributes are numbered from 1 onwards
        obj_var.flags[attr - 1] = 1
        # Encode object
        self.memory.set_obj(obj_var, obj)

    def clear_attr(self, obj, attr):
        obj_var = self.memory.get_obj(obj)
        # attributes are number from 1 onwards
        obj_var.flags[attr - 1] = 0
        # Encode object
        self.memory.set_obj(obj_var, obj)

    def put_prop(self, obj, prop, a):
        # Set prop on obj to a. The property must be present on the object(property is in property list? or flag == 1?)
        self.memory.put_prop(obj, prop, a)

    def get_prop(self, result, obj, prop):
        # The result is the first word/byte of prop on obj, if present
        # Else result is default result on default prop list
        obj_var = self.memory.get_obj(obj)
        properties = self.memory.get_properties(obj_var.properties_add)
        try:
            obj_prop = properties[prop]    
            assert (len(obj_prop) <= 2), "Property length is greater than 2 bytes"
        except KeyError:
            # Property not present on obj, get default 
            obj_prop = self.memory.loadw(self.memory.prop_defaults, prop)
        self.store(result, obj_prop)

    def get_prop_addr(self, result, obj, prop):
        obj_var = self.memory.get_obj(obj)
        properties = self.memory.get_properties(obj_var.properties_add)
        try:
            obj_prop = properties[prop]    
            assert (len(obj_prop) <= 2), "Property length is greater than 2 bytes"
        except KeyError:
            print("Property does not exist on the obj")
        address = self.memory.get_properties(obj_var.properties_add, prop=prop, add=None)
        self.store(result, address)
    
    def get_next_prop(self, result, obj, prop):
        # if prop is 0, get the value of the highest property number
        # else get the next prop (lower prop num)
        # store as result
        obj_var = self.memory.get_obj(obj)
        properties = self.memory.get_properties(obj_var.properties_add)
        sorted_properties = [(i, a(i)) for i in sorted(properties)]
        if prop == 0:
            obj_prop = sorted_properties[len(sorted_properties) - 1]
        else:
            value = properties[prop]
            for i in range(i):
                if value == sorted_properties[i]:
                    value = sorted_properties[i + 1]
                    break
        self.store(result, value)

    def get_prop_len(self, result, baddr):
        prop_len = self.memory.get_prop_len(baddr)
        self.store(result, prop_len)

# Windows

# =============================================================================
# End of Class
# =============================================================================

file_name = '/Users/kaizhe/Desktop/Telegram/ifbot/games/zork1.z5'
# file_name = '/Users/kaizhe/Desktop/Telegram/ifbot/games/hhgg.z3'

# opens file in binary
file = open(file_name, "rb")

# need to write file in binary as well

# checks attributes of Memory
machine = Interpreter(file)

mem = machine.memory.get_memory()
