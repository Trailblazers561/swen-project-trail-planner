# Testings Documentation

## Overview

This directory contains all tests for the Trail Planner application. All tests use pytest with the format defined in [pytest.ini](pytest.ini). More information on testing can be found in the [Testing Guidebook](https://docs.google.com/document/d/1MuMDhpsaSYin0_dwiCYS0pto_3ukT58MzCKLO7v9ang/edit?tab=t.0) 
<span style="color: red;font-size: 50pt;font-family: Comic Sans MS;"> UPDATE THIS TO INTERNAL LINK </span>

## Prerequisites

### Required Packages

All the required python packages are defined in [requirements.txt](requirements.txt).
To install them run the following command

```bash
pip install -r requirements.txt
```

### Environment Variables

The tests require specific references to the resources that need to be tested. Generally, when making local changes, it is assumed that you will use your aws account to deploy the application. When performed locally terraform will automatically create a [.env](.env) file with the neccisary variables to run the tests.


In the event this doesn't reflect what you wan't, there is also a [setup_env.py](setup_env.py) file that when run will create a [.env](.env). It takes a *--env* parameter which should be *local* for a local run, or *tst* if hooked up to the sponsor's account. To look more at linking your local aws credentials to the sponsor account look at [README.md](../README.md). To run [setup_env.py](setup_env.py) run the following command from the `root` directory:

```bash
python tests/setup_env.py --env <ENV_PREFIX>
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