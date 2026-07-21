# Verify Area Adding

## Preconditions Guest/User

1. N/A

## Preconditions Registered Trail Manager/Admin

1. The user is currently on the dashboard (`/dashboard`) and is logged in as a registered trail manager/admin.

## Test Steps & Expected Results

| Step | Action Description                                                  | Expected Result                                                  | Pass/Fail               |
| :--- | :------------------------------------------------------------------ | :--------------------------------------------------------------- | :---------------------- |
| 1    | Click on the **"Trail Data"** button. Then, click on **"Add Trail"** | The 'Create new area' popup appears opens                                    | [x] Pass<br /> [ ] Fail |
| 2    | Enter valid name into **'Trail Name'** textbox                       | Entered text displays and is displayed correctly                                  | [x] Pass<br /> [ ] Fail |
| 3    | (Optional) Enter text into the **Notes** field.                       | Entered text displays and is displayed correctly                                  | [x] Pass<br /> [ ] Fail |
| 4    | Enter values into the Latitude and Longitude fields.             | The values are accepted and displayed correctly. | [x] Pass<br />[ ] Fail  |
| 5    | (Optional) Select an area from the Area dropdown.                           | The selected area is displayed in the dropdown.                | [x] Pass<br />[ ] Fail  |
| 6    | Click the yellow "Create Trail" button.       | The trail is successfully created and a success message is displayed. The menu closes.   | [x] Pass<br />[ ] Fail  |
| 7    | Click the **'Trails'** dropdown on **`/dashboard`**                         | Verify that newly created trail is in the list of trails           | [x] Pass<br />[ ] Fail  |
|      |                                                                     |                                                                  |                         |

## Post-conditions

* The trail is added to the system.
* If an area was selected, the trail is associated with that area.
* The trail can be selected and viewed on the dashboard.