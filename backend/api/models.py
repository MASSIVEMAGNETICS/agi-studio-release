from pydantic import BaseModel, Field

class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The input prompt")
    user_id: str = Field("default_user", description="The user ID")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(150, gt=0)
