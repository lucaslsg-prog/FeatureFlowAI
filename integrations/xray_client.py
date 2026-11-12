from __future__ import annotations

import json
import time
from typing import Any

import requests


class XrayClient:
    BASE_URL = "https://xray.cloud.getxray.app/api/v2"

    @staticmethod
    def build_test_steps_payload(testcases: list[dict[str, Any]], xray_issue: str, summary_title: str, project_key: str) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        step_counter_index = 1

        for tc in testcases:
            description = tc.get("descricao", "")
            obj_data = tc.get("dados", {})
            formatted_data = json.dumps(obj_data, ensure_ascii=True, separators=(",", ":")) if obj_data else ""
            actions = tc.get("acoes", [])
            results = tc.get("resultadoEsperado", [])

            if not actions:
                raise ValueError(f"Action not found for description field: {description}")

            for index, action in enumerate(actions):
                expected_result = results[index] if index < len(results) else ""
                summary = f"CASE {step_counter_index} - {description}"
                data = formatted_data if index == 0 else ""

                if all([summary, action, data, expected_result]):
                    steps.append(
                        {
                            "Summary": summary,
                            "action": action,
                            "data": data,
                            "result": expected_result,
                        }
                    )
                    step_counter_index += 1

        return [{
            "key": xray_issue,
            "testtype": "Manual",
            "fields": {"project": {"key": project_key}, "summary": summary_title},
            "steps": steps,
        }]

    def auth_xray_api_token(self, client_id: str, client_secret: str) -> str:
        response = requests.post(
            f"{self.BASE_URL}/authenticate",
            json={"client_id": client_id, "client_secret": client_secret},
            timeout=60,
        )

        if response.status_code not in (200, 201, 204):
            raise RuntimeError(f"❌ Request failed to create Xray API Token: {response.text}")

        print("✅ Xray API Token Created")
        return response.text.strip().replace('"', '')

    def get_job_id(self, payload: list[dict[str, Any]], token: str, retries: int = 5) -> str:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        for attempt in range(retries):
            try:
                response = requests.post(
                    f"{self.BASE_URL}/import/test/bulk",
                    json=payload,
                    headers=headers,
                    timeout=60,
                )

                if response.status_code in (200, 201, 202):
                    data = response.json()
                    job_id = data.get("jobId")
                    if not job_id:
                        raise RuntimeError("JobId not found in response")
                    print("\n⏳ Awaiting response from Xray API...")
                    print(f"✅ Job created with ID: {job_id}")
                    return job_id

                if response.status_code in (500, 502, 503, 504):
                    delay = 2 ** attempt
                    print(f"⚠️ Retry in {delay}s...")
                    time.sleep(delay)
                    continue

                raise RuntimeError(f"❌ Request failed: {response.status_code} - {response.text}")
            except requests.RequestException as exc:
                delay = 2 ** attempt
                print(f"⚠️ Network error, retrying in {delay}s...")
                time.sleep(delay)

        raise RuntimeError("❌ Max retries reached")

    def check_bulk_import_status(self, job_id: str, token: str):
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        response = requests.get(
            f"{self.BASE_URL}/import/test/bulk/{job_id}/status",
            headers=headers,
            timeout=30,
        )
        print("\n⏳ Import Steps in progress: ", response.text)

        if response.status_code not in (200, 201, 204):
            raise RuntimeError("❌ Failed to check job status")

        print("✅ Job status retrieved successfully")
        return response.json()