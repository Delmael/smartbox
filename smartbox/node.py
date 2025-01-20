from pydantic import BaseModel, RootModel
from typing import Optional
from typing import Any, Dict, Any


class NodeFactoryOptions(BaseModel):
    temp_compensation_enabled: bool
    window_mode_available: bool
    true_radiant_available: bool
    duty_limit: int
    boost_config: int
    button_double_press: bool
    prog_resolution: int
    bbc_value: int
    bbc_available: bool
    lst_value: int
    lst_available: bool
    fil_pilote_available: bool
    backlight_time: int
    button_down_code: int
    button_up_code: int
    button_mode_code: int
    button_prog_code: int
    button_off_code: int
    button_boost_code: int
    splash_screen_type: int


class NodeExtraOptions(BaseModel):
    boost_temp: str
    boost_time: int


class NodeSetup(BaseModel):
    sync_status: str
    control_mode: int
    units: str
    power: str
    offset: str
    away_mode: int
    away_offset: str
    modified_auto_span: int
    window_mode_enabled: bool
    true_radiant_enabled: bool
    user_duty_factor: int
    flash_version: str
    factory_options: NodeFactoryOptions
    extra_options: NodeExtraOptions


class NodeStatus(BaseModel):
    sync_status: str
    mode: str
    active: bool
    ice_temp: str
    eco_temp: str
    comf_temp: str
    units: str
    stemp: str
    mtemp: str
    power: str
    locked: int
    duty: int
    act_duty: int
    pcb_temp: str
    power_pcb_temp: str
    presence: bool
    window_open: bool
    true_radiant_active: bool
    boost: bool
    boost_end_min: int
    boost_end_day: int
    error_code: str


class Node(BaseModel):
    name: str
    addr: int
    type: str
    installed: bool
    lost: bool
    status: Optional[NodeStatus] = None
    setup: Optional[NodeSetup] = None


class Nodes(BaseModel):
    nodes: list[Node]


class SmartboxNode:
    def __init__(self, node: Node | str | Dict[str, Any], session):
        if isinstance(node, str):
            # TODO : aller get le device
            response = session._api_request("devs")
            devices = Nodes.model_validate(response)
            self._device = next(item for item in devices.devs if item.dev_id == node)
        elif isinstance(node, Node):
            self._node = node
        else:
            self._node = Node.model_validate(node)
        self._session = session

    @property
    def device(self):
        return self._device

    @property.setter
    def device(self, device):
        self._device = device

    @property
    def name(self) -> str:
        return self._node.home

    @property
    def addr(self) -> int:
        return self._node.addr

    @property
    def type(self) -> str:
        return self._node.type

    @property
    def installed(self) -> str:
        return self._node.installed

    @property
    def node(self) -> str:
        return self._node

    @property
    def status(self) -> NodeStatus:
        return NodeStatus.model_validate(
            self._session._api_request(
                f"devs/{self.device.dev_id}/{self.node.type}/{self.node.addr}/status"
            )
        )

    def set_status(
        self,
        status_args: Dict[str, Any],
    ) -> Dict[str, Any]:
        data = {k: v for k, v in status_args.items() if v is not None}
        if "stemp" in data and "units" not in data:
            raise ValueError("Must supply unit with temperature fields")
        return self._session._api_post(
            data=data, path=f"devs/{self.device.dev_id}/{self.type}/{self.addr}/status"
        )

    # def get_status(self) -> NodeStatus:
    #     return NodeStatus.model_validate(
    #         self._session._api_request(
    #             f"devs/{self.node.device.dev_id}/{self.node.type}/{self.node.addr}/status"
    #         )
    #     )

    # def set_node_status(
    #     self,
    #     status_args: Dict[str, Any],
    # ) -> Dict[str, Any]:
    #     data = {k: v for k, v in status_args.items() if v is not None}
    #     if "stemp" in data and "units" not in data:
    #         raise ValueError("Must supply unit with temperature fields")
    #     return self._session._api_post(
    #         data=data, path=f"devs/{self.device.dev_id}/{self.type}/{self.addr}/status"
    #     )

    def get_node_setup(self) -> NodeSetup:
        return NodeSetup.model_validate(
            self._session._api_request(
                f"devs/{self.device.dev_id}/{self.type}/{self.addr}/setup"
            )
        )

    def set_node_setup(
        self,
        setup_args: Dict[str, Any],
    ) -> Dict[str, Any]:
        data = {k: v for k, v in setup_args.items() if v is not None}
        # setup seems to require all settings to be re-posted, so get current
        # values and update
        setup_data = self.get_node_setup().model_dump(mode="json")
        setup_data.update(data)
        return self._session._api_post(
            data=setup_data,
            path=f"devs/{self.device.dev_id}/{self.type}/{self.addr}/setup",
        )
