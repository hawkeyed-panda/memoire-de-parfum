import json
import asyncio
from pathlib import Path
from app.pipeline.fragrance_pipeline import run_fragrance_pipeline
from app.evaluation.rubric import evaluate, RubricScore
from app.models.intent import MemoryFrame


TEST_CASES_DIR = Path(__file__).parent / "test_cases"
PASS_THRESHOLD = 0.7


async def run_single_case(case: dict) -> dict:
    """Run a single test case through the pipeline and evaluate it."""
    try:
        result = await run_fragrance_pipeline(
            memory_frame=MemoryFrame(case["memory_frame"]),
            questionnaire_data=case["questionnaire_data"],
            free_text_memory=case.get("free_text_memory", ""),
        )

        score = evaluate(
            intent=result["intent"],
            blueprint=result["blueprint"],
            fragrance_story=result["fragrance_story"],
        )

        return {
            "case_id": case["id"],
            "memory_frame": case["memory_frame"],
            "passed": score.passed(PASS_THRESHOLD),
            "scores": {
                "relevance": score.relevance,
                "coherence": score.coherence,
                "safety": score.safety,
                "consistency": score.consistency,
                "experiential": score.experiential,
                "overall": score.overall,
            },
            "error": None,
        }

    except Exception as e:
        return {
            "case_id": case["id"],
            "memory_frame": case["memory_frame"],
            "passed": False,
            "scores": None,
            "error": str(e),
        }


async def run_eval(frame: str = None) -> dict:
    """
    Run evaluation on test cases.
    Args:
        frame: Optional — "past", "present", or "future".
               If None, runs all frames.
    """
    files = {
        "past": TEST_CASES_DIR / "past_cases.json",
        "present": TEST_CASES_DIR / "present_cases.json",
        "future": TEST_CASES_DIR / "future_cases.json",
    }

    if frame:
        files = {frame: files[frame]}

    all_results = []

    for frame_name, filepath in files.items():
        if not filepath.exists():
            print(f"[Eval] No test cases found for {frame_name} — skipping")
            continue

        with open(filepath) as f:
            cases = json.load(f)

        print(f"[Eval] Running {len(cases)} {frame_name} cases...")

        for case in cases:
            result = await run_single_case(case)
            all_results.append(result)
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"  {status} → case {result['case_id']} | overall: {result['scores']['overall'] if result['scores'] else 'ERROR'}")

    # Summary
    total = len(all_results)
    passed = sum(1 for r in all_results if r["passed"])
    failed = total - passed

    summary = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total, 2) if total > 0 else 0,
        "results": all_results,
    }

    print(f"\n[Eval] Summary: {passed}/{total} passed ({summary['pass_rate']*100:.0f}%)")
    return summary


if __name__ == "__main__":
    asyncio.run(run_eval())
