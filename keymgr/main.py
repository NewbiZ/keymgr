import argparse
import logging

import keymgr

parser = argparse.ArgumentParser(description='YubiKey OpenPGP/PIV manager.')

parser.add_argument(
    '--log-level', dest='log_level', action='store', default='INFO',
    help='Set the log level.')

parser_action = parser.add_mutually_exclusive_group(required=True)

parser_action.add_argument(
    '--status', dest='status', action='store_true', default=False,
    help='Display status of the YubiKey OpenPGP applet.', )

parser_action.add_argument(
    '--reset', dest='reset', action='store_true', default=False,
    help='Reset the YubiKey OpenPGP applet.')

parser_action.add_argument(
    '--bootstrap', dest='bootstrap', action='store_true', default=False,
    help='Bootstrap a new masterkey.')


def main():
    options = parser.parse_args()

    print 'keymgr version %s' % keymgr.__version__

    # Allow user to change default log level
    numeric_loglevel = getattr(logging, options.log_level.upper(), None)
    if not isinstance(numeric_loglevel, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=numeric_loglevel)

    # Ensure gpg-agent is reachable
    keymgr.init()

    # Perform the appropriate action
    if options.reset:
        keymgr.reset()
    elif options.bootstrap:
        keymgr.bootstrap('')
    elif options.status:
        keymgr.status()
