"""Capture what the outside world actually did with this repository. On no schedule, gating nothing.

    python capture_exposure.py            capture now, write a dated record
    python capture_exposure.py --check    report the series without writing

⛔ WHY THIS EXISTS, AND WHY IT NO LONGER DECIDES ANYTHING. A reviewer of v17 put the problem
plainly: §2c of `PRE-REGISTRATION.md` made silence a finding about the ecosystem, and the protocol
had no instrument for the one input that licenses that claim -- whether anyone saw the call.

    "A protocol under which doing nothing is compliant and yields the preferred result can produce
     a dishonest paper without anyone lying."

⛔ v18 §1 ANSWERS THAT BY WITHDRAWING THE CLAIM, NOT BY MEASURING HARDER. Two repairs were
available -- build the instrument so silence can be interpreted, or drop the interpretation -- and
the second was taken, because the first required posting obligations and a capture cadence running
to December, which are commitments outside the laboratory work itself.

⛔ SO THIS FILE HAS NO THRESHOLD AND NAMES NO OUTCOME. It is kept because traffic is a dated
observation about the world, it is cheap to record, and GitHub keeps only 14 rolling days of it --
so a figure not captured is one that cannot be recovered. Run it or do not.

⇒ The exposure series is an ARTIFACT, captured from GitHub's own records and OpenTimestamps-
stamped, rather than a narrative composed by the interested party.

⛔ AND THE CLAIM IT WAS BUILT TO SUPPORT IS WITHDRAWN. v18 §1 takes the second of two repairs: not
"measure exposure so silence can be interpreted", but "draw no inference from silence, so no
exposure measurement is needed". This file therefore has no threshold, names no outcome, and is
under no obligation to run on any cadence. It remains because a dated observation about the world
is worth recording, and because GitHub keeps only 14 rolling days of it.

⛔ THE 14-DAY WINDOW IS THE REASON THIS MUST RUN ON A SCHEDULE. GitHub's traffic API returns a
rolling 14 days and keeps nothing older. A gap longer than that is DATA PERMANENTLY LOST, not data
delayed, so this refuses rather than pretending a gap is a zero.

⚠️ AND THE DENOMINATOR IS NOT UNIQUE CLONERS. Measured 7 Sep 2026, before any announcement, this
repository showed **41 unique cloners against 1 unique viewer** -- a ratio that says the clone count
is crawlers, CI mirrors and scrapers, not readers. Reporting 41 as "exposure" would let the study
claim an audience it never had, which is the same defect the instrument exists to prevent, arriving
through the flattering number instead of the flattering narrative. Both series are recorded; the
human-signal series is the one the exposure floor is set against.
"""
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

HERE = pathlib.Path(__file__).resolve().parent
SERIES = HERE / "exposure"
REPO = "provenance-laboratory/reproduction"
MAX_GAP_DAYS = 14
D, W = chr(0x26D4), chr(0x26A0)
NL = chr(10)

ENDPOINTS = {
    "clones": "repos/%s/traffic/clones" % REPO,
    "views": "repos/%s/traffic/views" % REPO,
    "referrers": "repos/%s/traffic/popular/referrers" % REPO,
    "paths": "repos/%s/traffic/popular/paths" % REPO,
}


def gh(path, paginate=False):
    """Query the API. A missing or unauthenticated `gh` is a REFUSAL, never a skip.

    ⚠ `paginate` follows Link headers to exhaustion. It is not the default, because the traffic
    endpoints return a single object and paginating one would concatenate it into nonsense; it is
    for the LIST endpoints, where a single page silently caps the count at 30.
    """
    # ⛔ THIS REFUSED ON THE FIRST FAILURE OF ANY KIND, INCLUDING A TLS TIMEOUT -- and one did occur
    # in testing. Refusing is right for a MISSING TOOL or a PERMISSION error, which will not fix
    # themselves. It is wrong for a transient network blip, because GitHub's traffic window is 14
    # rolling days: a capture abandoned today is data that CANNOT be recovered tomorrow.
    #
    # ⇒ Transient failures are retried before the refusal stands. **The retry is not silent** -- a
    # channel that needed three attempts is a fact about the measurement, and this project has a
    # standing record of one flaky sample being read as the state of the world.
    cmd = ["gh", "api"] + (["--paginate", "--slurp"] if paginate else []) + [path]
    # ⚠ Widened after a genuinely degraded network produced three distinct wordings in one session.
    # The list is a heuristic and it is allowed to be wrong in ONE direction only: a non-transient
    # error retried three times still refuses, while a transient one mistaken for permanent costs a
    # week of data that cannot be recovered.
    _TRANSIENT = ("timeout", "TLS handshake", "connection reset", "EOF", "temporarily",
                  "502", "503", "504", "no such host", "dial tcp", "connectex",
                  "connection attempt failed", "network is unreachable", "i/o timeout")
    last = ""
    for attempt in range(1, 4):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
        except FileNotFoundError:
            raise SystemExit("%s `gh` is not installed. A missing dependency is a refusal: a "
                             "capture that silently records nothing is worse than no capture, "
                             "because the series would show a zero that means 'not measured'." % D)
        if r.returncode == 0:
            if attempt > 1:
                print("  %s %s succeeded on attempt %d" % (W, path.split("/")[-1], attempt))
            return json.loads(r.stdout)
        last = (r.stderr or "").strip()
        if not any(k.lower() in last.lower() for k in _TRANSIENT):
            break
        print("  %s attempt %d for %s: %s" % (W, attempt, path.split("/")[-1], last[:90]))
        time.sleep(5 * attempt)
    raise SystemExit("%s `gh api %s` failed after retries: %s\n  Traffic endpoints need PUSH "
                     "access to the repository." % (D, path, last[:200]))


def existing():
    return sorted(SERIES.glob("exposure-*.json"))


# ⛔ THE FLOOR IS WITHDRAWN, ALONG WITH THE CLAIM IT GATED. v18 set a threshold of 100 "unique
# viewers over the window" and a round-2 reviewer showed the quantity does not exist: GitHub returns
# a rolling 14 days of per-day uniques plus a 14-day total, there is no API figure for uniques over
# 90 days, and uniques do not add. Three candidate readings differed by more than an order of
# magnitude and two already disagreed at the baseline. Whoever computed it in December would have
# been choosing, with the answer visible, between a rule that licenses the ecosystem claim and one
# that forbids it.
#
# ⇒ THAT ANALYSIS WAS RIGHT AND IT IS NOT WHY THE FLOOR IS GONE. v18 §1 withdrew the inference
# from silence entirely, so there is no claim for a threshold to gate. A floor with nothing behind
# it is a number this file would compute and nobody would read -- and a number that exists is a
# number that eventually gets quoted.
#
# ⚠ THE SERIES IS STILL CAPTURED, AND `exposure_to_date()` STILL COMPUTES IT. Traffic is a dated
# observation about the world, it is cheap to record, and GitHub keeps only 14 days of it. What is
# removed is the THRESHOLD and the outcome it licensed -- not the measurement, and not the honesty
# about what the measurement is worth.


def exposure_to_date():
    """(figure, n_dates, disagreements) — the ONE reading of exposure this study uses.

    ⇒ THE SUM OF `views[].uniques` OVER EVERY DISTINCT DATE IN THE SERIES. Captures overlap (7-day
    cadence, 14-day window), so each date is taken ONCE. This **over-counts returning visitors** --
    a person on two days is two daily uniques and one person -- so it is an UPPER BOUND on persons.

    ⛔ AND THE FIRST VERSION OF THIS COMMENT GOT THE DIRECTION BACKWARDS, IN OUR FAVOUR. It said
    over-counting "makes failing the floor harder, which is the right direction". It does the
    opposite: an inflated figure clears the floor MORE easily, so the ecosystem claim is easier to
    license, and **a gate on a claim should be hard to pass**. That sentence travelled from here
    into the anchored DISTRIBUTION-PLAN.md and then into the review brief asking someone to check
    it -- each copy citing the last.

    ⚠ The metric is kept, because the alternatives are worse in the ways the plan lists, and the
    bound is DECLARED rather than reworded: clearing the floor shows no more than N people saw the
    call, not that N did.

    ⚠ A date appearing in two captures should carry the same value in both; GitHub's figures for a
    past day do not move. Any disagreement is REPORTED rather than silently resolved, because a
    changing past is a fact about the source and not something to average away.
    """
    per_date, clash = {}, []
    for f in existing():
        rec = json.loads(f.read_text(encoding="utf-8"))
        for row in rec.get("views", {}).get("views", []):
            d, u = row["timestamp"][:10], row["uniques"]
            if d in per_date and per_date[d] != u:
                clash.append((d, per_date[d], u))
            per_date[d] = max(per_date.get(d, 0), u)
    return sum(per_date.values()), len(per_date), clash


def main():
    check_only = "--check" in sys.argv
    SERIES.mkdir(exist_ok=True)
    prior = existing()

    # ── the gap rule, applied BEFORE the capture, because it decides whether the series is intact
    if prior:
        last = json.loads(prior[-1].read_text(encoding="utf-8"))
        then = datetime.datetime.fromisoformat(last["captured_utc"].replace("Z", "+00:00"))
        gap = (datetime.datetime.now(datetime.timezone.utc) - then).days
        print("  previous capture %s, %d day(s) ago" % (prior[-1].name, gap))
        if gap > MAX_GAP_DAYS:
            print("  %s GAP OF %d DAYS EXCEEDS THE %d-DAY API WINDOW. The days between the last "
                  "capture and\n     today are gone from GitHub's records and cannot be recovered. "
                  "This capture is still\n     written, and the gap is recorded in it so the series "
                  "cannot be read as continuous."
                  % (W, gap, MAX_GAP_DAYS))
    else:
        print("  no previous capture -- this is the BASELINE, and it should be taken BEFORE any "
              "announcement")

    rec = {
        "captured_utc": datetime.datetime.now(datetime.timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": REPO,
        "window_days": MAX_GAP_DAYS,
        "gap_days_since_previous": None,
        "note": "unique cloners is NOT the exposure denominator; see the module docstring",
    }
    if prior:
        rec["gap_days_since_previous"] = gap
        rec["previous"] = prior[-1].name

    # ⛔ THE CAPTURES ARE THE SECOND WITNESS OVER THE ATTEMPTS LOG, and they are the one that runs
    # on a schedule. `attempts-<n>.head` is stamped when an attempt is recorded, which depends on
    # somebody remembering; this record is written and stamped every seven days regardless, so a
    # tail deletion has to contradict a capture even if no head file was ever stamped.
    #
    # ⚠ THE HEAD IS RECORDED, NOT JUDGED. Whether every venue has been attempted is a publishing
    # condition and belongs where the decision to publish is taken. A capture that refused to write
    # itself because the announcement was incomplete would destroy the only data GitHub does not
    # keep -- and the baseline capture is taken BEFORE any attempt exists at all.
    try:
        import attempts as _AT
        _entries = _AT.read_log()
        rec["attempts"] = {"count": len(_entries),
                           "head": _AT.head_at(_entries, len(_entries)),
                           "venues": [e["venue"] for e in _entries]}
    except SystemExit as _e:
        # A broken log is recorded as broken. Refusing to capture would lose the exposure window.
        rec["attempts"] = {"count": None, "head": None, "error": str(_e)}
        print("  %s the attempts log does not check out; recorded in this capture and NOT "
              "silently skipped:%s     %s" % (W, NL, str(_e)[:150]))

    for k, p in ENDPOINTS.items():
        rec[k] = gh(p)

    intake = gh("repos/%s" % REPO)
    rec["intake"] = {
        "issues_open": intake.get("open_issues_count", 0),
        "forks": intake.get("forks_count", 0),
        "stars": intake.get("stargazers_count", 0),
        "watchers": intake.get("subscribers_count", 0),
    }
    # ⛔ THIS COUNTED ONE PAGE AND CALLED IT THE TOTAL. GitHub paginates at 30 by default, so the
    # numerator of this entire study -- how many people filed anything -- would have silently
    # capped at 30 and reported a smaller number than the truth. The failure only appears on
    # success, which is the worst possible time for a count to be wrong.
    #
    # ⇒ Paged to exhaustion, and the page size is stated so a reader can see the cap is not the
    # answer. `--paginate` follows Link headers; the per_page is belt and braces.
    # ⚠ `--slurp` yields a list of PAGES, each itself a list. Counting that counts pages, which for
    # a repository with 0 issues and for one with 200 both look plausible.
    _pages = gh("repos/%s/issues?state=all&per_page=100" % REPO, paginate=True)
    _issues = [i for p in _pages for i in p] if _pages and isinstance(_pages[0], list) else _pages
    rec["intake"]["issues_all"] = len(_issues)
    rec["intake"]["issues_by_label"] = {}
    for _i in _issues:
        for _lab in (l.get("name", "") for l in _i.get("labels", [])):
            rec["intake"]["issues_by_label"][_lab] = \
                rec["intake"]["issues_by_label"].get(_lab, 0) + 1

    uc = rec["clones"].get("uniques", 0)
    uv = rec["views"].get("uniques", 0)
    rec["summary"] = {
        "unique_cloners_14d": uc,
        "unique_viewers_14d": uv,
        "clone_to_view_ratio": (round(uc / uv, 1) if uv else None),
        "referrers": [r["referrer"] for r in rec["referrers"]],
        "issues_all": rec["intake"]["issues_all"],
    }

    print()
    print("  unique cloners (14d)   %d" % uc)
    print("  unique viewers (14d)   %d" % uv)
    print("  clone:view ratio       %s%s"
          % (rec["summary"]["clone_to_view_ratio"],
             "   " + W + " a high ratio is automation, not readers" if uv and uc / uv > 5 else ""))
    print("  referrers              %s" % (", ".join(rec["summary"]["referrers"]) or "none"))
    print("  issues filed (all)     %d" % rec["intake"]["issues_all"])
    print("  forks / stars          %d / %d" % (rec["intake"]["forks"], rec["intake"]["stars"]))

    # ⚠ REPORTED, NOT ADJUDICATED. This printed "EXPOSURE n / 100 — FLOOR NOT MET" and, below a
    # threshold, named an outcome: INSUFFICIENT EXPOSURE rather than a null about the ecosystem.
    # Both the threshold and that outcome are withdrawn with the claim they served, so the figure
    # is printed as what it is -- a count of daily uniques over the dates captured -- and nothing
    # is inferred from its size in either direction.
    _fig, _nd, _clash = exposure_to_date()
    print()
    print("  EXPOSURE %d over %d distinct date(s) in the series" % (_fig, _nd))
    print("     sum of views[].uniques, each date taken once")
    print("     ⚠ over-counts returning visitors; an UPPER BOUND on persons, not a count of them")
    print("     ⚠ no threshold attaches to this number. v18 withdrew the inference from silence,")
    print("        so a larger or smaller figure licenses nothing either way.")
    if _clash:
        print("     %s %d date(s) carry different values in different captures: %s"
              % (W, len(_clash), _clash[:3]))

    if check_only:
        print("\n  --check: nothing written")
        return 0

    out = SERIES / ("exposure-%s.json" % rec["captured_utc"][:10])
    if out.exists():
        print("\n  %s %s already exists; a second capture on one day would overstate the series. "
              "Not written." % (W, out.name))
        return 0
    body = json.dumps(rec, indent=2, sort_keys=True)
    out.write_text(body, encoding="utf-8", newline="\n")
    print("\n  wrote %s (%d B, sha256 %s)"
          % (out.name, len(body), hashlib.sha256(body.encode()).hexdigest()[:16]))
    # ⛔ THE TWO HALVES OF THIS COMMAND WERE RELATIVE TO DIFFERENT DIRECTORIES: the script path
    # to the CWD, the argument to the grandparent. A round-6 reviewer noticed because
    # `prepare_anchor.py` gets it right, which is how the disagreement was visible at all. Both
    # are relative to the study directory, which is where the message tells you to be.
    print("  %s NOW STAMP IT (from this directory): python ../../_ots_stamp.py %s"
          % (W, out.relative_to(HERE).as_posix()))
    print("     An unstamped capture is a file we wrote, which is exactly what this replaces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
