from pydantic import BaseModel, Field

class Size(BaseModel):
    w: float
    h: float

class Constraints(BaseModel):
    min_w: float = Field(default=0.0)
    max_w: float = Field(default=float('inf'))
    min_h: float = Field(default=0.0)
    max_h: float = Field(default=float('inf'))

    def clamp_w(self, w: float) -> float:
        return max(self.min_w, min(self.max_w, w))

    def clamp_h(self, h: float) -> float:
        return max(self.min_h, min(self.max_h, h))