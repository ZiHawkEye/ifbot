# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:30:51 2018

@author: User
"""
from helper import Helper
from helper import Instruction

class Memory():
    def __init__(self, file):        
        #determines endianness of bits - big
        #bits are numbered from right to left, counting from zero
        #bit with lowest number is least significant
        self.order = 'big'

        #loads the entirety of the story file
        self.memory = self.load_memory(file)
        
        #sets version number of z machine
        self.ver_num = self.get_ver()
        
        #instantiates object containing predetermined values
        self.help = Helper(self.ver_num)

        #variables containing memory indexes of 'memory' denoting the start and end of each 
        #memory segment
        #dynamic memory starts at 0x00 to BYTE address stored at 0x0e 
        #in the header(defined as first 64 bytes in the story file)        
        self.dynamic = []
        
        #static follows immediately after dynamic,
        #must end by address 0xffff or end of file, whichever is lower
        self.static = []
        
        #high memory begins at the BYTE address stored at 0x04 and 
        #continues to the end of the file
        #may overlap with static memory
        self.high = []
        
        
        #segments memory into dynamic, static and high
        self.segment_mem()
        
        #addresses of subcategories of header
        #byte address to initialize program counter
        #index of 'memory' where first routine instruction is stored
        self.program_counter = self.get_pc()
        
        #index of 'memory' where abbreviation table is stored
        self.abbrev_table = self.get_abbrev()
        
        #dictionary
        self.dict = 0
        
        #object tree
        self.obj_tree = 0
        
        
# =============================================================================
# Set Methods for Attributes       
# =============================================================================
    #segments memory
    def segment_mem(self):
        #sorts 'memory' into dynamic, static and high
        #start and end of dynamic
        dstart = 0
        
        #converts 0x0e to index and gets byte address(2 bytes)
        address = self.help.dyn_end_add
        dend = self.get_byte_address(self.memory[address:address + 2])

                
        #start and end of static
        sstart = dend
        
        if len(self.memory) - 1 < 65535:
            send = len(self.memory) - 1
        else:
            send = 65535

        
        #start and end of high
        #converts 0x04 to index and gets byte address(2 bytes) 
        address = self.help.hi_start_add
        hstart = self.get_byte_address(self.memory[address: address + 2])        
        
        hend = len(self.memory) - 1

        
        #marks the start and end of each segment of memory
        self.dynamic = [dstart, dend]
        self.static = [sstart, send]
        self.high = [hstart, hend]

        
    def load_memory(self, file):
        #reads the file in 1 byte elements into 'memory' list and closes the file
        memory = []
        
        try:
            while True:
                byte = file.read(1)
                memory.append(byte)
                if not byte:
                    break
                
        finally:
            file.close()
        
        return memory

# =============================================================================
# Get Methods for Attributes
# =============================================================================
    def get_ver(self):
        return self.get_int(self.memory[0])
    
    def get_memory(self):
        #can't just return must make a copy otherwise you're just aliasing
        memory = self.memory[:]
        return memory
    
    def get_dynamic(self):
        dynamic = self.dynamic[:]
        return dynamic
    
    def get_static(self):
        static = self.static[:]
        return static
    
    def get_high(self):
        high = self.high[:]
        return high
    
    def get_pc(self):
        address = self.help.pc_add
        if self.ver_num != 6:
            return self.get_byte_address(self.memory[address:address + 2])
        else:
            return self.get_packed_address(self.memory[address:address + 2]) + 1
    
    def get_abbrev(self):
        address = self.help.abbrev_add
        return self.get_byte_address(self.memory[address:address + 2])
    

    
# =============================================================================
# Helper Functions
# # =============================================================================
# =============================================================================
# Data Structures
# =============================================================================
    #arithmetic
    #converts a hexadecimal number to base 10
    def get_int(self, hexa, order='default'):
        if order == 'default':
            num = int.from_bytes(hexa, byteorder=self.order)
        elif order == 'big' or order == 'little':
            num = int.from_bytes(hexa, byteorder=order)
        return num
    
    
    #converts list of hexadecimal numbers(2 bytes/elems long) to base- 10 integer
    def get_num(self, hexa, signed=False):
        #converts hexa list to int
        hexanum = b''.join(hexa)
        num = self.get_int(hexanum)

        #checks if num is signed 
        if signed == True:
            if num >> 15 == 0:#if the top bit is 0, num is unsigned            
                return num 
            else:
                return num - 2 ** 16 
        else:
            return num
    
# =============================================================================
# Text
# =============================================================================
    #converts 2 byte list of hexa char into 1x 1 bit int and 3 5 bit ints
    def get_zscii(self, hexa):
        #probably a more efficient way to do this
        #converts hexa to int
        intchar = self.get_num(hexa)
        
        #splits bit into 1 bit followed by 3x 5 bit ints
        zscii = []
        shift = [15, 10, 5, 0]
        for i in range(4):    
            n = shift[i]
            #extracts the desired bit substring by shifting the whole string
            #right and autotruncating
            temp = (intchar >> n) 
            
            #appends substring into zscii list
            zscii.append(temp)
            
            #removes the extracted substring from the overall bit string
            intchar -= (temp << n)
        
        #zscii list now consists of a 2 byte 'word' broken up into
        #1x 1 bit int followed by 3x 5 bit ints(aka z chars)
        return zscii
    
    
    #takes in a 5 bit int 'zchar' and maps zscii to characters
    #depending on zmachine version
    def map_zscii(self, zchar, shift=0):
        #special chars
        if self.help.check_space(zchar, shift):
            return ' '
        elif self.help.check_newline(zchar, shift):
            return '\n'
        
        #ascii chars
        else:
            if shift == 0:
                #uppercase
                return self.help.lower[zchar]
            elif shift == 1:
                #lowercase
                return self.help.upper[zchar]
            elif shift == 2:
                #punctuation
                return self.help.punct[zchar]
    
    
    #takes in memory address('memory' index) as argument since the length of a char
    #is not defined apriori
    def get_string(self, address):
        zlist = []
        memadd = address
        
        while True:
            #convert 2 byte hexa to list containing 3 zchars and 1 bit (of type int)
            hexa = self.memory[memadd:memadd + 2]
            zword = self.get_zscii(hexa)
            
            #appends all zchars to zlist
            for i in range(1, 4):
                zlist.append(zword[i])
              
            #checks for terminating condition
            if zword[0] == 1 or (memadd + 2) > len(self.memory):
                break
            
            #increments memory address
            memadd += 2
        
        
        charlist = []
        #converts zlist ints to chars
        shift = 0
        for i in range(len(zlist)):
            zchar = zlist[i]
            #check if special chars are inside and act accordingly
            if self.help.check_upper(zchar, shift):
                #shifts to uppercase
                shift = 1
            
            elif self.help.check_punct(zchar, shift):
                #shifts to punctuation
                shift = 2
                
            elif self.help.check_output(zchar, shift):
                #literal output character
                a = zlist[i + 1]
                b = zlist[i + 2]
                long_zchar = (a << 5) + b
                #convert to little endian?
                i += 2#will increment one more after the loop ends
                charlist.append(long_zchar)
                
# =============================================================================
# When we encounter A2-06, we read two more Z-characters,
# join the two pentets, interpret the resulting dectet 
# as a little-endian 10-bit integer, 
# and that's the ZSCII character being represented. 
# =============================================================================         
            
            elif self.help.check_abbrev(zchar, shift):
                #gets abbreviated string
                a = zchar#this works cus zchar is int
                b = zlist[i + 1]
                i += 1#will increment one more after the loop ends                
                                
                #gets the index where word address to abbreviation is stored
                word_address_index = self.abbrev_table + (a - 1) * 32 + b
                
                #gets the word address where abbreviation is stored
                #and converts it to index in 'memory'
                word_address = self.get_word_address(
                        self.memory[word_address_index:word_address_index + 2])
                
                #finds the z string and appends it to charlist
                temp = self.get_string(word_address)#CHECK IM NOT SURE
                for word in temp:
                    charlist.append(word)
            
            else:
                #CHECK IM NOT SURE
                #does not use the algorithm involving shift and lock keys
                #maps zscii to characters(depends on the zmachine version)
                ascii_char = self.map_zscii(zchar, shift=shift)
                charlist.append(ascii_char)
                
                #CHECK not sure if this step is correct
                shift = 0
        
        return charlist



# =============================================================================
# Routines and Instructions
# =============================================================================
    #takes in 'memory' index as argument since the length of an instruction
    #is not defined apriori
    #instr arg is a Instruction object (refer to helper.py)
    #types of operands, operands
    #returns the program counter
    #note: python passes args by assignment so mutable variables can be changed
    #inside the function
    #HOW TO PASS PROGRAM COUNTER IN BY REFERENCE?
    #MAKE AN INSTR CLASS CONTAINING 5 ELEMS AND THE PROGRAM COUNTER?
    def get_instr(self, pc):
        #an instruction contains a format type, op count, opcode number,
        #types of operands, operands, arguments specifying return addresses
        
        #representations of the 4 different instr formats (includes all except operands)
        #long
        #0abxxxxx
        #short
        #10ttxxxx
        #variable
        #11axxxxx tttttttt
        #extended
        #0xbe     xxxxxxxx tttttttt
                
        #format is contained within 1 byte of instruction
        byte = self.memory[pc]
        #UNDO
        #print('byte ' + str(byte))
        

        #gets format: 0:long, 1:short, 2:variable, 3:extended
        form = self.get_format(byte)
        #UNDO
        #print('form ' + str(form))
        

        #gets opcode
        #if format is extended, the op num is in the 2nd byte
        if form == 3:
            pc += 1
            byte = self.memory[pc]
        
        #get opcode number of opcode in int
        op_num = self.get_op_num(byte, form)
        #UNDO
        #print('op_num ' + str(op_num))

        
        #it is an error for a variable instr with 2op code to not have 2 operands
        #unless it is op_code: 2op:1 (CHECK not accounted for)
        #get operand count of opcode: 0:0OP, 1:1OP, 2:2OP or 3:VAR
        op_count = self.get_op_count(byte, form)
        #UNDO
        #print('op_count ' + str(op_count))


        #get sequence of bytes indicating types of operands
        #if format is long or short, operand types are in 1st byte
        #if format is var, operand types are in 2nd byte (next byte)
        #if extended, operand types are in 3rd byte(next byte)
        if form == 0 or form == 1:
            pc += 0
        elif form == 2 or form == 3:
            pc += 1

        type_seq_add = pc
            
        #get operand types
        #there are 2 double variable instructions, where type_seq is of 2 bytes
        #op_code var:1a and op_code var:c 
        #get_types was changed (double == True)
        types = []
        if (op_num == self.get_int(b'\x1a') or \
           op_num == self.get_int(b'\x0c')) and op_count == 3:
            
            type_seq = self.memory[type_seq_add: type_seq_add + 2]
            types = self.get_types(type_seq, form, double=True)
            pc += 2

        else:
            type_seq = self.memory[type_seq_add]            
            types = self.get_types(type_seq, form)
            pc += 1
        
        
        #get the next sequences of bits representing operands
        #if form is 0, 1 the operands start from the 2nd byte
        #if form is 2 the operands start from the 3rd byte
        #if form is 3 the operands start from the 4th byte
        #all start on the next byte (already incremented)
        op_start = pc
        
        #CHECK
        
        #get operands - pass in address because the length is not determined apriori?
        #what does each type represent? determined by the function
        #returns pc
        operands = []
        pc = self.get_operands(op_start, types, operands)
        
        #error catching
        #if op_count is 0 - 2, number of elems in types and operands == op_count
        if op_count in range(0, 3):
            assert (op_count == len(types)), 'Number of types does not equal\
                                                op count (0OP, 1OP, 2OP)'
            assert (op_count == len(operands)), 'Number of operands does not \
                                                equal op count (0OP, 1OP, 2OP)'

        #instr requires 3 args to be (re?)initiated (is this permanent after the function terminates?):
        #KIND(deduced from form, op count), op num
        #KIND(0:0OP, 1:1OP, 2:2OP, 3:VAR, 4:EXT)
        kind = 0
        if form == 3:
            kind = 4
        else:
            kind = op_count
            
        instr = Instruction(self.ver_num, kind, op_num)
        
        #should map instruction to function after this (done automatically in
        #Instruction class)
        #check for args and read them in, also perform conversion into types in memory
        #Instruction should contain kind, op_num, operands (converted into data types)
        #there has to be a better way to do this - the attributes of Instruction obj
        #depend on methods in Memory
        #alternatively, view it as all mapping is performed in helper and data conversion in memory
        
        
        #check_add() in Instruction - pass in instruction obj and modify accordingly
        #check_add() requires reading from memory
        #pass instr obj into function
        #execute() in interpreter (but execution might require reading from memory?)
        
        return [pc, instr]
        
    #gets format of opcode and returns the corresponding int
    def get_format(self, byte):
        #default format: long
        #if top 2 bits of opcode are 11 the form is variable, 10: short
        #if opcode is 0xbe and ver is 5 or later, form is extended
        #opcode for all except extended are 1 byte long
        
        #converts byte to int
        int_byte = self.get_int(byte)
        
        #if 1st bit is 0, long
        if (int_byte >> 7) == 0:
            return 0
        #if 1st 2 bits is 10, short
        elif (int_byte >> 6) == 2:
            return 1
        #if 1st 2 bits is 11, variable
        elif (int_byte >> 6) == 3:
            return 2
        #if the byte is of value '0xbe' and ver_num is 5+, extended
        if self.ver_num >= 5 and int_byte == self.get_int(b'\xbe'):
            return 3
        
        
    #gets operand count of opcode: 0:0OP, 1:1OP, 2:2OP or 3:VAR
    def get_op_count(self, byte, form):
        #converts from byte to int
        int_byte = self.get_int(byte)
        #UNDO
        #print('int_byte ' + str(int_byte))
        
        if form == 0:
            #long
            return 2
            
        elif form == 1:
            #short
            #gets bits 3 and 4 of the opcode
            operand_type = (int_byte >> 4) - (int_byte >> 6 << 2)
            
            #if bits 3,4 are 11
            if operand_type == 3:
                return 0
            else:
                return 1
            
        elif form == 2:
            #variable
            #gets bit 3
            bit = (int_byte >> 5) - (int_byte >> 6 << 1)
            
            if bit == 0:
                return 2
            else:
                return 3
            
        elif form == 3:
            #extended
            return 3
        
    #gets opcode number
    def get_op_num(self, byte, form):
        #converts opcode from byte to int
        int_byte = self.get_int(byte)
        
        if form == 0:
            #long
            #gets the last 5 bits of the op code
            return int_byte - (int_byte >> 5 << 5)
            
        elif form == 1:
            #short
            #gets last 4 bits of op code
            return (int_byte - (int_byte >> 4 << 4))
            
        elif form == 2:
            #variable
            #returns the last 5 bits of the op code
            return (int_byte - (int_byte >> 5 << 5)) 
            
        elif form == 3:
            #extended
            #the whole byte is the op_num
            return int_byte
        
    #gets operands by returning a list
    def get_operands(self, op_start, types, operands):
        cur = op_start
        byte_operand = []
        
        for args in types:
            if args == 0:
                #large - 2 bytes
                byte_operand = self.memory[cur:cur + 2]
                cur += 2
                
            elif args == 1 or args == 2:
                #small and variable - 1 byte
                byte_operand = self.memory[cur]
                cur += 1           
                
            #operand is a byte list
            #CHECK IM NOT SURE BUT just append as is
            #operands should be a nested list
            operands.append(byte_operand)

        return cur        
        
    #gets operand types:0:large(2 bytes), 1:small(1 byte),
    #2:variable(1 byte), 3:omitted(0 bytes and not appended)
    def get_types(self, type_seq, form, double=False):
        #converts from byte to int
        int_type_seq = self.get_int(type_seq)
        #UNDO
        #print('int_type_seq ' + str(int_type_seq))
        
        #gets operand types and returns a list
        types = []
        if form == 0:
            #long
            #gets bits 2, 3
            bits = (int_type_seq >> 5) - (int_type_seq >> 7 << 2)
            
            bitlist = []
            
            #bit 2 gives the type of the first operand
            two = bits >> 1
            bitlist.append(two)
            
            #bit 3 gives the type of the second operand
            three = bits - (bits >> 1 << 1)
            bitlist.append(three)
            
            for bit in bitlist:
                if bit == 0:
                    #small
                    types.append(1)
                elif bit == 1:
                    #variable
                    types.append(2)
            
        elif form == 1:
            #short
            #gets bits 3,4 
            bits = (int_type_seq >> 4) - (int_type_seq >> 6 << 2)
            
            if bits != 3:
                #bits corresponds to the type
                types.append(bits)
            
        elif form == 2 or form == 3:
            #variable or extended
            bitlist = []
            #if double variable
            if double == True:
                n = 14
            else:
                n = 6
            
            #splits byte seq into 2 bit sequences
            for i in range(n, -2, -2):
                temp = (int_type_seq >> i) - (int_type_seq >> (i + 2) << 2 )
                bitlist.append(temp)
            #UNDO
            #print('bitlist ' + str(bitlist))
            
            for bits in bitlist:
                #it is an error if an omitted type occurs before a non omitted type
                if bits == 3:
                    break
                #bits corresponds to the type
                types.append(bits)            
                
        return types
    
    
# =============================================================================
# Memory Addresses    
# =============================================================================
    #converts byte address list(2 bytes/elems long) to index in 'memory'
    def get_byte_address(self, byte_list): 
        index = self.get_num(byte_list)
        return index
    
    #converts word address list(2 bytes/elems long) to index in 'memory'
    def get_word_address(self, word_list):
        index = self.get_byte_address(word_list) * 2
        return index
    
    #converts packed address list(2 bytes/elems long) to index in 'memory'
    def get_packed_address(self, packed_list, is_routine_call = False, 
                           is_print_paddr = False):
        pindex = self.get_byte_address(packed_list)
        
        
        vn = self.ver_num
        if vn == 1 or vn == 2 or vn == 3:
            index = 2 * pindex
        
        elif vn == 4 or vn == 5:
            index = 4 * pindex
        
        elif vn  == 6 or vn == 7: 
            if is_routine_call:
                #gets the routine offset in hexadecimal
                #gets int memory address
                address = self.help.ro_add
                rohexa = self.memory[address]
                
                #converts hexadecimal to int offset
                ro = self.get_int(rohexa)
                index = 4 * pindex + ro
                
            elif is_print_paddr:
                #gets the string offset in hexadecimal
                #gets int memory address
                address = self.help.so_add
                sohexa = self.memory[address]
                
                #converts hexadecimal to int offset
                so = self.get_int(sohexa)
                index = 4 * pindex + so
                
        elif vn == 8:
            index = 8 * pindex
        
        
        return index

# =============================================================================
# End of Class
# =============================================================================



    

