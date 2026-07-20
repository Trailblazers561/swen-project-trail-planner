# Verify User Ban and Unban

## Preconditions Guest/User

1. User does not have access the Privileges page.

## Preconditions Registered Trail Manager/Admin

1. User is logged in as an admin or Root Admin and is logged in as a registered trail manager/admin.

## Test Steps & Expected Results

| Step | Action Description                                                  | Expected Result                                                  | Pass/Fail               |
| :--- | :------------------------------------------------------------------ | :--------------------------------------------------------------- | :---------------------- |
| 1    | Locate a user who is not banned. | The selected user is shown with **No** under the **Banned?** column.                                   | [x] Pass<br /> [ ] Fail |
| 2    | Click the dark red "Ban" button for that user.                      | The ban confirmation popup appears.                              | [x] Pass<br /> [ ] Fail |
| 3    | Select "Yes" on the ban confirmation popup.                      | The table refreshes to reflect the change.                                   | [x] Pass<br /> [ ] Fail |
| 4    | Verify the user's status in the table.             | The selected user now displays **Yes** in the **Banned?** column. | [x] Pass<br />[ ] Fail  |
| 5    | Click the blue Unban button for the same user.                          | The unban confirmation popup appears.                | [x] Pass<br />[ ] Fail  |
| 6    | Select "Yes" on the ban confirmation popup.                      | The table refreshes to reflect the change.     | [x] Pass<br />[ ] Fail  |
| 7    | Verify the user's status in the table.                         | The user's ban status goes back to No.          | [x] Pass<br />[ ] Fail  |
|      |                                                                     |                                                                  |                         |

## Post-conditions

* The selected user's ban status has been updated successfully.
* The updated status persists after refreshing the page.