# OGS Connectors

## Overview

This repository regroups the connectors used for the OGS project, it is based on Kedro's framework.

Kedro version `Kedro 0.17.2`.
[Kedro documentation](https://kedro.readthedocs.io).

Each connector is an individual pipeline, defined in src/pipelines

## How to use

### Install kedro

Kedro highly recommend that you use a virtual environment in order to use , as
explained [here](https://kedro.readthedocs.io/en/stable/02_get_started/01_prerequisites.html#virtual-environments).

Install kedro
https://kedro.readthedocs.io/en/stable/02_get_started/02_install.html

If you are using pip

```
pip install kedro
```

or conda

```
conda install -c conda-forge kedro
```

### Install the project

To install the project, run:

```
kedro install
```

### Jupyter

To use Jupyter notebooks in your Kedro project, you need to install Jupyter:

```
pip install jupyter
```

After installing Jupyter, you can start a local notebook server:

```
kedro jupyter notebook
```

You can then easily access to data written in the data catalog

## Connectors

Pipelines overview:

![plot](./pipelines_overview.png)

Generated using kedro viz

- [Ademe](src/ogs_connectors/pipelines/ademe/README.md)

## Contribute

## How to install dependencies

Declare any dependencies in `src/requirements.txt` for `pip` installation and `src/environment.yml` for `conda`
installation.

## How to run Kedro

You can run your Kedro project with:

```
kedro run
```

It will run the default pipeline, defined here _src/ogs_connectors/pipeline_registry.py_ as the \___default__\_.

## How to test your Kedro project

Have a look at the file `src/tests/test_run.py` for instructions on how to write your tests. You can run your tests as
follows:

```
kedro test
```

To configure the coverage threshold, look at the `.coveragerc` file.

## Project dependencies

To generate or update the dependency requirements for your project:

```
kedro build-reqs
```

