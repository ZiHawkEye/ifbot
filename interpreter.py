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
#consider converting all of memory to int list?
#what are dectets used for in zstrings?

import warnings
import threading
import random
from memory import Memory
from helper import *
from frame import *
from window import *
from math import *

class Interpreter():
    def __init__(self, file):        
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
            first_frame = Frame5(pc, [], None)
        elif self.ver_num == 6:
            localvars = self.memory.get_routine(pc)
            pc = self.memory.get_pc
            first_frame = Frame5(pc, localvars, None)
        self.stack.append(first_frame)
        self.cur_frame = first_frame

    def start(self):
        # start to execute instructions
        for i in range(200):
            self.cur_frame = self.stack[-1]
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
                    # UNDO
                    # print("op: " + str(operands[i]) + " var: " + str(var))

            # updates program counter 
            # this ensures that the program counter is not affected by the execution of instructions except for call instructions
            self.cur_frame.set_pc(self.memory.get_pc())
            # UNDO
            # print('0x{0:02x}'.format(self.cur_frame.get_pc()))
            # executes
            # UNDO
            # print('ops: ' + str(instr.operands) + " args: " + str(instr.arguments))
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
        assert (len(value) == 2 and type(value[0]) == int), "Incorrect format of value in loadw"
        self.store(result, value)

    def loadb(self, result, baddr, n):
        value = self.memory.loadb(baddr, n)
        assert(type(value) == int), "Incorrect format of value in loadb"
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
        self.load(0, var)
        temp = self.pop()
        temp = temp if type(temp) == int else self.memory.get_num(temp)
        temp += 1
        self.store(var, temp)

    def dec(self, var):
        self.load(0, var)
        temp = self.pop()
        temp = temp if type(temp) == int else self.memory.get_num(temp)
        temp -= 1
        self.store(var, temp)

    def inc_jg(self, is_reversed, offset, var, s):
        self.inc(var)
        self.load(0, var)
        temp = self.pop()
        self.jg(is_reversed, offset, temp, s)

    def dec_jl(self, is_reversed, offset, var, s):
        self.dec(var)
        self.load(0, var)
        temp = self.pop()
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
            pass
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
        condition = a & b
        self.branch(condition, is_reversed, offset)

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
        self.cur_frame = self.stack[-1]
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
        # obj refers to a legal obj number
        # Gets the object of type Object 
        obj_var = self.memory.get_obj(obj)
        # sibling is a legal obj number
        # sibling should be value 0 if it doesnt exist
        sibling = obj_var.sibling
        self.store(result, sibling)
        condition = sibling != 0
        self.branch(condition, is_reversed, offset)

    def get_child(self, result, is_reversed, offset, obj):
        # obj refers to a legal obj number
        # Gets the object of type Object 
        obj_var = self.memory.get_obj(obj)
        # child is a legal obj number 
        # child should be value 0 if it doesnt exist
        child = obj_var.child
        self.store(result, child)
        condition = child != 0
        self.branch(condition, is_reversed, offset)

    def get_parent(self, result, obj):
        # obj refers to a legal obj number
        # Gets the object of type Object
        obj_var = self.memory.get_obj(obj)
        # parent is a legal obj number
        # parent should be value 0 if it doesnt exist
        parent = obj_var.parent
        self.store(result, parent)

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
        # attributes are numbered from 0 onwards
        condition = obj_var.flags[attr] == 1
        self.branch(condition, is_reversed, offset)

    def set_attr(self, obj, attr):
        obj_var = self.memory.get_obj(obj)
        # attributes are numbered from 0 onwards
        obj_var.flags[attr] = 1
        # Encode object
        self.memory.set_obj(obj, obj_var)

    def clear_attr(self, obj, attr):
        obj_var = self.memory.get_obj(obj)
        # attributes are numbered from 0 onwards
        obj_var.flags[attr] = 0
        # Encode object
        self.memory.set_obj(obj, obj_var)

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
            assert (len(obj_prop) <= 2), "Property " + str(obj_prop) + " of " + properties['name'] + " is greater than 2 bytes"
            self.store(result, obj_prop)
        except KeyError:
            # Property not present on obj, get default 
            # properties are numbered from 1
            self.loadw(result, self.memory.prop_defaults, prop - 1)

    def get_prop_addr(self, result, obj, prop):
        obj_var = self.memory.get_obj(obj)
        properties = self.memory.get_properties(obj_var.properties_add)
        try:
            obj_prop = properties[prop]    
        except KeyError:
            print("Property does not exist on the obj")
        address = self.memory.get_properties(obj_var.properties_add, prop=prop, add=True)
        self.store(result, address)
    
    def get_next_prop(self, result, obj, prop):
        # if prop is 0, get the value of the highest property number
        # else get the next prop (lower prop num)
        # store as result
        obj_var = self.memory.get_obj(obj)
        properties = self.memory.get_properties(obj_var.properties_add)
        if prop == 0:
            temp = 0
            for key in properties:
                if key != "name":
                    if key > temp:
                        temp = key
        else:
            temp = 0
            for key in properties:
                if key != "name":
                    if key < prop and key > temp:
                        temp = key
        self.store(result, temp)

    def get_prop_len(self, result, baddr):
        prop_len = self.memory.get_prop_len(baddr)
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

    def read_char(self, one, time=None, raddr=None):
        assert (one == 1), "Error in read_char()"

# Character based output
    def print_char(self, n):
        self.print_(chr(n))
    
    def new_line(self):
        self.print_("\n")
    
    def print_(self, string):
        if self.ostream[0] == True:
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
        properties_add = obj_var.properties_add
        properties = self.memory.get_properties(properties_add)
        self.print_(properties["name"]) 

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
    
    def quit(self):
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

path = '/Users/kaizhe/Desktop/Telegram/ifbot/games/'

# file_name = path + 'zork1.z5'
file_name = path + 'hhgg.z3'

# opens file in binary
file = open(file_name, "rb")

machine = Interpreter(file)

# UNDO
machine.start()