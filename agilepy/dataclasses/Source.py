from dataclasses import dataclass
from typing import List

@dataclass
class Parameter:
    name: str
    value: float
    free: int = None
    scale: float = None
    min: float = None
    max: float = None

class ValueParamFinder:
    def getParamAttributeWhere(self, attributeName, key, value):
        return [getattr(param, attributeName) for param in self.parameters if getattr(param, key) == value].pop()

@dataclass
class Spectrum(ValueParamFinder):
    type: str
    parameters: List[Parameter]

@dataclass
class SpatialModel(ValueParamFinder):
    type: str
    location_limit: int
    free: int
    parameters: List[Parameter]

@dataclass
class Source:
    name: str
    type: str
    spatialModel: SpatialModel = None
    spectrum: Spectrum = None


@dataclass
class SourceLibrary:
    title: str
    sources: List[Source]
