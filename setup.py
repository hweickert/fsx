import setuptools


description = r'''A low-level and easily mockable file system wrapper.'''

setuptools.setup(
    name='fsx',
    packages = setuptools.find_packages(exclude=['tests*']),
    version="1.0.4",
    description=description,
    author = 'Henry Weickert',
    author_email = 'henryweickert@gmail.com',
    url = 'https://github.com/hweickert/fsx',
    keywords = [],
    entry_points={},
    install_requires=['fstree==1.0.3']
)
