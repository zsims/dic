from distutils.core import setup
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    long_description = readme.read()

from dic import __version__

setup(
    name='dic',
    version=__version__,
    author='Zachary Sims',
    author_email='zsims@users.noreply.github.com',
    packages=['dic', 'dic.test'],
    scripts=[],
    url='https://github.com/zsims/dic',
    license='LICENSE.txt',
    description='Inversion of Control micro-framework',
    long_description=long_description,
    install_requires=[],
)
