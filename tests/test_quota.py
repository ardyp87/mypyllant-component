from datetime import datetime, timedelta

import pytest as pytest
from freezegun import freeze_time
from homeassistant.helpers.update_coordinator import UpdateFailed
from myPyllant.api import MyPyllantAPI
from myPyllant.tests.test_api import list_test_data

from custom_components.mypyllant import QUOTA_PAUSE_INTERVAL


async def test_quota(
    mypyllant_aioresponses, mocked_api: MyPyllantAPI, system_coordinator_mock
):
    # Trigger quota error in the past and check that it raises an exception
    with freeze_time(datetime.now() - timedelta(seconds=QUOTA_PAUSE_INTERVAL + 180)):
        with mypyllant_aioresponses(test_quota=True) as _:
            with pytest.raises(UpdateFailed, match=r"Quota.*") as _:
                system_coordinator_mock.data = (
                    await system_coordinator_mock._async_update_data()
                )

    # Quota error should still raise before the interval is over
    with freeze_time(datetime.now() - timedelta(seconds=QUOTA_PAUSE_INTERVAL / 2)):
        with mypyllant_aioresponses() as _:
            with pytest.raises(UpdateFailed, match=r"Quota.*") as _:
                system_coordinator_mock.data = (
                    await system_coordinator_mock._async_update_data()
                )

    # No more error adter interval is over
    with mypyllant_aioresponses(test_data=list_test_data()[0]) as _:
        system_coordinator_mock.data = (
            await system_coordinator_mock._async_update_data()
        )
    await mocked_api.aiohttp_session.close()
