#!/usr/bin/env python3
"""Validate project-local mobile review report quality."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SCORE_CATEGORIES = [
    "mobile_quality",
    "accessibility",
    "performance",
    "security",
    "release_readiness",
]
NO_ISSUE_MARKERS = {
    "없음",
    "none",
    "no critical",
    "no unresolved",
    "해당 없음",
}
PLACEHOLDER_WORDS = {
    "todo",
    "tbd",
    "placeholder",
    "template",
    "템플릿",
    "작성 필요",
    "추후 작성",
    "미정",
    "개선 권고",
    "다음 액션",
}
MIN_SCORE = 8.0
MAX_PLACEHOLDERS = 3


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def load_template() -> str:
    harness_root = Path(__file__).resolve().parents[1]
    return (harness_root / "templates" / "mobile-review.md").read_text(encoding="utf-8")


def extract_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def score_map(text: str) -> dict[str, float]:
    scores: dict[str, float] = {}
    for category in SCORE_CATEGORIES:
        patterns = [
            rf"\b{re.escape(category)}\s*:\s*(-?\d+(?:\.\d+)?)\s*/\s*10\b",
            rf"\|\s*{re.escape(category)}\s*\|\s*(-?\d+(?:\.\d+)?)\s*(?:/\s*10)?\s*\|",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                scores[category] = float(match.group(1))
                break
    return scores


def unresolved_critical_issue(section: str) -> bool:
    lowered = section.lower()
    has_none_marker = any(marker in lowered for marker in NO_ISSUE_MARKERS)
    meaningful_lines: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("| ---"):
            continue
        if any(marker in stripped.lower() for marker in NO_ISSUE_MARKERS):
            continue
        if re.fullmatch(r"[-| :`{}.,/\\\[\]]+", stripped):
            continue
        if "|  |" in stripped or re.search(r"\|\s*\|\s*\|", stripped):
            continue
        meaningful_lines.append(stripped)
    if meaningful_lines:
        return True
    return not has_none_marker


def has_verification_result(section: str) -> bool:
    if not section:
        return False
    meaningful = 0
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if any(word in stripped.lower() for word in PLACEHOLDER_WORDS):
            continue
        match = re.match(r"^-\s*(build|test|mobile verification)\s*:\s*(.+)$", stripped, re.IGNORECASE)
        if match and match.group(2).strip():
            meaningful += 1
    return meaningful >= 2


def placeholder_count(text: str) -> int:
    return sum(len(re.findall(re.escape(word), text, re.IGNORECASE)) for word in PLACEHOLDER_WORDS)


def validate(project_root: Path) -> list[str]:
    failures: list[str] = []
    path = project_root / ".harness" / "reports" / "mobile-review.md"
    if not path.exists():
        return [f"필수 파일이 없습니다: {path}"]

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        failures.append("mobile-review.md가 비어 있습니다.")

    if normalize(text) == normalize(load_template()):
        failures.append("mobile-review.md가 템플릿 그대로입니다.")

    scores = score_map(text)
    for category in SCORE_CATEGORIES:
        if category not in scores:
            failures.append(f"필수 score category가 없습니다: {category}")
        elif scores[category] == 0:
            failures.append(f"{category} 점수가 0/10 그대로입니다.")
        elif scores[category] < 0 or scores[category] > 10:
            failures.append(f"{category} 점수 범위가 올바르지 않습니다: {scores[category]}")
        elif scores[category] < MIN_SCORE:
            failures.append(f"{category} 점수가 기준 미만입니다: {scores[category]} < 8")

    critical_section = extract_section(text, "Critical Issues")
    if not critical_section:
        failures.append("Critical Issues 섹션이 없거나 비어 있습니다.")
    elif unresolved_critical_issue(critical_section):
        failures.append("Critical Issues 섹션에 unresolved issue가 남아 있습니다.")

    verification = extract_section(text, "검증 결과")
    if not has_verification_result(verification):
        failures.append("검증 결과 섹션의 build/test 또는 mobile verification 결과가 비어 있습니다.")

    placeholders = placeholder_count(text)
    if placeholders >= MAX_PLACEHOLDERS:
        failures.append(f"placeholder 표현이 너무 많습니다: {placeholders}개")

    useful_words = re.findall(r"[A-Za-z0-9가-힣_/-]+", text)
    if len(useful_words) < 100:
        failures.append(f"실제 리뷰 내용이 너무 적습니다: 의미 있는 단어 {len(useful_words)}개")

    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="모바일 리뷰 산출물 검증")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="실제 프로젝트 root")
    args = parser.parse_args()

    failures = validate(args.project_root.resolve())
    if failures:
        print("mobile-review 검증 실패")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("mobile-review 검증 통과")


if __name__ == "__main__":
    main()
