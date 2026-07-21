# Verify Successful User Logout

## Preconditions Guest/User

1. User does not have permission to create devices.

## Preconditions Manager/Admin/Root Admin

1. he user is currently on the device management page and is logged in as a registered trail manager/admin.

## Test Steps & Expected Results

| Step | Action Description                                                  | Expected Result                                                  | Pass/Fail               |
| :--- | :------------------------------------------------------------------ | :--------------------------------------------------------------- | :---------------------- |
| 1    | Click the **"Create Device"** button. | The Create Device popup appears.                                  | [x] Pass<br /> [ ] Fail |
| 2    | Enter a valid name into the **Device Name** field.                      | The entered device name displays correctly.                              | [x] Pass<br /> [ ] Fail |
| 3    | Enter a valid unique device serial number into the **Device Serial** field.                      | The entered serial number displays correctly.                                   | [x] Pass<br /> [ ] Fail |
| 4    | Click the **"Create Device"** button.                          | The success message appears and the table refreshes to reflect the change.                | [x] Pass<br />[ ] Fail  |
| 5    | Verify the newly created device appears in the Device Management table.                      | The new device is listed with the correct device name and serial number     | [x] Pass<br />[ ] Fail  |
|      |                                                                     |                                                                  |                         |

## Post-conditions

* A new device has been added to the system.
* TThe new device appears in the Device Management table.
* The device is available for future association with a trail.