import csv
from pathlib import Path

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from relaytic.interoperability import (
    find_available_port,
    run_live_streamable_http_smoke_check,
    start_streamable_http_server_process,
)
from tests.public_datasets import write_public_breast_cancer_dataset


def test_streamable_http_mcp_smoke_is_ok() -> None:
    report = run_live_streamable_http_smoke_check()
    assert report["status"] == "ok"
    assert report["server_status"] == "ok"
    assert report["tool_count"] >= 10


def test_streamable_http_mcp_can_run_relaytic_end_to_end_on_public_dataset(tmp_path: Path) -> None:
    data_path = _write_small_public_breast_cancer_dataset(tmp_path / "breast_cancer_small.csv")
    run_dir = tmp_path / "mcp_run"
    port = find_available_port()
    process = start_streamable_http_server_process(port=port)
    url = f"http://127.0.0.1:{port}/mcp"

    async def _flow() -> None:
        last_error: str | None = None
        for _ in range(30):
            try:
                async with streamable_http_client(url) as (read_stream, write_stream, _get_session_id):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tool_result = await session.call_tool(
                            "relaytic_run",
                            {
                                "run_dir": str(run_dir),
                                "data_path": str(data_path),
                                "text": "Do everything on your own. Predict diagnosis_flag from the provided features.",
                                "actor_type": "agent",
                                "channel": "mcp-test",
                                "overwrite": True,
                            },
                        )
                        run_payload = _structured_payload(tool_result)
                        assert run_payload["surface_payload"]["status"] == "ok"
                        assert run_payload["surface_payload"]["run_summary"]["decision"]["task_type"] in {
                            "classification",
                            "binary_classification",
                            "fraud_detection",
                        }

                        status_result = await session.call_tool("relaytic_get_status", {"run_dir": str(run_dir)})
                        status_payload = _structured_payload(status_result)
                        assert status_payload["surface_payload"]["status"] == "ok"
                        assert status_payload["surface_payload"]["completion"]["action"] is not None

                        predict_result = await session.call_tool(
                            "relaytic_predict",
                            {
                                "run_dir": str(run_dir),
                                "data_path": str(data_path),
                            },
                        )
                        predict_payload = _structured_payload(predict_result)
                        assert predict_payload["status"] == "ok"
                        assert predict_payload["prediction_count"] > 0
                        return
            except Exception as exc:  # pragma: no cover - retried below
                last_error = str(exc)
                await anyio.sleep(0.25)
        raise AssertionError(f"Failed to complete streamable HTTP Relaytic flow: {last_error}")

    try:
        anyio.run(_flow)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except Exception:
                process.kill()
                process.wait(timeout=5)


def _structured_payload(result: object) -> dict:
    structured = getattr(result, "structuredContent", None) or getattr(result, "structured_content", None)
    assert isinstance(structured, dict)
    return structured


def _write_small_public_breast_cancer_dataset(path: Path, *, row_limit: int = 80) -> Path:
    full_path = write_public_breast_cancer_dataset(path.with_name(path.stem + "_full.csv"))
    with full_path.open("r", encoding="utf-8", newline="") as source, path.open(
        "w", encoding="utf-8", newline=""
    ) as destination:
        reader = csv.reader(source)
        writer = csv.writer(destination)
        for index, row in enumerate(reader):
            if index == 0 or index <= row_limit:
                writer.writerow(row)
            else:
                break
    return path
