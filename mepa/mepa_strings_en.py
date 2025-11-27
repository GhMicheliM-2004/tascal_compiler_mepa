
#------------------------------------------------------------------------#
#                                                                        #
# Last update: "mepa_strings_en.py: 2015-10-07 (Wed)  12:43:03 BRT (tk)" #
#                                                                        #
#------------------------------------------------------------------------#
# See mepa.py file for description, history and copyright.               #
#------------------------------------------------------------------------#

#------------------------------------------------------------------------#
#                                                                        #
# Definitions of language dependant strings: English                     #
#                                                                        #
#------------------------------------------------------------------------#

# General

INTERNAL_ERROR = "Internal error %d"

# main.py

BANNER = "\nMepa Interpreter version %s"
UNRECOGNIZED_OPTION = "\nUnrecognized option(s)"
ILLEGAL_OPTION = "Illegal option '--%s %s'"
ILLEGAL_OPTIONS = "Illegal option(s)"
EXECUTION_ERROR = "Execution error %d"
UNEXPECTED_EXCEPTION = "Unexpected exception"
OPTIONS_TITLE = "Options:"
STEP_STDIN = "Option '--step' cannot be used without '--progfile'\n"

# main_defs.py

UNEXPECTED_PROGRAM_READING_EXCEPTION = "\nUnexpected exception in program file"
UNEXPECTED_EOF_PROGRAM = "Unexpected end of program file"
ILLEGAL_INSTRUCTION_LABEL = "Illegal instruction label %d:  %s" 
MISSING_INSTRUCTION_CODE = "Missing instruction code  %d:  %s"
PROGRAM_TOO_LARGE = "Program too large; use option '--programsize'"
ILLEGAL_INSTRUCTION  = "Illegal instruction  (%3d)  %s" 
ILLEGAL_INSTRUCTION_ARGUMENTS = "Illegal instruction  arguments %d:  %s" 
REDEFINED_LABEL = "Redefined label  (%3d)  %s" 
ILLEGAL_ARGUMENT = "Illegal argument or undefined label in line %3d" 

# mepa_interp.py

ILLEGAL_ARGUMENT_TYPE = "Illegal argument type in an instruction or some limit exceeded"
EXECUTED_INSTRUCTIONS = "\nExecuted %d instructions\n"
MAXIMUM_INSTRUCTIONS_EXCEEDED = "Maximum number of instructions exceeded (%d)"
UNEXPECTED_EOF_INPUT = "Unexpected end of input file"
ILLEGAL_INPUT_VALUE = "Illegal input value"
PROG_END = "Program end reached without a stop instruction"
STARTING_DEBUGGING = "Starting debugging"
STOPPING_DEBUGGING = "Stopping debugging"
STARTING_STEPEXEC = "\nStarting step-by-step execution"
STOPPING_STEPEXEC = "Stopping step-by-step execution"
DUMP = "\n\nDump"
DISPLAY = "\nDisplay"
MEMORY = "\nMemory"
LABELS = "\nLabels"
END_DUMP = "\nEnd dump"
ILLEGAL_DEBUG_VALUE = "Illegal value in debugging"
OPEN_FILE_ERROR = "Open file '%s' error"
ILLEGAL_VALUE = "Illegal value found during interpretation of instruction %d"
