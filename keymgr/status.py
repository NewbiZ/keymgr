import pexpect


def status():
    print pexpect.run('gpg --card-status')
