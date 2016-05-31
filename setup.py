import setuptools

from keymgr import __version__

setuptools.setup(
    name='keymgr',
    version=__version__,
    description='SmartCard manager',
    author='Aurelien Vallee',
    author_email='vallee.aurelien@gmail.com',
    packages=['keymgr'],
    install_requires=['pexpect==4.1.0'],
    entry_points={
        'console_scripts': [
            'keymgr=keymgr.main:main',
        ],
    }
)
