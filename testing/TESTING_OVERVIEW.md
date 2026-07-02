# Testings Documentation

## Overview

This directory contains all tests for the Trail Count application. All tests use pytest with the format defined in [pytest.ini](pytest.ini). 

## Prerequisites

### Required Packages

All the required python packages are defined in [requirements.txt](requirements.txt).
To install them run the following command

```bash
pip install -r requirements.txt
```

### Environment Variables

The tests require specific references to the resources that need to be tested. Generally, when making local changes, it is assumed that you will use your aws account to deploy the application. When performed locally terraform will automatically create a [.env](.env) file with the necessary variables to run the tests.


In the event this doesn't reflect what you want, there is also a [setup_env.py](setup_env.py) file that when run will create a [.env](.env). It takes a *--env* parameter which should be *local* for a local run, or *tst* if hooked up to the sponsor's account. To look more at linking your local aws credentials to the sponsor account look at [README.md](../README.md). To run [setup_env.py](setup_env.py) run the following command from the `root` directory:

```bash
python tests/setup_env.py --env <ENV_PREFIX> --password <USER_PASSWORDS>
```

## Running Tests

### Run All Tests

From the `root` directory:

```bash
pytest tests/
```

Or from the `tests` directory:

```bash
pytest
```

### Run Tests with Markers

Run only UI tests:

```bash
pytest tests/ -m UI
```

Exclude UI tests:

```bash
pytest tests/ -m "not UI"
```

### Run Specific Test File

```bash
pytest path/to/file.py
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Print Statements

```bash
pytest tests/ -s
```

### Run with HTML Report

```bash
pip install pytest-html
pytest tests/ --html=test-results.html
```

### Run Tests in Parallel (if needed)

```bash
pip install pytest-xdist
pytest tests/ -n auto
```