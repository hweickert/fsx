`fsx` is a low-level and *easily mockable* file system wrapper.

# Usage
Your production code may write a file to disk.

*create_file.py*:

    import fsx

    def run():
        with fsx.open('/files/file1.txt', 'w') as file_:
            file_.write('Hello World')


You may write a test which checks if the content gets written correctly.
Using the [pytest-fixture] `fsx_fake` you can create virtual files or directories.
All calls to `fsx` will then work with the virtual instead of the real files.

*test_main.py*:

    import fsx
    from fsx.test import fsx_fake
    import create_file

    def test_hello_world_is_written(fsx_fake):
        fsx_fake.add('/files/')

        create_file.run()

        result = fsx.open('/files/file1.txt', 'r').read()
        assert result == 'Hello World'

`fsx_fake` will keep a tree of virtual files (and their contents) for the currently executing test.

# Installation

    pip install fsx

# Currently Supported Functions

| Function                      | Note                              |
|:------------------------------|:----------------------------------|
| `os.path.isfile`              |                                   |
| `os.path.isdir`               |                                   |
| `os.path.exists`              |                                   |
| `os.listdir`                  |                                   |
| `os.remove`                   |                                   |
| `os.makedirs`                 | Not all parameters supported yet. |
| `os.walk`                     | Not all parameters supported yet. |
| `open`                        | Not all parameters supported yet. |
| `shutil.rmtree`               |                                   |
| `glob.glob`                   |                                   |
| `glob.iglob`                  |                                   |
| `tempfile.NamedTemporaryFile` |                                   |
| `zipfile.ZipFile`             |                                   ||


# Philosophy
I think mocking built-in file system modules like `os` or `glob` directly is not a good idea.
You may have 3rd party libraries which do require access to the real file system.

I do prefer to make a *conscious effort* and select which parts of my production-code are to be mockable.

If you just want to mock the Python's built-in file system modules you can use [pyfakefs]

# Notes
- The `fsx.glob` module is slightly different from Python's built-in `glob` module.
  It ensures that calling `glob`/`iglob` will not swap forwardslashes for backslashes on Windows.

[pytest-fixture]: https://docs.pytest.org/en/latest/fixture.html
[pyfakefs]: https://github.com/jmcgeheeiv/pyfakefs
