from pydantic import BaseModel, RootModel
from typing import Optional
from smartbox.error import SmartboxHomeNotFound


class Home(BaseModel):
    id: str
    name: str
    devs: "Optional[list[Device]]" = None
    owner: bool


class Homes(RootModel):
    root: list[Home]


from smartbox.device import Device

Home.model_rebuild()


class SmartboxHome:
    def __init__(self, home: Home, session):
        self._home = home
        self._session = session

    def _set_devices(self) -> list[Device]:
        response = self._session._api_request("grouped_devs")
        homes = Homes.model_validate(response)
        for home in homes.root:
            if home.id == self._home.id:
                self.home = home
                return home.devs
        raise SmartboxHomeNotFound(f"Home {self.name} nout found.")

    @property
    def id(self) -> str:
        return self._home.id

    @property
    def name(self) -> str:
        return self._home.name

    @property
    def owner(self) -> bool:
        return self._home.owner

    @property
    def devices(self) -> list[Device]:
        if self.home.devs is None:
            return self._set_devices()
        return self._home.devs
