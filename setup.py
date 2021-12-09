from setuptools import find_packages
from setuptools import setup
from setuptools.command.upload import upload
import os

class ReleaseToPyPICommand(upload):

    def finalize_options(self):
        self.repository = os.environ['PYPI_URL']
        self.username = os.environ['PYPI_USERNAME']
        self.password = os.environ['PYPI_PASSWORD']

setup(
    name='kms-encryption-toolbox',
    version='0.2.2',
    url='https://github.com/ApplauseOSS/kms-encryption-toolbox',
    license='MIT',
    description='Encryption toolbox to be used with the Amazon Key Management Service for securing your deployment secrets. It encapsulates the aws-encryption-sdk package to expose cmdline actions.',
    author='Applause App Quality, Inc.',
    author_email='ops@applause.com',
    zip_safe=False,
    packages=['kmsencryption'],
    install_requires=[
        'cffi>=1.10.0',
        'aws-encryption-sdk>=1.2.0,<2.0',
        'click>=6.6',
        'cryptography>=1.8.1,!=3.4',
        'future>=0.16.0'
    ],
    entry_points={
        "console_scripts": [
            "kms-encryption = kmsencryption.__main__:main",
        ]
    },
    scripts=["kmsencryption/scripts/decrypt-and-start"],
    cmdclass={
        'release_to_pypi': ReleaseToPyPICommand
    }
)
