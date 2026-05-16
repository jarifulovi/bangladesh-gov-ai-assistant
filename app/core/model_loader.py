"""Model loading utilities with optional LoRA adapter support."""

from functools import lru_cache
import os

from app.core.config import get_settings


class ModelLoader:
    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None

    def load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError("transformers is required for model loading") from exc

        settings = get_settings()
        self._tokenizer = AutoTokenizer.from_pretrained(settings.model_name)
        self._model = AutoModelForCausalLM.from_pretrained(
            settings.model_name,
            torch_dtype="auto",
            device_map="auto",
        )

        # Only load LoRA if adapter path is set and exists
        if settings.lora_adapter_path and os.path.exists(settings.lora_adapter_path):
            try:
                from peft import PeftModel
            except ImportError as exc:
                raise RuntimeError("peft is required for LoRA adapters") from exc

            self._model = PeftModel.from_pretrained(self._model, settings.lora_adapter_path)
        # else: use base model only

    @property
    def model(self):
        self.load()
        return self._model

    @property
    def tokenizer(self):
        self.load()
        return self._tokenizer


@lru_cache
def get_model_loader() -> ModelLoader:
    return ModelLoader()
