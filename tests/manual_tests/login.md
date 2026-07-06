# Verify Successful User Login

## Preconditions Guest
1. None

## Preconditions Registered User/Trail Manager/Admin/Root Admin
1. The user must have an active, verified account in the staging database.
2. The user is currently on the application homepage (`/home`) and is logged out.

## Test Steps & Expected Results

| Step | Action Description | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- |
| 1 | Click on the **"Guest"** button in the top navigation bar. Then, **Login/Register** | Redirected to the login page (`/login`). URL is updated. | [x] Pass <br> [ ] Fail |
| 2 | Type your email into the email field. | Text displays correctly without masking. | [x] Pass <br> [ ] Fail |
| 3 | Enter valid password into the password input. | Characters display as masked dots (`•••••`) for privacy. | [x] Pass <br> [ ] Fail |
| 4 | Click the Yellow **"Login"** button. | Redirected to the home page (`/home`). | [x] Pass <br> [ ] Fail |
| 5 | Verify change in username on the top right in the navigation bar. | Username space displays: Username, **Role** | [x] Pass <br> [ ] Fail |

![alt text](images/login.png)

## Post-conditions
* A secure session cookie is established in the browser storage.
* User is left in an authenticated homepage state.