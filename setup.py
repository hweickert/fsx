import setuptools


description = r'''Lightweight os-wrapper with focus on testability.'''

setuptools.setup(
    name='fsx',
    packages = setuptools.find_packages(exclude=['tests*']),
    version='0.0.1',
    description=description,
    author = 'Henry Weickert',
    author_email = 'henryweickert@gmail.com',
    url = 'https://github.com/hweickert/fsx',
    keywords = [],
    entry_points={},
    install_requires=[]
)
