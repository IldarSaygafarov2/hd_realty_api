"""
Domain entities - чистые Python-объекты без Django.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Entity:
    """Base entity with id."""

    id: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
