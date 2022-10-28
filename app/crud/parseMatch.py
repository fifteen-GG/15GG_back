from typing import Optional, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.parseMatch import ParseMatch
from app.schemas.parseMatch import ParseMatchCreate, ParseMatchUpdate


class CRUDParseMatch(CRUDBase[ParseMatch, ParseMatchCreate, ParseMatchUpdate]):
    # Declare model specific CRUD operation methods.
    pass


parseMatch = CRUDParseMatch(ParseMatch)
