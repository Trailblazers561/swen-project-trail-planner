
# Verify Area Adding

## Preconditions Guest/User

1. N/A

## Preconditions Registered Trail Manager/Admin

1. The user is currently on the dashboard (`/dashboard`) and is logged in as a registered trail manager/admin.

## Test Steps & Expected Results

| Step | Action Description                                                  | Expected Result                                                  | Pass/Fail               |
| :--- | :------------------------------------------------------------------ | :--------------------------------------------------------------- | :---------------------- |
| 1    | Click on the**"Area Options"** button. Then, click on**"Add Area"** | 'Create new area' popup opens                                    | [x] Pass<br /> [ ] Fail |
| 2    | Enter valid username into 'Area Name' textbox                       | Entered text displays correctly                                  | [x] Pass<br /> [ ] Fail |
| 3    | Click on trails in the 'Select Trails' check box list               | Trails can be checked/unchecked, to add to the area when created | [x] Pass<br />[ ] Fail  |
| 4    | Click the Yellow**"Create Area"** button.                           | Green text displays - 'Area Created Successfully'                | [x] Pass<br />[ ] Fail  |
| 5    | Enter 'Code' (from email), 'Password', and 'Confirm Password'       | Text displays, code is not masked, passwords are masked          | [x] Pass<br />[ ] Fail  |
| 6    | Click the 'Areas' dropdown on`/dashboard`                         | Verify that newly created area is in the list of areas           | [x] Pass<br />[ ] Fail  |
|      |                                                                     |                                                                  |                         |

## Post-conditions

* The area is added to the system
* Trails that were selected are now associated to the new area
