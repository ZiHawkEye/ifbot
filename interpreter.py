# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 22:09:06 2018

@author: User
"""

#TODO
#how to pass a reference to interpreter methods from helper?
#foo = class.method
#foo(obj)

#read from memory
#return instruction obj
#finish the stack class and program counter
#link the stack to the memory so interpreter can execute instructions

from memory import Memory
from helper import Helper

#implement program counter and stack
#map instructions to functions

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
        self.program_counter = self.memory.get_pc()
        self.stack = []
        self.routine_call_state = 0

        # start to execute instructions
        # issue with dectets, abbrev?
        for i in range(3):
            # gets instr details 
            instr = self.memory.get_instr(self.program_counter)
            # executes
            print('operands: ' + str(instr.operands))
            # updates program counter
            self.program_counter = self.memory.get_pc()
        
# =============================================================================
# Get Methods
# =============================================================================
        
# # Operations
#     def rtrue(self):
#     def rfalse(self):
#     def print_(self):
#     def print_rtrue(self):
#     def nop(self):
#     def save_b(self):
#     def restore_b(self):
#     def save_r(self):
#     def restore_r(self):
#     def restart(self):
#     def retpulled(self):
#     def pop(self):
#     def catch(self):
#     def quit(self):
#     def (self):
#     def (self):


# =============================================================================
# End of Class
# =============================================================================

#testing code
file_name = 'C:/Users/User/Desktop/TelegramBot/ifbot/games/hhgg.z3'

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
