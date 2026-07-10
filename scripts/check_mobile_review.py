#!/usr/bin/env python3
"""Validate project-local mobile review report quality."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import stat
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
NO_ISSUE_CONFLICT_PATTERNS = [
    re.compile(r"\bunresolved\b", re.IGNORECASE),
    re.compile(r"\bpending\b", re.IGNORECASE),
    re.compile(r"\bblocked\b", re.IGNORECASE),
    re.compile(r"\bcritical\b", re.IGNORECASE),
    re.compile(r"\bhigh\b", re.IGNORECASE),
    re.compile(r"미해결"),
    re.compile(r"차단"),
    re.compile(
        r"\brelease\s+blocker\s*[:=]?\s*(?:yes|true|blocked|block)\b",
        re.IGNORECASE,
    ),
]
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
REQUIRED_EVIDENCE_GROUPS = {
    "device matrix": [
        "device matrix",
        "ios simulator",
        "android emulator",
        "real device",
        "생략 사유",
        "small screen",
        "large screen",
        "dark mode",
        "offline mode",
    ],
    "permission evidence": ["permission", "permission prompt", "push notification", "denied", "granted", "limited"],
    "offline evidence": ["offline", "poor network", "retry", "conflict"],
    "deep link evidence": ["deep link", "cold start", "warm start"],
    "accessibility evidence": [
        "screen reader label",
        "touch target size",
        "dynamic type",
        "font scaling",
        "reduced motion",
        "contrast",
        "keyboard avoidance",
        "safe area",
    ],
    "release evidence": [
        "eas build",
        "eas submit",
        "signing",
        "app version",
        "build number",
        "crash reporting",
        "ota update",
        "rollback",
        "release checklist",
    ],
    "release risk evidence": ["permission prompt", "push notification", "app icon", "splash", "store metadata"],
}
ISSUE_SECTION_HEADINGS = ["High Issues", "Release Blockers"]
STRUCTURED_PLACEHOLDER_SECTIONS = [
    "device matrix",
    "permission/offline/deep link evidence",
    "accessibility evidence",
    "release evidence",
    "recommendations",
    "next actions",
    "검증 결과",
]


def is_template_like(text: str) -> bool:
    """Detect the bundled blank review without reading outside the project root."""
    scores = score_map(text)
    required_headings = [
        "Critical Issues",
        "device matrix",
        "permission/offline/deep link evidence",
        "검증 결과",
    ]
    return (
        all(scores.get(category) == 0 for category in SCORE_CATEGORIES)
        and all(extract_section(text, heading) for heading in required_headings)
        and not has_verification_result(extract_section(text, "검증 결과"))
    )


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


def has_verification_result(section: str) -> bool:
    if not section:
        return False
    meaningful = 0
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(r"^-\s*(build|test|mobile verification)\s*:\s*(.+)$", stripped, re.IGNORECASE)
        if match and match.group(2).strip() and not is_placeholder_value(match.group(2)):
            meaningful += 1
    return meaningful >= 2


def is_placeholder_value(value: str) -> bool:
    normalized = value.strip().strip("`*_[](){}.,; ").casefold()
    for marker in PLACEHOLDER_WORDS:
        folded = marker.casefold()
        if normalized == folded or re.match(rf"^{re.escape(folded)}\s*[:：-]", normalized):
            return True
    return False


def structured_placeholder_count(text: str) -> int:
    count = 0
    for heading in STRUCTURED_PLACEHOLDER_SECTIONS:
        section = extract_section(text, heading)
        for line in section.splitlines():
            stripped = line.strip()
            label = re.match(r"^[-*]\s+[^:：|]+[:：]\s*(.*)$", stripped)
            if label and is_placeholder_value(label.group(1)):
                count += 1
                continue
            if stripped.startswith("|") and stripped.endswith("|"):
                cells = [cell.strip() for cell in stripped.strip("|").split("|")]
                count += sum(1 for cell in cells[1:] if is_placeholder_value(cell))
    return count


def has_terms(text: str, terms: list[str], minimum: int) -> bool:
    lowered = text.lower()
    hits = sum(1 for term in terms if term.lower() in lowered)
    return hits >= minimum


def project_file(
    project_root: Path,
    relative_path: str | Path,
    label: str,
    *,
    required: bool,
) -> tuple[Path | None, str | None]:
    try:
        root = project_root.resolve(strict=True)
    except OSError as exc:
        return None, f"project root를 확인할 수 없습니다: {project_root}: {exc}"
    candidate = Path(os.path.abspath(root / relative_path))
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, f"{label} 경로가 project root 외부를 가리킵니다: {candidate}"

    current = root
    relative = candidate.relative_to(root)
    for part in relative.parts:
        current = current / part
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            if required or current != candidate:
                return None, f"필수 파일이 없습니다: {candidate}"
            return None, None
        except OSError as exc:
            return None, f"{label} 경로를 확인할 수 없습니다: {current}: {exc}"
        if stat.S_ISLNK(mode):
            return None, f"{label} 경로에 symlink가 포함되어 있습니다: {current}"

    try:
        mode = os.lstat(candidate).st_mode
    except FileNotFoundError:
        return (None, f"필수 파일이 없습니다: {candidate}") if required else (None, None)
    except OSError as exc:
        return None, f"{label} 파일을 확인할 수 없습니다: {candidate}: {exc}"
    if not stat.S_ISREG(mode):
        return None, f"{label}는 project 내부 regular file이어야 합니다: {candidate}"
    if os.lstat(candidate).st_nlink != 1:
        return None, f"{label} hardlink는 허용되지 않습니다: {candidate}"
    return candidate, None


def _table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _table_separator(line: str) -> bool:
    cells = _table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _standalone_marker(line: str) -> bool:
    stripped = re.sub(r"^\s*[-*+]\s+", "", line.strip())
    stripped = re.sub(r"^\[[ xX]\]\s+", "", stripped).strip()
    cells = _table_cells(stripped)
    value = cells[0] if cells else stripped
    if value.strip().casefold() not in NO_ISSUE_MARKERS:
        return False
    if cells:
        remainder = " | ".join(cells[1:])
        if any(pattern.search(remainder) for pattern in NO_ISSUE_CONFLICT_PATTERNS):
            return False
    return True


def unresolved_issue(section: str) -> bool:
    raw_lines = [line for line in section.splitlines() if line.strip()]
    marker_found = False
    meaningful: list[str] = []
    for index, line in enumerate(raw_lines):
        stripped = line.strip()
        if _table_separator(stripped):
            continue
        if _table_cells(stripped) is not None and index + 1 < len(raw_lines) and _table_separator(raw_lines[index + 1]):
            continue
        if _standalone_marker(stripped):
            marker_found = True
            continue
        if re.fullmatch(r"[-| :`{}.,/\\\[\]()]+", stripped):
            continue
        meaningful.append(stripped)
    return bool(meaningful) or not marker_found


def validate_review_score_json(project_root: Path) -> list[str]:
    path, path_error = project_file(
        project_root,
        ".harness/reports/review-score.json",
        "review-score.json",
        required=True,
    )
    if path_error:
        return [path_error]
    assert path is not None

    failures: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeError) as exc:
        return [f"review-score.json JSON 파싱 실패: {exc}"]
    if not isinstance(data, dict):
        return ["review-score.json root는 object여야 합니다."]

    category_values = data.get("categories")
    if category_values is None:
        category_values = data
    if not isinstance(category_values, dict):
        category_values = {}
    for category in SCORE_CATEGORIES:
        value = category_values.get(category)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            failures.append(f"review-score.json에 숫자 score가 아닙니다: {category}")
        elif not math.isfinite(float(value)):
            failures.append(f"review-score.json에 유한한 숫자 score가 아닙니다: {category}")
        elif value < 0 or value > 10:
            failures.append(f"review-score.json 점수 범위가 올바르지 않습니다: {category}={value}")
        elif value < MIN_SCORE:
            failures.append(f"review-score.json {category} 점수가 기준 미만입니다: {value} < 8")

    security = data.get("security")
    security_values = security if isinstance(security, dict) else {}
    required_indicator_groups = {
        "critical": any(key in data for key in ["critical_issues", "critical_count", "security_critical"])
        or "critical" in security_values,
        "high": any(key in data for key in ["high_issues", "high_count", "security_high"])
        or "high" in security_values,
        "release blocker": any(key in data for key in ["release_blockers", "blocking_reasons"]),
        "readiness": any(key in data for key in ["release_ready", "passed"]),
    }
    for label, present in required_indicator_groups.items():
        if not present:
            failures.append(f"review-score.json에 {label} indicator가 없습니다.")

    def issue_value(key: str, label: str) -> None:
        if key not in data:
            return
        value = data[key]
        if isinstance(value, bool):
            failures.append(f"review-score.json {key} 값이 올바르지 않습니다.")
        elif isinstance(value, list):
            if value:
                failures.append(f"review-score.json에 {label}가 남아 있습니다.")
        elif isinstance(value, (int, float)):
            if not math.isfinite(float(value)) or value < 0:
                failures.append(f"review-score.json {key} count가 올바르지 않습니다: {value}")
            elif value != 0:
                failures.append(f"review-score.json에 {label}가 남아 있습니다.")
        else:
            failures.append(f"review-score.json {key}는 count 또는 list여야 합니다.")

    issue_value("critical_issues", "critical issue")
    issue_value("critical_count", "critical issue")
    issue_value("high_issues", "high issue")
    issue_value("high_count", "high issue")
    issue_value("release_blockers", "release blocker")
    issue_value("blocking_reasons", "release blocker")

    if security is not None:
        if not isinstance(security, dict):
            failures.append("review-score.json security는 object여야 합니다.")
        else:
            for key, label in [("critical", "critical issue"), ("high", "high issue")]:
                if key not in security:
                    continue
                value = security[key]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    failures.append(f"review-score.json security.{key} count가 올바르지 않습니다.")
                elif not math.isfinite(float(value)) or value < 0:
                    failures.append(f"review-score.json security.{key} count가 올바르지 않습니다: {value}")
                elif value != 0:
                    failures.append(f"review-score.json에 {label}가 남아 있습니다.")

    for key, label in [("security_critical", "critical issue"), ("security_high", "high issue")]:
        if key in data:
            value = data[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                failures.append(f"review-score.json {key} count가 올바르지 않습니다.")
            elif not math.isfinite(float(value)) or value < 0:
                failures.append(f"review-score.json {key} count가 올바르지 않습니다: {value}")
            elif value != 0:
                failures.append(f"review-score.json에 {label}가 남아 있습니다.")

    findings = data.get("findings", [])
    if not isinstance(findings, list):
        failures.append("review-score.json findings는 list여야 합니다.")
    else:
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            severity = str(finding.get("severity", "")).casefold()
            if severity in {"critical", "p0", "blocker"}:
                failures.append("review-score.json findings에 critical issue가 남아 있습니다.")
            elif severity in {"high", "p1"}:
                failures.append("review-score.json findings에 high issue가 남아 있습니다.")

    if "release_ready" in data:
        if data.get("release_ready") is not True:
            failures.append("review-score.json release_ready가 true가 아닙니다.")
    elif "passed" in data:
        if data.get("passed") is not True:
            failures.append("review-score.json legacy passed가 true가 아닙니다.")
    else:
        failures.append("review-score.json release_ready 또는 legacy passed=true가 필요합니다.")

    return failures


def validate(project_root: Path) -> list[str]:
    failures: list[str] = []
    path, path_error = project_file(
        project_root,
        ".harness/reports/mobile-review.md",
        "mobile-review.md",
        required=True,
    )
    if path_error:
        return [path_error]
    assert path is not None

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        failures.append("mobile-review.md가 비어 있습니다.")

    if is_template_like(text):
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
    elif unresolved_issue(critical_section):
        failures.append("Critical Issues 섹션에 unresolved issue가 남아 있습니다.")

    for heading in ISSUE_SECTION_HEADINGS:
        issue_section = extract_section(text, heading)
        if not issue_section:
            failures.append(f"{heading} 섹션이 없거나 비어 있습니다.")
        elif unresolved_issue(issue_section):
            failures.append(f"{heading} 섹션에 unresolved issue가 남아 있습니다.")

    verification = extract_section(text, "검증 결과")
    if not has_verification_result(verification):
        failures.append("검증 결과 섹션의 build/test 또는 mobile verification 결과가 비어 있습니다.")

    for label, terms in REQUIRED_EVIDENCE_GROUPS.items():
        minimum = 2 if len(terms) <= 4 else 3
        if not has_terms(text, terms, minimum):
            failures.append(f"필수 모바일 review evidence가 부족합니다: {label}")

    failures.extend(validate_review_score_json(project_root))

    placeholders = structured_placeholder_count(text)
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
