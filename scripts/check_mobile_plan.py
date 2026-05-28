#!/usr/bin/env python3
"""Validate project-local mobile plan quality."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_SECTIONS = [
    "앱 목표",
    "대상 플랫폼",
    "선택한 runtime/tooling",
    "선택한 architecture",
    "navigation 전략",
    "state management 전략",
    "API 연동 전략",
    "storage 전략",
    "권한 요청 계획",
    "offline behavior",
    "테스트 전략",
    "배포 전략",
    "주요 리스크",
]
PLACEHOLDER_WORDS = {
    "todo",
    "tbd",
    "placeholder",
    "template",
    "작성 필요",
    "추후 작성",
    "미정",
    "없음",
    "n/a",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def section_names(text: str) -> set[str]:
    names: set[str] = set()
    for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE):
        names.add(match.group(1).strip())
    return names


def meaningful_text(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        if re.fullmatch(r"[-*: `{}.,/\\\[\]]+", stripped):
            continue
        lines.append(stripped)
    return "\n".join(lines)


def empty_item_count(text: str) -> int:
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^-\s*[^:\n]+:\s*$", stripped):
            count += 1
        elif re.match(r"^[A-Za-z_][\w-]*:\s*$", stripped):
            count += 1
    return count


def placeholder_count(text: str) -> int:
    return sum(len(re.findall(re.escape(word), text, re.IGNORECASE)) for word in PLACEHOLDER_WORDS)


def load_template() -> str:
    harness_root = Path(__file__).resolve().parents[1]
    return (harness_root / "templates" / "mobile-plan.md").read_text(encoding="utf-8")


def validate(project_root: Path) -> list[str]:
    failures: list[str] = []
    path = project_root / ".harness" / "mobile-plan.md"
    if not path.exists():
        return [f"필수 파일이 없습니다: {path}"]

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        failures.append("mobile-plan.md가 비어 있습니다.")

    if normalize(text) == normalize(load_template()):
        failures.append("mobile-plan.md가 템플릿 그대로입니다.")

    names = section_names(text)
    for section in REQUIRED_SECTIONS:
        if section not in names:
            failures.append(f"필수 섹션이 없습니다: {section}")

    empty_items = empty_item_count(text)
    if empty_items >= 6:
        failures.append(f"빈 항목이 너무 많습니다: {empty_items}개")

    placeholders = placeholder_count(text)
    if placeholders >= 3:
        failures.append(f"placeholder 표현이 너무 많습니다: {placeholders}개")

    useful = meaningful_text(text)
    words = re.findall(r"[A-Za-z0-9가-힣_/-]+", useful)
    if len(words) < 120:
        failures.append(f"실제 내용이 너무 적습니다: 의미 있는 단어 {len(words)}개")

    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="모바일 계획 산출물 검증")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="실제 프로젝트 root")
    args = parser.parse_args()

    failures = validate(args.project_root.resolve())
    if failures:
        print("mobile-plan 검증 실패")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("mobile-plan 검증 통과")


if __name__ == "__main__":
    main()
