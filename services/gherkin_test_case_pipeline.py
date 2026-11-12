from __future__ import annotations

from pathlib import Path

from integrations.fit_insight_client import FitInsightClient
from services.file_service import FileService
from utils.prompts import load_gherkin_test_case_prompt


class GherkinTestCasePipeline:
    def __init__(self, file_service: FileService, fit_client: FitInsightClient):
        self.file_service = file_service
        self.fit_client = fit_client

    def process_file(self, file_path: str | Path, clean_name: str) -> str:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"❌ File not found: {file_path}")

        if not self.fit_client.upload_file(file_path, clean_name):
            raise RuntimeError(f"❌ Upload Failed: {clean_name}")

        response = self.fit_client.send_chat_single_file(
            prompt=load_gherkin_test_case_prompt(),
            filename=clean_name,
        )

        if response.status_code != 200:
            raise RuntimeError(f"❌ Chat Failed: {clean_name} (status {response.status_code})")

        if not response.text.strip():
            raise ValueError("❌ Empty response from LLM")

        try:
            payload = response.json()
        except ValueError as exc:
            raise ValueError("LLM response is not valid JSON") from exc

        if not isinstance(payload, str):
            raise TypeError(f"LLM response must contain a Gherkin string, got {type(payload)}")

        gherkin = payload.strip()
        if not gherkin:
            raise ValueError("LLM response contains an empty Gherkin string")

        return gherkin
