from . import FirebaseService, NintendoSwitchOnlineService

__all__ = ("Service",)


class Service(FirebaseService, NintendoSwitchOnlineService):
    pass
