from pydantic import BaseModel, Field
from typing import Optional, List

class OnDemandArticleSchema(BaseModel):
    """
    Strict validation schema for LLM output defense.
    Rejects malformed or injected field responses.
    """
    title: str = Field(..., min_length=1, max_length=300)
    author: Optional[str] = Field(default="Unknown", max_length=100)
    publication_date: Optional[str] = Field(default="Unknown", max_length=50)
    content: str = Field(..., min_length=10, max_length=50000)
    url: str = Field(..., min_length=1, max_length=1000)

class OnDemandResponseSchema(BaseModel):
    articles: List[OnDemandArticleSchema] = Field(..., min_length=1, max_length=10)
