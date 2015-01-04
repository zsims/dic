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
    description='Dependency Injection Container for Python 3+. Uses Python 3 annotations to provide hints for the components that should be injected.',
    long_description=long_description,
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='development design ioc di',
)
