"""
Sprint Benchmark — Action Points Assistant
Читає датасети з input_dataset/{small,middle,Large}_dataset/
Зберігає результати у output_results/output_data/ та timetraker_results/
Генерує звіт total_time_analytics.md
"""

import os
import json
import time
import pathlib
import argparse
import statistics
from datetime import datetime, timezone

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash-lite"
SYSTEM_PROMPT_FILE = "system_prompt.md"

SEGMENTS = {
    "small":  "small_dataset",
    "middle": "middle_dataset",
    "large":  "Large_dataset",
}

RESULTS_FILES = {
    "small":  "small_dataset_results.json",
    "middle": "middle_dataset_results.json",
    "large":  "Large_dataset_results.json",
}


def process_file(
    md_path: pathlib.Path,
    output_dir: pathlib.Path,
    generate_config: types.GenerateContentConfig,
    client: genai.Client,
) -> dict:
    content = md_path.read_text(encoding="utf-8")
    line_count = len([l for l in content.splitlines() if l.strip()])

    ttft = None
    input_tokens = None
    output_tokens = None
    text_chunks = []

    t_start = time.perf_counter()

    try:
        stream = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=content,
            config=generate_config,
        )

        for chunk in stream:
            if ttft is None:
                ttft = time.perf_counter() - t_start
            if chunk.text:
                text_chunks.append(chunk.text)
            if chunk.usage_metadata:
                input_tokens = chunk.usage_metadata.prompt_token_count
                output_tokens = chunk.usage_metadata.candidates_token_count

        total_time = time.perf_counter() - t_start
        output_text = "".join(text_chunks)

        out_file = output_dir / f"output_{md_path.stem}.md"
        out_file.write_text(output_text, encoding="utf-8")

        return {
            "file": md_path.name,
            "status": "ok",
            "ttft_s": round(ttft, 4) if ttft is not None else None,
            "total_time_s": round(total_time, 4),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "line_count": line_count,
            "output_file": out_file.as_posix(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        total_time = time.perf_counter() - t_start
        return {
            "file": md_path.name,
            "status": "error",
            "error": str(e),
            "total_time_s": round(total_time, 4),
            "line_count": line_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def segment_stats(results: list[dict]) -> dict:
    ok = [r for r in results if r["status"] == "ok"]
    if not ok:
        return {}

    total_times = sorted(r["total_time_s"] for r in ok)
    ttfts = [r["ttft_s"] for r in ok if r.get("ttft_s") is not None]
    line_counts = [r["line_count"] for r in ok]
    n = len(total_times)

    return {
        "total": len(results),
        "ok": len(ok),
        "errors": len(results) - len(ok),
        "avg_lines": round(statistics.mean(line_counts), 1) if line_counts else 0,
        "total_time_median": round(statistics.median(total_times), 3),
        "total_time_p75": round(total_times[int(n * 0.75)], 3),
        "total_time_p90": round(total_times[int(n * 0.90)], 3),
        "total_time_p95": round(total_times[int(n * 0.95)], 3),
        "ttft_median": round(statistics.median(ttfts), 3) if ttfts else None,
    }


def generate_report(
    all_stats: dict[str, dict],
    all_results: dict[str, list],
    model: str,
    output_path: pathlib.Path,
) -> None:
    date_str = datetime.now().strftime("%Y-%m-%d")

    total_cases = sum(s.get("total", 0) for s in all_stats.values())
    total_ok = sum(s.get("ok", 0) for s in all_stats.values())

    all_ok_results = [r for rs in all_results.values() for r in rs if r["status"] == "ok"]
    all_times = sorted(r["total_time_s"] for r in all_ok_results)
    n = len(all_times)
    all_ttfts = [r["ttft_s"] for r in all_ok_results if r.get("ttft_s")]

    lines = [
        f"# Sprint Benchmark Summary — {model}",
        "",
        f"**Date:** {date_str}  ",
        f"**Model:** {model}  ",
        f"**Total cases:** {total_ok} / {total_cases} successful  ",
        "",
        "---",
        "",
        "## Overall Latency",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]

    if all_times:
        lines += [
            f"| TTFT median | {statistics.median(all_ttfts):.3f}s |" if all_ttfts else "| TTFT median | — |",
            f"| total_time median | {statistics.median(all_times):.3f}s |",
            f"| total_time p75 | {all_times[int(n * 0.75)]:.3f}s |",
            f"| total_time p90 | {all_times[int(n * 0.90)]:.3f}s |",
            f"| total_time p95 | {all_times[int(n * 0.95)]:.3f}s |",
        ]

    lines += ["", "---", "", "## Segmentation Results", ""]

    segment_labels = {"small": "Small", "middle": "Middle", "large": "Large"}

    for seg_key, label in segment_labels.items():
        s = all_stats.get(seg_key)
        if not s:
            lines.append(f"### {label} — no data\n")
            continue

        lines += [
            f"### {label} (`{SEGMENTS[seg_key]}/`)",
            "",
            f"- **Cases:** {s['ok']} / {s['total']} successful",
            f"- **Avg lines per case:** {s['avg_lines']}",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| TTFT median | {s['ttft_median']}s |" if s.get("ttft_median") else "| TTFT median | — |",
            f"| total_time median | {s['total_time_median']}s |",
            f"| total_time p75 | {s['total_time_p75']}s |",
            f"| total_time p90 | {s['total_time_p90']}s |",
            f"| total_time p95 | {s['total_time_p95']}s |",
            "",
        ]

    if any(s.get("errors", 0) > 0 for s in all_stats.values()):
        lines += ["---", "", "## Errors", ""]
        for seg_key, rs in all_results.items():
            errors = [r for r in rs if r["status"] == "error"]
            for e in errors:
                lines.append(f"- `{seg_key}/{e['file']}` — {e.get('error', 'unknown')}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Sprint benchmark for Action Points Assistant")
    parser.add_argument("--input-dir", default="input_dataset", help="Директорія з датасетами")
    parser.add_argument("--output-dir", default="output_results/output_data", help="Директорія для виводу моделі")
    parser.add_argument("--tracker-dir", default="timetraker_results", help="Директорія для JSON результатів")
    parser.add_argument("--report", default="total_time_analytics.md", help="Файл звіту")
    parser.add_argument("--prompt", default=SYSTEM_PROMPT_FILE, help="Файл системної інструкції")
    parser.add_argument("--delay", type=float, default=0.5, help="Затримка між запитами (секунди)")
    parser.add_argument("--skip-existing", action="store_true", help="Пропускати вже оброблені файли")
    args = parser.parse_args()

    if not API_KEY:
        print("[!] GEMINI_API_KEY не задано. Встановіть змінну середовища або вкажіть ключ у коді.")
        return

    prompt_file = pathlib.Path(args.prompt)
    if not prompt_file.exists():
        print(f"[!] Файл промпту не знайдено: {prompt_file}")
        return
    system_prompt = prompt_file.read_text(encoding="utf-8")

    client = genai.Client(api_key=API_KEY)
    generate_config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.1,
        top_p=0.5,
        top_k=5,
        max_output_tokens=8000,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    input_dir = pathlib.Path(args.input_dir)
    output_dir = pathlib.Path(args.output_dir)
    tracker_dir = pathlib.Path(args.tracker_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results: dict[str, list] = {}
    all_stats: dict[str, dict] = {}

    for seg_key, folder_name in SEGMENTS.items():
        seg_dir = input_dir / folder_name
        if not seg_dir.exists():
            print(f"[~] Пропуск: {seg_dir} не існує")
            continue

        md_files = sorted(seg_dir.glob("*.md"))
        if not md_files:
            print(f"[~] Пропуск: немає .md файлів у {seg_dir}")
            continue

        print(f"\n[{seg_key.upper()}] {len(md_files)} файлів у {seg_dir}")
        t_seg_start = time.perf_counter()
        results = []

        for i, md_path in enumerate(md_files, 1):
            out_file = output_dir / f"output_{md_path.stem}.md"
            if args.skip_existing and out_file.exists():
                print(f"  [{i:>3}/{len(md_files)}] {md_path.name} — пропущено (вже існує)")
                continue

            elapsed = time.perf_counter() - t_seg_start
            remaining = len(md_files) - i
            eta = (elapsed / i * remaining) if i > 0 else 0

            print(
                f"  [{i:>3}/{len(md_files)}] {md_path.name} ...",
                end=" ", flush=True,
            )

            result = process_file(md_path, output_dir, generate_config, client)
            results.append(result)

            if result["status"] == "ok":
                print(
                    f"TTFT={result['ttft_s']}s  total={result['total_time_s']}s  "
                    f"tokens={result['output_tokens']}  ETA≈{eta:.0f}s"
                )
            else:
                print(f"ERROR: {result['error']}")

            if i < len(md_files) and args.delay > 0:
                time.sleep(args.delay)

        # Зберегти JSON для цього сегмента
        json_path = tracker_dir / RESULTS_FILES[seg_key]
        json_path.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  → Збережено: {json_path}")

        all_results[seg_key] = results
        all_stats[seg_key] = segment_stats(results)

    if not all_results:
        print("\n[!] Не знайдено жодного файлу для обробки.")
        return

    # Генерувати звіт
    report_path = pathlib.Path(args.report)
    generate_report(all_stats, all_results, MODEL_NAME, report_path)
    print(f"\n[✓] Звіт збережено → {report_path.resolve()}")


if __name__ == "__main__":
    main()
