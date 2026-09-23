"""
------------------------------------------------------
CommandLine.py

	2026 09 23		started using Git
	2026 09 23		version 1.0.0
------------------------------------------------------

"""

from __future__				import annotations

from collections.abc		import Callable

from Utilities.Utilities	import match_all_in_list

import sys

sys.stdout.reconfigure( encoding = "utf-8")

OK					= "OK"
NO_SUCH_COMMAND		= "NO_SUCH_COMMAND"
AMBIGUOUS_COMMAND	= "AMBIGUOUS_COMMAND"
MISSING_COMMAND		= "MISSING_COMMAND"

"""
-----------------------------------------------------------------------------------
 This class is designed to be a framework for simple command line programs.
 The commands and the actions (functions) they invoke are defined outside
 the framework in a command registry dictionary. The command is the dictionary
 key and the functon to be invoked is the value for that key. For example:

 registry = {
   "Open":				open_function,
   "Show Person":		show_person_function,
   "Show Family":		show_family_function,
   "Exit":				exit_function
 }

 The command line is of the form "<command> <arguments>"" where the command
 may consist of one or two words. One or both words may be abbreviated to their
 shortest unique form and are case insensitive. The function must accept a single
 string argument (it may be None or "") which is taken from the command line.
 Common sense must be used in choosing commands, In the above example, there
 can not be a "Show" command and a "Show Person" command as it would create an
 ambiguity in parsing the command line

 The steps to using the framework are:

   1) Create the action functions. Each function must accept a single string
      argument (which may be None or ""). The argument is the part of the command
      line following the command.

   2) Create the command registry. It is a dictionary where the command is the
      dictionary key and the function to be invoked for that command is the
      value for that key. the command may be one or two case insensitive words.
      They may be abbreviated to their shortest unambiguous form.'

   3) Create an instance of the framework with the register_commands() method.
      It has one argument, the command registry dictionary.

   4) Invoke the run() method which enters a loop prompting for a command
      and invoking the action function for that command. There are three optional
      arguments to the run() method: prompt, exit_command, and error_handler. A
      command line is obtained with the input() function. The default prompt string
      is "Command: ", but it may be overridden by the prompt argument. The loop
      terminates, by default, when the command line is equal to "". Alternatively,
      the exit_command argument may specify a command that, after its action
      function is invoked, terminates the loop. An optional error_handler function
      may be specified with the error_handler argument. When an error is detected,
      the error_handler function is called with four string arguments: 1) the error
      detected (NO_SUCH_COMMAND, AMBIGUOUS_COMMAND, or MISSING_COMMAND), 2) the
      first command word, 3) the second command word (or "missing_sub_command" if
      the error is MISSING_COMMAND, and 4) the arguments, i.e. the remainder of the
      command line.
--------------------------------------------------------------------------------"""

class Framework():
	def __init__( self: Framework):
		self.command_registry		= {}
		self.command_list			= []
		self.sub_command_dict		= {}

	def register_commands( self: Framework, registry: dict[ str, Callable[ [ str], None]]):
		for (command, action) in registry.items():
			key = command.lower().replace( " ", "_")
			self.command_registry[key] = action
		command_set = set()
		for command in registry.keys():
			words = command.lower().split( maxsplit=1)
			if len( words) < 1:
				continue
			command_set.add( words[0])
		self.command_list = list( command_set)
		for command in self.command_list:
			self.sub_command_dict[ command] = []
		for command in registry.keys():
			words = command.lower().split( maxsplit=1)
			if len( words) < 2:
				continue
			self.sub_command_dict[ words[0]].append( words[1])
	#end def
	
	def parse_line( self: Framework, line: str) -> (str, str, str, str):
		command: str		= ""
		sub_command: str	= ""
		arguments: str		= ""

		words: str = line.split( maxsplit=1)

		if len( words) == 0:
			return (NO_SUCH_COMMAND, "", sub_command, arguments)
	
		candidates = match_all_in_list( words[0].lower(), self.command_list)
		if len( candidates) == 0:
			return (NO_SUCH_COMMAND, words[0], sub_command, arguments)
	
		if len( candidates) > 1:
			return (AMBIGUOUS_COMMAND, words[0], sub_command, arguments)
	
		command = candidates[0]

		#===================================================================================
		# if the sub command list corrensponding to the command does not exist or is empty
		# there are no sub commands, anything after the command is arguments for the command
		#===================================================================================

		if command not in self.sub_command_dict.keys() or len( self.sub_command_dict[command]) == 0:
			if len( words) > 1:
				arguments = words[1]
			return (OK, command, sub_command, arguments)

		#===================================
		# the command requires a sub command
		#===================================

		if len( words) < 2:
			return (MISSING_COMMAND, command, "<missing sub command>", arguments)

		remainder	= words[1]
		words		= remainder.split( maxsplit=1)
		candidates	= match_all_in_list( words[0].lower(), self.sub_command_dict[ command])
		if len( candidates) == 0:
			return (NO_SUCH_COMMAND, command, words[0], arguments)
	
		if len( candidates) > 1:
			return (AMBIGUOUS_COMMAND, command, words[0], arguments)
	
		sub_command = candidates[0]
		if len( words) > 1:
			arguments = words[1]

		return (OK, command, sub_command, arguments)

	# end def

	def run( self: Framework, prompt: str = "Command:", exit_command: str = "", error_handler: Callable[ [ str, str, str, str], None] = None):
		
		self.prompt					= prompt
		self.error_handler			= error_handler
		self.exit_command			= exit_command

		while True:
			line = input( f"\n{self.prompt}")
			if line == "":
				break
			
			(status, command, sub_command, arguments) = self.parse_line( line)

			if status != OK:

				if self.error_handler:
					error_handler( status, command, sub_command, arguments)
				continue
		
			if command != "" and sub_command != "":
				action = self.command_registry[command + "_" + sub_command]
				action( arguments)
				continue

			if (command != ""):
				action = self.command_registry[command]
				action( arguments)

			if command == self.exit_command.lower():
				break

	# end def

# end class

#------------------------------------------------------------------------------------------------------------------#

def main():
	
	import sys

	def error_handler( status: str, command: str, sub_command: str, arguments: str):
		print( f"\n{status}:  {command} {sub_command} {arguments}")
	# end def

	def open( arguments: str):
		print( f"\nOpen {arguments}")

	def show( arguments: str):
		print( f"\nShow {arguments}")

	def show_person( arguments: str):
		print( f"\nShow Person {arguments}")

	def show_family( arguments: str):
		print( f"\nShow Family {arguments}")

	def show_group( arguments: str):
		print( f"\nShow Group {arguments}")

	def show_commands( arguments: str):
		print( f"\nShow Commands {arguments}")

	def export( arguments: str):
		print( f"\nExport {arguments}")

	def exit( arguments: str):
		print( f"\nExit {arguments}")

	registry =	{
		"Open"				: open,
		"Show"				: show,
		"Show Person"		: show_person,
		"Show Family"		: show_family,
		"Show Group"		: show_group,
		"Show Commands"		: show_commands,
		"Export"			: export,
		"Exit"				: exit
	}
	
	framework = Framework()

	framework.register_commands( registry)

	if False:
		print( framework.command_list)
		for (command, sub_command_list) in framework.sub_command_dict.items():
			print( f"{command} {sub_command_list}")
		# end for
		for (command, action) in framework.command_registry.items():
			print( f"{command} {action.__name__}")
		# end for
	# end if

	framework.run( prompt = "Command: ", exit_command = "Exit", error_handler = error_handler)

	sys.exit()
# end def main()
	
if __name__ == "__main__":
	main()
