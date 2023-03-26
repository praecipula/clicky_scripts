import subprocess
import logging
import python_logging_base

LOG = logging.getLogger("clicky_base")
LOG.setLevel(logging.TRACE)

class CliClick:
    '''
    The actual command runner, which takes a list of classes that implement CommandBase and runs the script.
    '''

    COMMAND_NAME="cliclick"

    def __init__(self, commands = []):
        self._commands = commands

    def add_command(self, command):
        self._commands.append(command)

    def execute(self):
        command_string = [CliClick.COMMAND_NAME] + [c.command_string for c in self._commands]
        LOG.trace(f"Command to be executed: `{command_string}`")
        result = subprocess.run(command_string, capture_output=True)
        result_stdout = result.stdout.decode("utf-8")
        LOG.trace(f"Result: {result_stdout}")
        # HACK for dev
        if self._commands[0].expects_output:
            self._commands[0].handle_output(result_stdout)
        # HACK should handle cliclick result codes.
        return True 
        
class CommandBase:
    '''
    Base class of commands
    '''

    def __init__(self, command_string):
        self._command_string = command_string

    @property
    def command_string(self):
        return self._command_string

    @property
    def expects_output(self):
        # If the command expects output, then it should both return true from expects_output
        # AND implement handle_output.
        raise Exception("Subclasses are expected to implement #expects_output")

    def handle_output(self, output_string):
        raise Exception("If you return True from #expects_output, you must override #handle_output")