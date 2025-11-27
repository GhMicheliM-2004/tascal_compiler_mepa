
#------------------------------------------------------------------------#
#                                                                        #
# Last update: "mepa_instr_en.py: 2015-08-08 (Sat)  12:19:29 BRT (tk)"   #
#                                                                        #
#------------------------------------------------------------------------#
# See mepa.py file for description, history and copyright.               #
#------------------------------------------------------------------------#

#------------------------------------------------------------------------#
#                                                                        #
# Instructions and their function mappings -- English versionion         #
#                                                                        #
# Upper case codes may be redefined, but only those.                     #
#                                                                        #
#------------------------------------------------------------------------#


# No args instructions

# End instruction
END_INSTR = "END"  # end

INSTR_DICT = {
          # 0 args
          "ADDD": "add",
          "SUBT": "subt",
          "MULT": "mult",
          "DIVI": "divi",
          "NEGT": "inv",
          "LAND": "andd",
          "LORR": "orr",
          "LNOT": "nott",
          "LESS": "less",
          "GRTR": "grt",
          "EQUA": "eql",
          "DIFF": "dif",
          "LEQU": "leq",
          "GEQU": "geq",
          "NOOP": "nop",
          "STOP": "halt",
          "READ": "read",
          "PRNT": "writ",
          "MAIN": "init",
          "CONT": "cont",
          "DUMP": "dump",
          
          # 1 arg
          "LDCT": "ldct",
          "JUMP": "jmp",
          "JMPF": "jmpf",
          "ALOC": "alloc",
          "DLOC": "dealloc",
          "ENFN": "entproc",
          "RTRN": "retproc",
          "INDX": "indx",
          "LDMV": "ldmv", ###
          "STMV": "stmv",
          "DBUG": "dbug",
          "STEP": "step",
   
          # 2 args
          "LDVL": "ldvl", ##
          "LADR": "ldaddr",
          "STVL": "stvl",  ##
          "LVLI": "ldvi",
          "STVI": "stvi",
          "ENLB": "entlabl",
          "LGAD": "ldgaddr",
          "CFUN": "call",  ##

          # 3 args
          "CPFN": "callpar", ##
          }
          
          
INSTR_0 = [
          "add",
          "subt",
          "mult",
          "divi",
          "inv",
          "andd",
          "orr",
          "nott",
          "less",
          "grt",
          "eql",
          "dif",
          "leq",
          "geq",
          "nop",
          "halt",
          "read",
          "writ",
          "init",
          "cont",
          "dump",
          ]

# One arg instructions
INSTR_1 = [
          "ldct",
          "jmp",
          "jmpf",
          "alloc",
          "dealloc",
          "entproc",
          "retproc",
          "indx",
          "ldmv",
          "stmv",
          "dbug",
          "step",
          ]


# Two args instructions
INSTR_2 = [
          "ldvl",
          "ldaddr",
          "stvl",
          "ldvi",
          "stvi",
          "entlabl",
          "ldgaddr",
          "call",
         ]

# Three args instructions
INSTR_3 = [
          "callpar",
          ]


# All instructions
INSTR_CODES = INSTR_DICT.keys()
INSTR_ALL = INSTR_0 + INSTR_1 + INSTR_2 + INSTR_3
