# UI Tests Documentation

## Overview

This directory contains UI tests for the Trail Planner application using Selenium WebDriver. All tests use pytest and are configured to test the React frontend application. The general purpose testing documentation can be found in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.).

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

The UI testing structure consists of breaking down the code into four major components, DTOs, pages, steps, and workflows, and using those to easily construct new tests.

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

### Dashboard Graph Test

Basic testing of the dashboard features and trail graph. Verifies all dashboard inputs work (date range, granularity, areas, trails) and that the graph reflects the selected inputs. All tests are performed as a guest user.

### Dashboard Trail Status Test

Basic testing of the dashboard trail status overview table. Ensures data displayed is correct and that sorting the table works as expected. All tests are performed as a guest user.
Checks to Add
 - Trail dropdown is reflected in table

### Import Export Data Test

Basic testing of the import and export features. Ensures export works with each granularity, and import... All tests are performed as a trail manager.
Checks to Add
 - Import

### Add Edit Trail Test

Basic testing of the add and edit trail option. Creates a trail with and without a group, updates a trail's name, and retires a trail. All tests are performed as a trail manager.
Checks to Add
 - Creating a trail with latitude, longitude, notes

### Add Edit Area Test

Basic testing of the add and edit area option. Creates an area with and without trails, updates an area's name, and deletes an area. All tests are performed as a trail manager.
Checks to Add
 - Make it work

### Associate Device Test

Basic testing of the associate device feature. Accociates an unpaired device, repairs a paired device, pairs a device to an already paired trail, and unpairs a paired device. All tests are performed as a trail manager.
Checks to Add
 - Make it work

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

### Pipeline Errors

 - Many things break on the pipeline that work locally, getting things to work consistantly on the pipeline is an important part of UI testing
 - Each pipeline run attaches error screenshots and test results to help debug the issue
 - Change the .env LOCAL_RUN to false to run the test in headless mode to mimic a pipeline run
 - The biggest difference between local and pipeline is timezone, watch out for potential timezone errors
 - Try determining the next step based on current state of something if there is an issue that is pipeline exclusive (ie, click a button again if a process doesn't happen)
 - Things take a lot longer to load on the pipeline, make sure to give everything enough time 
