import pexpect


def init():
    pexpect.run('gpg-connect-agent /bye')
