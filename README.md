# OGS Connectors

## Overview

This repository regroups the connectors used for the OGS project.
What we call a "connector" is a packaged piece of code whose role is to integrate data from an outside source to our database(s), in a reliable way.
In our case, the goal is to Extract and Transform data from the different open data sources to finally Load them into our environment (often called ETL).

We distinguish two major external data sources (not exhaustive list):
- **APIs**: "pullable" data from servers, often also allowing live data access
- **Files**: downloadable data from websites, most of the time "snapshots"

In the first weeks of OGS, we will focus on _files_, being the simplest way to access data.

The raw data extracted from websites will be stored in our cloud provider's datalake, currently [AWS S3](https://aws.amazon.com/s3/).
S3 is an easy access datalake, allowing us to share a single shared storage environment, with great read and write performances.

## Connectors

Pipelines overview:

![plot](./pipelines_overview.png)

Generated using kedro viz

Implemented connectors so far:

- [Ademe - WIP](src/ogs_connectors/pipelines/ademe/README.md)


## Data modeling

WIP

## Contribute

If you'd like to contribute, you can create your own pipeline to connect a given dataset and transform it to our data model!

More can be found about creating your own pipeline in the [kedro section](#kedro)

You can create a pull request to add or update an existing pipeline, do not forget to declare any dependencies in `src/requirements.txt`.

## How to use

### Before starting

Kedro highly recommend that you use a virtual environment. In order to do so, follow the instructions [here](https://kedro.readthedocs.io/en/stable/02_get_started/01_prerequisites.html#virtual-environments). 
I recommend using:
- conda environment over venv
- having the name `ogs-connectors` as the name of the conda virtual environment
- using python=3.9

Make sure you activate your environment each time you are opening your terminal to work on the project.
```
conda activate ogs-connectors
```

### Get the project

Install the project using git clone
```
git clone https://github.com/OpenGeoScales/ogs-connectors.git
```

### Install the project

Move to the created directory
```
cd ogs-connectors
```

Install the dependencies
```
pip install -r src/requirements.txt
```

Test the kedro installation
```
kedro info
```

The command should be recognized, and you should see the kedro logo as well as the version.
Finally, to install the kedro's dependencies, make sure you are at the rood of the directory and run:

```
kedro install
```

You should see at the end `Requirements installed!`

### Trying out jupyter

By default, Jupyter will be installed. You can launch it through the command:
```
kedro jupyter notebook
```

You can try out to create a new notebook in the `notebooks/` directory.

*You are ready to go*!

### Credentials

Credentials need to be filled in a file located at `conf/local/credentials.yml`. File needs to be created manually, and **should never be pushed onto git**.

Structure is as followed:

```yaml
# conf/local/credentials.yml
# Here you can define credentials for different data sets and environment.
dev_s3:
  key: YOUR S3 KEY
  secret: YOUR S3 secret
```

Contact the admin if you did not get your credentials.

## Kedro

### What is it ?

At OGS, we are using Kedro as our main python developing framework.
Simply put, Kedro is a python library which offers a project structure/organization that facilitates the set up of reliable data pipelines, from data exploration, to production ready code.
The main features that we will be taking advantage of are:
- **Project structure**: Software-Engineering based code organisation. 
- **Data catalog**: A simple declarative file to define the input output of your code, without caring about the read/write methods anymore.
- **Pipelines / Nodes**: A DAG (direct acyclic graph) conception, allowing us to build well-defined data flows.
- **Kedro-viz**: Useful visualization of the project's DAGs at a single glance.
- **Notebook integration**: Kedro allows the creation of notebooks to prototype your workflows, _using the datacatalog_!

We believe than using such a framework will facilitate the collaboration among the community. 
Since its release in 2019, it got a lot of success from data science community, and the dev team keeps bringing additional features.
I personally highly recommend starting using it even for personal projects, especially for the code organization feature, which really helps when your project tends to get complicated.

If you want to know more about the Kedro's motivations, you can check their [original article](https://medium.com/quantumblack/introducing-kedro-the-open-source-library-for-production-ready-machine-learning-code-d1c6d26ce2cf) on medium.
All the documentation is pretty straightforward: [Kedro documentation](https://kedro.readthedocs.io).

We are using version `0.17.2`

In the following we'll dive into some major features.

We will be using the ADEME data for the following examples, explained [here](https://opengeoscales.github.io/CarbonData/#ademe).

### Data Catalog

The data catalog is one of the most useful feature in Kedro. It allows us to define a dataset in a yaml file, it can be used for both input and output purposes.
By defining a dataset within the data catalog, it can easily be read or written.
The data catalog is defined in `conf/base/catalog.yml`.

Let's take an example. We define the entry for one of the ademe file: 

```yaml
ademe_assessments:
  type: pandas.CSVDataSet
  filepath: s3://opengeoscales-dev/raw/ademe/beges/assessments.csv
  credentials: dev_s3
```

Root key: _ademe_assessments_ is the name of our dataset, used as an identifier of the dataset.
On the next level one defines a set of mandatory and optional parameters.

In our case we simply precise the **type** of our dataset: _pandas.CSVDataset_, meaning our dataset is a CSV file that we want to manipulate as a Pandas DataFrame.
**filepath** is the location of the file. In our case it is situated on AWS s3, so we include the full path.
Next key is the **credentials**, it is necessary as we are using s3 and therefore need some credentials to access it.
More can be found about credentials in the [credentials section](#credentials).

Within a kedro jupyter notebook, we can then list the defined datasets using:
```python
# catalog is an object instantiated by default when starting a kedro jupyter notebook
catalog.list()
```

We can then directly access one dataset 
```python
# Load our pandas DataFrame
assessments_df = catalog.load('ademe_assessments')
```

Super easy!

All the documentation related to data catalog can be found [here](https://kedro.readthedocs.io/en/stable/05_data/01_data_catalog.html).

### Pipelines / Nodes

Pipelines and Nodes are two major concepts of Kedro projects' architecture. If you are familiar with the concept of DAG (Direct Acyclic Graphs), then a DAG is a Kedro Pipeline, and a task/node is a Kedro Node.

#### Node

A Node is a simple task, it takes: 
- a function 
- some inputs (datasets or parameters)
- some outputs (datasets)

Input/Output datasets are entities from the data catalog, referenced by their identifier.
Parameters are fields defined in the `conf/base/parameters.yml` file.

Let's take an example: 

```python
# Import the Node object
from kedro.pipeline import node

# Define our node function
def ademe_connector(assessments, emissions):
    """
    @param assessments: pandas Dataframe
    @param emissions: pandas Dataframe
    """
    # Function code here
    ...
    return

# Define the kedro node
ademe_connector_node = node(
    func=ademe_connector,
    inputs=dict(
        assessments='ademe_assessments',
        emissions='ademe_emissions',
    ),
    outputs='ademe_merged'
)
```

Here we have declared a single node to process ademe data, this is just one example as our connector could be split in several nodes rather than one big one.
Our function is _ademe_connector_, our input are two datasets from the data catalog: _ademe_assessments_ and _ademe_emissions_.
We define _ademe_merged_ dataset as our output dataset.

When running the node, Kedro will load the datasets as Pandas Dataframe and pass them on to the function. We are thus expecting pandas Dataframe to be the input of our _ademe_connector_ function.

As mentioned previously, we are never bothered to write a single line of code to deal with the read/write tasks, we are just using references to our datasets defined in our data catalog.

Complete official documentation [here](https://kedro.readthedocs.io/en/0.15.4/04_user_guide/05_nodes.html).

#### Pipeline

A Pipeline is simply a list of Nodes. It takes as input a list of Kedro nodes, once ran, it will trigger the different nodes.
The order of the nodes matters, as by default, one node will be executed once the previous one has been finished.
You also have the option to activate multi threading so that all nodes are executed at the same time.
You can also create a pipeline created from other pipelines, in order to have complex DAGs.

Let's take a simple example:

```python
# Import the Pipeline object
from kedro.pipeline import Pipeline

# Import our created nodes
from .nodes import ademe_transformer_node
from .nodes import ademe_mapper_node

# Define our pipeline
def create_pipeline(**kwargs):
    return Pipeline(
        [
            ademe_transformer_node,
            ademe_mapper_node
        ]
    )

```

Here we simply imported our nodes from a different python file, we have written down the _create_pipeline_ function, which simply returns a Pipeline object, instantiated with the two nodes we have imported, _ademe_transformer_node_ and _ademe_mapper_node_ (fake nodes).

When this pipeline will be run, it will first launch the _ademe_transformer_node_ and once it's succeeded it will trigger the _ademe_mapper_node_.

Complete official documentation [here](https://kedro.readthedocs.io/en/0.15.4/04_user_guide/06_pipelines.html).

### Files organisation

Each pipeline is defined inside its own sub repository inside the main directory, in our case `ogs_connectors/pipelines`.
A pipeline folder is organised as followed:

```
__init__.py
nodes.py
pipeline.py
some_python_file.py
some_sub_directory/
```

- *\_\_init\_\_.py* should be untouched, it contains a single line to allow easy import for Kedro's framework.
- *pipeline.py* is where we defined our pipeline, as explained in [precedent section](#pipeline)
- *nodes.py* is where we defined our different nodes, as explained in [precedent section](#pipeline)
- some_python_file.py is just an example to illustrate the fact that additional python file can be defined here to be imported for example by our _nodes.py_ file.
- some_sub_directory/ is just an example to illustrate the fact than a sub folder can also be created at the pipeline root if needed.

It is recommended to have all the code related to a pipeline and its nodes within the pipeline folder.
However, it is also a good practice to have a higher level folder containing other functions / modules than can be mutually shared by pipelines.
Same goes with nodes, one can imagine that 2 different pipelines share the same nodes, with or without the same input/outputs.

Once a pipeline has been written, it needs to be registered, in the file `src/ogs_connectors/pipeline_registry.py`

It looks like such:

```python

# Import your pipeline
from ogs_connectors.pipelines import ademe


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.

    """
    # Declare your pipeline here
    ademe_pipeline = ademe.create_pipeline()

    # Define the trigger key word
    return {
        "ademe": ademe_pipeline,
        "__default__": ademe_pipeline,
    }
```

In our example, we have imported our `ademe` pipeline, we simply declare the pipeline with the `create_pipeline()` method.
Once done, we add an entry to the output directory to associate a key word with our pipeline.
We can later trigger our pipeline by launching in the terminal:

```bash
kedro run --pipeline ademe
```

Which will trigger our `ademe_pipeline`.

There also is a `__default__` key word, that can also be linked to a pipeline, to be triggered as the default pipeline.
To run the default pipeline, simply run

```bash
kedro run
```

### Annexes

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
