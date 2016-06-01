import os
import subprocess
import logging


LOGGER = logging.getLogger(__name__)


def reset():
    reset_commands = """
scd reset
scd serialno undefined
scd apdu 00 A4 04 00 06 D2 76 00 01 24 01
scd apdu 00 20 00 81 08 40 40 40 40 40 40 40 40
scd apdu 00 20 00 81 08 40 40 40 40 40 40 40 40
scd apdu 00 20 00 81 08 40 40 40 40 40 40 40 40
scd apdu 00 20 00 81 08 40 40 40 40 40 40 40 40
scd apdu 00 20 00 83 08 40 40 40 40 40 40 40 40
scd apdu 00 20 00 83 08 40 40 40 40 40 40 40 40
scd apdu 00 20 00 83 08 40 40 40 40 40 40 40 40
scd apdu 00 20 00 83 08 40 40 40 40 40 40 40 40
scd apdu 00 e6 00 00
scd reset
scd serialno undefined
scd apdu 00 A4 04 00 06 D2 76 00 01 24 01
scd apdu 00 44 00 00
/bye
    """
    pipe_read, pipe_write = os.pipe()
    os.write(pipe_write, reset_commands)
    os.close(pipe_write)

    FNULL = open(os.devnull, 'w')
    subprocess.check_call(['gpg-connect-agent'], stdin=pipe_read, stdout=FNULL)
    LOGGER.info('Smartcard successfully reset')
