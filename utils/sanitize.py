import re


def sanitize_llm_json(json_str: str) -> str:
    json_str = re.sub(r"\\'", "'", json_str)
    json_str = json_str.replace("´", "'")
    json_str = json_str.replace("`", "'")
    json_str = re.sub(r'"a"\.repeat\(\d+\)', '"string_repetida"', json_str)
    json_str = re.sub(r",\s*(\]|\})", r"\1", json_str)
    return json_str