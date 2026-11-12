from __future__ import annotations

import requests
from requests.auth import HTTPBasicAuth

from domain.test_case import test_cases_to_gherkin


class JiraClient:
    def __init__(self, base_url: str, email: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.jira_token = token
        self.last_created_issue_type: str | None = None

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.email, self.jira_token)

    def _create_issue(
        self,
        *,
        project_key: str,
        summary: str,
        preferred_issue_type: str,
        description: dict | None = None,
        fallback_description: dict | None = None,
    ):
        url = f"{self.base_url}/rest/api/3/issue"

        issue_types = tuple(dict.fromkeys((preferred_issue_type, "Task")))

        for issue_type in issue_types:
            fields = {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
            }
            issue_description = (
                fallback_description
                if issue_type == "Task" and fallback_description is not None
                else description
            )
            if issue_description is not None:
                fields["description"] = issue_description

            try:
                if issue_type == "Task" and preferred_issue_type != "Task":
                    print(
                        f"⚠️ Issue type '{preferred_issue_type}' unavailable; "
                        "falling back to 'Task'."
                    )

                response = requests.post(
                    url,
                    json={"fields": fields},
                    auth=self._auth(),
                    headers=self._headers(),
                    timeout=60,
                )
                if response.status_code == 201:
                    self.last_created_issue_type = issue_type
                    return response.json()

                print(
                    f"❌ Request failed to create issue with type '{issue_type}': "
                    f"{response.status_code} - {response.text}"
                )
            except Exception as exc:
                print(f"❌ Error creating issue with type '{issue_type}': {exc}")

        return None

    def create_test_set(self, project_key: str, summary: str):
        try:
            issue = self._create_issue(
                project_key=project_key,
                summary=summary,
                preferred_issue_type="Test Set",
            )
            return issue
        except Exception as exc:
            print(f"❌ Error creating Test Set: {exc}")
            return None

    def create_xray_test_issue(
        self,
        project_key: str,
        summary: str,
        testcases: list[dict] | None = None,
    ):
        description = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "casos de teste no formato Xray"}],
                }
            ],
        }

        gherkin_description = (
            test_cases_to_gherkin(testcases)
            if testcases is not None
            else ""
        )

        task_description = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "codeBlock",
                    "attrs": {"language": "gherkin"},
                    "content": [{"type": "text", "text": gherkin_description}],
                }
            ],
        } if gherkin_description else description

        try:
            issue = self._create_issue(
                project_key=project_key,
                summary=summary,
                preferred_issue_type="Xray Test",
                description=description,
                fallback_description=task_description,
            )
            return issue
        except Exception as exc:
            print(f"❌ Error creating Xray Test: {exc}")
            return None

    def add_test_to_test_set(self, test_set_key: str, test_key: str) -> bool:
        url = f"{self.base_url}/rest/api/3/issueLink"
        payload = {
            "type": {"name": "Relates"},
            "inwardIssue": {"key": test_set_key},
            "outwardIssue": {"key": test_key},
        }

        try:
            response = requests.post(
                url,
                json=payload,
                auth=self._auth(),
                headers=self._headers(),
                timeout=60,
            )
            if response.status_code not in (200, 201, 204):
                print(f"❌ Request failed: {response.status_code} - {response.text}")
                return False
            print(f"✅ Test {test_key} inserted into {test_set_key}")
            return True
        except Exception as exc:
            print(f"❌ Error inserting Test into Test Set: {exc}")
            return False