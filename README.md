🥧 speckle-py example
=====================

This is a simple example of using the speckle python SDK to receive data from a server, do fun stuff with the data, and send changes back to the server. 

## Documentation

Comprehensive developer and user documentation can be found on our:

#### 📚 [Speckle Docs website](https://speckle.guide/dev/)

## Developing & Debugging

This project uses [poetry](https://python-poetry.org/docs/#installation) to handle requirements. If you've never used it before, I recommend adding the following config to place the virtual environment within the project directory.

```shell
$ poetry config virtualenvs.in-project true
```

To install the requirements, simply run:

```shell
$ poetry install
```

Note that this is using a local version of `speckle-py` located in the root of the project as it is not yet published. It will soon be a published package, but for now please pull from `main` in the [project repo](https://github.com/specklesystems/speckle-py) to get the latest updates. To package up a new tarball, run `$ poetry build` from the `speckle-py` repo and copy over the new `tar.gz` from the `dist` directory.