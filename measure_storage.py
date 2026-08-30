"""Measurement 2: the storage cost of the provenance apparatus — with its numerator declared.

⛔ THIS NUMBER WAS COMPUTED ONCE, BY HAND, IN A THROWAWAY SCRIPT. It reported 0.509% and nothing
shipped that could recompute it. A reviewer's objection is exact: a ratio whose numerator is a
SELECTED SUBSET is not a measurement, it is a choice presented as one, and neither the selection
nor its rule could be inspected.

⇒ So the two populations are defined here, in code, and the rule for each is stated:

    ARTIFACT     what a consumer wants: the corpus they would train on, and the weights that
                 result. If you removed the provenance apparatus entirely, this is what is left

⚠️ AND WHICH QUANTITY IS THIS? A reviewer asked, correctly, whether measurement 2 reports the
provenance overhead of ONE MODEL RELEASE or the size of an entire experimental apparatus. It is
the first: the files below are what a publisher would have to ship alongside a release so a
stranger could check it. The measurement instruments themselves -- measure_cost.py,
reproduce_findings.py, verify_package.py, the findings document -- are NOT counted, because they
are this study's apparatus and not a release's. That boundary is a choice and it is stated here
rather than left to be inferred from a total.
    APPARATUS    what exists ONLY so a third party can check the artifact: manifests, digests,
                 timestamp proofs, the pre-registration, the run records, and the code that
                 produces or verifies them

⚠️ THE BOUNDARY IS A JUDGEMENT AND IT IS ARGUABLE. `train.py` is in the apparatus because without
provenance you would still need a training script -- but you would not need one written to be
re-run byte-identically by a stranger. `build_corpus.py` is apparatus because the cleaning rule is
part of the specification, not of the corpus. A reviewer may draw either line elsewhere; both
totals are printed so the effect of moving it can be seen rather than argued about.

    python measure_storage.py
"""
import io
import json
import pathlib
import sys

NL = chr(10)
# used in the missing-file refusal below; it was referenced and never defined, so
# that control would have raised NameError instead of reporting. It had never run.
D = chr(0x26D4)
HERE = pathlib.Path(__file__).resolve().parent

# ── the two populations, by RULE ──────────────────────────────────────────────────────
ARTIFACT = [
    ("corpus/clean/*.txt", "the corpus a consumer would train on"),
    ("reference/weights.npz", "the trained weights that result"),
]
APPARATUS = [
    ("corpus/MANIFEST.json", "digests and Merkle root"),
    ("corpus/MANIFEST.json.ots", "the proof the corpus preceded training"),
    ("corpus/sources.json", "where each text came from"),
    ("corpus/build_corpus.py", "the cleaning rule, which is part of the specification"),
    ("PRE-REGISTRATION-v2-CONFIRMATORY.md", "the protocol the study runs under"),
    ("PRE-REGISTRATION-v2-CONFIRMATORY.md.ots", "its proof"),
    ("ENVIRONMENT-LOCK.json", "the interpreter and library record"),
    ("PRE-REGISTRATION.md", "version 1, retained as the pilot protocol"),
    ("PRE-REGISTRATION.md.ots", "its proof"),
    ("AMENDMENT-2026-08-30.md", "the recorded deviation"),
    ("train.py", "the pipeline, written to be re-run byte-identically"),
    ("reference/run.json", "the environment and result record"),
    ("reference/loss.json", "the loss curve"),
    ("reference/loss-full.json", "full-precision losses"),
    ("reference/trace.json", "per-step, per-array digests"),
    ("reference/SHA256SUMS", "covers the reference bundle"),
]
# Moving these across the boundary is the arguable part, so the effect is reported separately.
ARGUABLE = {"train.py", "corpus/build_corpus.py"}


def total(patterns, missing):
    out = {}
    for pat, why in patterns:
        if "*" in pat:
            for f in sorted(HERE.glob(pat)):
                out[str(f.relative_to(HERE)).replace(chr(92), "/")] = (f.stat().st_size, why)
        else:
            f = HERE / pat
            if f.exists():
                out[pat] = (f.stat().st_size, why)
            else:
                missing.append(pat)
    return out


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    # ⛔ A DECLARED FILE THAT IS ABSENT WAS SILENTLY SKIPPED, so this measured whatever
    # happened to be on disk and called it the apparatus. A reviewer ran the shipped script and
    # got 169,558 bytes where the stored record said 182,542 -- the script and its own output
    # disagreed, and neither was wrong about what it saw. A measurement whose population depends
    # on what is lying around is not a measurement.
    missing = []
    art = total(ARTIFACT, missing)
    app = total(APPARATUS, missing)
    if missing:
        raise SystemExit(D + " %d declared file(s) are absent, so the populations are not the "
                         "ones this measurement is defined over: %s" % (len(missing), missing))
    a = sum(v[0] for v in art.values())
    p = sum(v[0] for v in app.values())
    arguable = sum(v[0] for k, v in app.items() if k in ARGUABLE)
    ots = sum(v[0] for k, v in app.items() if k.endswith(".ots"))

    print("=" * 78)
    print("  MEASUREMENT 2 — storage cost of the apparatus")
    print("=" * 78)
    print()
    print("  ARTIFACT — what a consumer wants")
    for k, (n, why) in sorted(art.items(), key=lambda x: -x[1][0])[:6]:
        print("    %-34s %10d   %s" % (k, n, why))
    if len(art) > 6:
        print("    ... and %d more corpus files" % (len(art) - 6))
    print("    %-34s %10d" % ("TOTAL", a))
    print()
    print("  APPARATUS — what exists only so a stranger can check it")
    for k, (n, why) in sorted(app.items(), key=lambda x: -x[1][0]):
        print("    %-34s %10d   %s" % (k, n, why))
    print("    %-34s %10d" % ("TOTAL", p))
    print()
    print("  apparatus / artifact                 %.4f%%" % (100.0 * p / a))
    print("  moving train.py and build_corpus.py   %.4f%%   (the arguable %d bytes)"
          % (100.0 * (p - arguable) / a, arguable))
    print("  of the apparatus, timestamp proofs    %d bytes" % ots)
    print()
    print("  " + chr(0x26A0) + " THE PERCENTAGE DOES NOT TRANSFER. The apparatus is near-CONSTANT")
    print("  in size -- a manifest, two proofs and a run record do not grow with the model --")
    print("  while this artifact is deliberately tiny. On a release a thousand times larger the")
    print("  same apparatus is a thousandth of the fraction. The ABSOLUTE figure is what carries:")
    print("  %d bytes, of which %d are timestamp proofs." % (p, ots))
    print("=" * 78)

    rec = {"artifact_bytes": a, "apparatus_bytes": p,
           "apparatus_excluding_arguable_bytes": p - arguable,
           "arguable_bytes": arguable, "timestamp_proof_bytes": ots,
           "percent_of_artifact": round(100.0 * p / a, 4),
           "percent_excluding_arguable": round(100.0 * (p - arguable) / a, 4),
           "artifact_files": {k: v[0] for k, v in art.items()},
           "apparatus_files": {k: v[0] for k, v in app.items()},
           "_boundary": ("train.py and build_corpus.py are counted as apparatus because they exist "
                         "in this form to make the artifact checkable; a reviewer may draw that "
                         "line differently, so both totals are reported."),
           "_caveat": ("The apparatus is near-constant in size and this artifact is deliberately "
                       "tiny, so the percentage does not transfer to a real release. The absolute "
                       "figure is the one that carries.")}
    (HERE / "MEASUREMENT-2.json").write_text(json.dumps(rec, indent=2) + NL,
                                             encoding="utf-8", newline=NL)
    print("  written to MEASUREMENT-2.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
