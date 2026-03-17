# UI Tests Documentation

## Overview

This directory contains UI tests for the Trail Planner application using Selenium WebDriver. All tests use pytest and are configured to test the React frontend application.

## Prerequisites

### Required Packages

Install the required Python packages:

```bash
pip install pytest selenium
```

### WebDriver Setup

The tests use Chrome WebDriver. You need to have:

1. **Chrome browser** installed on your system
2. **ChromeDriver** installed and available in your PATH, OR
3. Use `webdriver-manager` to automatically manage ChromeDriver:

```bash
pip install webdriver-manager
```

If using `webdriver-manager`, update the test files to use:
```python
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
```

## Configuration

Before running tests, update the `config.py` file with your deployment details:

- **BASE_URL**: Your website URL
  - S3 website
  - CloudFront
  - Get from Terraform: `terraform output website_url`
- **LOGIN_EMAIL**: Your login email address
- **LOGIN_PASSWORD**: Your login password
- **Wait times**: Adjust if needed based on your network speed
- **Test data**: Update dates if needed for your test scenarios

## Test Files

### Core Functionality Tests

1. **test_LoginLogout.py**
   - `test_Login_Logout()`: Tests login and logout functionality

2. **test_AllTrails.py**
   - `test_AllTrails()`: Tests selecting "All Trails" in the trail selector

3. **test_OneTrail.py**
   - `test_OneTrail()`: Tests selecting a single trail

4. **test_MultipleTrails.py**
   - `test_MultipleTrails()`: Tests selecting multiple trails

5. **test_WildernessGroups.py**
   - `test_WildernessGroups()`: Tests selecting trails from wilderness groups

### Date and Granularity Tests

6. **test_EditDates.py**
   - `test_EditDates()`: Tests editing both start and end dates

7. **test_EditStartDate.py**
   - `test_EditStartDate()`: Tests editing the start date

8. **test_EditEndDate.py**
   - `test_EditEndDate()`: Tests editing the end date

9. **test_granularity.py**
   - `test_Granularity()`: Tests changing the granularity setting

### New Feature Tests

10. **test_ListView.py**
    - `test_SwitchToListView()`: Tests switching from graph to list view
    - `test_ListViewTableDisplay()`: Tests that the list view table displays correctly
    - `test_SwitchBackToGraphView()`: Tests switching back to graph view

11. **test_TrailModals.py**
    - `test_AddTrailModal()`: Tests opening and interacting with Add Trail modal
    - `test_EditTrailModal()`: Tests opening Edit Trail Info modal

12. **test_TrailGroupModals.py**
    - `test_AddGroupModal()`: Tests opening and interacting with Add Group modal
    - `test_EditGroupModal()`: Tests opening Edit Group modal

## Running Tests

### Run All Tests

From the `swen-project-react-app-UI-tests` directory:

```bash
pytest completed/ -v
```

Or from the `completed` directory:

```bash
pytest -v
```

### Run Tests with Markers

Run only UI tests:

```bash
pytest completed/ -m UI -v
```

Exclude UI tests:

```bash
pytest completed/ -m "not UI" -v
```

### Run Specific Test File

```bash
pytest completed/test_LoginLogout.py -v
```

### Run Specific Test Function

```bash
pytest completed/test_LoginLogout.py::test_Login_Logout -v
```

### Run with Verbose Output and Print Statements

```bash
pytest completed/ -v -s
```

### Run with HTML Report

```bash
pip install pytest-html
pytest completed/ -v --html=report.html
```

### Run Tests in Parallel (if needed)

```bash
pip install pytest-xdist
pytest completed/ -v -n auto
```

## Test Structure

All tests follow a consistent pattern:

1. Initialize WebDriver
2. Use `login()` helper function from `test_helpers.py`
3. Perform test actions
4. Assert expected behavior
5. Clean up (close browser in `finally` block)

## Helper Functions

### test_helpers.py

Contains reusable helper functions:

- **`login(driver, url=None, email=None, password=None)`**: Logs into the application
  - Uses values from `config.py` by default
  - Can be overridden with custom values if needed

- **`select_trail_from_dropdown(driver, wait, trail_name="All Trails")`**: Selects a trail from the react-select dropdown
  - Handles dynamic react-select IDs reliably
  - Uses multiple selector strategies for robustness
  - Includes explicit waits for rendering delays
  - Defaults to "All Trails" if no trail name is specified

## Common Issues

### ChromeDriver Not Found

If you get an error about ChromeDriver not being found:

1. Download ChromeDriver from https://chromedriver.chromium.org/
2. Add it to your PATH, OR
3. Use `webdriver-manager` (see Prerequisites)

### Tests Timing Out

If tests are timing out:

1. Increase wait times in `config.py`
2. Check your network connection
3. Verify the BASE_URL is correct and accessible

### Element Not Found Errors

If elements are not found:

1. Verify the application is deployed and accessible at BASE_URL
2. Check that element selectors in `config.py` match the current UI
3. Increase wait times if the page loads slowly

### Login Failures

If login fails:

1. Verify credentials in `config.py` are correct
2. Check that the login page is accessible
3. Verify the application is running