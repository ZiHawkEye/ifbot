# testing code

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