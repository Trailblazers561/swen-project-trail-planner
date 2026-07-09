
# Verify Successful User Login

## Preconditions Guest

1. None

## Preconditions Registered User/Trail Manager/Admin/Root Admin

1. The user must have an active, verified account in the staging database.
2. The user is currently on the application homepage (`/home`) and is logged out.

## Test Steps & Expected Results

| Step | Action Description                                                                      | Expected Result                                                                   | Pass/Fail               |
| :--- | :-------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------- | :---------------------- |
| 1    | Click on the**"Guest"** button in the top navigation bar. Then,**Login/Register** | Redirected to the login page (`/login`). URL is updated.                        | [x] Pass<br /> [ ] Fail |
| 2    | Click "Forgot Password"                                                                 | Page updates to 'Reset Password' mode                                             | [x] Pass<br /> [ ] Fail |
| 3    | Enter valid username/email into the text box.                                           | Entered text displays correctly, no masking                                       | [x] Pass<br />[ ] Fail  |
| 4    | Click the Yellow**"Continue"** button.                                                  | Page updates and displays a textbox for 'Code', 'Password' and 'Confirm Password' | [x] Pass<br />[ ] Fail  |
| 5    | Enter 'Code' (from email), 'Password', and 'Confirm Password'                       | Text displays, code is not masked, passwords are masked                                  | [x] Pass<br />[ ] Fail  |
| 6    | Click eye icon                                                | Password switches from masked to no mask | [x] Pass<br />[ ] Fail  |
| 7    | Click the 'Resend Code' button                                                 | New code is sent to email to use | [x] Pass<br />[ ] Fail  |
| 8    | Click the Yellow**"Update password"** button.                                                  | Page updates back to 'Welcome Back' page | [x] Pass<br />[ ] Fail  |
| 9    | Login regularly (follow steps 3-5 from login.md for help)                                                  | User logs in successfully | [x] Pass<br />[ ] Fail  |



## Post-conditions

* A secure session cookie is established in the browser storage.
* User is left in an authenticated homepage state.
