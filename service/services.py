from .nso import NintendoSwitchOnlineService
from .types.services import Service as IService

__all__ = ("Service",)


class Service(NintendoSwitchOnlineService, IService):
    pass
