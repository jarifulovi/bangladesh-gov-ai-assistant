"""LLM service placeholder."""


import uuid

import anyio

from app.core.config import get_settings
from app.core.model_loader import get_model_loader
from app.models.chat import ChatRequest, ChatResponse


class LLMService:
    async def generate_response(
        self,
        request: ChatRequest,
        session_id: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> ChatResponse:
        settings = get_settings()
        active_session_id = session_id or str(uuid.uuid4())

        if settings.use_mock:
            return ChatResponse(
                response=f"Mock response for: {request.message}",
                session_id=active_session_id,
                thread_id="",
            )

        response_text = await anyio.to_thread.run_sync(
            self._generate_sync,
            request.message,
            settings.system_prompt,
            history,
        )
        return ChatResponse(response=response_text, session_id=active_session_id, thread_id="")

    def _generate_sync(self, message: str, system_prompt: str, history: list[dict[str, str]] | None = None) -> str:
        loader = get_model_loader()
        model = loader.model
        tokenizer = loader.tokenizer

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        if hasattr(tokenizer, "apply_chat_template"):
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            prompt = f"System: {system_prompt}\nUser: {message}\nAssistant:"

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        settings = get_settings()
        output_ids = model.generate(
            **inputs,
            max_new_tokens=settings.max_new_tokens,
            temperature=settings.temperature,
            top_p=settings.top_p,
            do_sample=False,
        )
        input_len = inputs["input_ids"].shape[-1]
        generated_ids = output_ids[0][input_len:]
        generated = tokenizer.decode(generated_ids, skip_special_tokens=True)

        return generated.strip()
