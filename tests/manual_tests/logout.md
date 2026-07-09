
# Verify Successful User Logout

## Preconditions Guest

1. N/A

## Preconditions Registered User/Trail Manager/Admin/Root Admin

1. The user must be logged in, and able to access the navbar where the logout options are.

## Test Steps & Expected Results

| Step | Action Description                                                             | Expected Result                                            | Pass/Fail         |
| :--- | :----------------------------------------------------------------------------- | :--------------------------------------------------------- | :---------------- |
| 1    | Click on the**"User"** button in the top navigation bar. Then,**Logout** | Redirected to the login page (`/login`). URL is updated. | [x] Pass [ ] Fail |
| 2    | Navigate back to`/home)`                                                    | Verify text displays 'Guest' in top navigation bar.        | [x] Pass [ ] Fail |

![alt text](images/login.png)

## Post-conditions

* User is unauthenticated and logged out of the system.
