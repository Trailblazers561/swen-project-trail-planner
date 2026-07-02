# Lambda Component Tests Documentation

## Overview

This directory contains component tests for the Trail Count lambdas. The general purpose testing documentation can be found in [TESTING_OVERVIEW](/tests/TESTING_OVERVIEW.md).

## Prerequisites

### Required Packages

Follow the prerequisites outlined in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.).

## Configuration

There is no configuration required outside of the mock objects created in the conftest.py file. If you need an object mocked that isn't already, you'll need to update that file.

## Running Tests

Information about running tests in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.). It's recommended to simply run `pytest` on this directory to run all tests. 