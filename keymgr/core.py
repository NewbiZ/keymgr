import logging
import shutil
import contextlib
import tempfile
import os
import sys
import subprocess

import pexpect


LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def temporary_file():
    """Securely create a temporary file.

    The file is automatically destroyed when leaving the context. The file
    contains restricted permissions to only allow rwx by the owner.
    """
    fd, path = tempfile.mkstemp()
    LOGGER.debug('Created temporary file %s' % path)
    try:
        yield path
    finally:
        LOGGER.debug('Removing temporary file %s' % path)
        os.close(fd)
        subprocess.call(['shred', '-fu', path])


@contextlib.contextmanager
def temporary_directory():
    """Securely create a temporary directory.

    The directory is automatically destroyed when leaving the context. The
    directory contains restricted permissions to only allow rwx by the owner.
    """
    path = tempfile.mkdtemp()
    LOGGER.debug('Created temporary directory %s' % path)
    os.chmod(path, 0700)
    try:
        yield path
    finally:
        LOGGER.debug('Removing temporary directory %s' % path)
        # Shred all files recursively
        for root, directories, filenames in os.walk(path):
            for filename in filenames:
                subprocess.call(['shred', '-fu', os.path.join(root, filename)])
        # Remove the directory itself
        shutil.rmtree(path)


def get_passphrase(child):
    child.logfile = sys.stdout
    child.interact(output_filter=hide)


def hide(s):
    if 'pass' in s.lower():
        return s
    else:
        return ''
