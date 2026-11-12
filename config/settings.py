from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    fit_api_key: str
    upload_route: str
    chat_route: str
    jira_base_url: str
    jira_email: str
    jira_token: str
    client_id: str
    client_secret: str
    project_key: str
    test_set_name: str
    docs_path: Path
    output_dir: Path

    @classmethod
    def load(cls, *, require_jira: bool = True) -> "Settings":
        load_dotenv()

        project_key = os.getenv("PROJECT_KEY")
        test_set_name = os.getenv("TEST_SET_NAME")
        docs_path = Path(os.getenv("DOCS_PATH", "MDSC_requirements")).resolve()
        output_dir = Path(os.getenv("OUTPUT_DIR", "output")).resolve()

        values = {
            "fit_api_key": os.getenv("FIT_INSIGHT_API_KEY"),
            "upload_route": os.getenv("UPLOAD_ROUTE"),
            "chat_route": os.getenv("CHAT_ROUTE"),
            "jira_base_url": os.getenv("JIRA_BASE_URL", ""),
            "jira_email": os.getenv("JIRA_EMAIL", ""),
            "jira_token": os.getenv("JIRA_TOKEN", ""),
            "client_id": os.getenv("CLIENT_ID", ""),
            "client_secret": os.getenv("CLIENT_SECRET", ""),
            "project_key": project_key,
            "test_set_name": test_set_name,
            "docs_path": docs_path,
            "output_dir": output_dir,
        }

        required = ["fit_api_key", "upload_route", "chat_route"]
        if require_jira:
            required.extend(
                [
                    "jira_base_url",
                    "jira_email",
                    "jira_token",
                    "client_id",
                    "client_secret",
                    "project_key",
                    "test_set_name",
                ]
            )

        missing = [key for key in required if values[key] in (None, "")]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

        return cls(**values)