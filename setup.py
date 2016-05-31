import setuptools

setuptools.setup(
    name='keymgr',
    version='0.1',
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
