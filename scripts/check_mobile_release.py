#!/usr/bin/env python3
"""Validate project-local mobile release checklist quality."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_SECTIONS = [
    "build",
    "signing",
    "crash reporting",
    "OTA update policy",
    "release evidence",
    "store readiness",
]
REQUIRED_CONCEPT_GROUPS = {
    "EAS/native build": ["eas build", "xcode", "gradle", "release build"],
    "EAS/store submit": ["eas submit", "app store connect", "play console", "store"],
    "version/build number": ["app version", "build number", "versioncode", "release tag"],
    "environment config": ["environment config", "dev/staging/prod", "production build"],
    "signing": ["ios certificate", "provisioning", "android keystore", "signing credential"],
    "crash reporting": ["crash reporting", "source map", "symbol upload"],
    "OTA rollback policy": ["ota", "eas update", "runtimeversion", "rollback"],
    "device matrix evidence": [
        "ios simulator",
        "android emulator",
        "real device",
        "생략 사유",
        "small screen",
        "large screen",
        "dark mode",
        "offline mode",
    ],
    "permission evidence": ["permission", "permission prompt", "denied", "granted", "limited"],
    "offline/deep link evidence": ["offline", "poor network", "retry", "conflict", "deep link", "cold start", "warm start"],
    "accessibility evidence": [
        "screen reader label",
        "dynamic type",
        "font scaling",
        "reduced motion",
        "reduce motion",
        "touch target size",
        "contrast",
        "keyboard avoidance",
        "safe area",
    ],
    "release risk evidence": [
        "permission prompt",
        "push notification",
        "deep link",
        "app icon",
        "splash",
        "crash reporting",
        "store metadata",
    ],
}
REQUIRED_CHECKBOX_PATTERNS = {
    "iOS simulator evidence": r"-\s*\[[xX]\]\s+.*ios simulator",
    "Android emulator evidence": r"-\s*\[[xX]\]\s+.*android emulator",
    "real device evidence or exception": r"-\s*\[[xX]\]\s+.*(real device|생략 사유)",
    "small screen evidence": r"-\s*\[[xX]\]\s+.*small screen",
    "large screen evidence": r"-\s*\[[xX]\]\s+.*large screen",
    "dark mode evidence": r"-\s*\[[xX]\]\s+.*dark mode",
    "offline mode evidence": r"-\s*\[[xX]\]\s+.*offline mode",
    "permission prompt evidence": r"-\s*\[[xX]\]\s+.*permission prompt",
    "push notification evidence": r"-\s*\[[xX]\]\s+.*push notification",
    "app icon/splash evidence": r"-\s*\[[xX]\]\s+.*(app icon|splash)",
    "store metadata evidence": r"-\s*\[[xX]\]\s+.*store metadata",
    "screen reader label evidence": r"-\s*\[[xX]\]\s+.*screen reader label",
    "touch target size evidence": r"-\s*\[[xX]\]\s+.*touch target size",
    "contrast evidence": r"-\s*\[[xX]\]\s+.*contrast",
    "keyboard avoidance evidence": r"-\s*\[[xX]\]\s+.*keyboard avoidance",
    "reduced motion evidence": r"-\s*\[[xX]\]\s+.*reduced motion",
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
}
MIN_CHECKED_ITEMS = 24
MIN_DETAIL_LINES = 8
MIN_USEFUL_WORDS = 180


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def section_names(text: str) -> set[str]:
    names: set[str] = set()
    for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE):
        names.add(match.group(1).strip())
    return names


def extract_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def load_template() -> str:
    harness_root = Path(__file__).resolve().parents[1]
    return (harness_root / "templates" / "release-checklist.md").read_text(encoding="utf-8")


def placeholder_count(text: str) -> int:
    return sum(len(re.findall(re.escape(word), text, re.IGNORECASE)) for word in PLACEHOLDER_WORDS)


def checked_count(text: str) -> int:
    return len(re.findall(r"^\s*-\s*\[[xX]\]\s+", text, re.MULTILINE))


def unchecked_count(text: str) -> int:
    return len(re.findall(r"^\s*-\s*\[\s\]\s+", text, re.MULTILINE))


def detail_line_count(text: str) -> int:
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if re.match(r"^-\s*\[[ xX]\]\s+", stripped):
            continue
        if stripped.startswith("|") or stripped.startswith("```"):
            continue
        if len(re.findall(r"[A-Za-z0-9가-힣_/-]+", stripped)) >= 6:
            count += 1
    return count


def has_terms(text: str, terms: list[str], minimum: int) -> bool:
    lowered = text.lower()
    hits = sum(1 for term in terms if term.lower() in lowered)
    return hits >= minimum


def checkbox_labels(text: str) -> list[str]:
    labels: list[str] = []
    for match in re.finditer(r"^\s*-\s*\[[ xX]\]\s+(.+?)\s*$", text, re.MULTILINE):
        labels.append(normalize(match.group(1)))
    return labels


def validate(project_root: Path, release_path: Path | None = None) -> list[str]:
    failures: list[str] = []
    path = release_path or project_root / ".harness" / "release-checklist.md"
    if not path.exists():
        return [f"필수 파일이 없습니다: {path}"]

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        failures.append("release-checklist.md가 비어 있습니다.")

    if normalize(text) == normalize(load_template()):
        failures.append("release-checklist.md가 템플릿 그대로입니다.")

    if checkbox_labels(text) == checkbox_labels(load_template()) and detail_line_count(text) < MIN_DETAIL_LINES:
        failures.append("release-checklist.md가 템플릿 체크 항목만 채운 상태이며 실제 evidence detail이 부족합니다.")

    names = section_names(text)
    for section in REQUIRED_SECTIONS:
        if section not in names:
            failures.append(f"필수 섹션이 없습니다: {section}")

    for label, terms in REQUIRED_CONCEPT_GROUPS.items():
        minimum = 2 if len(terms) <= 4 else 4
        if not has_terms(text, terms, minimum):
            failures.append(f"필수 release checklist 근거가 부족합니다: {label}")

    for label, pattern in REQUIRED_CHECKBOX_PATTERNS.items():
        if not re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            failures.append(f"필수 완료 체크 항목이 없습니다: {label}")

    unchecked = unchecked_count(text)
    if unchecked:
        failures.append(f"완료되지 않은 release checklist 항목이 남아 있습니다: {unchecked}개")

    checked = checked_count(text)
    if checked < MIN_CHECKED_ITEMS:
        failures.append(f"완료된 release checklist 항목이 너무 적습니다: {checked}개")

    details = detail_line_count(text)
    if details < MIN_DETAIL_LINES:
        failures.append(f"release evidence 상세 설명이 부족합니다: {details}개 detail line")

    release_evidence = extract_section(text, "release evidence")
    if release_evidence:
        for label in ["ios simulator", "android emulator", "small screen", "large screen", "dark mode", "offline mode"]:
            if label not in release_evidence.lower():
                failures.append(f"release evidence 섹션에 필수 기기/상태 근거가 없습니다: {label}")

    placeholders = placeholder_count(text)
    if placeholders >= 3:
        failures.append(f"placeholder 표현이 너무 많습니다: {placeholders}개")

    useful_words = re.findall(r"[A-Za-z0-9가-힣_/-]+", text)
    if len(useful_words) < MIN_USEFUL_WORDS:
        failures.append(f"release checklist 내용이 너무 적습니다: 의미 있는 단어 {len(useful_words)}개")

    return failures


def result_payload(project_root: Path, release_path: Path, failures: list[str]) -> dict[str, object]:
    return {
        "validator": "mobile-release",
        "status": "fail" if failures else "pass",
        "project_root": str(project_root),
        "artifact": str(release_path),
        "required_artifacts": [".harness/release-checklist.md"],
        "pm_gate": {
            "output": ".harness/release-checklist.md",
            "score_category": "release_readiness",
            "blocks_on_failure": True,
        },
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="모바일 release checklist 검증")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="실제 프로젝트 root")
    parser.add_argument("--release-checklist", type=Path, help="검증할 release checklist 경로")
    parser.add_argument("--json", action="store_true", help="PM gate가 읽을 수 있는 JSON 결과 출력")
    parser.add_argument("--output-json", type=Path, help="JSON 결과를 파일로 저장")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    release_path = args.release_checklist.resolve() if args.release_checklist else None
    artifact_path = release_path or project_root / ".harness" / "release-checklist.md"
    failures = validate(project_root, release_path)
    payload = result_payload(project_root, artifact_path, failures)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if failures:
            raise SystemExit(1)
        return

    if failures:
        print("mobile-release 검증 실패")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("mobile-release 검증 통과")


if __name__ == "__main__":
    main()
