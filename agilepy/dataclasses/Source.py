from dataclasses import dataclass
from typing import List

@dataclass
class Parameter:
    free: int = None
    name: str = None
    value: float = None
    min: float = None
    max: float = None
    scale: float = None

@dataclass
class SourceDescription:
    parameters: List[Parameter]
    name: str = None #spectrum or spatialModel
    type: str = None

@dataclass
class Source:
    SourceDescription: List[SourceDescription]
    name: str = None
    type: str = None
    ROI_Center_Distance: float = None

@dataclass
class SourceLibrary:
    sources: List[Source]
    title: str
