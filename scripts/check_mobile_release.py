#!/usr/bin/env python3
"""Run the PM registry-facing mobile review and release gate."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import tempfile
from pathlib import Path

if __package__:
    from .check_mobile_review import SCORE_CATEGORIES as REVIEW_SCORE_CATEGORIES
    from .check_mobile_review import project_file
    from .check_mobile_review import validate as validate_mobile_review
else:
    from check_mobile_review import SCORE_CATEGORIES as REVIEW_SCORE_CATEGORIES
    from check_mobile_review import project_file
    from check_mobile_review import validate as validate_mobile_review


SCORE_CATEGORIES = [
    "mobile_quality",
    "accessibility",
    "performance",
    "security",
    "release_readiness",
]
if SCORE_CATEGORIES != REVIEW_SCORE_CATEGORIES:
    raise RuntimeError("mobile review와 registry entrypoint의 score category가 일치하지 않습니다.")


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


def output_path_within_project(project_root: Path, requested_path: Path) -> tuple[Path | None, str | None]:
    supplied_root = Path(os.path.abspath(project_root))
    try:
        root = project_root.resolve(strict=True)
    except OSError as exc:
        return None, f"project root를 확인할 수 없습니다: {project_root}: {exc}"
    if requested_path.is_absolute():
        requested_absolute = Path(os.path.abspath(requested_path))
        try:
            candidate = root / requested_absolute.relative_to(supplied_root)
        except ValueError:
            candidate = requested_absolute
    else:
        candidate = root / requested_path
    candidate = Path(os.path.abspath(candidate))
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, f"output JSON 경로가 project root 외부입니다: {candidate}"

    current = root
    relative = candidate.relative_to(root)
    for part in relative.parts[:-1]:
        current = current / part
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            try:
                current.mkdir()
                mode = os.lstat(current).st_mode
            except OSError as exc:
                return None, f"output JSON parent를 만들 수 없습니다: {current}: {exc}"
        except OSError as exc:
            return None, f"output JSON parent를 확인할 수 없습니다: {current}: {exc}"
        if stat.S_ISLNK(mode):
            return None, f"output JSON 경로에 symlink component가 있습니다: {current}"
        if not stat.S_ISDIR(mode):
            return None, f"output JSON parent가 directory가 아닙니다: {current}"

    try:
        mode = os.lstat(candidate).st_mode
    except FileNotFoundError:
        return candidate, None
    except OSError as exc:
        return None, f"output JSON 경로를 확인할 수 없습니다: {candidate}: {exc}"
    if stat.S_ISLNK(mode):
        return None, f"output JSON symlink는 허용되지 않습니다: {candidate}"
    if not stat.S_ISREG(mode):
        return None, f"output JSON은 regular file이어야 합니다: {candidate}"
    return candidate, None


def output_input_collision_error(
    project_root: Path,
    output_path: Path,
    release_path: Path | None,
) -> str | None:
    root = project_root.resolve(strict=True)

    def normalized_input(requested: Path) -> Path:
        candidate = requested if requested.is_absolute() else root / requested
        return Path(os.path.abspath(candidate))

    protected_inputs = {
        normalized_input(Path(".harness/release-checklist.md")),
        normalized_input(Path(".harness/reports/mobile-review.md")),
        normalized_input(Path(".harness/reports/review-score.json")),
    }
    if release_path is not None:
        protected_inputs.add(normalized_input(release_path))
    if output_path in protected_inputs:
        return f"output JSON 경로가 validation input artifact와 충돌합니다: {output_path}"
    return None


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    descriptor: int | None = None
    temp_path: Path | None = None
    try:
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
        )
        temp_path = Path(temp_name)
        mode = os.fstat(descriptor).st_mode
        if not stat.S_ISREG(mode):
            raise OSError(f"temporary output이 regular file이 아닙니다: {temp_path}")
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = None
            stream.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def validate_release_checklist(project_root: Path, release_path: Path | None = None) -> list[str]:
    failures: list[str] = []
    requested_path = release_path or project_root / ".harness" / "release-checklist.md"
    path, path_error = project_file(
        project_root,
        requested_path,
        "release checklist",
        required=True,
    )
    if path_error:
        return [path_error]
    assert path is not None

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        failures.append("release-checklist.md가 비어 있습니다.")

    checked = checked_count(text)
    unchecked = unchecked_count(text)
    details = detail_line_count(text)
    if checked == 0 and unchecked >= MIN_CHECKED_ITEMS:
        failures.append("release-checklist.md가 템플릿 그대로입니다.")

    if checked >= MIN_CHECKED_ITEMS and details < MIN_DETAIL_LINES:
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

    if unchecked:
        failures.append(f"완료되지 않은 release checklist 항목이 남아 있습니다: {unchecked}개")

    if checked < MIN_CHECKED_ITEMS:
        failures.append(f"완료된 release checklist 항목이 너무 적습니다: {checked}개")

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


def validate(project_root: Path, release_path: Path | None = None) -> list[str]:
    """Validate both canonical mobile review evidence and release readiness."""
    project_root = project_root.resolve()
    review_failures = [f"mobile-review: {failure}" for failure in validate_mobile_review(project_root)]
    release_failures = [
        f"release-checklist: {failure}"
        for failure in validate_release_checklist(project_root, release_path)
    ]
    return review_failures + release_failures


def result_payload(project_root: Path, release_path: Path, failures: list[str]) -> dict[str, object]:
    return {
        "validator": "mobile-release",
        "status": "fail" if failures else "pass",
        "project_root": str(project_root),
        "artifact": str(release_path),
        "artifacts": {
            "mobile_review": ".harness/reports/mobile-review.md",
            "review_score": ".harness/reports/review-score.json",
            "release_checklist": str(release_path),
        },
        "required_artifacts": [
            ".harness/reports/mobile-review.md",
            ".harness/reports/review-score.json",
            ".harness/release-checklist.md",
        ],
        "score_categories": SCORE_CATEGORIES,
        "pm_gate": {
            "output": ".harness/release-checklist.md",
            "score_category": "release_readiness",
            "score_categories": SCORE_CATEGORIES,
            "blocks_on_failure": True,
        },
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="PM registry용 모바일 review/release 통합 검증")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="실제 프로젝트 root")
    parser.add_argument("--release-checklist", type=Path, help="검증할 release checklist 경로")
    parser.add_argument("--json", action="store_true", help="PM gate가 읽을 수 있는 JSON 결과 출력")
    parser.add_argument("--output-json", type=Path, help="JSON 결과를 파일로 저장")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    release_path = args.release_checklist
    requested_artifact = release_path or Path(".harness/release-checklist.md")
    artifact_path = Path(
        os.path.abspath(
            requested_artifact
            if requested_artifact.is_absolute()
            else project_root / requested_artifact
        )
    )
    failures = validate(project_root, release_path)

    output_path: Path | None = None
    if args.output_json:
        output_path, output_error = output_path_within_project(args.project_root, args.output_json)
        if output_error:
            failures.append(output_error)
        elif output_path is not None:
            collision_error = output_input_collision_error(project_root, output_path, release_path)
            if collision_error:
                failures.append(collision_error)
                output_path = None

    payload = result_payload(project_root, artifact_path, failures)

    if output_path is not None:
        try:
            atomic_write_json(output_path, payload)
        except OSError as exc:
            failures.append(f"output JSON atomic write 실패: {exc}")
            payload = result_payload(project_root, artifact_path, failures)

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
