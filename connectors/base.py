from abc import ABC, abstractmethod
from pydantic import BaseModel, ValidationError


class ConnectorConfig(BaseModel):
    """Generic connector config; extend in subclasses."""
    pass


class BaseConnector(ABC):
    ConfigModel = ConnectorConfig

    def __init__(self, config: dict):
        try:
            self.config = self.ConfigModel(**config)
        except ValidationError as e:
            raise ValueError(f"Invalid config for {self.__class__.__name__}: {e}")

    @abstractmethod
    def fetch(self):
        pass

