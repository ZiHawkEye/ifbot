# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:30:51 2018

@author: User
"""
from helper import *

class Memory():
    def __init__(self, file):        
        # determines endianness of bits - big
        # bits are numbered from right to left, counting from zero
        # bit with lowest number is least significant
        self.order = 'big'

        # loads the entirety of the story file
        self.memory = self.load_memory(file)
        
        # sets version number of z machine
        self.ver_num = self.get_ver()
        
        # instantiates object containing predetermined values
        self.help = Helper(self.ver_num)

        # variables containing memory indexes of 'memory' denoting the start and end of each 
        # memory segment
        # dynamic memory starts at 0x00 to BYTE address stored at 0x0e 
        # in the header(defined as first 64 bytes in the story file)        
        self.dynamic = []
        
        # static follows immediately after dynamic,
        # must end by address 0xffff or end of file, whichever is lower
        self.static = []
        
        # high memory begins at the BYTE address stored at 0x04 and 
        # continues to the end of the file
        # may overlap with static memory
        self.high = []
        
        # segments memory into dynamic, static and high
        self.segment_mem()
        
        # addresses of subcategories of header
        # byte address to initialize program counter
        # index of 'memory' where first routine instruction is stored
        self.pc = self.get_pc_start()
        
        # index of 'memory' where abbreviation table is stored
        self.abbrev_start = self.get_abbrev_start()

        # index of 'memory' where global variables are stored
        self.gvars_start = self.get_gvars_start()
        
        # dictionary
        dict_header = self.get_dict_start()
        n = self.get_int(self.memory[dict_header])
        sep_start = dict_header + 1
        # converts each byte to num, then to ascii char
        self.separators = [self.get_num(value) for value in self.memory[sep_start:sep_start + n]]
        self.separators = [chr(value) for value in self.separators]
        self.dict = sep_start + n
        
        # property defaults table before object table
        self.prop_defaults = self.get_property_defaults_start()

        # object table
        self.obj_tb = self.prop_defaults + (31*2) if self.ver_num in [1, 2, 3] else self.prop_defaults + (63*2)        
        
# =============================================================================
# Set Methods for Attributes       
# =============================================================================
    # segments memory
    def segment_mem(self):
        # sorts 'memory' into dynamic, static and high
        # start and end of dynamic
        dstart = 0
        
        # converts 0x0e to index and gets byte address(2 bytes)
        address = self.help.dyn_end_add
        dend = self.get_byte_address(self.memory[address:address + 2])

                
        # start and end of static
        sstart = dend
        
        if len(self.memory) - 1 < 65535:
            send = len(self.memory) - 1
        else:
            send = 65535

        
        # start and end of high
        # converts 0x04 to index and gets byte address(2 bytes) 
        address = self.help.hi_start_add
        hstart = self.get_byte_address(self.memory[address: address + 2])        
        
        hend = len(self.memory) - 1

        
        # marks the start and end of each segment of memory
        self.dynamic = [dstart, dend]
        self.static = [sstart, send]
        self.high = [hstart, hend]

        
    def load_memory(self, file):
        # reads the file in 1 byte elements into 'memory' list and closes the file
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

    def set_gvar(self, var, value):
        if type(value) == int:
            if value < (2 ** 8):
                value = [b'\x00'] + [bytes([value])]
            elif value < (2 ** 16):
                value = self.get_bytes(value, 2)
        assert (len(value) == 2 and type(value[0]) == bytes), "Incorrect format for value " + str(value) + " to be stored in global variable"
        address = self.gvars_start + var*2
        self.memory[address:address + 2] = value[:]

    def storew(self, baddr, n, a):
        if type(a) == int:
            if a < (2 ** 8):
                a = [b'\x00'] + [bytes([a])]
            elif a < (2 ** 16):
                a = self.get_bytes(a, 2)
        assert(len(a) == 2 and type(a[0]) == bytes), "Incorrect format for a " + str(a) + " in storew"
        index = baddr + 2*n
        self.memory[index: index + 2] = a[:]

    def storeb(self, baddr, n, byte):
        if type(byte) == int:
            byte = bytes([byte])
        assert(len(byte) == 1 and type(byte) == bytes), "Incorrect format for byte " + str(byte) + " in storeb"
        index = baddr + n
        self.memory[index] = byte

    def copy_table(self, baddr1, baddr2, s):
        if baddr2 == 0:
            for i in range(s):
                self.memory[baddr1 + i] = 0
        else:
            if s < 0:
                s *= -1 
                # if s is negative, copy forwards table at add1 to add2 even if it corrupts add1 table
                # assume that add1 table entries wont be corrupted before they are read?
                for i in range(s):
                    self.memory[baddr2 + i] = self.memory[baddr1 + i]
            
            elif s > 0:
                # checks if tables overlap
                # if tables overlap then copy backwards to avoid corruption
                # otherwise copy forwards by default
                if baddr1 < baddr2 and baddr1 + s > baddr2:
                    # copies table backwards
                    for i in range(s - 1, -1, -1):
                        self.memory[baddr2 + i] = self.memory[baddr1 + i]
                else:
                    for i in range(s):
                        self.memory[baddr2 + i] = self.memory[baddr1 + i]

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
        return self.pc

    def get_pc_start(self):
        address = self.help.pc_add
        if self.ver_num != 6:
            return self.get_byte_address(self.memory[address:address + 2])
        else:
            return self.get_packed_address(self.memory[address:address + 2])
    
    def get_abbrev_start(self):
        address = self.help.abbrev_add
        return self.get_byte_address(self.memory[address:address + 2])
    
    def get_gvars_start(self):
        address = self.help.gvar_add
        return self.get_byte_address(self.memory[address:address + 2])

    def get_gvar(self, var):
        address = self.gvars_start + var*2
        return self.memory[address:address+2]

    def get_property_defaults_start(self):
        address = self.help.obj_add
        byte_address = self.memory[address:address + 2]
        assert(byte_address != b'\x00'), "No objects detected"
        return self.get_byte_address(byte_address)

    def get_dict_start(self):
        address = self.help.dict_add
        return self.get_byte_address(self.memory[address:address + 2])

    def loadw(self, baddr, n):
        address = baddr + 2*n
        return self.memory[address:address + 2]

    def loadb(self, baddr, n):
        address = baddr + n
        return self.memory[address]
    
    def scan_table(self, a, baddr, n, byte):
        index = baddr
        
        # top bit of byte is 0 to search for a byte, 1 to search for a word, remaining 7 bits 
        # give the unsigned length of an entry in bytes
        # default format is \x82, looking for a word in a table of words
        
        # convert byte to int
        int_byte = self.get_int(byte)
        one = int_byte >> 7
        seven = int_byte - one << 7
        format_word = self.get_int(b'\x82')
        if one == 0:
            assert (len(a) == 1), "Variable a should not be a word in scan_table"  
            assert (seven != format_word), "Wrong format code to search for byte in scan_table"
            for i in range(0, n, 1):
                if self.memory[index + i] == a:
                    return index + i
            return 0
            
        elif one == 1:
            assert (len(a) == 2), "Variable a should not be a byte in scan_table"
            assert (seven == format_word), "Wrong format code to search for word in scan_table"
            for i in range(0, n, 2):
                if self.memory[index + i: index + i + 2] == a[:]:
                    return index + i
            return 0


# =============================================================================
# Helper Functions
# # =============================================================================
# =============================================================================
# Data Structures
# =============================================================================
    # arithmetic
    # converts a hexadecimal number to base 10
    def get_int(self, hexa, order='default'):
        assert (type(hexa) == bytes), "hexa " + str(hexa) + " should be of type bytes"
        if order == 'default':
            num = int.from_bytes(hexa, byteorder=self.order)
        elif order == 'big' or order == 'little':
            num = int.from_bytes(hexa, byteorder=order)
        return num
    
    
    # converts list of hexadecimal numbers to base- 10 integer
    def get_num(self, hexa, signed=False):
        # converts hexa list to int        
        # assert (len(hexa) == 2), "Hexadecimal number is not 2 bytes long for get_num"
        hexanum = b''.join(hexa) if len(hexa) != 1 else hexa
        assert (type(hexanum) == bytes), "hexanum " + str(hexanum) + " should be of type bytes"
        num = self.get_int(hexanum)

        # checks if num is signed 
        if signed == True:
            if num >> 15 == 0:#if the top bit is 0, num is unsigned            
                return num 
            else:
                # CHECK
                return num - 2 ** 16 
        else:
            return num

    # convert integers greater than 1 byte into a list of bytes
    def get_bytes(self, num, bytes_num):
        assert (num < 2 ** (bytes_num*8)), "num " + str(num) + " should be less than " + str(2 ** (bytes_num*8))
        byte_list = []
        for i in range(bytes_num - 1, -1, -1):
            temp = num >> (i*8)
            num -= temp << (i*8)
            byte_list.append(bytes([temp]))
        return byte_list
# =============================================================================
# Text
# =============================================================================
    # converts 2 byte list of hexa char into 1x 1 bit int and 3 5 bit ints
    def get_zscii(self, hexa):
        assert (len(hexa) == 2), "zscii characters should be of 2 bytes"
        # converts hexa to int
        intchar = self.get_num(hexa)
        
        # splits byte into 1 bit followed by 3x 5 bit ints
        zscii = []
        shifts = [15, 10, 5, 0]
        for shift in shifts:    
            # extracts the desired bit substring by shifting the whole string
            # right and autotruncating
            temp = (intchar >> shift) 
            
            # appends substring into zscii list
            zscii.append(temp)
            
            # removes the extracted substring from the overall bit string
            intchar -= (temp << shift)
        
        # zscii list now consists of a 2 byte 'word' broken up into
        # 1x 1 bit int followed by 3x 5 bit ints(aka z chars)
        return zscii
    
    
    # takes in a 5 bit int 'zchar' and maps zscii to characters
    # depending on zmachine version
    def map_zscii(self, zchar, shift=0):
        # special chars
        is_space = (zchar == 0)
        is_newline = ((self.ver_num in [1] and
                        zchar == 1) or
                        (self.ver_num in [2, 3, 4, 5, 6, 7, 8] and
                        (zchar == 7 and shift == 2)))
        if is_space:
            return ' '
        elif is_newline:
            return '\n'
        
        # ascii chars
        else:
            if shift == 0:
                return self.help.lower[zchar]
            elif shift == 1:
                return self.help.upper[zchar]
            elif shift == 2:
                return self.help.punct[zchar]
            else:
                raise Exception("Invalid zscii code")
    
    
    # takes in memory address('memory' index) as argument since the length of a char
    # is not defined apriori
    def get_string(self, address):
        zlist = []
        
        while True:
            # convert 2 byte hexa to list containing 3 zchars and 1 bit (of type int)
            hexa = self.memory[address:address + 2]
            zword = self.get_zscii(hexa)

            # increments memory address
            address += 2
            
            # appends all zchars to zlist
            for i in range(1, 4):
                zlist.append(zword[i])
              
            # checks for terminating condition
            if zword[0] == 1 or (address + 2) > len(self.memory):
                break
                
        charlist = []
        # converts zlist ints to chars
        shift = 0
        # Cannot change loop index inside for loop for python, must use while loop instead
        i = 0
        while i < len(zlist):
            zchar = zlist[i]
            # check if special chars are inside and act accordingly
            is_upper = ((self.ver_num in [1, 2] and
                            zchar in [2, 3, 4, 5]) or
                            (self.ver_num in [3, 4, 5, 6, 7, 8] and
                            zchar == 4))
            is_punct = ((self.ver_num in [1, 2] and
                            zchar in [2, 3, 4, 5]) or
                            (self.ver_num in [3, 4, 5, 6, 7, 8] and
                            zchar == 5))
            is_abbrev = ((self.ver_num in [2] and
                            zchar == 1) or 
                            (self.ver_num in [3, 4, 5, 6, 7, 8] and
                            zchar in [1, 2, 3]))
            is_output = (zchar == 6 and shift == 2)
            if is_upper:
                # shifts to uppercase
                shift = 1
            
            elif is_punct:
                # shifts to punctuation
                shift = 2
                
            elif is_output:
                # literal output character
                a = zlist[i + 1]
                b = zlist[i + 2]
                long_zchar = (a << 5) + b
                # convert to little endian?
                i += 2
                assert (type(long_zchar) == str), "What to do with literal output characters in get_string()?"
                charlist.append(long_zchar)
                
# =============================================================================
# When we encounter A2-06, we read two more Z-characters,
# join the two pentets, interpret the resulting dectet 
# as a little-endian 10-bit integer, 
# and that's the ZSCII character being represented. 
# =============================================================================         
            
            elif is_abbrev:
                # gets abbreviated string
                a = zchar# this works cus zchar is int
                b = zlist[i + 1]
                i += 1 
                                
                entry = (a - 1) * 32 + b # this is the nth entry in the abbrev table, starting from 0
                # gets the index where word address to abbreviation is stored
                wa_index = self.abbrev_start + entry * 2
                
                # gets the word address where abbreviation is stored
                # and converts it to index in 'memory'
                word_address = self.get_word_address(self.memory[wa_index:wa_index + 2])
                
                # finds the z string and appends it to charlist
                temp = self.get_string(word_address)#CHECK IM NOT SURE
                charlist.append(temp)
            
            else:
                # CHECK IM NOT SURE
                # does not use the algorithm involving shift and lock keys
                # maps zscii to characters(depends on the zmachine version)
                ascii_char = self.map_zscii(zchar, shift=shift)
                charlist.append(ascii_char)
                
                # CHECK not sure if this step is correct (only for ver 3+)
                shift = 0
            # increments the while loop
            i += 1
        
        # Updates program counter
        self.pc = address
        zstr = ''.join(charlist)
        # UNDO
        # print("zstr: " + zstr)
        return zstr

# =============================================================================
# Objects
# =============================================================================
    def get_obj(self, obj):
        # obj is a legal obj number (obj is numbered from 1)
        obj_size = self.help.obj_size
        address = self.obj_tb + (obj_size * (obj - 1))
        if self.ver_num in [1, 2, 3]:
            # Get flags (4 bytes)
            flags_int = self.get_num(self.memory[address:address + 4])
            address += 4
            flags = []
            for i in range(31, -1, -1):
                bit = flags_int >> i
                flags.append(bit)
                flags_int -= bit << i
            # Get parent, sibling, child (3 bytes)
            parent = self.get_int(self.memory[address])
            sibling = self.get_int(self.memory[address + 1])
            child = self.get_int(self.memory[address + 2])
            address += 3
            # Get properties (2 bytes)
            properties_add = self.get_byte_address(self.memory[address:address + 2])
            address += 2
            return Object(flags, parent, sibling, child, properties_add)
        elif self.ver_num in [4, 5, 6]:
            address = pc
            # Get flags (6 bytes)
            flags_int = self.get_num(self.memory[address:address + 6])
            address += 6
            flags = []
            for i in range(47, -1, -1):
                bit = flags_int >> i << i
                flags.append(bit)
                flags_int -= bit << i
            # Get parent, sibling, child (6 bytes)
            parent = self.get_num(self.memory[address:address + 2])
            sibling = self.get_num(self.memory[address + 2:address + 4])
            child = self.get_num(self.memory[address + 4:address + 6])
            address += 6
            # Get properties (2 bytes)
            properties_add = self.get_byte_address(self.memory[address:address + 2])
            address += 2
            return Object(flags, parent, sibling, child, properties_add)
    
    def get_properties(self, pc, prop=None, add=None):
        # Returns all properties of object if prop == None
        # Else returns the address of the property, after the size byte
        # Get text-length (1 byte)
        properties = {}
        text_len = self.get_int(self.memory[pc])
        pc += 1
        name = self.get_string(pc)
        assert (self.pc - pc == text_len*2), "Property name length does not equal to stated text_length"
        properties['name'] = name
        # updates pc to point to end of name string
        pc = self.pc
        if self.ver_num in [1, 2, 3]:
            for i in range(31):
                # Get size byte (1 byte)
                size_byte = self.get_int(self.memory[pc])
                pc += 1
                if size_byte == 0:
                    break
                # Get number of data bytes (top 3 bits)
                data_num = (size_byte >> 5) + 1
                # Get property num (bottom 5 bits)
                property_num = size_byte - (size_byte >> 5 << 5)
                if property_num == prop and add == None:
                    # pc should point to located data byte
                    return pc
                elif property_num == prop and add == True:
                    # pc should point to start of property block
                    return pc - 1
                # Get data bytes (data_num bytes)
                data_bytes = self.memory[pc:pc + data_num]
                pc += data_num
                properties[property_num] = data_bytes
        elif self.ver_num in [4, 5, 6]:
            for i in range(63):
                # Get size byte (1 - 2  bytes)
                size_byte = self.get_int(self.memory[pc])
                pc += 1
                if size_byte == 0:
                    break
                one = size_byte << 7
                if one == 1:
                    # if bit one of size byte is 1, size byte has a 2nd byte
                    second_byte = self.get_int(self.memory[pc])
                    pc += 1
                    # Get number of data bytes (bottom 6 bits of second byte)
                    data_num = second_byte - (second_byte >> 6 << 6)    
                else:
                    # size byte is only one byte
                    # Get number of data bytes (top 2 bits)
                    data_num = (size_byte >> 6) + 1
                # Get property num (bottom 6 bits)
                property_num = size_byte - (size_byte >> 6 << 6)
                if prop == property_num and add == None:
                    # pc should point to start of data byte
                    return pc
                elif prop == property_num and add == True:
                    # pc should point to start of property block
                    if one == 1:
                        return pc - 2
                    else:
                        return pc - 1
                # Get data bytes (data_num bytes)
                data_bytes = self.memory[pc:pc + data_num]
                pc += data_num
                properties[property_num] = data_bytes

        return properties

    def set_obj(self, obj, obj_var):
        # takes an object of type Object and encodes it into the object table
        obj_size = self.help.obj_size
        address = self.obj_tb + (obj_size * (obj - 1))
        obj_bytes = []
        if self.ver_num in [1, 2, 3]:
            # Get flags and convert into 4 bytes
            flags = obj_var.flags
            flags_int = 0
            for i in range(32):
                flags_int += flags[i] << (31 - i)
            flags_byte = self.get_bytes(flags_int, 4)
            # Get parent, sibling, child and convert into 1 byte each
            parent_byte = [bytes([obj_var.parent])]
            sibling_byte = [bytes([obj_var.sibling])]
            child_byte = [bytes([obj_var.child])]
            # Get properties and convert into 2 bytes
            properties_byte = self.get_bytes(obj_var.properties_add, 2)
            # obj_var has been encoded into bytes
            obj_bytes = (flags_byte + 
                        parent_byte + 
                        sibling_byte + 
                        child_byte + 
                        properties_byte)
            assert (len(obj_bytes) == 9), "Error encoding object as bytes"
            # read into memory
            self.memory[address:address + 9] = obj_bytes[:]
        elif self.ver_num in [4, 5, 6]:
            # Get flags and convert into 6 bytes
            flags = obj_var.flags
            flags_int = 0
            for i in range(64):
                flags_int += flags[i] << (63 - i)
            flags_byte = self.get_bytes(flags_int, 6)
            # Get parent, sibling, child and convert into 2 bytes each
            parent_byte = [self.get_bytes(obj_var.parent, 2)]
            sibling_byte = [self.get_bytes(obj_var.sibling, 2)]
            child_byte = [self.get_bytes(obj_var.child, 2)]
            # Get properties and convert into 2 bytes
            properties_byte = self.get_bytes(obj_var.properties_add, 2)
            # obj_var has been encoded into bytes
            obj_bytes = (flags_byte + 
                        parent_byte + 
                        sibling_byte + 
                        child_byte + 
                        properties_byte)
            assert (len(obj_bytes) == 9), "Error encoding object as bytes"
            # read into memory
            self.memory[address:address + 14] = obj_bytes[:]

    def put_prop(self, obj, prop, a):
        # Set prop on obj to a. The property must be present on the object(property is in property list? or flag == 1?)
        obj_var = self.get_obj(obj)
        properties = self.get_properties(obj_var.properties_add)
        # Check if property is present on object and set it to a
        try:
            # this may not be necessary
            # assert (obj_var.flags[prop] == 1), "Attribute flag is not set to 1 - object does not have property"
            properties[prop] = a
            a_byte = bytes([a])
        except KeyError:
            print("Property not found in object's property list")
        except ValueError:
            print("a should be byte-valued for put_prop(obj, prop, a)")
        # iterate through properties until specifed property is found, then return address
        prop_add = self.get_properties(obj_var.properties_add, prop=prop)
        # CHECK
        # need some way to test
        # modify property - is it necessary to change size byte of property block? 
        # No, it is not recommended to change the property length in the size byte
        self.memory[prop_add] = a_byte

    def get_prop_len(self, baddr):
        byte = self.memory[baddr]
        if self.ver_num in [1, 2, 3]:
            # get top 3 bits
            prop_len = (byte >> 5) + 1
        elif self.ver_num in [4, 5, 6]:
            # get top bit
            one = byte >> 7
            if one == 0:
                # top 2 bits
                prop_len = (byte >> 6) + 1
            elif one == 1:
                byte = self.memory[baddr + 1]
                # CHECK
                # bottom 6 bits of second byte 
                prop_len = byte - (byte >> 6 << 6)
        return prop_len

# =============================================================================
# Routines and Instructions
# =============================================================================
    # start of a routine: function, interrupt or procedure
    # end of routine: return
    def get_routine(self, pc):
        self.pc = pc
        localvars_num = self.get_int(self.memory[pc])
        self.pc += 1
        localvars = []

        if self.ver_num in [1, 2, 3, 4]:
            for i in range(localvars_num):
                localvars.append(self.memory[self.pc:self.pc + 2])
                self.pc += 2
        elif self.ver_num in [5, 6]:
            for i in range(localvars_num):
                localvars.append(0)

        return localvars
    
    # takes in 'memory' index as argument since the length of an instruction
    # is not defined apriori
    # note: python passes args by assignment so mutable variables can be changed
    # inside the function
    def get_instr(self, pc):
        # an instruction contains a format type, op count, opcode number,
        # types of operands, operands, arguments specifying return addresses
        
        # representations of the 4 different instr formats (includes all except operands)
        # long
        # 0abxxxxx
        # short
        # 10ttxxxx
        # variable
        # 11axxxxx tttttttt
        # extended
        # 0xbe     xxxxxxxx tttttttt
                
        self.pc = pc

        # format is contained within 1 byte of instruction
        byte = self.memory[self.pc]

        # gets format: 0:long, 1:short, 2:variable, 3:extended
        form = self.get_format(byte)

        # UNDO
        if form == 0:
            data = self.memory[pc]
        elif form == 1:
            data = self.memory[pc]
        elif form == 2:
            data = self.memory[pc:pc + 2]
        elif form == 3:
            data = self.memory[pc:pc + 3]
        # UNDO
        print("data: " + str(data))

        # gets opcode
        # if format is extended, the op num is in the 2nd byte
        if form == 3:
            self.pc += 1
            byte = self.memory[self.pc]
            assert (self.pc - pc == 1), "Wrong byte for op num in extended format"
        
        # get opcode number of opcode in int
        op_num = self.get_op_num(byte, form)
        
        # it is an error for a variable instr with 2op code to not have 2 operands
        # unless it is op_code: 2op:1 (CHECK not accounted for)
        # get operand count of opcode: 0:0OP, 1:1OP, 2:2OP or 3:VAR
        op_count = self.get_op_count(byte, form)

        # get sequence of bytes indicating types of operands
        # if format is long or short, operand types are in 1st byte
        # if format is var, operand types are in 2nd byte (next byte)
        # if extended, operand types are in 3rd byte(next byte)
        if form == 0 or form == 1:
            assert (self.pc - pc == 0), "Wrong byte for types in long/short format"
        elif form == 2 or form == 3:
            self.pc += 1
            if form == 2:
                assert (self.pc - pc == 1), "Wrong byte for types in variable format"
            elif form == 3:
                assert (self.pc - pc == 2), "Wrong byte for types in extended format"

        type_seq_add = self.pc
            
        # get operand types
        # there are 2 double variable instructions, where type_seq is of 2 bytes
        # op_code var:1a and op_code var:c 
        if (op_num == self.get_int(b'\x1a') or \
           op_num == self.get_int(b'\x0c')) and op_count == 3:
            type_seq = self.memory[type_seq_add: type_seq_add + 2]
            types = self.get_types(type_seq, form, double=True)
            self.pc += 2
            assert (self.pc - pc == 4), "Wrong byte for operands in extended format, double variable instructions"

        else:
            type_seq = self.memory[type_seq_add]            
            types = self.get_types(type_seq, form)
            self.pc += 1
            if form == 0 or form == 1:
                assert (self.pc - pc == 1), "Wrong byte for operands in long/short format"
            elif form == 2:
                assert (self.pc - pc == 2), "Wrong byte for operands in variable format"
            elif form == 3:
                assert (self.pc - pc == 3), "Wrong byte for operands in extended format"
        
        # get the next sequences of bits representing operands
        # if form is 0, 1 the operands start from the 2nd byte
        # if form is 2 the operands start from the 3rd byte
        # if form is 3 the operands start from the 4th byte
        # all start on the next byte (already incremented)
        op_start = self.pc
        
        operands = self.get_operands(op_start, types)

        # if op_count is 0 - 2, number of elems in types and operands == op_count
        if op_count in range(0, 3):
            assert (op_count == len(types)), 'Number of types does not equal\
                                                op count (0OP, 1OP, 2OP)'
            assert (op_count == len(operands)), 'Number of operands does not \
                                                equal op count (0OP, 1OP, 2OP)'

        # KIND(deduced from form, op count), op num
        # KIND(0:0OP, 1:1OP, 2:2OP, 3:VAR, 4:EXT)
        kind = 0
        if form == 3:
            kind = 4
        else:
            kind = op_count
                    
        # maps instruction to kind and op_num
        instr_details = self.help.op_table[kind][op_num] # instr_details is of type dict
        assert (instr_details != {}), "Not a valid instruction"
        # UNDO
        print(str(instr_details))

        # reads in other data and initializes Instruction obj containing decoded arguments and function reference
        # if multiple arguments are specified, which one is read first?
        str_arg = None
        res_arg = None
        is_reversed = None
        offset = None
        if instr_details["is_str"] == True:
            str_arg = self.get_string(self.pc)

        elif instr_details["is_res"] == True:
            # decode byte variable number
            byte = self.memory[self.pc]
            res_arg = self.get_int(byte)
            self.pc += 1
            # 0: on top of the routine stack
            # 1-15: the local variable
            # 16-255: global variable of that num - 16

        if instr_details["is_br"] == True:
            # the branch argument is always the last of the sequence of arguments
            # checks bit 2 to see if branch arg is 1 or 2 bytes
            byte = self.memory[self.pc]
            int_byte = self.get_int(byte)
            # gets bit 2
            one = (int_byte >> 7)
            two = (int_byte >> 6) - (one << 1)
            # checks if reverse logic
            is_reversed = True if one == 0 else False
            is_one = True if (two == 1) else False
            br_arg_byte = self.memory[self.pc] if is_one else self.memory[self.pc: self.pc + 2]
            br_arg = self.get_num(br_arg_byte)
            # gets offset
            # unsigned if 1 byte and signed if 2
            if is_one:
                offset = (br_arg - (br_arg >> 6 << 6))
            else:
                signed_bits = (br_arg - (br_arg >> 14 << 14))
                offset = signed_bits if (signed_bits < 1 << 13) else (signed_bits - n ** 14)

            self.pc = self.pc + 1 if is_one else self.pc + 2

        # program counter should point to end of instruction at this point

        # data conversion for operands
        op_types = instr_details["types"]
        if op_types != []:
            for i in range(len(operands)):
                opt = op_types[i]
                op = operands[i]
                
                if opt == "s" or opt == "t":
                    operands[i] = self.get_num(op, signed=True)

                elif opt == "bit":
                    operands[i] = self.get_int(op)

                elif opt == "byte":
                    pass

                elif opt == "var":
                    assert (len(op) == 1), "Variable number operand is not 1 byte"
                    operands[i] = self.get_int(op)

                elif opt == "baddr":
                    operands[i] = self.get_byte_address(op)

                elif opt == "raddr":
                    operands[i] = self.get_packed_address(op, is_routine_call=True)

                elif opt == "saddr":
                    operands[i] = self.get_packed_address(op, is_print_paddr=True)

                elif opt == "obj":
                    operands[i] = self.get_int(op)

                elif opt == "attr":
                    operands[i] = self.get_int(op)

                elif opt == "prop":
                    operands[i] = self.get_int(op)

                elif opt == "window":
                    pass

                elif opt == "time":
                    pass

                elif opt == "pic":
                    pass

                else:
                    operands[i] = self.get_num(op)

        # initializes instr obj with values/args
        # types may not be necessary for execution
        name = instr_details['name']
        instr = Instruction(name, types, operands, str_arg, res_arg, is_reversed, offset)
        return instr
        
    # gets format of opcode and returns the corresponding int
    def get_format(self, byte):
        # default format: long
        # if top 2 bits of opcode are 11 the form is variable, 10: short
        # if opcode is 0xbe and ver is 5 or later, form is extended
        # opcode for all except extended are 1 byte long
        
        # converts byte to int
        int_byte = self.get_int(byte)
        
        # if 1st bit is 0, long
        if (int_byte >> 7) == 0:
            return 0
        # if 1st 2 bits is 10, short
        elif (int_byte >> 6) == 2:
            return 1
        # if 1st 2 bits is 11, variable
        elif (int_byte >> 6) == 3:
            return 2
        # if the byte is of value '0xbe' and ver_num is 5+, extended
        if self.ver_num >= 5 and int_byte == self.get_int(b'\xbe'):
            return 3
        
        
    # gets operand count of opcode: 0:0OP, 1:1OP, 2:2OP or 3:VAR
    def get_op_count(self, byte, form):
        # converts from byte to int
        int_byte = self.get_int(byte)
        
        if form == 0:
            # long
            return 2
            
        elif form == 1:
            # short
            # gets bits 3 and 4 of the opcode
            operand_type = (int_byte >> 4) - (int_byte >> 6 << 2)
            
            # if bits 3,4 are 11
            if operand_type == 3:
                return 0
            else:
                return 1
            
        elif form == 2:
            # variable
            # gets bit 3
            bit = (int_byte >> 5) - (int_byte >> 6 << 1)
            
            if bit == 0:
                return 2
            else:
                return 3
            
        elif form == 3:
            # extended
            return 3
        
    # gets opcode number
    def get_op_num(self, byte, form):
        # converts opcode from byte to int
        int_byte = self.get_int(byte)
        
        if form == 0:
            # long
            # gets the last 5 bits of the op code
            return int_byte - (int_byte >> 5 << 5)
            
        elif form == 1:
            # short
            # gets last 4 bits of op code
            return int_byte - (int_byte >> 4 << 4)
            
        elif form == 2:
            # variable
            # returns the last 5 bits of the op code
            return int_byte - (int_byte >> 5 << 5)
            
        elif form == 3:
            # extended
            # the whole byte is the op_num
            return int_byte
        
    # gets operands by returning a list
    def get_operands(self, op_start, types):
        self.pc = op_start
        operands = []
        byte_operand = []
        
        for args in types:
            if args == 0:
                # large - 2 bytes
                byte_operand = self.memory[self.pc:self.pc + 2]
                self.pc += 2
                
            elif args == 1 or args == 2:
                # small and variable - 1 byte
                byte_operand = self.memory[self.pc]
                self.pc += 1           
                
            # operand is a byte list
            # operands should be a nested list
            operands.append(byte_operand)

        return operands
        
    # gets operand types:0:large(2 bytes), 1:small(1 byte),
    # 2:variable(1 byte), 3:omitted(0 bytes and not appended)
    def get_types(self, type_seq, form, double=False):
        # converts from byte to int
        int_type_seq = self.get_int(type_seq)

        # gets operand types and returns a list
        types = []
        if form == 0:
            # long
            # gets bits 2, 3
            bits = (int_type_seq >> 5) - (int_type_seq >> 7 << 2)
            
            bitlist = []
            
            # bit 2 gives the type of the first operand
            two = bits >> 1
            bitlist.append(two)
            
            # bit 3 gives the type of the second operand
            three = bits - (bits >> 1 << 1)
            bitlist.append(three)
            
            assert (bits == (two << 1) + three), "Error in getting bits to determine types for long format"

            for bit in bitlist:
                if bit == 0:
                    # small
                    types.append(1)
                elif bit == 1:
                    # variable
                    types.append(2)
            
        elif form == 1:
            # short
            # gets bits 3,4 
            bits = (int_type_seq >> 4) - (int_type_seq >> 6 << 2)
            
            if bits != 3:
                # bits corresponds to the type
                types.append(bits)
            
        elif form == 2 or form == 3:
            # variable or extended
            bitlist = []
            # if double variable
            if double == True:
                n = 16 # bits
            else:
                n = 8 # bits
            
            # splits byte seq into 2 bit sequences
            for i in range(n - 2, -2, -2):
                temp = (int_type_seq >> i) - (int_type_seq >> (i + 2) << 2 )
                bitlist.append(temp)

            temp = 0
            for i in range(len(bitlist)):
                temp += bitlist[i] << n - 2 - i*2
            assert temp == int_type_seq, "Error in splitting bits to determine types for variable/extended format"
            
            for bits in bitlist:
                # it is an error if an omitted type occurs before a non omitted type
                if bits == 3:
                    break
                # bits corresponds to the type
                types.append(bits)            
                
        return types
    
    
# =============================================================================
# Memory Addresses    
# =============================================================================
    # converts byte address list(2 bytes/elems long) to index in 'memory'
    def get_byte_address(self, byte_list):
        # assert (len(byte_list) == 2), "Byte address " +  str(byte_list) + " is not 2 bytes" 
        index = self.get_num(byte_list)
        return index
    
    # converts word address list(2 bytes/elems long) to index in 'memory'
    def get_word_address(self, word_list):
        index = self.get_byte_address(word_list) * 2
        return index
    
    # converts packed address list(2 bytes/elems long) to index in 'memory'
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
                # gets the routine offset in hexadecimal
                # gets int memory address
                address = self.help.ro_add
                rohexa = self.memory[address]
                
                # converts hexadecimal to int offset
                ro = self.get_int(rohexa)
                index = 4 * pindex + ro
                
            elif is_print_paddr:
                # gets the string offset in hexadecimal
                # gets int memory address
                address = self.help.so_add
                sohexa = self.memory[address]
                
                # converts hexadecimal to int offset
                so = self.get_int(sohexa)
                index = 4 * pindex + so
                
        elif vn == 8:
            index = 8 * pindex
        
        
        return index

# =============================================================================
# End of Class
# =============================================================================



    

