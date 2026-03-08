class Entity:
    """
    The main domain abstract Entity class.
    It shall contain a name and an identifier.
    """
    def get_id(self) -> int: pass
    def get_name(self) -> str: pass
    def set_id(self, new_id: int) -> None: pass
    def set_name(self, new_name: str) -> None: pass