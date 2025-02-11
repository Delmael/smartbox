from unittest.mock import patch

from asyncclick.testing import CliRunner
import pytest

from smartbox.resailer import SmartboxResailer
from smartbox.session import AsyncSession, AsyncSmartboxSession, Session
from smartbox.update_manager import UpdateManager
from tests.common import fake_get_request


@pytest.fixture
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture
def mock_session(mocker):
    return mocker.patch("smartbox.cmd.AsyncSmartboxSession")


@pytest.fixture
def update_manager(mock_session):
    return UpdateManager(mock_session, "device_id")


@pytest.fixture
def async_smartbox_session(mocker, resailer):
    async_smartbox_session = AsyncSmartboxSession(
        api_name="test_api",
        username="test_user",
        password="test_password",
    )
    with (
        patch(
            "smartbox.session.AsyncSmartboxSession._api_request",
            autospec=True,
            side_effect=fake_get_request,
        ),
        patch(
            "smartbox.update_manager.SocketSession",
            autospec=True,
            side_effect=fake_get_request,
        ),
    ):
        yield async_smartbox_session


@pytest.fixture
def session(resailer):
    return Session(
        api_name="test_api",
        username="test_user",
        password="test_password",
    )


@pytest.fixture
def async_session(resailer):
    api_name = "test_api"
    username = "test_user"
    password = "test_password"

    session = AsyncSession(
        api_name=api_name,
        username=username,
        password=password,
    )
    with patch(
        "smartbox.session.AsyncSession.client",
        autospec=True,
        side_effect=fake_get_request,
    ):
        yield session


@pytest.fixture
def person():
    return SmartboxResailer(
        name="test",
        api_url="test_api",
        basic_auth="test_credentials",
        serial_id=10,
        web_url="http",
    )


@pytest.fixture
def resailer(mocker):
    return mocker.patch(
        "smartbox.resailer.AvailableResailers.resailers",
        new_callable=mocker.PropertyMock,
        return_value={
            "test_api": SmartboxResailer(
                name="test",
                api_url="test_api",
                basic_auth="test_credentials",
                serial_id=10,
                web_url="http",
            ),
        },
    )
