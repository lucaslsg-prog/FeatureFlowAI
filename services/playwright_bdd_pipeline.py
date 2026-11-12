from __future__ import annotations

from pathlib import Path

from integrations.fit_insight_client import FitInsightClient
from services.file_service import FileService
from utils.prompts import load_playwright_bdd_prompt


class PlaywrightBddPipeline:
    def __init__(self, file_service: FileService, fit_client: FitInsightClient):
        self.file_service = file_service
        self.fit_client = fit_client

    def process_feature(self, feature_path: str | Path, docx_path: str | Path) -> str:
        feature_path = Path(feature_path)
        if not feature_path.is_file():
            raise FileNotFoundError(f"❌ Feature file not found: {feature_path}")

        gherkin = feature_path.read_text(encoding="utf-8")
        if not gherkin.strip():
            raise ValueError(f"Gherkin input cannot be empty: {feature_path}")

        uploaded_path = self.file_service.convert_feature_to_docx(feature_path, docx_path)
        filename = uploaded_path.name
        if self.fit_client.upload_file(uploaded_path, filename) is None:
            raise RuntimeError(f"❌ Upload Failed: {filename}")

        response = self.fit_client.send_chat_single_file(
            prompt=load_playwright_bdd_prompt(gherkin.strip()),
            filename=filename,
        )

        if response.status_code != 200:
            error_detail = response.text.strip() or "(empty response body)"
            if len(error_detail) > 2000:
                error_detail = f"{error_detail[:2000]}... (truncated)"
            raise RuntimeError(
                f"❌ Chat Failed: could not generate Playwright-BDD steps "
                f"(status {response.status_code}): {error_detail}"
            )

        if not response.text.strip():
            raise ValueError("❌ Empty response from LLM")

        try:
            payload = response.json()
        except ValueError as exc:
            raise ValueError("LLM response is not valid JSON") from exc

        if not isinstance(payload, str):
            raise TypeError(
                f"LLM response must contain TypeScript code as a string, got {type(payload)}"
            )

        typescript = payload.strip()
        if not typescript:
            raise ValueError("LLM response contains empty TypeScript code")

        return typescript
