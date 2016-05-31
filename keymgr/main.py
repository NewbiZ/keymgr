import argparse

import keymgr

parser = argparse.ArgumentParser(description='YubiKey OpenPGP/PIV manager.')

parser_action = parser.add_mutually_exclusive_group(required=True)

parser_action.add_argument('--status', dest='status', action='store_true',
        help='Display status of the YubiKey OpenPGP applet.', default=False)

parser_action.add_argument('--reset', dest='reset', action='store_true',
        help='Reset the YubiKey OpenPGP applet.', default=False)

parser_action.add_argument('--bootstrap', dest='bootstrap',
        action='store_true', help='Bootstrap a new masterkey.', default=False)

def main():
    options = parser.parse_args()

    print 'keymgr version %s' % keymgr.__version__

    if options.reset:
        keymgr.reset()
    elif options.bootstrap:
        keymgr.bootstrap()
    elif options.status:
        keymgr.status()
