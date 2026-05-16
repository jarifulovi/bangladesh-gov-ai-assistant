"""Configuration for model loading.

- Always loads the base model (Qwen2.5-1.5B-Instruct by default).
- If lora_adapter_path is set and exists, loads LoRA adapter on top.
- Otherwise, uses only the base model.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Default LoRA adapter output directory (can be overridden)
LORA_ADAPTER_DEFAULT_PATH = "training/outputs/lora_adapter"


class Settings(BaseSettings):
    model_name: str = Field(
        default="model/qwen_model/content/qwen_model",
        description="Base model local path",
    )
    lora_adapter_path: Optional[str] = Field(
        default="training/outputs/lora_adapter",
        description="Optional LoRA adapter path (default: training/outputs/lora_adapter)",
    )
    mongodb_url: str = Field(
        default="mongodb+srv://db-user:db-password@cluster0.wropbbw.mongodb.net/?appName=Cluster0",
        description="MongoDB connection URL",
    )
    mongodb_db: str = Field(
        default="bangladesh_gov_ai",
        description="MongoDB database name",
    )
    max_new_tokens: int = Field(default=32, ge=1, le=2048)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_history_messages: int = Field(
        default=6,
        ge=0,
        description="Max prior user/assistant message pairs to include per thread",
    )
    system_prompt: str = Field(
        default=(
            "You are a helpful assistant for Bangladesh government services. "
            "Respond with a concise, structured answer. Use numbered steps, and use short bullets only when needed."
        )
    )
    use_mock: bool = Field(default=False, description="Return mocked responses")

    model_config = SettingsConfigDict(env_prefix="BG_ASSISTANT_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
