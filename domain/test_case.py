from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class TestCase:
    descricao: str
    acoes: List[str]
    dados: Dict[str, Any] = field(default_factory=dict)
    resultadoEsperado: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict) -> "TestCase":
        return cls(
            descricao=str(payload["descricao"]),
            acoes=list(payload.get("acoes", [])),
            dados=dict(payload.get("dados", {})),
            resultadoEsperado=list(payload.get("resultadoEsperado", [])),
        )

    def to_gherkin(self) -> str:
        lines = [f"Scenario: {self.descricao}"]

        if self.dados:
            dados = json.dumps(self.dados, ensure_ascii=False, sort_keys=True)
            lines.append(f"  Given dados: {dados}")

        action_keyword = "Given" if not self.dados else "When"
        for index, action in enumerate(self.acoes):
            keyword = action_keyword if index == 0 else "And"
            lines.append(f"  {keyword} {action}")

        for index, expected_result in enumerate(self.resultadoEsperado):
            keyword = "Then" if index == 0 else "And"
            lines.append(f"  {keyword} {expected_result}")

        return "\n".join(lines)


def test_cases_to_gherkin(testcases: list[dict]) -> str:
    scenarios = [
        TestCase.from_dict(testcase).to_gherkin()
        for testcase in testcases
    ]
    return "\n\n".join(scenarios)