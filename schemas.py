from enum import IntEnum
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

# ——— ENUMS (INT) ———
class Criticity(IntEnum):
    VERYLOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERYHIGH = 5

class StoryType(IntEnum):
    USER = 1
    TECHNICAL = 2
    BUG = 3

class Priority(IntEnum):
    BAJA = 0
    MEDIA = 1
    ALTA = 2

# ——— STORY SCHEMAS ———
class StoryBase(BaseModel):
    title: str
    raw_description: Optional[str] = None
    criticity: Optional[Criticity] = None
    story_points: Optional[int] = Field(None, ge=0)
    acceptance_criteria: Optional[str] = None
    business_value: Optional[int] = Field(None, ge=0)
    complexity: Optional[int] = Field(None, ge=0)
    story_type: StoryType = StoryType.USER
    continuation: int = 0
    internal_dependencies: int = 0

class StoryCreate(StoryBase):
    pass

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    raw_description: Optional[str] = None
    criticity: Optional[Criticity] = None
    story_points: Optional[int] = Field(None, ge=0)
    acceptance_criteria: Optional[str] = None
    business_value: Optional[int] = Field(None, ge=0)
    complexity: Optional[int] = Field(None, ge=0)
    story_type: Optional[StoryType] = None
    continuation: Optional[int] = None
    internal_dependencies: Optional[int] = None
    formatted_description: Optional[str] = None
    priority: Optional[Priority] = None

class Story(StoryBase):
    id: int
    formatted_description: Optional[str] = None
    priority: Optional[Priority] = None

    class Config:
        from_attributes = True
        use_enum_values = True  

# ——— PBI SCHEMAS ———
class PBIBase(BaseModel):
    title: str
    description: Optional[str] = None

class PBICreate(PBIBase):
    sprint_id: int

class PBIUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sprint_id: Optional[int] = None

class PBI(PBIBase):
    id: int
    sprint_id: Optional[int] = None
    stories: List[Story] = Field(default_factory=list)

    class Config:
        from_attributes = True
        use_enum_values = True  

# ——— SPRINT SCHEMAS ———
class SprintBase(BaseModel):
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class SprintCreate(SprintBase):
    pass

class SprintUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class Sprint(SprintBase):
    id: int
    pbis: List[PBI] = Field(default_factory=list)

    class Config:
        from_attributes = True
        use_enum_values = True  
