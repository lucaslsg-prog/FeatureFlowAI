from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class FitInsightClient:
    def __init__(self, api_key: str, upload_url: str, chat_url: str):
        self.api_key = api_key
        self.upload_url = upload_url
        self.chat_url = chat_url

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def upload_file(self, file_path: str | Path, filename: str) -> dict[str, Any] | None:
        if isinstance(file_path, Path):
            file_path = str(file_path)

        if not filename or not isinstance(filename, str):
            raise TypeError(f"filename must be a non-empty string, got {type(filename)}")

        try:
            with open(file_path, "rb") as file_handle:
                response = requests.post(
                    self.upload_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    data={"path": ""},
                    files={"files": (filename, file_handle)},
                    timeout=120,
                )

            if response.status_code not in (200, 201):
                print(f"❌ Upload failed with status {response.status_code}: {response.text}")
                return None

            try:
                return response.json()
            except ValueError:
                return {"raw": response.text, "filename": filename}

        except requests.RequestException as exc:
            print(f"❌ Upload Error (requests): {exc}")
            return None

    def send_chat_single_file(self, prompt: str, filename: str) -> requests.Response:
        return self._send_chat(prompt=prompt, file_list=[filename])

    def send_chat(self, prompt: str) -> requests.Response:
        return self._send_chat(prompt=prompt, file_list=[])

    def _send_chat(self, prompt: str, file_list: list[str]) -> requests.Response:
        body = {
            "model_id": 9,
            "user_input": prompt,
            "file_list": file_list,
            "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "topic": "Creating test cases",
        }

        return requests.post(
            self.chat_url,
            json=body,
            headers=self._auth_headers(),
            timeout=120,
        )