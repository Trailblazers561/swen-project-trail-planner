# UI Tests Documentation

## Overview

This directory contains UI tests for the Trail Planner application using Selenium WebDriver. All tests use pytest and are configured to test the React frontend application.

## Prerequisites

### Required Packages

Follow the prerequisites outlined in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.).

### WebDriver Setup

The tests use Chrome WebDriver. You need to have:

1. **Chrome browser** installed on your system
2. **ChromeDriver** is automatically installed via `webdriver-manager`

## Configuration

Configuration is automatically determined from the `tests/.env` file, more information in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.).

## Running Tests

Information about running tests in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.).

## Test Structure

The UI testing structure consists of breaking down the code into four major components, DTOs, pages, steps, and workflows, and using those to easily construct new tests. A more in-depth overview with examples can be found in the [Testing Guidebook](https://docs.google.com/document/d/1MuMDhpsaSYin0_dwiCYS0pto_3ukT58MzCKLO7v9ang/edit?tab=t.0) 
<span style="color: red;font-size: 50pt;font-family: Comic Sans MS;"> UPDATE THIS TO INTERNAL LINK </span>

### Selenium Helper

A [selenium_helper.py](selenium_helper.py) file has been created to help interact with selenium and element handling. This is used by all tests to retrieve the driver via ```get_driver```, and by pages to interact with various elements in various ways.

### Data Test Objects (DTOs)

DTOs are found in the `ui_tests/dtos` directory, and are objects that act as a collection of variables that go together. It makes it easy to pass information that is commonly needed together, and to easily test that one group of information matches another. These are often created in tests and passed into steps/workflows, or created in pages and returned by steps/workflows. Often, there is one created in a test, and then compared against the one created by the page.

### Pages

Pages are found in the `ui_tests/pages` directory, and are objects that represent a specific page or view of the site. They handle all interaction with the UI themselves, throguh the use of the [Selenium Helper](#selenium-helper). They outline locators for all the elements of the page at the top, and then methods that perform various tasks after. Locators are usually in the form of xpaths, but all of the following would work: id, xpath, link_text, partial_link_text, name, tag_name, class_name, and css_selector. Pages are used by steps and workflows to perform various predefined tasks. You should avoid using a page object directly within a test, and instead create a step to do whatever needs to be done.

### Steps

Steps are found in the `ui_tests/steps` directory, and are objects that utilize one or more page objects to perform a given task. They can be very simple, like clicking a specific button, or somewhat complex. If a step is too complex it should be broken down into multiple steps and turned into a workflow. They all have a constructor to define the variables used in the step, and a ```run()``` method to perform the step.

### Workflows

Workflows are found in the `ui_tests/workflows` directory, and are objects that utilize multiple steps to perform a given task. A workflow should be created when steps are often called together in multiple tests. If steps are often called togeteher, but it is in the same test, there should just be a method defined in the test file itself.

### Tests

Tests are found in the `ui_tests`directory, and are the methods that perform a given test. There should be only one test performed within a test file, and it should be prefixed with ```@pytest.mark.UI``` to denote it is a UI test. There are two main things that should be tested in UI tests, the flow and the fields.

#### The Flow

The flow is ensuring that the process we expect to happen is the one that is actually happening. This is tested by simply performing our steps in the correct order, and when Selenium looks for an element that isn't there it will throw an error and the test will fail. If nothing is ever missing when expected, then the flow worked properly.

#### The Fields

The fields are ensuring that the data presented to the user is correct. This is tested via asserts, specifically with pytest_check so that the test will fail but continue moving forward whenever something doesn't match our assertion. This can be tested within the test itself, or by using a DTO's ```.compare()``` function

## Test Files

### Login Test

Basic testing of the login feature. Ensures you can log in with all accounts, and verifies the error messages when submitting invalid login information.

## Common Issues

### Element Not Found Errors

If elements are not found:

1. Verify the application is deployed and accessible at BASE_URL
2. Check that element selectors in the specific page match the current UI
3. Increase wait times if the page loads slowly

### Login Failures

If login fails:

1. Verify credentials in [enums/user_enum.py](enums/user_enum.py) are correct
2. Check that the login page is accessible
3. Verify the application is running

