from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from docx import Document

from integrations.jira_client import JiraClient
from services.file_service import FileService
from services.playwright_bdd_pipeline import PlaywrightBddPipeline


def test_jira_xray_issue_falls_back_to_task(mocker) -> None:
    jira_client = JiraClient(
        base_url="https://jira.example.com",
        email="user@example.com",
        token="token",
    )

    unavailable = mocker.Mock(status_code=400, text="Issue type Xray Test unavailable")
    unavailable.json.return_value = {}

    created = mocker.Mock(status_code=201, text="")
    created.json.return_value = {"key": "PROJ-123"}

    post = mocker.patch(
        "integrations.jira_client.requests.post",
        side_effect=[unavailable, created],
    )

    result = jira_client.create_xray_test_issue(
        project_key="PROJ",
        summary="TC - requirement",
        testcases=[
            {
                "descricao": "Adicionar produto",
                "acoes": ["Informar dados validos"],
                "dados": {"nome": "Produto A"},
                "resultadoEsperado": ["Produto criado"],
            }
        ],
    )

    assert result == {"key": "PROJ-123"}
    assert jira_client.last_created_issue_type == "Task"
    assert post.call_count == 2
    assert post.call_args_list[0].kwargs["json"]["fields"]["issuetype"]["name"] == "Xray Test"
    assert post.call_args_list[1].kwargs["json"]["fields"]["issuetype"]["name"] == "Task"
    description = post.call_args_list[1].kwargs["json"]["fields"]["description"]
    gherkin_text = description["content"][0]["content"][0]["text"]
    assert "Scenario: Adicionar produto" in gherkin_text
    assert "Informar dados validos" in gherkin_text
    assert "Produto criado" in gherkin_text


def test_convert_feature_to_docx_preserves_gherkin_lines() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        feature_path = root / "products.feature"
        docx_path = root / "output" / "products.docx"

        gherkin = (
            "Feature: Products\n"
            "\n"
            "  Scenario: Add product\n"
            "    Given valid data\n"
        )

        feature_path.write_text(gherkin, encoding="utf-8")

        file_service = FileService(root)

        converted_path = file_service.convert_feature_to_docx(
            feature_path,
            docx_path,
        )

        assert converted_path == docx_path

        assert [
            paragraph.text
            for paragraph in Document(docx_path).paragraphs
        ] == gherkin.splitlines()


def test_process_feature_uploads_docx_and_uses_it_in_chat(mocker) -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        feature_path = root / "products.feature"
        docx_path = root / "output" / "products.docx"

        feature_path.write_text(
            "Feature: Products\n",
            encoding="utf-8",
        )

        fit_client = mocker.Mock()

        fit_client.upload_file.return_value = {
            "filename": "products.docx"
        }

        response = mocker.Mock(
            status_code=200,
            text='"generated steps"',
        )

        response.json.return_value = "generated steps"

        fit_client.send_chat_single_file.return_value = response

        pipeline = PlaywrightBddPipeline(
            file_service=FileService(root),
            fit_client=fit_client,
        )

        result = pipeline.process_feature(
            feature_path,
            docx_path,
        )

        assert result == "generated steps"

        fit_client.upload_file.assert_called_once_with(
            docx_path,
            "products.docx",
        )

        fit_client.send_chat_single_file.assert_called_once()

        assert (
            fit_client.send_chat_single_file.call_args.kwargs["filename"]
            == "products.docx"
        )


def test_process_feature_does_not_start_chat_when_upload_fails(
    mocker,
) -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        feature_path = root / "products.feature"

        feature_path.write_text(
            "Feature: Products\n",
            encoding="utf-8",
        )

        fit_client = mocker.Mock()

        fit_client.upload_file.return_value = None

        pipeline = PlaywrightBddPipeline(
            file_service=FileService(root),
            fit_client=fit_client,
        )

        with pytest.raises(
            RuntimeError,
            match="Upload Failed",
        ):
            pipeline.process_feature(
                feature_path,
                root / "products.docx",
            )

        fit_client.send_chat_single_file.assert_not_called()