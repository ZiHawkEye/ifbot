# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 22:09:06 2018

@author: User
"""

#TODO
# bugs
# hello in zork
# drink water, darkness in hhgg
# i don't know the word
# issues with read?
#need some way to monitor the state of the game
#when does type conversion of global, local, routine variables occur?
#what are dectets used for in zstrings?

import warnings
import threading
import random
from memory import Memory
from helper import *
from frame import *
from window import *
from math import *
import sys

class Interpreter():
    def __init__(self, file, o=None):
        # where output is stored
        self.o = o
                
        # represents story file/memory
        self.memory = Memory(file)

        # version number of z machine
        self.ver_num = self.memory.get_ver()
        
        # set of predetermined values and functions
        self.help = Helper(self.ver_num)

        # input and output streams
        self.ostream = [True, True, False, False]
        self.istream = 0
        
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
            first_frame = Frame5(pc, [], None, 0)
        elif self.ver_num == 6:
            localvars = self.memory.get_routine(pc)
            pc = self.memory.get_pc
            first_frame = Frame5(pc, localvars, None)
        self.stack.append(first_frame)
        self.cur_frame = first_frame

    def start(self, n, has_input=False):
        if n == 0:
            while True:
                self.run(has_input)
                has_input = False
        else:
            for i in range(n):
                self.run(has_input)
                has_input = False
    
    def run(self, has_input):
        # UNDO
        test = False
        self.cur_frame = self.stack[-1]
        pc = self.cur_frame.get_pc()
        instr = self.memory.get_instr(self.cur_frame.get_pc())
        # updates program counter 
        # this ensures that the program counter is not affected by the execution of instructions except for call instructions
        self.cur_frame.set_pc(self.memory.get_pc())
        # UNDO
        if instr.name in ['read', 'read_w', 'read_char'] and not has_input and self.o != None:
            self.cur_frame.set_pc(pc)
            raise KeyboardInterrupt

        # converts unsigned numbers to variable numbers
        for i in range(len(instr.operands)):
            # checks if operand is an unsigned variable num - for instructions that may take it either variable or unsigned operands
            op = instr.operands[i]
            typ = instr.types[i]
            opt = instr.op_types[i]
            if typ == 2:
                var = op    
                # moves value from variable to top of routine stack
                self.load(0, var)
                # pops routine stack
                op = self.pop()
                # UNDO
                if test == True:
                    print("op: " + str(op) + " var: " + str(var), end=' ')
                assert(op != 0 or opt != "var"), "Error"
            # data conversion for all operands
            if opt in ["bit", "byte",
                        "obj", "attr", "prop",
                        "window", "time", "pic"]:
                # May be a list if taken from global/local variables
                op = self.memory.get_num(op)
                assert (op < 1 << 8), "Operand {} of type {}, instr {} is not 1 byte".format(str(op), opt, instr.name)
            elif opt == "var":
                # an indirect ref to the stack pointer means that it is read or written in place
                if op == 0:
                    op = -1
            elif opt in ["s", "t"]:
                op = self.memory.get_num(op, signed=True)
            elif opt == "baddr":
                op = self.memory.get_byte_address(op)
            elif opt == "raddr":
                op = self.memory.get_packed_address(op, is_routine_call=True)
            elif opt == "saddr":
                op = self.memory.get_packed_address(op, is_print_paddr=True)
            else:
                op = self.memory.get_num(op)
            assert (op < 1 << 16 or opt in ["baddr", "raddr", "saddr"]), "Interpreter is 16 bit, cannot store " + str(op)
            instr.operands[i] = op                    

        # UNDO
        if test == True:
            print(instr.name, end=' ')
            print('{0:02x}'.format(self.cur_frame.get_pc()), end=' ')
            print('ops: ' + str(instr.operands) + " args: " + str(instr.arguments))
        # executes
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
    def branch(self, condition, is_reversed, offset):
        if is_reversed:
            condition = not condition
        if condition:
            if offset == 0:
                self.rfalse()
            elif offset == 1:
                self.rtrue()
            else:
                self.jump(offset)

    def push(self, a):
        self.cur_frame.push_routine_stack(a)
    
    def pop(self):
        temp = self.cur_frame.pop_routine_stack()
        temp = self.memory.get_num(temp)
        return temp

    def store(self, var, a):
        assert (var in range(0, 256)), "Incorrect value of var " + str(var) + " in store"
        # a is always 2 bytes
        a = self.memory.get_num(a)
        a = [a >> 8] + [0xff & a]
        if var == -1:
            # an indirect ref to the stack pointer means that it is read or written in place
            self.pop()
            self.push(a)
        elif var == 0:
            self.push(a)
        elif var in range(1, 16):
            self.cur_frame.set_localvar(a, var)
        elif var in range(16, 256):
            self.memory.set_gvar(var - 16, a)
            
    def load(self, result, var):
        assert (var in range(0, 256)), "Incorrect value of var " + str(var) + " in load"
        if var == -1:
            value = self.pop()
            self.push(value)
        elif var == 0:        
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
        self.store(result, value)

    def loadb(self, result, baddr, n):
        value = self.memory.loadb(baddr, n)
        self.store(result, value)

    def pull(self, var):
        value = self.pop()
        self.store(var, value)
    
    def pull_b(self, result, baddr):
        warnings.warn("Not implemented")

    def scan_table(self, result, is_reversed, offset, a, baddr, n, byte):
        value = self.memory.scan_table(a, baddr, n, byte)
        condition = value == 0
        if condition:
            self.store(result, 0)
        else:
            self.store(result, value)
        self.branch(condition, is_reversed, offset)

    def copy_table(self, baddr1, baddr2, s):
        self.memory.copy_table(baddr1, baddr2, s)

    def push_stack(self, is_reversed, offset, a, baddr):
        warnings.warn("Not implemented")

    def pull_stack(self, n, baddr):
        warnings.warn("Not implemented")

# Arithmetic (signed 16 bit)
    def add(self, result, a, b):
        value = (a + b) % (0xffff)
        self.store(result, value)
    
    def sub(self, result, a, b):
        value = (a - b) % (0xffff)
        self.store(result, value)
    
    def mul(self, result, a, b):
        value = (a*b) % (0xffff)
        self.store(result, value)
    
    def div(self, result, s, t):
        # s and t are signed numbers
        value = floor(s/t) % (0xffff)
        self.store(result, value)

    def mod(self, result, s, t):
        value = (s - t * floor(s/t)) % (0xffff)
        self.store(result, value)

    def inc(self, var):
        self.load(0, var)
        temp = self.pop()
        temp = self.memory.get_num(temp, signed=True)
        self.add(var, temp, 1)

    def dec(self, var):
        self.load(0, var)
        temp = self.pop()
        temp = self.memory.get_num(temp, signed=True)
        self.sub(var, temp, 1)

    def inc_jg(self, is_reversed, offset, var, s):
        self.inc(var)
        self.load(0, var)
        temp = self.pop()
        temp = self.memory.get_num(temp, signed=True)
        self.jg(is_reversed, offset, temp, s)

    def dec_jl(self, is_reversed, offset, var, s):
        self.dec(var)
        self.load(0, var)
        temp = self.pop()
        temp = self.memory.get_num(temp, signed=True)
        self.jl(is_reversed, offset, temp, s)

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
        self.je(is_reversed, offset, a, 0)
    
    def je(self, is_reversed, offset, a, b1=None, b2=None, b3=None):
        if b1 == None and b2 == None and b3 == None:
            raise Exception("je with just one operand is not allowed")
        else:
            condition = a in [b1, b2, b3]
            self.branch(condition, is_reversed, offset)

    def jl(self, is_reversed, offset, s, t):
        condition = s < t
        self.branch(condition, is_reversed, offset)

    def jg(self, is_reversed, offset, s, t):
        condition = s > t
        self.branch(condition, is_reversed, offset)

    def jin(self, is_reversed, offset, obj, n):
        self.get_parent(0, obj)
        temp = self.pop()
        self.je(is_reversed, offset, temp, n)

    def test(self, is_reversed, offset, a, b):
        self.and_(0, a, b)
        temp = self.pop()
        self.je(is_reversed, offset, temp, b)

    def jump(self, s):
        pc = self.cur_frame.get_pc()
        self.cur_frame.set_pc(pc + s - 2)

# Call and return, throw and catch
    # Last character of function name refers to number of operands - 1:1, v:0-3, d:0-7
    # 2nd last char of func name refers to presence of result args - f:yes, p:no 
    def call(self, raddr, values=[], result=None, ret=None, n=None):
        # if raddr is 0, either it is the result or if result is already present, nothing happens
        if raddr == 0:
            # self.rfalse()
            # Equivalent to creating a new frame and then rfalse()
            self.store(result, 0)
            return 0
        localvars = self.memory.get_routine(raddr)
        pc = self.memory.get_pc()
        
        if self.ver_num in [1, 2]:
            new_frame = Frame(pc, localvars, result)
        elif self.ver_num in [3, 4]:
            new_frame = Frame3(pc, localvars, ret, result)
        elif self.ver_num in [5, 6]:
            new_frame = Frame5(pc, localvars, ret, n, result)

        self.stack.append(new_frame)
        self.cur_frame = new_frame
        
        # passes in operands into localvars
        if values != []:
            for i in range(len(values)):
                self.store(i + 1, values[i])

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
        assert (len(self.stack) > 1), "Stack should not be left empty on return instruction"
        result = self.cur_frame.get_result()
        self.stack.pop()
        # UNDO
        self.cur_frame.get_localvars()
        self.cur_frame = self.stack[-1]
        # UNDO
        self.cur_frame.get_localvars()
        # CHECK
        # if the routine was called as an interrupt, return the value a to the caller
        if ret == "interrupt" or ret == "function":
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
        self.branch(condition, is_reversed, offset)

    def catch(self, result):
        # CHECK
        warnings.warn("Not implemented")
    
    def throw(self):
        # CHECK
        warnings.warn("Not implemented")

# Objects, attributes and their properties
# Note: Reading in the obj may change the program counter due to the get_string() function but
# Any changes in the memory's program counter should not affect the frame program counter
    def get_sibling(self, result, is_reversed, offset, obj):
        obj_var = self.memory.get_obj(obj)
        # sibling should be value 0 if it doesnt exist
        self.store(result, obj_var.sibling)
        condition = (obj_var.sibling != 0)
        self.branch(condition, is_reversed, offset)

    def get_child(self, result, is_reversed, offset, obj):
        obj_var = self.memory.get_obj(obj)
        # child should be value 0 if it doesnt exist
        self.store(result, obj_var.child)
        condition = (obj_var.child != 0)
        self.branch(condition, is_reversed, offset)

    def get_parent(self, result, obj):
        obj_var = self.memory.get_obj(obj)
        # parent should be value 0 if it doesnt exist
        self.store(result, obj_var.parent)

    def remove_obj(self, obj):
        # the current obj is set to have no parents and siblings
        # its children remain unchanged - all its children move with it
        # no other objects should reference obj and the sibling chain should be closed
        # either obj's parent or sib will ref it
        # if parent is 0, nothing happens
        obj_var = self.memory.get_obj(obj)
        if obj_var.parent == 0:
            assert(obj_var.sibling == 0), "Object should not have siblings"
            return 0
        parent = self.memory.get_obj(obj_var.parent)
        if parent.child != obj:
            # Gets the first sibling
            sibling_num = parent.child
            cur_sibling = self.memory.get_obj(sibling_num)
            # iterates through siblings until the sibling before the current obj is found
            while cur_sibling.sibling != obj and cur_sibling.sibling != 0:
                sibling_num = cur_sibling.sibling
                cur_sibling = self.memory.get_obj(sibling_num)
            sibling_before = cur_sibling
            # close the sibling chain
            sibling_before.sibling = obj_var.sibling
            # encode changes
            self.memory.set_obj(sibling_num, sibling_before)
        else:
            parent.child = obj_var.sibling
            self.memory.set_obj(obj_var.parent, parent)
        # obj has no parents and siblings
        obj_var.parent = 0
        obj_var.sibling = 0
        self.memory.set_obj(obj, obj_var)

    def insert_obj(self, obj1, obj2):
        # Remove obj1 from its current position in the tree 
        self.remove_obj(obj1)
        # Insert it as the 1st child of obj2
        obj1_var = self.memory.get_obj(obj1)
        obj2_var = self.memory.get_obj(obj2)
        obj1_var.sibling = obj2_var.child
        obj1_var.parent = obj2
        obj2_var.child = obj1
        # Encode changes
        self.memory.set_obj(obj1, obj1_var)
        self.memory.set_obj(obj2, obj2_var)

    def test_attr(self, is_reversed, offset, obj, attr):
        # Branch if object has attribute
        obj_var = self.memory.get_obj(obj)
        # attributes are numbered from 0 onwards
        condition = (obj_var.flags[attr] == 1)
        self.branch(condition, is_reversed, offset)

    def set_attr(self, obj, attr):
        obj_var = self.memory.get_obj(obj)
        # attributes are numbered from 0 onwards
        obj_var.flags[attr] = 1
        self.memory.set_obj(obj, obj_var)

    def clear_attr(self, obj, attr):
        obj_var = self.memory.get_obj(obj)
        # attributes are numbered from 0 onwards
        obj_var.flags[attr] = 0
        self.memory.set_obj(obj, obj_var)

    def put_prop(self, obj, prop, a):
        # Set prop on obj to a. The property must be present on the object(property is in property list? or flag == 1?)
        self.memory.put_prop(obj, prop, a)

    def get_prop(self, result, obj, prop):
        # The result is the first word/byte of prop on obj, if present
        # It is illegal for the prop len to be greater than 2
        obj_var = self.memory.get_obj(obj)
        prop_details = self.memory.get_prop_addr(obj_var.properties_add, prop)
        if prop_details == 0:
            # Result is from property defaults table
            self.loadw(result, self.memory.prop_defaults, prop - 1)
        elif prop_details['prop_len'] > 2:
            raise Exception("Property length cannot be greater than 2")
        else:
            data_add = prop_details['data_add']
            prop_len = prop_details['prop_len']
            prop_data = self.memory.memory[data_add] if prop_len == 1 else self.memory.memory[data_add:data_add + 2]
            self.store(result, prop_data)

    def get_prop_addr(self, result, obj, prop):
        # The result is the byte address of the property data in the prop block
        obj_var = self.memory.get_obj(obj)
        prop_details = self.memory.get_prop_addr(obj_var.properties_add, prop)
        if prop_details == 0:
            self.store(result, 0)
        else:
            self.store(result, prop_details['data_add'])
    
    def get_next_prop(self, result, obj, prop):
        # Gives the number of the next property on the list
        # Can be zero, indicating end of list
        # If prop is zero, give the prop num of the first property
        # If prop cannot be found, ideally should halt
        prop_num = self.memory.get_next_prop(obj, prop)
        self.store(result, prop_num)

    def get_prop_len(self, result, baddr):
        # the result is the length of the property starting at baddr
        # this is stored in the byte at baddr - 1
        prop_len = self.memory.get_prop_blk(baddr - 1)['prop_len'] if baddr != 0 else 0
        self.store(result, prop_len)

# Windows
    def get_wind_prop(self, result, window, p):
        warnings.warn("Not implemented")

    def put_wind_prop(self, window, p, a):
        warnings.warn("Not implemented")

    def split_screen(self, n):
        warnings.warn("Not implemented")

    def set_window(self, window):
        warnings.warn("Not implemented")

    def set_cursor(self, s, x):
        warnings.warn("Not implemented")

    def set_cursor_w(self, s, w, window=None):
        warnings.warn("Not implemented")

    def get_cursor(self, baddr):
        warnings.warn("Not implemented")

    def buffer_mode(self, bit):
        warnings.warn("Not implemented")

    def set_colour(self, byte0, byte1):
        warnings.warn("Not implemented")

    def set_text_style(self, n):
        warnings.warn("Not implemented")

    def set_font(self, result, n):
        warnings.warn("Not implemented")

    def set_font_w(self, result, n, window=None):
        warnings.warn("Not implemented")

    def move_window(self, window, y, x):
        warnings.warn("Not implemented")

    def window_size(self, window, y, x):
        warnings.warn("Not implemented")

    def set_margins(self, x1, xr, window=None):
        warnings.warn("Not implemented")

    def window_style(self, window, flags, op):
        warnings.warn("Not implemented")

# Input and output streams
    def output_stream(self, s, baddr=None, w=None):
        assert (abs(s) in [-1, -2, -3, -4, 1, 2, 3, 4]), "Incorrect value of s " + str(s) + " in output_stream()"
        if s > 0:
            stream = s - 1
            if s == 3:
                assert (baddr != None), "baddr cannot be None if writing to memory"
            self.ostream[stream] = True
            # CHECK
            # what happens if baddr or w are present?
        elif s < 0:
            stream = (s + 1)*(-1)
            self.ostream[stream] = False
    
    def output_stream_b(self, s, baddr=None):
        self.output_stream(s, baddr)

    def output_stream_bw(self, s, baddr=None, w=None):
        self.output_stream(s, baddr, w)

    def input_stream(self, n):
        assert (n in [0, 1]), "Incorrect value of n " + str(n) + " in input_stream()"
        self.istream = n

# Input
    def read(self, baddr1, baddr2, time=None, raddr=None, result=None):
        # refresh status bar
        stream = None
        if time != None and raddr != None:
            timer = threading.Timer(time/10, thread.interrupt_main)
            # read in char from current input stream (mouse not implemented)
            try:
                timer.start()
                stream = input()
            except KeyboardInterrupt:
                # CHECK
                # if result is zero vs non zero
                self.call(raddr, result=result, ret="interrupt", n=0)
            timer.cancel()    
        else:
            stream = input()

        stream = stream.lower()
        self.memory.read(baddr1, baddr2, stream)
        if not (self.ver_num in [5, 6] and baddr2 == 0):
            self.memory.tokenise(baddr1, baddr2)
        # if status bar is present, show_status()
        # in v5+ the result is the terminating char
        if self.ver_num in [5, 6]:
            # newline is always a terminating character
            self.store(result, 13)
    
    def read_t(self, baddr1, baddr2, time=None, raddr=None):
        self.read(baddr1, baddr2, time)

    def read_w(self, result, baddr1, baddr2, time=None, raddr=None):
        self.read(baddr1, baddr2, time, result)

    def read_char(self, result, one, time=None, raddr=None):
        assert (one == 1), "Error in read_char()"
        raise NotImplementedError

# Character based output
    def print_char(self, n):
        self.print_(chr(n))
    
    def new_line(self):
        self.print_("\n")
    
    def print_(self, string):
        if self.ostream[0] == True:
            if self.o != None:
                self.o = self.o + string
            else:
                print(string, end="")
        elif self.ostream[2] == True:
            print("Reading to memory")

    def print_rtrue(self, string):
        self.print_(string)
        self.new_line()
        self.rtrue()

    def print_addr(self, baddr):
        string = self.memory.get_string(baddr)
        self.print_(string)

    def print_paddr(self, saddr):
        string = self.memory.get_string(saddr)
        self.print_(string)

    def print_num(self, s):
        self.print_(str(s))

    def print_obj(self, obj):
        obj_var = self.memory.get_obj(obj)
        name = self.memory.get_obj_name(obj_var.properties_add)
        self.print_(name) 

    def print_table(self, baddr, x, y=None, n=None):
        warnings.warn("Not implemented")

    def print_form(self, baddr):
        warnings.warn("Not implemented")

    def scroll_window(self, window, s):
        warnings.warn("Not implemented")

 # Miscellaneous screen input
    def erase_line(self):
        warnings.warn("Not implemented")
    
    def erase_line_n(self, n):
        warnings.warn("Not implemented")

    def erase_window(self, window):
        warnings.warn("Not implemented")

    def draw_picture(self, pic, y=None, x=None):
        warnings.warn("Not implemented")

    def erase_picture(self, pic, y=None, x=None):
        warnings.warn("Not implemented")

    def picture_data(self, is_reversed, offset, n, baddr):
        warnings.warn("Not implemented")

    def picture_table(self, baddr):
        warnings.warn("Not implemented")

# Sound, mouse and menus
    def sound(self, n, op=None, vol=None, raddr=None):
        warnings.warn("Not implemented")

    def read_mouse(self, baddr):
        warnings.warn("Not implemented")
    
    def mouse_window(self, window):
        warnings.warn("Not implemented")

    def make_menu(self, is_reversed, offset, n, baddr):
        warnings.warn("Not implemented")
        
# Save, restore, undo
    def save_b(self, is_reversed, offset):
        warnings.warn("Not implemented")

    def save_r(self, result):
        warnings.warn("Not implemented")

    def save(self, result, baddr1=None, n=None, baddr2=None):
        warnings.warn("Not implemented")

    def restore_b(self, is_reversed, offset):
        warnings.warn("Not implemented")
    
    def restore_r(self, result):
        warnings.warn("Not implemented")

    def restore(self, result, baddr1=None, n=None, baddr2=None):
        warnings.warn("Not implemented")
    
    def save_undo(self, result):
        warnings.warn("Not implemented")

    def restore_undo(self, result):
        warnings.warn("Not implemented")

# Miscellaneous
    def nop(self):
        pass

    def random(self, result, s):
        if s > 0:
            value = random.randint(1, s)
        if s < 0:
            random.seed(s)
            value = random.randint(1, 32767)
        elif s == 0:
            value = random.randint(1, 32767)
        # should the result arg always be 0?
        self.store(0, s)

    def restart(self):
        warnings.warn("Not implemented")
    
    def quit_(self):
        raise KeyboardInterrupt
    
    def show_status(self):
        warnings.warn("Not implemented")
    
    def verify(self, is_reversed, offset):
        condition = self.memory.verify()
        self.branch(condition, is_reversed, offset)

    def piracy(self, is_reversed, offset):
        # always branch since condition is not specified
        self.jump(offset)

    def tokenise(self, baddr1, baddr2, baddr3=None, bit=None):
        self.memory.tokenise(baddr1, baddr2, baddr3, bit)

    def encode_text(self, baddr1, n, p, baddr2):
        self.memory.encode_text(baddr1, n, p, baddr2)

# =============================================================================
# End of Class
# =============================================================================

# path = '/Users/kaizhe/Desktop/Telegram/ifbot/games/'

# # file_name = path + '905.z5'
# # file_name = path + 'zork1.z5'
# file_name = path + 'hhgg.z3'

# file = open(file_name, "rb")

# machine = Interpreter(file)

# try:
#     machine.start(0)
# except:
#     raise 