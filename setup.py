from distutils.core import setup

setup(
    name='dic',
    version='0.1.0',
    author='Zachary Sims',
    author_email='zsims@users.noreply.github.com',
    packages=['dic', 'dic.test'],
    scripts=[],
    url='https://github.com/zsims/dic',
    license='LICENSE.txt',
    description='Inversion of Control micro-framework',
    long_description=open('README.txt').read(),
    install_requires=[],
)
