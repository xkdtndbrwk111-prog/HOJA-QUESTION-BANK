#!/usr/bin/env python3
"""Verify the HOJA Question Bank recovery checkpoint; no third-party dependencies."""
import json
import pathlib
import sys
import collections
import hashlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
def fail(msg):
    raise ValueError(msg)
def file_at(path):
    if not isinstance(path, str) or not path or path.startswith("/") or ".." in pathlib.PurePosixPath(path).parts:
        fail("unsafe file path: " + repr(path))
    full = (ROOT / path).resolve()
    if not full.is_file() or ROOT not in full.parents:
        fail("missing file: " + path)
    return full
def main():
    s = json.loads(file_at("workflow/state.json").read_text("utf-8"))
    if s.get("schemaVersion") != "hoja-resume-v1" or s.get("branch") != "main":
        fail("bad checkpoint version or branch")
    if s.get("activeWorkstream") not in {x["id"] for x in s["workstreams"]}:
        fail("unknown active workstream")
    ids = [w["id"] for w in s["workstreams"]]
    if len(ids) != len(set(ids)) or not {"math-187", "science-64", "renderer", "social-grade6-64", "korean-grade5-four-stories"}.issubset(set(ids)):
        fail("missing/duplicate workstreams")
    for w in s["workstreams"]:
        file_at(w["entry"])
        for path in w["evidence"]:
            file_at(path)
        if not w.get("facts") or not w.get("next"):
            fail("incomplete workstream: " + w["id"])
    for name in ("AGENTS.md", "CURRENT_WORK.md", "docs/CHAT_RESUME_PROTOCOL.md"):
        file_at(name)
    cat = json.loads(file_at("approved/catalog.json").read_text("utf-8"))
    counts = cat["summary"]
    r = s["registeredApproved"]
    if (counts["approvedUnits"],counts["approvedQuestions"]) != (r["units"],r["questions"]):
        fail("approved catalog and checkpoint disagree")
    rv = json.loads(file_at("renderer/VERSION.json").read_text("utf-8"))
    if rv["rendererVersion"] != s["rendererCurrent"]:
        fail("renderer current version differs from checkpoint")
    math = json.loads(file_at("renderer/experiments/2026-11-22/math-187-meaning-render-tags-review.4.json").read_text("utf-8"))
    questions = math["questions"]
    if len(questions) != 187:
        fail("math tag count is not 187")
    families = collections.Counter(q["layout"]["preferredLayout"] for q in questions.values())
    if families != {"A":120,"C":48,"D":19}:
        fail("math A/C/D distribution mismatch: " + str(families))
    if sum(1 for q in questions.values() if q.get("needsHumanReview")) != 68:
        fail("math manual-review count differs")
    science = next(w for w in s["workstreams"] if w["id"] == "science-64")
    if science["status"] == "GITHUB_BINARY_UPLOAD_PENDING":
        science_dir = ROOT / "approved/science"
        if science_dir.exists() and list(science_dir.rglob("*.zip")):
            fail("science ZIP now exists; verify and update checkpoint")
    elif science["status"] == "APPROVED_GITHUB_REGISTERED":
        expected = {
            "sci5-s2-heat-common": "a503459e875d4565e888ce40878d279e9b3513c76e95711ff6f806a610186947",
            "sci5-s2-u4-common": "7b711e6d2d29e77152b49958b9bfe22690e1b297a45edd3828cb56270b8b7fae",
        }
        for cid, digest in expected.items():
            p = "approved/science/grade5/semester2/" + cid + "/"
            m = json.loads(file_at(p + "manifest.json").read_text("utf-8"))
            archive = file_at(p + m["archive"])
            if hashlib.sha256(archive.read_bytes()).hexdigest() != digest or m["archiveSha256"] != digest:
                fail("science archive mismatch: " + cid)
            with zipfile.ZipFile(archive) as z:
                if z.testzip() is not None or json.loads(z.read("release/approval.json"))["teacherApproval"] != "APPROVED":
                    fail("science archive approval or CRC mismatch: " + cid)
        if counts.get("science") != 64:
            fail("science count missing")
    else:
        fail("unknown science checkpoint status")
    readme = file_at("CURRENT_WORK.md").read_text("utf-8")
    if s["activeWorkstream"] == "math-187" and "수학 187" not in readme:
        fail("human-readable checkpoint missing active work")
    print("PASS: checkpoint references, catalog, renderer version, 187 math tags, manual review count")
    print("NOTE: This is NOT a browser visual QA, scientific content approval, or game deployment test.")
    return 0
if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        print("FAIL:", str(e), file=sys.stderr)
        sys.exit(1)
