# Update Python and Support UV

Goal: Update to Python 3.14, pyproject.toml, and support use of UV.

Python 3.8 and 3.9 are end of life. See: [Python Versions](https://devguide.python.org/versions/). Python 3.15 is the latest version that is currently released, and end of life is not until 2030-10.

UV uses pyproject.tom and can manage python versions as well as a host of other features currently provided by pip, pipenv, and other package manager and build tools. Modify the setup to allow maintenance by UV, as well as pipenv, the current package management, test and build tool.
