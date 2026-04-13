import pytest
import pytest_check
from pathlib import Path
import time

from selenium_helper import SeleniumHelper as SH
from test_data import DEVICES, TRAILS

from dtos.user_dto import UserDTO
from enums.user_enum import User
from steps.dashboard.associate_device_step import AssociateDeviceStep
from steps.dashboard.retrieve_associated_devices_step import RetrieveAssociatedDevicesStep
from steps.login.login_step import LoginStep

@pytest.mark.UI
@pytest.mark.skip(reason="feature bugged")
def associate_device_test():
    """
    Tests Everthing About Associating A Device
     - Displayed Associations Correct
     - Pairs A Device
     - Unpairs A Device
    """
    driver = SH.get_driver()

    try:
        # Login
        login_step = LoginStep(driver, UserDTO(user=User.ADMIN))
        login_step.run()

        # Wait for API Calls To Be Made
        SH.wait(3)

        associate_device = DEVICES[11]
        expected_unpaired_devices = {associate_device}
        expected_paired_devices = set(DEVICES.values())
        expected_paired_devices.remove(associate_device)

        # Retrieve Associations and Verify
        retrieve_associations_original_step = RetrieveAssociatedDevicesStep(driver)
        retrieve_associations_original_step.run()

        pytest_check.equal(expected_unpaired_devices, set(retrieve_associations_original_step.unpaired_devices))
        pytest_check.equal(expected_paired_devices, set(retrieve_associations_original_step.paired_devices))

        # Pair Device
        associate_device.current_trail = TRAILS[11]
        associate_device_step = AssociateDeviceStep(driver, associate_device)
        associate_device_step.run()

        # Verify Device Paired
        expected_unpaired_devices = set()
        expected_paired_devices.add(associate_device)

        retrieve_associations_paired_step = RetrieveAssociatedDevicesStep(driver)
        retrieve_associations_paired_step.run()

        pytest_check.equal(expected_unpaired_devices, set(retrieve_associations_paired_step.unpaired_devices))
        pytest_check.equal(expected_paired_devices, set(retrieve_associations_paired_step.paired_devices))

        # Unpair Device
        associate_device.current_trail = None
        unassociate_device_step = AssociateDeviceStep(driver, associate_device)
        unassociate_device_step.run()

        # Verify Device Unpaired
        expected_unpaired_devices = {associate_device}
        expected_paired_devices.remove(associate_device)

        retrieve_associations_unpaired_step = RetrieveAssociatedDevicesStep(driver)
        retrieve_associations_unpaired_step.run()

        pytest_check.equal(expected_unpaired_devices, set(retrieve_associations_unpaired_step.unpaired_devices))
        pytest_check.equal(expected_paired_devices, set(retrieve_associations_unpaired_step.paired_devices))
    except:
        driver.save_screenshot(Path(__file__).parent / f"errors/associate_device_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()