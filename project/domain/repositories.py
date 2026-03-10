"""
Repository interfaces - абстракции для доступа к данным.
Implementations живут в infrastructure.
"""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository interface."""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def list_all(self) -> List[T]:
        pass
