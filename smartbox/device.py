from pydantic import BaseModel
from typing import Optional
from smartbox.node import Node, Nodes
from typing import Any, Dict, Any

# from smartbox.home import SmartboxHome


class DeviceAwayStatus(BaseModel):
    enabled: bool
    away: bool
    forced: bool


class Device(BaseModel):
    dev_id: str
    name: str
    product_id: str
    fw_version: str
    serial_id: str
    nodes: Optional[list[Node]] = None
    # away_status: Optional[DeviceAwayStatus] = None


#     home: "Optional[Home]" = None


# from smartbox.home import Home

# Device.model_rebuild()


class Devices(BaseModel):
    devs: list[Device]
    invited_to: list


class SmartboxDevice:
    def __init__(self, device: Device | str | Dict[str, Any], session):
        if isinstance(device, str):
            response = session._api_request("devs")
            devices = Devices.model_validate(response)
            self._device = next(item for item in devices.devs if item.dev_id == device)
        elif isinstance(device, Device):
            self._device = device
        else:
            self._device = Device.model_validate(device)
        self._session = session

    @property
    def dev_id(self) -> str:
        return self._device.dev_id

    @property
    def name(self) -> str:
        return self._device.name

    @property
    def product_id(self) -> str:
        return self._device.product_id

    @property
    def fw_version(self) -> str:
        return self._device.fw_version

    @property
    def device(self) -> str:
        return self._device

    @property
    def nodes(self) -> list[Node]:
        if self._device.nodes is None:
            self._device.nodes = self.get_nodes()
        return self.get_nodes()

    def get_nodes(self) -> list[Node]:
        response = self._session._api_request(f"devs/{self.dev_id}/mgr/nodes")
        nodes = Nodes.model_validate(response)
        return nodes.nodes

    @property
    def away_status(self) -> DeviceAwayStatus:
        return DeviceAwayStatus.model_validate(
            self._session._api_request(f"devs/{self.dev_id}/mgr/away_status")
        )

    @property
    def home(self):
        raise Exception("not impemented")
        # TODO : si c'est None alors il faut faire un get_home_from_device
        return self.home

    def set_device_away_status(self, status_args: Dict[str, Any]) -> Dict[str, Any]:
        data = {k: v for k, v in status_args.items() if v is not None}
        return self._api_post(data=data, path=f"devs/{self.dev_id}/mgr/away_status")

    def get_device_power_limit(self) -> int:
        resp = self._api_request(f"devs/{self.dev_id}/htr_system/power_limit")
        return int(resp["power_limit"])

    def set_device_power_limit(self, power_limit: int) -> None:
        data = {"power_limit": str(power_limit)}
        self._api_post(data=data, path=f"devs/{self.dev_id}/htr_system/power_limit")
