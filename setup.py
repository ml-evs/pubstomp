from setuptools import setup, find_packages

with open("README.md") as flines:
    readme = flines.read()

with open("LICENSE") as flines:
    license = flines.read()

with open("requirements.txt") as flines:
    requirements = [line.strip() for line in flines]

setup(
    name='pubstomp',
    version='0.1',
    description='Stomping publications since 2019',
    long_description=readme,
    url='http://github.com/ml-evs/pubstomp',
    author='Matthew Evans',
    author_email='',
    license=license,
    setup_requires=['pytest_runner'],
    tests_require=['pytest'],
    install_requires=requirements,
    packages=find_packages(exclude=('tests', 'examples','htmlcov')),
)
