import argparse
from pathlib import Path

from config.settings import Settings
from integrations.fit_insight_client import FitInsightClient
from integrations.jira_client import JiraClient
from integrations.xray_client import XrayClient
from services.file_service import FileService
from services.gherkin_test_case_pipeline import GherkinTestCasePipeline
from services.playwright_bdd_pipeline import PlaywrightBddPipeline
from services.test_case_pipeline import TestCasePipeline


def _create_fit_client(settings: Settings) -> FitInsightClient:
    return FitInsightClient(
        api_key=settings.fit_api_key,
        upload_url=settings.upload_route,
        chat_url=settings.chat_route,
    )


def _run_generated_pipelines(
    settings: Settings,
    fit_client: FitInsightClient,
    pipeline_mode: str,
    gherkin_dir: Path | None,
) -> None:
    file_service = FileService(settings.docs_path)
    gherkin_pipeline = GherkinTestCasePipeline(file_service=file_service, fit_client=fit_client)
    playwright_pipeline = PlaywrightBddPipeline(file_service=file_service, fit_client=fit_client)
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    if pipeline_mode in ("gherkin", "all"):
        for original_path, clean_name in file_service.iter_files():
            feature_path = settings.output_dir / f"{Path(clean_name).stem}.feature"
            print(f"\n🚀 Generating Gherkin for: {original_path}")
            gherkin = gherkin_pipeline.process_file(original_path, clean_name)
            feature_path.write_text(gherkin + "\n", encoding="utf-8")
            print(f"✅ Gherkin saved: {feature_path}")

            if pipeline_mode == "all":
                docx_path = settings.output_dir / f"{feature_path.stem}.docx"
                typescript = playwright_pipeline.process_feature(feature_path, docx_path)
                print(f"✅ Gherkin Word document saved: {docx_path}")
                typescript_path = settings.output_dir / f"{Path(clean_name).stem}.steps.ts"
                typescript_path.write_text(typescript + "\n", encoding="utf-8")
                print(f"✅ Playwright-BDD steps saved: {typescript_path}")

    if pipeline_mode == "playwright-bdd":
        source_dir = gherkin_dir or settings.output_dir
        feature_files = sorted(source_dir.glob("*.feature"))
        if not feature_files:
            raise FileNotFoundError(f"No .feature files found in Gherkin directory: {source_dir}")

        for feature_path in feature_files:
            print(f"\n🚀 Generating Playwright-BDD steps for: {feature_path}")
            docx_path = settings.output_dir / f"{feature_path.stem}.docx"
            typescript = playwright_pipeline.process_feature(feature_path, docx_path)
            print(f"✅ Gherkin Word document saved: {docx_path}")
            typescript_path = settings.output_dir / f"{feature_path.stem}.steps.ts"
            typescript_path.write_text(typescript + "\n", encoding="utf-8")
            print(f"✅ Playwright-BDD steps saved: {typescript_path}")


def _run_json_pipeline(settings: Settings, fit_client: FitInsightClient) -> None:
    file_service = FileService(settings.docs_path)
    jira_client = JiraClient(
        base_url=settings.jira_base_url,
        email=settings.jira_email,
        token=settings.jira_token,
    )
    xray_client = XrayClient()
    pipeline = TestCasePipeline(file_service=file_service, fit_client=fit_client)

    print("\n🚀 Starting Fit Insight Pipeline...\n")

    test_set = jira_client.create_test_set(
        project_key=settings.project_key,
        summary=settings.test_set_name,
    )
    if not test_set:
        raise RuntimeError("❌ Failed to create Test Set")

    test_set_key = test_set["key"]
    print(f"✅ Test Set Created: {test_set_key}")

    for original_path, clean_name in file_service.iter_files():
        title = f"TC - {clean_name}"
        print(f"\n🚀 Processing file: {original_path}")

        try:
            testcases = pipeline.process_file(original_path, clean_name)
            if not testcases:
                print("⚠️ No test cases generated")
                continue

            issue = jira_client.create_xray_test_issue(
                project_key=settings.project_key,
                summary=title,
                testcases=testcases,
            )
            if not issue:
                raise RuntimeError("❌ Creation Jira issue failed")

            issue_key = issue["key"]
            if jira_client.last_created_issue_type == "Xray Test":
                print(f"\n📦 Xray Test Created: {issue_key}")

                payload = xray_client.build_test_steps_payload(
                    testcases=testcases,
                    xray_issue=issue_key,
                    summary_title=title,
                    project_key=settings.project_key,
                )
                token = xray_client.auth_xray_api_token(
                    client_id=settings.client_id,
                    client_secret=settings.client_secret,
                )
                job_id = xray_client.get_job_id(payload=payload, token=token)
                xray_client.check_bulk_import_status(job_id=job_id, token=token)
            else:
                print(
                    f"\n📦 Task Created: {issue_key} "
                    "(Xray Test unavailable; Xray import skipped)"
                )

            added = jira_client.add_test_to_test_set(
                test_set_key=test_set_key,
                test_key=issue_key,
            )
            if added:
                print(f"✅ Test {issue_key} added into Test Set {test_set_key}")
            else:
                print(f"⚠️ Failed adding {issue_key} into Test Set")

        except Exception as exc:
            print(str(exc))
            raise RuntimeError(f"❌ Error processing file: {original_path}") from exc

    print("\n🎉 Pipeline Completed Successfully")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate test cases from requirements.")
    parser.add_argument(
        "--pipeline",
        choices=("json", "gherkin", "playwright-bdd", "all"),
        default="json",
        help=(
            "Pipeline to run: JSON tests (default), Gherkin, Playwright-BDD steps "
            "from existing .feature files, or both new pipelines in sequence."
        ),
    )
    parser.add_argument(
        "--gherkin-dir",
        type=Path,
        help="Directory containing .feature files for --pipeline playwright-bdd.",
    )
    args = parser.parse_args()

    settings = Settings.load(require_jira=args.pipeline == "json")
    fit_client = _create_fit_client(settings)

    if args.pipeline == "json":
        _run_json_pipeline(settings, fit_client)
    else:
        _run_generated_pipelines(
            settings=settings,
            fit_client=fit_client,
            pipeline_mode=args.pipeline,
            gherkin_dir=args.gherkin_dir.resolve() if args.gherkin_dir else None,
        )


if __name__ == "__main__":
    main()