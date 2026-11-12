from __future__ import annotations

import unicodedata
from pathlib import Path

from docx import Document


class FileService:
    def __init__(self, folder_path: str | Path):
        self.folder_path = Path(folder_path)
        if not self.folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {self.folder_path}")

    def normalize_filename(self, filename: str) -> str:
        normalized = unicodedata.normalize("NFKD", filename)
        normalized = normalized.encode("ascii", "ignore").decode("ascii")
        return (
            normalized.replace(" ", "_")
            .replace("[", "")
            .replace("]", "")
            .replace("(", "")
            .replace(")", "")
        )

    def iter_files(self):
        for file_path in self.folder_path.iterdir():
            if file_path.is_file():
                yield file_path, self.normalize_filename(file_path.name)

    def convert_feature_to_docx(
        self,
        feature_path: str | Path,
        output_path: str | Path,
    ) -> Path:
        source_path = Path(feature_path)
        docx_path = Path(output_path)

        if not source_path.is_file():
            raise FileNotFoundError(f"Feature file not found: {source_path}")
        if source_path.suffix.lower() != ".feature":
            raise ValueError(f"Expected a .feature file, got: {source_path}")
        if docx_path.suffix.lower() != ".docx":
            raise ValueError(f"Expected a .docx output path, got: {docx_path}")

        gherkin = source_path.read_text(encoding="utf-8")
        if not gherkin.strip():
            raise ValueError(f"Feature file is empty: {source_path}")

        document = Document()
        for line in gherkin.splitlines():
            document.add_paragraph(line)

        docx_path.parent.mkdir(parents=True, exist_ok=True)
        document.save(docx_path)
        return docx_path