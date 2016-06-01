import sys
import pexpect
import logging
import tempfile
import subprocess
import os

from keymgr.core import (
    get_passphrase,
    temporary_file,
    temporary_directory,
)


LOGGER = logging.getLogger(__name__)


def generate_masterkey(temporary_keyring, realname, username, email,
                       passphrase):
    LOGGER.info('Generating master key')

    genkey_conf = """
    Key-Type: RSA
    Key-Length: 2048
    Key-Usage: sign
    Name-Real: %s
    Name-Comment: %s
    Name-Email: %s
    Expire-Date: 0
    Passphrase: %s
    %%commit
    """ % (realname, username, email, passphrase)

    with temporary_file() as genkey_file_path:
        genkey_file = open(genkey_file_path, 'w')
        genkey_file.write(genkey_conf)
        genkey_file.close()

        FNULL = open(os.devnull, 'w')
        subprocess.check_call(['gpg', '--homedir', temporary_keyring,
                               '--batch', '--gen-key', genkey_file_path],
                              stdout=FNULL, stderr=FNULL)


def generate_subkey_encrypt(temporary_keyring, passphrase, keyid):
    LOGGER.info('Generating subkey: encrypt')

    child = pexpect.spawn('gpg', ['--passphrase', passphrase, '--homedir',
                                  temporary_keyring, '--edit-key', keyid])

    child.expect('gpg> ')
    child.sendline('addkey')

    child.expect('Your selection\? ')
    child.sendline('6')

    child.expect('What keysize do you want\? \(2048\) ')
    child.sendline('2048')

    child.expect('Key is valid for\? \(0\) ')
    child.sendline('0')

    child.expect('Is this correct\? \(y/N\) ')
    child.sendline('y')
    child.expect('Really create\? \(y/N\) ')
    child.sendline('y')

    child.expect('gpg> ')
    child.sendline('save')

    child.expect(pexpect.EOF)


def generate_subkey_sign(temporary_keyring, passphrase, keyid, pin, admin_pin):
    LOGGER.info('Generating subkey: sign')

    child = pexpect.spawn('gpg', ['--passphrase', passphrase, '--homedir',
                                  temporary_keyring, '--edit-key', keyid])

    child.expect('gpg> ')
    child.sendline('addcardkey')

    child.expect('Your selection\? ')
    child.sendline('1')

    child.expect('What keysize do you want for the Signature key\? \(2048\) ')
    child.sendline('2048')

    child.expect('Key is valid for\? \(0\) ')
    child.sendline('1y')

    child.expect('Is this correct\? \(y/N\) ')
    child.sendline('y')

    child.expect('Really create\? \(y/N\) ')
    child.sendline('y')

    child.expect('gpg> ')
    child.sendline('save')

    child.expect(pexpect.EOF)


def generate_subkey_auth(temporary_keyring, passphrase, keyid, pin, admin_pin):
    LOGGER.info('Generating subkey: auth')

    child = pexpect.spawn('gpg', ['--passphrase', passphrase, '--homedir',
                                  temporary_keyring, '--edit-key', keyid])

    child.expect('gpg> ')
    child.sendline('addcardkey')

    child.expect('Your selection\? ')
    child.sendline('3')

    child.expect(
        'What keysize do you want for the Authentication key\? \(2048\) ')
    child.sendline('2048')

    child.expect('Key is valid for\? \(0\) ')
    child.sendline('1y')

    child.expect('Is this correct\? \(y/N\) ')
    child.sendline('y')

    child.expect('Really create\? \(y/N\) ')
    child.sendline('y')

    child.expect('gpg> ')
    child.sendline('save')

    child.expect(pexpect.EOF)


def get_masterkey_id(tmp_keyring):
    FNULL = open(os.devnull, 'w')
    key_list = subprocess.check_output(['gpg', '--list-keys', '--with-colons',
                                        '--homedir', tmp_keyring],
                                       stderr=FNULL)
    key_line = next(k for k in key_list.split() if k.startswith('pub:'))
    key_id = key_line.split(':')[4]

    return key_id


def backup_masterkey(tmp_keyring, offline_directory, keyid, username):
    LOGGER.info('Backuping masterkey in %s' % offline_directory)

    masterkey_dirname = os.path.join(username, keyid)
    masterkey_filename = '%s.secret.asc' % keyid
    masterkey_abspath = os.path.join(offline_directory, masterkey_dirname)
    masterkey_secret_file = os.path.join(masterkey_abspath, masterkey_filename)

    try:
        os.makedirs(masterkey_abspath)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(masterkey_abspath):
            pass
        else:
            raise

    subprocess.check_call(['gpg', '--armor', '--output', masterkey_secret_file,
                           '--homedir', tmp_keyring, '--export-secret-key',
                           keyid])


def store_smartcard_metainformation(firstname, lastname, username, passphrase,
                                    pin, admin_pin):
    LOGGER.info('Storing meta information on the smart card')

    # Set smartcard meta information
    child = pexpect.spawn('gpg', ['--card-edit', '--passphrase', admin_pin])

    child.expect('gpg/card> ')
    child.sendline('admin')

    child.expect('gpg/card> ')
    child.sendline('name')

    child.expect('surname: ')
    child.sendline(lastname)

    child.expect('given name: ')
    child.sendline(firstname)

    child.expect('gpg/card> ')
    child.sendline('sex')

    child.expect('Sex \(\(M\)ale, \(F\)emale or space\): ')
    child.sendline('m')

    child.expect('gpg/card> ')
    child.sendline('lang')

    child.expect('Language preferences: ')
    child.sendline('en')

    child.expect('gpg/card> ')
    child.sendline('login')

    child.expect('Login data \(account name\): ')
    child.sendline(username)

    child.expect('gpg/card> ')
    child.sendline('quit')

    # Set smartcard pin as passphrase
    child = pexpect.spawn('gpg', ['--card-edit'])

    child.expect('gpg/card> ')
    child.sendline('admin')

    child.expect('gpg/card> ')
    child.sendline('passwd')

    child.expect('Your selection\? ')
    child.sendline('1')

    child.expect('Enter PIN: ')
    child.sendline(pin)

    child.expect('Enter New PIN: ')
    child.sendline(passphrase)

    child.expect('Repeat this PIN: ')
    child.sendline(passphrase)

    child.expect('Your selection\? ')
    child.sendline('3')

    child.expect('Enter Admin PIN: ')
    child.sendline(admin_pin)

    child.expect('Enter New Admin PIN: ')
    child.sendline(passphrase)

    child.expect('Repeat this PIN: ')
    child.sendline(passphrase)

    child.expect('Your selection\? ')
    child.sendline('q')

    child.expect('gpg/card> ')
    child.sendline('quit')

    child.expect(pexpect.EOF)


def export_encrypt_subkey_to_card(temporary_keyring, keyid, passphrase):
    LOGGER.info('Exporting encryption subkey on smartcard')

    child = pexpect.spawn('gpg', ['--passphrase', passphrase, '--homedir',
                                  temporary_keyring, '--edit-key', keyid])
    child.logfile = sys.stdout

    child.expect('gpg> ')
    child.sendline('toggle')

    child.expect('gpg> ')
    child.sendline('key 1')

    child.expect('gpg> ')
    child.sendline('keytocard')

    child.expect('Your selection\? ')
    child.sendline('2')

    child.expect('gpg> ')
    child.sendline('save')

    child.interact()
    child.expect(pexpect.EOF)


def bootstrap(offline_directory, firstname=None, lastname=None, username=None,
              email=None):
    # DEBUG
    firstname = 'Aurelien'
    lastname = 'Vallee'
    username = 'avallee'
    email = 'vallee.aurelien@gmail.com'
    offline_directory = './offline'

    # Gather user information
    while not firstname:
        firstname = raw_input('First name: ')
    while not lastname:
        lastname = raw_input('Last name: ')
    while not username:
        username = raw_input('Username: ')
    while not email:
        email = raw_input('Email: ')
    realname = '%s %s' % (firstname, lastname)
    # TODO: choose proper default passphrase/pins here
    passphrase = 'Debug passphrase!'
    admin_pin = '12345678'
    pin = '123456'

    with temporary_directory() as tmp_keyring:
        # Generate a new master key
        generate_masterkey(tmp_keyring, realname, username, email, passphrase)

        # Retrieve the key id of the master key
        keyid = get_masterkey_id(tmp_keyring)

        # Generate a new encryption subkey
        generate_subkey_encrypt(tmp_keyring, passphrase, keyid)

        # Backup masterkey and encryption subkey in offline storage
        backup_masterkey(tmp_keyring, offline_directory, keyid, username)

        # Store meta information on the smart card
        store_smartcard_metainformation(firstname, lastname, username,
                                        passphrase, pin, admin_pin)

        # Generate a new authentication subkey
        generate_subkey_auth(tmp_keyring, passphrase, keyid, pin, admin_pin)

        # Generate a new signing subkey
        generate_subkey_sign(tmp_keyring, passphrase, keyid, pin, admin_pin)

        # Import encryption subkey to the card
        export_encrypt_subkey_to_card(tmp_keyring, keyid, passphrase)
