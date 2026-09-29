"""Assemble the internal-review packet for Paper B, with every figure measured here.

⛔ WHY THIS IS NOT A TEMPLATE WITH THE NUMBERS TYPED IN. Paper A's review packet opened with the
sentence "every number here is measured at build time" and carried `round 9` as a string literal
through two further rounds of work, with a covering note describing a finding from the round before
that. The live numbers were live and the noun beside them was dead. This reads the measurement
files and refuses to write if one is missing.

    python build_review_packet.py
"""
import hashlib
import io
import json
import pathlib
import re
import subprocess
import sys
import zipfile

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "review"

def _retired(prefix_rel):
    """Every superseded artifact bound to one file, whatever kind it is.

    A retired proof, signature or draft binds an EARLIER version of the file beside it and no
    longer binds that file -- which is the fact it exists to record, and the reason each ships.
    """
    base = HERE / prefix_rel
    out = []
    for sup in sorted(base.parent.glob(base.name + "*superseded-*")):
        kind = ("proof" if ".ots." in sup.name else
                "signature" if ".asc." in sup.name else "draft")
        out.append((sup.relative_to(HERE).as_posix(),
                    "a RETIRED %s: it binds an earlier draft and no longer binds the file beside "
                    "it, which is the fact it records" % kind))
    return out


# ⛔ A DOCUMENT NAMED BY THE PROJECTION AND BY HAND IS NAMED TWICE, and this builder refuses on
# a duplicate -- correctly, because a repeated zip entry is written silently and a reader may
# extract either copy. Round 9 added v19 to `SEND` to carry its reason, while the projection below
# had been finding every `PRE-REGISTRATION*.md` since round 8. **The list grew back to hold what
# the projection could not say, which is exactly how a list returns after a projection replaces
# it** -- the defect this project keeps naming, committed here by the round that was writing about
# it.
#
# ⇒ THE NOTE IS DATA, NOT A SECOND ENTRY. A document needing a specific reason declares one
# here; everything else takes the generic note; and one place decides which documents ship.
_WHY = {
    "PRE-REGISTRATION-v3-CONFIRMATORY.md":
        "THE CONFIRMATORY PROTOCOL -- READ THIS FIRST",
    "PRE-REGISTRATION-v19-CONFIRMATORY.md":
        "NEW: the split. v18 bundled a governance change -- a write path into pre-registration "
        "documents -- with the decision a reviewer is meant to be weighing, which v18's own "
        "section 1d forbids. v19 commits the two tools and argues them alone. Read it against "
        "v18 section 2b, which conceded the bundling in round 8 and recorded it instead of "
        "repairing it",
}


def _findings_send():
    """Every FINDING-*.md present, described by its own first heading.

    ⛔ THESE WERE LISTED BY HAND, and the list was inside a file the protocol PINS -- so shipping
    one new finding cost a signed, stamped, anchored version. Three rounds in a row paid it: v23
    pinned this file, v24 §2c re-pinned it to ship four findings, and v24 pinned it again.

    ⚠️ The rule is what deserves pinning, not the inventory. A round-21 reviewer put it exactly:
    pin *every FINDING-* file must be classified or the build refuses*, and the list can then change
    without a protocol version while the build still cannot silently drop a finding.

    ⚠️ THE DESCRIPTION IS READ, NOT TYPED. A hand-written summary beside a document drifts from
    it, and a reviewer reading the packet index would be told something the finding no longer says.
    The first heading is the document's own account of itself.
    """
    out = []
    for f in sorted(HERE.glob("FINDING-*.md")):
        head = ""
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                head = line.lstrip("#").strip()
                break
        out.append((f.name, head or "a finding record carrying no heading of its own"))
    return tuple(out)


def _protocol_send():
    """Every protocol document present, with its proof, its signature, and its retired proofs.

    ⛔ THIS WAS A LIST OF VERSION NAMES, like the two removed from `anchor_status.py` and
    `build_package.py` in the same round. It refused to build when v8 appeared, which is the
    fail-closed half working exactly as intended -- but the fix for a list that goes stale is not
    a longer list. What saved this file is that it stops on anything it has not been told about;
    what is fixed here is that it no longer needs telling.

    ⚠ SIGNATURES AND RETIRED PROOFS TRAVEL WITH THE DOCUMENT. An anchor answers WHEN and a
    signature answers WHO, so a packet carrying every proof and no signature ships half the
    question. And a `.superseded-` proof is evidence: it binds an earlier draft and no longer
    binds the file beside it, which is the fact it exists to record.
    """
    out = []
    for doc in sorted(HERE.glob("PRE-REGISTRATION*.md")):
        why = _WHY.get(doc.name, "a protocol document, retained as part of the record")
        out.append((doc.name, why))
        # ⛔ AND THE PROOF OVER THE SIGNATURE WAS A FOURTH SHAPE THIS LIST DID NOT HAVE. Signing
        # v18 and v19 produced `.asc.ots` — an anchor over the SIGNATURE, which is what dates the
        # act of signing rather than the document — and the builder refused, correctly, because
        # two new files matched nothing. Adding two names would have been the list growing back;
        # the shapes are enumerated once, here, and each is looked for beside every document.
        for extra, note in ((doc.name + ".ots", "its proof"),
                            (doc.name + ".asc", "its detached signature -- the anchor says WHEN, "
                                                "this says WHO"),
                            (doc.name + ".asc.ots", "the proof over that signature: it dates the "
                                                    "act of signing, not the document")):
            if (HERE / extra).exists():
                out.append((extra, note))
        # ⛔ THIS GLOBBED `.ots.superseded-*` AND ONLY THAT, inside a function whose docstring
        # says the fix for a list that goes stale is not a longer list. There are three kinds of
        # retired artifact here and it saw one: a retired PROOF (`.ots.superseded-`), a retired
        # SIGNATURE (`.asc.superseded-`), and a retired BODY (`.md.superseded-draft-`). The walk
        # over the whole tree found the other two sitting unshipped and unexcused.
        # ⇒ Project over the superseded SIBLINGS of this document, whatever kind they are.
        # ⚠️ ANCHOR ON THE FULL NAME, NOT THE STEM. `doc.stem` for `PRE-REGISTRATION.md` is
        # `PRE-REGISTRATION`, which prefixes EVERY versioned document -- so the unversioned one
        # claimed all 22 retired artifacts belonging to v2 through v11 as its own, and the
        # duplicate-entry check refused. Keeping `.md` in the pattern binds each retired artifact
        # to the one document it actually names.
        out += _retired(doc.name)
    return tuple(out)


# Read by the packet collector (`review-2026-09-19/collect.py`) by AST: the two members under a
# dot-directory this archive ships on purpose, with the reason. Every other dot-directory member is
# refused there on sight; these are the forms a reproducer files with, and the record counts them.
SHIP_DOTPATHS = {
    ".github/ISSUE_TEMPLATE/commitment.yml": "the issue form a reproducer files a commitment with",
    ".github/ISSUE_TEMPLATE/reproduction-report.yml": "the issue form a reproducer files a report with",
}
DOTFILES = (
    (".gitignore", "repository configuration; shipped so the tree the record describes is the tree"),
    (".gitattributes", "the same"),
    ("corpus/.gitignore", "the same, one directory down"),
    (".github/ISSUE_TEMPLATE/commitment.yml", "the issue form a reproducer files a commitment with"),
    (".github/ISSUE_TEMPLATE/reproduction-report.yml", "the issue form a reproducer files a report with"),
)

SEND = _protocol_send() + _findings_send() + DOTFILES + (
    # ⛔ THIS WAS EXCLUDED -- *a shipped copy would be a verdict not produced by the run the
    # reader is looking at* -- and the exclusion cost three rounds of a red hygiene bit: the
    # withdrawn-claims scan counts every text file in the tree, this one included, so the shipped
    # WITHDRAWN-CLAIMS.md said 139 files and a reviewer's extraction walked fewer. It ships now,
    # BOUND to `tree_digest`: `build_review_packet.py` refuses unless that digest is the tree being
    # shipped, and `REVIEW-COMMANDS.json` restates it as measured. A reviewer's own run overwrites
    # it, which is what a verdict file is for.
    ("CONTROL-SUITE-VERDICT.json",
     "the suite's verdict as DATA, bound to the tree digest it was produced on; a reviewer's own "
     "run replaces it, and nothing here treats a shipped copy as anyone's run but the builder's"),
    ("PUBKEY.asc",
     "the public key. ⛔ The round-6 repair shipped check_signature.py and NOT the key, so "
     "every reproducer got NO_PUBKEY on all eight documents -- a check that returns the same "
     "answer for a good signature and a forged one, for everyone except the one person who "
     "does not need it. A round-7 reviewer found it reported as fixed and absent"),
    ("pin_anchors.py",
     "the blocks our proofs name, fetched from a public explorer with the source and date kept. "
     "Parsing an attestation is not verifying one: two round-6 reviewers minted a structurally "
     "valid attestation offline, one naming block 999999, and moved authority with it"),
    ("ANCHORS.json",
     "the real merkle root of each of those blocks. ANCHORED now means the root computed from "
     "the document's own bytes IS the pinned root; a proof naming an unpinned block is "
     "STRUCTURAL and never authority. NOT pinned by v9, because anchoring a document changes "
     "this file -- see v9 section 14"),
    ("ots_verify.py",
     "the OpenTimestamps parser. Round 4's 35-bytes-of-junk attack survived its own repair "
     "because the repair added BINDING and never added PARSING -- run it against the forgeries"),
    ("check_signature.py",
     "who asserted the protocol documents. Anchoring is free, public and unilateral, so it "
     "answers WHEN and never WHO"),
    ("REGISTRATION.template.json",
     "what --publishing now requires: a reporting address and an OPEN close date. The first "
     "version of that gate accepted this template's own FILL-IN placeholder"),
    ("MEASUREMENT-4-recording-gap-no-pyyaml.json",
     "the same two arms as the CONFOUNDED record, re-evaluated: the arms did not change, the "
     "word for what went wrong did"),
    # ---- declared this round -----------------------------------------------------------------
    # ⛔ THE PACKET REFUSED UNTIL EVERY ONE OF THESE WAS NAMED, which is the rule working: a
    # review packet that omits what the round did is a packet the round cannot be judged from.
    ("withdrawn_claims.py",
     "NEW: which anchored documents still state a withdrawn claim, and where the withdrawal is. "
     "PRE-REGISTRATION.md states the ecosystem claim unmarked and is OpenTimestamped, so it "
     "cannot be edited -- the marker is additive and generated rather than written"),
    ("WITHDRAWN-CLAIMS.md", "NEW: what that generates. Travels with the documents it is about"),
    ("prepare_anchor.py",
     "what stands between a version and being in force, checked rather than written down. It "
     "verifies that the file digests the document pins still describe the files here, then prints "
     "the sign-and-stamp commands for the operator. It performs neither: the key is theirs and a "
     "stamp is an outward act. COMMITTED BY v19, not v18 -- it carries the write path, and round "
     "9 split that out of the version whose section 1 is the thing under review"),
    ("attempts.py",
     "NEW: the hash-chained attempt log. Note what it does NOT do any more -- the venue list is "
     "reported as CONTEXT and no longer gates what may be recorded, because a superseded plan "
     "cannot be both 'nothing in force' and the thing deciding what is recordable"),
    ("capture_exposure.py",
     "the v18 exposure instrument, stopped mid-build and shipped as it stood. Route 2 withdrew "
     "the claim instead of instrumenting it, so this is evidence of a road not taken rather than "
     "a working tool -- read it against section 1 of v18 and say whether withdrawing was right"),
    # ⛔ v18 PINS THIS AND THE ARCHIVE DID NOT SHIP IT, so `prepare_anchor.py` -- the command the
    # prompt tells a reviewer to run FIRST -- reported it as a broken commitment from the extracted
    # archive. The proof ships beside it for the same reason every signature here does: a capture
    # says what was seen, its proof says the capture existed by a date, and one half alone is not
    # checkable.
    ("exposure/exposure-2026-09-07.json",
     "the single exposure capture, pinned by v18. Route 2 withdrew the claim this instrument was "
     "built to support, so it is the record of a road not taken -- and it is pinned, so it must "
     "travel or the pin reads as broken rather than as unshipped"),
    ("exposure/exposure-2026-09-07.json.ots",
     "its timestamp proof; the capture and its proof ship together or neither is checkable"),
    ("DISTRIBUTION-PLAN.md",
     "the exposure plan v18 supersedes. Shipped BECAUSE it is superseded: the withdrawal is only "
     "judgeable beside the thing withdrawn"),
    # ⛔ THE FINDINGS ARE NO LONGER LISTED HERE. They were, and the list sat inside a file the
    #    protocol pins, so each new finding cost a protocol version. `_findings_send()` now collects
    #    every FINDING-*.md and reads each one's description from its own first heading. The
    #    fail-closed rule is untouched: a finding that does not match the pattern is still a stray
    #    file and still refuses the build.
    ("HOW-TO-RECHECK-THE-ANCHORS.md", "how to re-verify every proof here without trusting us"),
    ("REPRODUCER-STATUS-NOTE.md", "what a reproducer can and cannot currently do"),
    ("ZENODO-DEPOSIT.md", "the deposit record"),
    # ⇒ THE DISPOSITIONS ARE THE ROUND'S WORK, so they ship and a reviewer can argue with each
    # one. Each entry records a document, its digest, what that document does about the withdrawn
    # claim, and -- crucially -- whether a human read it or a phrase scan proposed it.
    #
    # ⚠️ DELIBERATELY NOT PINNED BY ANY VERSION. A reading is meant to go stale the moment its
    # file changes; pinning the record of the readings would make every re-reading a protocol
    # amendment, which is the opposite of the intent.
    #
    # ⛔ AND ROUND 8'S REASON FOR THAT WAS HALF RIGHT AND SHIPPED AS IF IT WERE WHOLE. It said
    # *the integrity that matters is the per-entry digest binding, and that is inside the file*.
    # The binding defends against THE DOCUMENT changing. It never defended against THE RECORD OF
    # THE READING changing, and a round-9 reviewer walked straight through the gap: every machine
    # seed promoted to `human`, the one anchored carrier flipped to `clean`, and a clean exit --
    # the document the tool exists for, gone from the published record.
    #
    # ⇒ The record is an append-only hash-chained log now, with a head file, the same
    # construction `attempts.py` uses. Both halves ship: a chain says the entries have not been
    # rewritten, a head says none has been deleted from the end, and one alone is not a control.
    ("WITHDRAWN-DISPOSITIONS.jsonl",
     "one entry per READING -- a file, its digest at the time, what it does about the withdrawn "
     "claim, and `prev`, the SHA-256 of the previous entry's exact bytes. Append-only and chained"),
    ("WITHDRAWN-DISPOSITIONS.head",
     "what pins how many readings there are. A chain cannot see entries deleted from its END; "
     "this can. Stamp it and the operator's own hand stops being the last word on it"),
    # ⚠️ ITS PROOF SHIPS BESIDE IT, AND SAYS LESS THAN IT WILL. The whole-tree walk surfaced
    # this one unaccounted -- the same remark about how long a file had been missing that the
    # LICENSE entry below records.
    ("WITHDRAWN-DISPOSITIONS.head.ots",
     "the head's timestamp proof, upgraded to a Bitcoin attestation (block 967531), which "
     "ANCHORS.json pins since round 14; the proof verifies against that pinned root offline"),
    # ⚠️ THE SUPERSEDED FLAT RECORD SHIPS TOO, for the same reason DISTRIBUTION-PLAN.md does:
    # ten of its entries are the provenance of the chain's first ten, and the other thirty-five
    # are the thing that was dropped. A reviewer can only argue with that if they can see it.
    ("WITHDRAWN-DISPOSITIONS.json.superseded-flat-20260914T110818Z",
     "the flat record the chain replaced. Its 35 `seeded_from: phrase-scan` entries were written "
     "by no code path in this tree and are not migrated; its 10 human readings are"),
    ("LICENSE", "the terms this archive travels under -- surfaced by the whole-tree walk, which "
                "is a remark about how long it had been missing"),
    # The detached signatures' own timestamp proofs. A signature says WHO; its proof says the
    # signature existed by a date. Both halves ship or neither is checkable.
    ("anchor_status.py", "the proof check -- run it; a pass is narrower than it sounds"),
    ("ENVIRONMENT-LOCK.json", "interpreter and library, recorded not locked"),
    ("MEASUREMENT-2.json", "storage overhead, from measure_storage.py"),
    ("measure_storage.py", "measurement 2's derivation, with its boundary declared"),
    ("PILOT-2026-08-29.md", "the observation that made the thread pin part of the protocol"),
    ("AMENDMENT-2026-08-30.md", "a deviation from section 2b, recorded on the day"),
    ("PHASE-2-FINDINGS.md", "what the pipeline found"),
    ("MEASUREMENT-1.json", "the cost of determinism, 11 interleaved reps"),
    ("MEASUREMENT-6.md", "engineering hours, self-reported and flagged as the weakest evidence"),
    ("REPRODUCTION-CALL.md", "the open request, written to section 2b"),
    ("PUBLICATION-CHECKLIST.md", "the decisions that must be made in the act of publishing"),
    ("train.py", "the pipeline"),
    ("build_package.py", "what a reproducer receives"),
    ("verify_package.py", "the package run as a stranger would"),
    ("build_review_packet.py", "this packet's own builder -- a reviewer asked for it"),
    ("REVIEW-ROUNDS.json", "the round record the covering note is generated from"),
    ("measure_cost.py", "measurement 1's instrument"),
    ("reproduce_findings.py",
     "re-derives the headline findings from scratch -- five runs, no timing, so a"
     " reviewer checks the RESULTS rather than the prose"),
    ("corpus/MANIFEST.json", "the corpus and its Merkle root"),
    ("corpus/MANIFEST.json.ots", "committed BEFORE the first training step, now anchored"),
    # ⇒ The corpus manifest has retired proofs too, and they were invisible until the coverage
    # check walked the tree. Same projection, same reason -- the kind of artifact does not depend
    # on which file it happens to sit beside.
    *_retired("corpus/MANIFEST.json"),
    ("corpus/build_corpus.py", "the corpus derivation, pinned by digest"),
    ("corpus/sources.json", "the ten texts and where they came from, pinned by digest"),
    ("corpus/verify_shipped.py",
     "checks a SHIPPED corpus using only what a package contains -- build_corpus.py --verify "
     "cannot, because it re-derives from raw/ and raw/ is not shipped"),
    ("check_commitments.py",
     "the control that enforces the digest commitments -- v3 §2 was prose, and was broken the "
     "next day without anything noticing"),
    ("measure_hardware.py", "measurement 4's instrument, which labels the COMPARISON"),
    ("MEASUREMENT-4-confounded-no-pyyaml.json",
     "the first hardware pair: bit-identical AND confounded, retained as record"),
    ("MEASUREMENT-4-RUNBOOK.md", "the second-machine procedure, and the two errors it contained"),
    ("MEASUREMENT-5-7.json", "measurements 5 and 7, computed rather than typed"),
    ("measure_divergence.py", "their instrument, including the seed-sensitivity arm"),
    ("seed_sensitivity.py", "the seed arm's driver"),
    # ⛔ THE ROUND'S ONE NEW RESULT SHIPPED WITH NONE OF ITS EVIDENCE. The packet printed
    # "m4 ... MATCHED-STACK ... bit-identical True" from MEASUREMENT-4.json while that file was
    # EXCLUDED with the reason "absent until measurement 4 is retaken" -- false, it was on disk and
    # the packet could only print from it by opening it. Neither arm's run.json shipped either,
    # because unclassified() globbed *.py/*.md/*.json beside the builder and never looked in
    # runs/. A reviewer found all of it and called it round 4's own headline defect inside round
    # 4's own fix. They were right.
    ("MEASUREMENT-4.json", "THE RESULT, with both arms' environments and every condition"),
    ("runs/det-1/run.json",
     "the reference run build_package.py requires. ⛔ Without it the builder "
     "refuses before reaching any control, so a round-9 reviewer could not exercise the "
     "repaired build path from this packet at all -- the fix was untestable exactly "
     "where it needed testing"),
    ("runs/tpc-thr-1/run.json", "arm A's run record -- rehash it"),
    ("runs/amd-thr-1/run.json", "arm B's run record -- rehash it"),
    ("runs/tpc-thr-1/weights.npz", "arm A's artifact, so bit-identity can be recomputed"),
    ("runs/amd-thr-1/weights.npz", "arm B's artifact, so bit-identity can be recomputed"),
    ("runs/amd-thr-1-no-pyyaml/run.json",
     "the first pair's arm B, retained: bit-identical AND inadmissible"),
    # the divergence runs MEASUREMENT-5-7.json is computed from -- found by the same coverage
    # check, one layer down: a measurement that names a run and does not ship it is the same
    # defect as m4's, and there were five more of them.
    ("runs/thr-1/run.json", "measurement 5/7 reference arm, 1 thread"),
    ("runs/thr-2/run.json", "measurement 5/7, 2 threads"),
    ("runs/thr-4/run.json", "measurement 5/7, 4 threads"),
    ("runs/thr-8/run.json", "measurement 5/7, 8 threads"),
    ("runs/thr-16/run.json", "measurement 5/7, 16 threads"),
    ("test_controls.py",
     "every attack round 4 used, as a suite -- the positive controls were prose and both "
     "reviewers broke the tools they described"),
)

# {D} SEND WAS A HAND-KEPT LIST AND IT HAD ALREADY DRIFTED TWICE OVER: `anchor_status.py` appeared
# in it TWICE, so the zip carried a duplicate entry -- silently, because zipfile only warns -- and
# every file added by two rounds of work was missing from a packet whose entire job is to show a
# reviewer everything. A reader would have judged the round on an artifact that omitted the
# governing protocol version, the control enforcing its digests, and the measurement instrument.
#
# ⇒ The descriptions stay curated, because they carry judgement a projection cannot. What is
# PROJECTED is the coverage check: every candidate file must be named in SEND or excused by name.
# Files in this archive that legitimately carry the author's identity, and the reason each does.
# See the note in paper 2's builder: the list lives here, `collect.py` reads it and refuses anything
# it does not cover, and the key is a BASENAME -- which is why `run.json` needs one entry and not
# fourteen that grow with every measurement run.
#
# ⚠️ `C:/Users/runneradmin` IS NOT A LOCAL PATH IN THE SENSE THE RULE MEANS. It is the hosted
# GitHub Actions Windows runner's own account, recorded as part of the environment a measurement
# ran in -- it identifies a public CI image, not a person or a machine of ours. The rule that
# catches it is right to be broad and this is the declaration that says which side of it these are.
IDENTITY_EXPECTED = {
    "run.json": "the CI runner's workspace path; a hosted GitHub Actions account, not ours",
    "MEASUREMENT-4.json": "the same runner path, in the measurement record it belongs to",
    "MEASUREMENT-4-confounded-no-pyyaml.json": "the same",
    "MEASUREMENT-4-recording-gap-no-pyyaml.json": "the same",
    "pin_anchors.py": "the signing key's identity; an anchor nobody can attribute commits to "
                      "nobody, which is the opposite of what an anchor is for",
    "build_corpus.py": "the same key identity, in the corpus manifest it signs",
    "ZENODO-DEPOSIT.md": "deposit metadata for a named, published record",
    # ⇒ Surfaced the moment LICENSE started shipping, which is the control doing its job on a
    # file that had been missing from the archive for the whole study. A copyright line names a
    # legal person; that is what a copyright line is.
    "LICENSE": "the copyright line; a licence that names nobody grants nothing",
    # ⚠️ This file ships, and the note above SPELLS the runner path in order to declare it -- so
    # the scan finds it here. A gate must spell what it forbids, and it must then say so about
    # itself rather than be granted a quiet exemption for being a gate. This is that sentence.
    "build_review_packet.py": "this declaration quotes the runner path it declares",
}

EXCLUDED = {
    "REVIEW-ROUNDS.json": "listed above; kept here so the excuse list is exhaustive",
}

# ⛔ AN EXCUSE THAT CLAIMS ABSENCE MUST BE TRUE. MEASUREMENT-4.json was excused as "absent until
# measurement 4 is retaken" while sitting on disk and being READ by this very script eighty lines
# later. The coverage check verified that every file was NAMED and never that the naming was
# accurate -- a control satisfied by the DESCRIPTION of the thing it checks, which is the exact
# generalisation a round-4 reviewer drew from the round's other defects.
_ABSENCE_WORDS = ("absent", "does not exist", "not yet", "pending", "until ")


def false_excuses(here):
    """Excuses that claim a file is absent while it sits on disk."""
    bad = []
    for rel, why in EXCLUDED.items():
        if (here / rel).exists() and any(w in why.lower() for w in _ABSENCE_WORDS):
            bad.append("%s is excused as %r and EXISTS" % (rel, why[:60]))
    return bad


# ⛔ DIRECTORIES EXCUSED AS A CLASS, each with a reason. A per-file excuse for 180 files is a
# list nobody reads; a per-directory excuse is a DECISION, and it is written here where it can be
# argued with.
EXCLUDED_DIRS = {
    "review": "this builder's own output and every previous round's packet; shipping it would put "
              "a copy of the packet inside the packet",
    # ⛔ THE REASON THIS CARRIED WAS FALSE. It said "the half-built package the transactional
    # build renamed rather than deleted" -- and the transaction has always written `package.prev`,
    # never `package.incomplete`. Nothing in this tree creates this directory; the one on disk was
    # renamed by hand. So the excuse described an act that never happened, in the file whose job
    # is to make every omission a stated decision, and `false_excuses()` could not catch it
    # because it iterates `EXCLUDED` and never reached `EXCLUDED_DIRS`.
    #
    # ⚠️ `package.prev` IS DELIBERATELY NOT EXCUSED. A leftover one is the fingerprint of an
    # interrupted build and may hold the only complete package; having it block the packet is the
    # right failure mode, and a standing excuse would make it invisible.
    "package.incomplete": "a half-built package renamed BY HAND, kept as evidence. No code path "
                          "produces this name. Not shipped: a tree that looks like a finished "
                          "package inside a review archive is exactly that confusion",
    "runs": "measurement run directories. The ones a shipped measurement CITES are required "
            "individually below; the rest are raw runs no claim rests on",
}
# Directories shipped wholesale by the walk in `main()` rather than named file by file.
#
# ⛔ AND A SHIPPED TREE THAT IS EMPTY CONTRIBUTES NOTHING TO EITHER PROJECTION. `shipped_rels()`
# and `unclassified()` both walk `rglob` over what EXISTS, so a deleted directory is invisible to
# both: a round-8 reviewer removed `reference/` -- 23 files, the bundle this packet explicitly
# tells reviewers to use to audit the configuration-A figures -- and the build succeeded, writing
# an archive of 165 files with the covering note still citing it.
#
# ⚠️ IT IS LAST ROUND'S FINDING ONE LEVEL UP, AND IN THIS PROJECT'S OWN WORDS: *to a checker
# that only hashes, an unshipped file and a deleted one are the same thing.* To a checker that
# only walks, AN EMPTY TREE AND A TREE WITH NOTHING TO SAY ARE THE SAME THING. The instance was
# fixed; the class was not.
SHIPPED_TREES = ("package", "reference")
# ⚠️ OF THOSE, WHICH MUST EXIST. `reference/` is cited by this packet's own text as the bundle
# a reviewer audits the configuration-A figures against, so its absence is a defect. `package/` is
# a BUILD OUTPUT that cannot exist while the governing document is not in force -- so its absence
# is a STATE, and the packet has to say so out loud rather than print a 0 in a stats box beneath a
# live instruction to run `verify_package.py` in it.
REQUIRED_TREES = ("reference",)

# ⚠️ Repository configuration, excused as a class. These are dot-FILES, not dot-directories:
# the tooling-state rule is about directories and says so, so these needed a decision of their own
# rather than being swept up by a rule that was not about them.
# ⛔ `.gitignore` AND `.gitattributes` WERE EXCLUDED HERE AND COUNTED BY `withdrawn_claims.py`,
# together with three dot-prefixed files `unclassified()` never walked (`.github/` templates,
# `corpus/.gitignore`). Five files in the tree and not in the archive, all text, all scanned:
# the shipped record said 139 and a reviewer's extraction walked 134. They are small and
# harmless, so they SHIP, and the one file that must not ship is skipped by the scan instead.
EXCLUDED_GLOBS = {}



def shipped_rels(here):
    """Every relative path the zip will contain. One answer, used by the coverage check and the
    writer both -- because they disagreed, and the check was the one that was wrong."""
    out = {rel for rel, _why in SEND}
    # ⇒ RAW SHIPS BESIDE CLEAN. `corpus/MANIFEST.json` pins the ten CLEAN texts and records the
    # cleaning rule; without the inputs that rule is a description nobody can check. The whole-tree
    # walk is what surfaced that `corpus/raw/` had never been shipped or excused.
    for sub in ("clean", "raw"):
        out |= {"corpus/%s/%s" % (sub, f.name)
                for f in (here / "corpus" / sub).glob("*.txt")}
    for d in SHIPPED_TREES:
        out |= {f.relative_to(here).as_posix() for f in (here / d).rglob("*") if f.is_file()}
    return out


def unclassified(here):
    """Files a reviewer could reasonably expect, that nothing ships and nothing excuses.

    ⚠ THIS GLOBBED BESIDE THE BUILDER AND IN `corpus/` AND NOWHERE ELSE -- four suffixes in two
    named directories, doing the work of a walk. `runs/` was bolted on afterwards for one filename.

    ⛔⛔ AND THE COST WAS REAL. `exposure/exposure-2026-09-07.json` is PINNED BY v18 and was not
    shipped; from the extracted archive the first command the prompt tells a reviewer to run
    reported it as a BROKEN COMMITMENT. Nothing here could see it, because `exposure/` was not one
    of the two names. That is paper 2's round-6 `iterdir()` finding in the sibling nobody grepped
    for -- fixing instance N by naming another directory is how instance N+1 gets made.

    ⇒ IT WALKS THE TREE NOW, and what is not shipped is excused by FILE or by DIRECTORY CLASS,
    with the reason written down. A new directory is unclassified until somebody decides about it,
    which is the failure mode this should have.
    """
    named = shipped_rels(here) | set(EXCLUDED)
    seen = set()
    for f in here.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(here)
        parts = rel.parts[:-1]
        # tooling state is never study material -- `.git` and the caches. ⚠ A dot-prefixed
        # directory is NOT the class: `.github/` holds the two issue forms a reproducer files,
        # and skipping every dot-part here is how they went unshipped and uncounted for a round.
        if any(s in (".git", "__pycache__") for s in parts) or f.suffix in (".pyc",):
            continue
        if set(parts) & set(EXCLUDED_DIRS):
            # a run directory a shipped measurement CITES is required despite the class excuse
            if parts[:1] == ("runs",) and f.name == "run.json" and _cited_by_a_measurement(
                    here, parts[1] if len(parts) > 1 else ""):
                seen.add(rel.as_posix())
            continue
        if f.name in EXCLUDED_GLOBS:
            continue
        seen.add(rel.as_posix())
    return sorted(seen - named)


def _cited_by_a_measurement(here, run_name):
    """Does any shipped MEASUREMENT record name this run directory?

    ⚠️ PREFIX IS NOT IDENTITY, and this was a bare `in` test. `thr` matched because `thr-16`
    is cited; the empty string matched every measurement file. It over-requires, so it fails
    closed and nothing was wrong -- but it is the same defect fixed forty lines away for
    `doc.stem`, in the same sitting, one caught and one not. The sibling corollary: a fix is not
    finished until the other call sites have been read.

    ⇒ The run name must appear as a whole token -- bounded by a quote, a slash, whitespace or a
    string end -- not as a substring of a longer name.
    """
    if not run_name:
        return False
    pat = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(run_name) + r"(?![A-Za-z0-9_-])")
    for m in here.glob("MEASUREMENT-*.json"):
        try:
            if pat.search(m.read_text(encoding="utf-8")):
                return True
        except OSError:
            continue
    return False


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    missing = [rel for rel, _ in SEND if not (HERE / rel).exists()]
    if missing:
        raise SystemExit(chr(0x26D4) + " the packet promises files that do not exist: %s" % missing)

    m1 = json.loads((HERE / "MEASUREMENT-1.json").read_text(encoding="utf-8"))
    m2 = json.loads((HERE / "MEASUREMENT-2.json").read_text(encoding="utf-8"))
    run = json.loads((HERE / "runs" / "det-1" / "run.json").read_text(encoding="utf-8"))
    man = json.loads((HERE / "corpus" / "MANIFEST.json").read_text(encoding="utf-8"))

    # the thread sweep, read from the runs rather than remembered
    sweep = {}
    for n in (1, 2, 4, 8, 16):
        p = HERE / "runs" / ("thr-%d" % n) / "run.json"
        if p.exists():
            sweep[n] = json.loads(p.read_text(encoding="utf-8"))["weights_sha256"]
    if len(sweep) != 5:
        raise SystemExit(chr(0x26D4) + " the thread sweep is incomplete: %s" % sorted(sweep))

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(HERE),
                            capture_output=True, text=True).stdout.strip() or "unknown"
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=str(HERE),
                           capture_output=True, text=True).stdout.strip()

    OUT.mkdir(exist_ok=True)
    zp = OUT / "paper-b-review.zip"
    _dupes = sorted({r for r, _w in SEND if [x for x, _ in SEND].count(r) > 1})
    if _dupes:
        raise SystemExit(D + " SEND names the same file twice: %s. A duplicate zip entry is "
                         "written silently and a reader may extract either copy, so this is a "
                         "substitution vector, not a cosmetic slip." % _dupes)
    _missing = [rel for rel, _w in SEND if not (HERE / rel).exists()]
    if _missing:
        raise SystemExit(D + " SEND names %d file(s) that do not exist: %s" % (len(_missing),
                                                                              _missing))
    # ⛔ A DIRECTORY EXCUSE MUST DESCRIBE A DIRECTORY. An excuse for something that is not there
    # is an excuse nobody can argue with, and it outlives whatever made it true.
    # ⇒ ROUND 16: unless this tree is an EXTRACTION OF A PACKET. `review/REVIEW-COMMANDS.json`
    # is written into the archive only, never onto disk here, so its presence on disk says the
    # tree was unpacked from a packet -- and in that tree an excused directory is absent BECAUSE
    # this excuse removed it. An excuse whose subject it removed itself has not outlived it. The
    # round-15 reader's clean extraction was refused over `package.incomplete` for exactly this.
    _extraction = (HERE / "review" / "REVIEW-COMMANDS.json").is_file()
    _phantom = [d for d in EXCLUDED_DIRS if not (HERE / d).is_dir()]
    if _phantom and _extraction:
        print("  note  this tree is an extraction of a packet; %d excused director%s absent "
              "because the packet omitted %s: %s" % (len(_phantom), "y is" if len(_phantom) == 1
              else "ies are", "it" if len(_phantom) == 1 else "them", ", ".join(_phantom)))
        _phantom = []
    if _phantom:
        raise SystemExit(
            D + " %d directory excuse(s) name nothing on disk: %s. An excuse is a decision about "
            "something real; one that survives its subject is a sentence nobody can check."
            % (len(_phantom), ", ".join(_phantom)))

    # ⛔ A SHIPPED TREE MUST HAVE CONTENTS. See the note on SHIPPED_TREES: both projections walk
    # what exists, so deleting one of these wholesale is invisible to both and the covering note
    # goes on citing it.
    _hollow = [d for d in REQUIRED_TREES
               if not (HERE / d).is_dir() or not any(p.is_file() for p in (HERE / d).rglob("*"))]
    if _hollow:
        raise SystemExit(
            D + " %d declared tree(s) are absent or empty: %s. This packet's own text tells a "
            "reviewer to use them, and a walk over what exists cannot tell an empty tree from a "
            "tree with nothing to say." % (len(_hollow), ", ".join(_hollow)))

    _fe = false_excuses(HERE)
    if _fe:
        raise SystemExit(D + " an excuse claims a file is absent and the file is on disk:" + NL
                         + NL.join("      " + x for x in _fe) + NL
                         + "  A coverage check that verifies a file is NAMED and not that the "
                         + "naming is TRUE is satisfied by a description of the thing it checks.")
    _un = unclassified(HERE)
    if _un:
        raise SystemExit(D + " file(s) in neither SEND nor EXCLUDED: " + NL
                         + NL.join("      " + u for u in _un) + NL
                         + "  Ship each or excuse it by name. A review packet that omits work the "
                         + "round did is a packet the reviewer cannot judge the round from.")

    # ⛔ EVERY FILE THE GOVERNING PROTOCOL DOCUMENT PINS MUST BE IN THIS ARCHIVE, and the list
    # is READ from that document rather than kept beside it.
    #
    # WHY. `PROMPT-B` tells the reviewer `python prepare_anchor.py` and says START HERE. Run from
    # an extracted archive it reported `exposure/exposure-2026-09-07.json` as **absent**, because
    # the archive did not ship it -- so the first command a reviewer runs gave a WORSE answer than
    # the tree gives, and the difference read as a broken commitment rather than a missing file.
    # An unshipped file and a deleted one are indistinguishable to a checker that only hashes.
    #
    # ⚠️ AND NOTHING NOTICED, because `unclassified()` looked in this folder and in `corpus/`
    # and nowhere else -- a list of two directory names doing the work of a walk. That is the same
    # defect paper 2's builder had with `iterdir()` in round 6, in the sibling nobody grepped for.
    # This check does not depend on that one: it projects over what v18 COMMITS TO, which is the
    # property that actually matters for the command the prompt tells a reviewer to run first.
    import prepare_anchor as _PA          # safe to import: it no longer rebinds stdout on import
    _vs = _PA.versions()
    if not _vs:
        raise SystemExit(D + " no pre-registration document to read pins from")
    # ⛔ `max(_vs)` IS THE HIGHEST DOCUMENT PRESENT, NOT THE ONE GOVERNING THIS TREE. With v20
    # waiting it selected v20's three pins while v18 and v19 compose thirty, so this check could
    # pass on a packet missing twenty-seven committed files. See `prepare_anchor.governing_pins`.
    _current, _forced, _unreadable = _PA.governing_pins()
    _pinned = sorted(_current)
    if not _pinned:
        raise SystemExit(D + " no version in force pins anything this parser can read, so what "
                             "this archive must ship could not be determined")
    print("  ok   the governing pin set is composed over %d version(s) in force: %d file(s)"
          % (len(_forced), len(_pinned)))
    _shipped = shipped_rels(HERE) | set(EXCLUDED)
    _unshipped = [n for n in _pinned if n not in _shipped and (HERE / n).is_file()]
    if _unshipped:
        raise SystemExit(
            D + " the versions in force pin %d file(s) this archive does not ship and does not "
            "excuse: %s. From the "
            "extracted archive `prepare_anchor.py` reports each as ABSENT -- a broken commitment "
            "that is really a packaging omission, which is the one report a protocol tool must "
            "never make for the wrong reason." % (len(_unshipped), ", ".join(_unshipped)))

    # ⛔⛔ THE LETTER CLAIMED FIVE rc=0 AND THE TREE PRODUCED TWO. Round 12's covering note
    # typed `check_signature.py # rc=0` and `anchor_status.py # rc=0` beside a shipped v22
    # that is an UNSIGNED DRAFT -- so both were 2 and 1 by design -- and printed a verdict
    # block with `hygiene_failed: False` while a reviewer's extraction produced true. Two
    # rounds running, the letter reported a state the tree does not produce. A number about
    # the artifact has to be produced by the thing that produces the artifact.
    #
    # ⇒ THE BUILDER RUNS THE DOCUMENTED COMMANDS AND SHIPS WHAT THEY RETURNED, in
    # `REVIEW-COMMANDS.json` inside the archive; the prompt's `# rc=N` annotations are checked
    # against this file by `collect.py`, so a letter cannot claim an exit code the builder did
    # not see. The suite is not re-run here (it takes minutes); its verdict file is READ and
    # REQUIRED TO BE ABOUT THIS TREE -- `tree_digest` must equal the tree as it stands -- or
    # the build refuses, because a verdict about some other tree is not a verdict.
    _measured = {}
    for _cmd in ("check_commitments.py", "check_signature.py", "anchor_status.py",
                 "prepare_anchor.py"):
        _r = subprocess.run([sys.executable, "-X", "utf8", _cmd], cwd=str(HERE),
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        _measured[_cmd] = _r.returncode
        print("  measured  python %-26s rc=%d" % (_cmd, _r.returncode))
    _vf = HERE / "CONTROL-SUITE-VERDICT.json"
    if not _vf.is_file():
        raise SystemExit(D + " CONTROL-SUITE-VERDICT.json is absent: run `python test_controls.py` "
                         "first. The packet ships the suite's verdict as measured, never typed.")
    _verdict = json.loads(_vf.read_text(encoding="utf-8"))
    import test_controls as _TC
    _now = _TC.tree_digest()
    if _verdict.get("tree_digest") != _now:
        raise SystemExit(D + " CONTROL-SUITE-VERDICT.json is about tree %s and this tree is %s: "
                         "the suite has not run on what is being shipped. Run `python "
                         "test_controls.py` and build again." % (_verdict.get("tree_digest"), _now))
    _measured["test_controls.py"] = 0 if not (_verdict.get("attacks_passed_that_should_not_have")
                                              or _verdict.get("positive_control_failed")
                                              or _verdict.get("hygiene_failed")) else 1
    print("  measured  python %-26s rc=%d  (from its verdict file, tree %s)"
          % ("test_controls.py", _measured["test_controls.py"], _now))
    _cmds_doc = json.dumps({
        "_readme": "exit codes of the documented commands as the packet builder ran them, on the "
                   "tree the archive was built from. A covering letter may quote these and no "
                   "others; collect.py checks that it does.",
        "tree_digest": _now,
        "commands": _measured,
        "control_suite_verdict": {k: _verdict.get(k) for k in sorted(_verdict) if k != "nonce"},
    }, indent=1) + NL
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        # under review/ -- the directory every projection over this tree (the packet walk, the
        # withdrawn-claims scan, the tree digest) excludes by the same declaration -- so the file
        # can describe the tree without being counted as part of it. Round 14: at the root it
        # was the one text file a reviewer's extraction had that the record did not (140 vs 139).
        z.writestr("review/REVIEW-COMMANDS.json", _cmds_doc)
        for rel, _why in SEND:
            z.write(HERE / rel, rel)
        # ⛔ THE CORPUS TEXTS WERE MISSING FROM THIS ZIP. The packet told reviewers to run
        # `python reproduce_findings.py`, which calls train.py, which reads corpus/clean/*.txt --
        # and the zip shipped corpus/MANIFEST.json without the files it describes. The instruction
        # could not be followed. A reviewer had to copy them out of the embedded package by hand
        # before the advertised workflow would start.
        for sub in ("clean", "raw"):
            for f in sorted((HERE / "corpus" / sub).glob("*.txt")):
                z.write(f, "corpus/%s/%s" % (sub, f.name))
        for p in sorted((HERE / "package").rglob("*")):
            if p.is_file():
                z.write(p, str(p.relative_to(HERE)).replace(chr(92), "/"))
        # the reference bundle, so a reviewer can audit the configuration-A numbers rather than
        # only re-derive their own
        for f in sorted((HERE / "reference").rglob("*")):
            if f.is_file():
                z.write(f, str(f.relative_to(HERE)).replace(chr(92), "/"))
    # ⛔⛔ ROUND 14: THE BINDING WAS CHECKED ON THE SOURCE TREE AND CLAIMED FOR THE ARCHIVE. The
    # verdict's tree_digest was compared with `tree_digest()` over HERE -- tautologically equal --
    # and never with the tree a reviewer extracts. ⇒ The zip is extracted and the digest
    # recomputed THERE, by the same function; anything else is a claim about the wrong tree.
    import tempfile as _tf
    import shutil as _sh
    _x = pathlib.Path(_tf.mkdtemp(prefix="pb-extract-"))
    try:
        with zipfile.ZipFile(zp) as _z:
            _z.extractall(_x)
        _there = _TC.tree_digest(_x)
    finally:
        _sh.rmtree(_x, ignore_errors=True)
    if _there != _now:
        zp.unlink(missing_ok=True)
        raise SystemExit(D + " the archive extracts to tree %s and the verdict is about tree %s. The "
                         "archive has been DELETED: a verdict bound to a tree nobody receives binds "
                         "nothing." % (_there, _now))
    print("  ok   the extracted archive is tree %s, the tree the verdict is about" % _there)
    zsha = hashlib.sha256(zp.read_bytes()).hexdigest()

    L = []
    A = L.append
    # Computed once, and BOTH the instruction and the statistic read it. They disagreed because
    # one was typed and the other measured.
    _PKG_FILES = sum(1 for p in (HERE / "package").rglob("*") if p.is_file()) \
        if (HERE / "package").is_dir() else 0
    # ⛔ EVERY CLAIM IN THIS PACKET IS NOW LIFTED FROM PHASE-2-FINDINGS.md, NOT RETYPED.
    # The round-1 packet was circulated carrying "+37%", "step 8", "83%" and "numerically
    # indistinguishable" -- all four withdrawn in the findings document it claimed to summarise --
    # because the covering note was a hardcoded string and a patch that was supposed to update it
    # silently matched nothing and reported success. Both reviewers read the contradiction.
    #
    # So the note is EXTRACTED, and a cross-check below refuses to write a packet whose numbers do
    # not appear in the findings.
    _find = (HERE / "PHASE-2-FINDINGS.md").read_text(encoding="utf-8")
    _round = json.loads((HERE / "REVIEW-ROUNDS.json").read_text(encoding="utf-8"))
    _last = max(_round["rounds"], key=lambda r: r["round"])
    A("# Paper B (`reproduction`) — internal review packet, round %d" % (_last["round"] + 1))
    A("")
    A("*Every figure below is read from the measurement files, and every claim is lifted from "
      "`PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a "
      "figure it prints is absent from that document.*")
    A("")
    A("## ⇒ SEND THESE TWO")
    A("")
    A("```")
    # ⛔ THIS PRINTED len(SEND) + 1 -- 41 -- WHILE THE ZIP HELD 108 MEMBERS. The zip also
    # carries corpus/clean/, package/ and reference/ by projection, so a count taken from the
    # NAMED list was never the count of the artifact. A reader checking the packet against the
    # file it describes would have found it wrong on the first line of the first block.
    A("paper-b-review.zip     %d files" % len(zipfile.ZipFile(zp).namelist()))
    A("  sha256 %s" % zsha)
    A("this file")
    A("```")
    A("")
    A("Repository `provenance-laboratory/reproduction`, commit `%s`%s."
      % (commit, "  ⚠️ TREE DIRTY" if dirty else ""))
    A("")
    A("---")
    A("")
    A("## ★ THE COVERING NOTE — paste this verbatim")
    A("")
    # ⛔ A STRING IS ITERABLE, SO THIS RENDERED ONE BULLET PER CHARACTER. Round 13's record was
    # written with `changed` as a prose string where every earlier round used a list of bullets,
    # and the packet emitted three hundred single-letter bullets under a heading that says PASTE
    # THIS VERBATIM. A round-14 reviewer regenerated the packet and reproduced it. Python's
    # willingness to iterate a string is exactly the shape this project keeps recording: the
    # wrong type produced plausible-looking output instead of an error.
    #
    # ⇒ The shape is checked before it is rendered. A record that cannot be rendered is a refusal,
    # not four hundred lines of noise in the document a reviewer is told to trust verbatim.
    for _fld in ("summary", "deadline"):
        if not isinstance(_last.get(_fld), str):
            raise SystemExit(D + " round %d's %r must be a string, not %s."
                             % (_last["round"], _fld, type(_last.get(_fld)).__name__))
    if not isinstance(_last.get("changed"), list) or not _last["changed"]:
        raise SystemExit(
            D + " round %d's 'changed' must be a NON-EMPTY LIST of bullets, not %s. A string is "
            "iterable, so rendering it produces one bullet per character in the covering note a "
            "reviewer is told to paste verbatim."
            % (_last["round"], type(_last.get("changed")).__name__))
    A("> **This is round %d.** %s" % (_last["round"] + 1, _last["summary"]))
    A(">")
    for _line in _last["changed"]:
        if not isinstance(_line, str):
            raise SystemExit(D + " a 'changed' bullet is %s, not a string." % type(_line).__name__)
        A("> - %s" % _line)
    A(">")
    A("> ⚠️ **%s**" % _last["deadline"])
    A("")
    A("## ⭐ CHECK THE FINDINGS, NOT ONLY THE PACKAGING")
    A("")
    A("```")
    A("python reproduce_findings.py     up to five training runs, nothing timed")
    A("```")
    A("")
    # ⛔ "~2 MINUTES" WAS A CLAIM ABOUT ONE MACHINE, in a paper whose subject is that machines
    # differ. One round-13 reviewer measured 26 s (a single core, so all five thread requests
    # collapse to one run) and another overran 180 s on their stack -- an order of magnitude
    # across exactly the hardware axis this experiment is about. Quoting a single duration here
    # was the paper contradicting itself in its own instructions.
    A("**Runtime spans an order of magnitude, and that is the finding rather than a caveat.** "
      "Measured between 26 s and over 180 s on reviewers' machines: a single-core host collapses "
      "all five thread requests into one run, a many-core host executes five. The script prints "
      "progress per run so a long one is visibly working rather than apparently hung. Do not "
      "treat any duration here as a timing measurement -- **nothing in this experiment is timed**, "
      "and the cost figures come from `measure_cost.py` under its own quiet-machine precondition.")
    A("")
    A("It re-derives the thread partition and the divergence table **on YOUR stack**, from "
      "nothing but the corpus and `train.py`.")
    A("")
    A("⛔ **It does not adjudicate the findings, and an earlier version of this packet said "
      "it did.** The sentence read *if its numbers disagree with PHASE-2-FINDINGS.md, the "
      "findings are wrong* — which is false, because the script measures a DIFFERENT "
      "MACHINE. A reviewer whose stack produced one digest across all five thread counts got "
      "exactly that disagreement, and the script itself said correctly that this does not "
      "contradict configuration A while the packet said it did. Both could not be true.")
    A("")
    A("⇒ To audit the CONFIGURATION-A numbers rather than your own, use the reference "
      "bundle: `reference/` ships the arrays and `MEASUREMENT-5-7.json` the derived values, so "
      "the published figures can be recomputed from published bytes without training anything.")
    A("")
    A("```")
    # ⛔ A DEAD INSTRUCTION BESIDE A LIVE NUMBER. This line told a reviewer to run the package
    # while, fifty lines below, the packet correctly reported `package/ -- 0 files`. The number was
    # computed and the instruction was typed, and nothing connected them -- which is the inverse of
    # the failure this builder's docstring was written to prevent.
    if _PKG_FILES:
        A("python verify_package.py         the package run in a directory it has never seen")
    else:
        A("# python verify_package.py       THERE IS NO PACKAGE IN THIS ARCHIVE -- see below")
    A("```")
    A("")
    A("## What is measured, and by what")
    A("")
    A("```")
    A("m1  cost of pinning     ratio %.3f  95%% CI [%.3f, %.3f]  sign-test p=%.1e  %d pairs"
      % (m1["ratio_of_medians"], m1["bootstrap_95_ratio"][0], m1["bootstrap_95_ratio"][1],
         m1["sign_test_p"], m1["reps"]))
    A("      threads=1  median %.2f s      threads=%s median %.2f s"
      % (m1["median_a"], m1["threads_b"], m1["median_b"]))
    A("      BLOCKED alternation, paired, execution order kept; both arms PINNED.")
    A("      order effect: AB %.4f vs BA %.4f -- the design's own control, printed"
      % (m1["order_effect"]["AB_median_ratio"], m1["order_effect"]["BA_median_ratio"]))
    A("      ⚠ the p is a SIGN TEST, not the randomisation distribution of a")
    A("      balanced design, whose space is C(n, n/2) rather than 2^n")
    A("      -> report as: roughly +%d%%, CI [+%d%%, +%d%%]. NOT as a decimal percentage"
      % (round((m1["ratio_of_medians"] - 1) * 100),
         round((m1["bootstrap_95_ratio"][0] - 1) * 100),
         round((m1["bootstrap_95_ratio"][1] - 1) * 100)))
    A("m2  apparatus           %d bytes on %d of artifact (%.3f%%); %d if train.py and"
      % (m2["apparatus_bytes"], m2["artifact_bytes"], m2["percent_of_artifact"],
         m2["apparatus_excluding_arguable_bytes"]))
    A("      build_corpus.py are called artifact instead -- the boundary is arguable and")
    A("      measure_storage.py reports it both ways. Timestamp proofs: %d bytes"
      % m2["timestamp_proof_bytes"])
    A("      " + chr(0x26a0) + " the PERCENTAGE does not transfer: the apparatus is near-")
    A("      constant and this artifact is deliberately tiny")
    _n_dig = len(m1["distinct_digests"][m1["threads_a"]])
    A("m3  REPEATABILITY, same hw %s"
      % ("one digest across %d runs at threads=%s" % (m1["reps"], m1["threads_a"])
         if _n_dig == 1
         else chr(0x26D4) + " %d DISTINCT DIGESTS: not even repeatable" % _n_dig))
    A("      " + chr(0x26D4) + " NOT REPORTED AS BIT-IDENTITY. Section 6 makes that an")
    A("      invalidating condition without an independent re-run. The previous revision of")
    A("      the findings said measurement 3 -HOLDS-; that was a violation and is withdrawn.")
    # ⛔ THIS SAID "NOT MEASURED" IN A PACKET SHIPPING THE FINDINGS THAT SAY IT WAS.
    # Three typed statements about measurement 4's status survived the measurement being taken --
    # the dead-noun defect in the file whose first line promises every figure is measured at build
    # time. The status is read from MEASUREMENT-4.json now, so it cannot be stale here and current
    # one file away.
    _m4p = HERE / "MEASUREMENT-4.json"
    if _m4p.exists():
        _m4 = json.loads(_m4p.read_text(encoding="utf-8"))
        A("m4  bit-identity, diff hw  %s -- %s, bit-identical %s"
          % (_m4["verdict"], _m4["arms"]["B"]["cpu"][:34], _m4["bit_identical"]))
    else:
        A("m4  bit-identity, diff hw  NOT MEASURED -- needs a second machine")
    _md = json.loads((HERE / "MEASUREMENT-5-7.json").read_text(encoding="utf-8"))
    _m5 = _md["m5_threads_1_vs_16"]
    A("m5  divergence            step 0 in EVERY array (trace records step -1 as the initial")
    A("                           state, and it is identical). relative L2 %.4e, %.2f%% of %d"
      % (_m5["relative_l2"], _m5["percent_differing"], _m5["params_total"]))
    A("                           parameters differ between threads 1 and 16")
    A("m6  engineering hours     NOT MEASURABLE under this design, and reported as such.")
    A("                           The estimand never existed: nothing was made deterministic")
    A("m7  monotonicity         %s: %s per cent differing"
      % ("monotone" if _md["m7_monotone_in_thread_count"] else "NOT monotone",
         ", ".join("%.1f" % v for v in _md["m7_percent_differing_by_thread_count"].values())))
    A("      " + chr(0x26D4) + " AND NOT SEPARABLE FROM THE SEED. Varying only the seed moves the")
    A("      differing fraction by %.1f percentage points and the relative L2 by %.1fx, against a"
      % (_md["seed_spread_percent_points"], _md["seed_relative_l2_ratio"]))
    A("      thread-count spread of %.1f points. m7's SHAPE is a claim about one trajectory."
      % (max(_md["m7_percent_differing_by_thread_count"].values())
         - min(_md["m7_percent_differing_by_thread_count"].values())))
    A("```")
    A("")
    A("## The thread sweep, read from the runs")
    A("")
    A("```")
    for n in sorted(sweep):
        A("threads=%-3d  %s" % (n, sweep[n][:48]))
    A("```")
    A("")
    A("⭐ **`--unconstrained` produces the threads=16 digest byte for byte**, so 'unconstrained' is "
      "not a separate condition on this machine — it is 16 threads. An identification, not an "
      "inference.")
    A("")
    A("## The artifact under test")
    A("")
    A("```")
    A("corpus        %d clean bytes, %d texts, merkle %s"
      % (man["total_clean_bytes"], man["text_count"], man["merkle_root"][:32]))
    A("model         %d-byte context, d_emb %d, d_hid %d, %d steps, batch %d, %s"
      % (run["spec"]["context"], run["spec"]["d_emb"], run["spec"]["d_hid"],
         run["spec"]["steps"], run["spec"]["batch"], run["spec"]["dtype"]))
    A("weights       sha256 %s" % run["weights_sha256"])
    if not _PKG_FILES:
        A("")
        A(chr(0x26D4) + " **THERE IS NO REPRODUCER PACKAGE IN THIS ARCHIVE, AND THAT IS A STATE, "
          "NOT AN OMISSION.**")
        A("   `build_package.py` refuses while the governing protocol version is not in force, so "
          "no")
        A("   package has been built since v18 was written. Nothing in this archive can be "
          "verified with")
        A("   `verify_package.py`, and the reproduction instructions downstream of it describe a "
          "directory")
        A("   that does not exist yet. The blocking act is a human one and it is named in "
          "`prepare_anchor.py`.")
        A("")
    A("published as  package/ -- %d files; OUR WEIGHTS ARE NOT IN IT, only the digest"
      % len(list((HERE / "package").rglob("*"))))
    A("```")
    A("")
    A("## ⚠️ Known-weak, and a reviewer should push here")
    A("")
    A("- **n = 2 machines.** Intel and AMD, matched on OS, Python, numpy and the OpenBLAS "
      "build -- and BOTH SELECTED THE SAME OpenBLAS MICROKERNEL (Haswell, X86_V3). So "
      "measurement 4 shows two vendors running the SAME REDUCTION SHAPE agree, which is not "
      "vendor-independence. A machine selecting a different kernel is a different experiment "
      "and has not been run.")
    A("- **Measurement 1 was +37%% in the previous revision and is +%d%% now.** The "
      "design was at fault, not the machine: fixed order, an \"unconstrained\" arm "
      "that was not a condition, and arrays sorted separately before storage. Ask "
      "whether the repaired design has its own faults."
      % round((m1["ratio_of_medians"] - 1) * 100))
    A("- **The model is an MLP, not a transformer.** Defensible — the mechanism under test is BLAS "
      "reduction order and capability is explicitly out of scope — but a reviewer may reasonably "
      "argue the finding does not transfer to attention kernels or to CUDA, where atomics add a "
      "second source of the same phenomenon.")
    A("- **Measurement 4 is DESCRIPTIVE, not confirmatory.** Its admissibility conditions were "
      "strengthened AFTER its result was known, and it bound itself to no protocol digest. "
      "Neither is repairable retroactively. A confirmatory pair needs a fresh run on both "
      "machines under the ANCHORED successor, and has not happened -- and train.py's digest "
      "moved this round (22cbfeb7 -> f44a74f0) for two recording defects, so the existing pair "
      "was produced by a pipeline the current protocol does not pin. The trained weights are "
      "identical under both, verified by running both, so no result changes; the RECORD does.")
    A("- **Authority is still not EXTERNAL.** The manifest lives in the same directory as the "
      "thing it governs; what stops the substitution attack is the anchor and now the signature, "
      "not the location. A reviewer asked for CI or signed release metadata to select it. Push on "
      "whether an anchor plus a signature by a key WE distribute is enough.")
    A("- **⛔ THE `PENDING` BRANCH IS THIS ROUND'S NEW ESCAPE HATCH, and it exists because the "
      "obvious strict rule was unusable.** Destroying a higher version's proof is refused now, "
      "because falling back to an older document would enforce a SMALLER table. But a document "
      "that PARSES, commits to its own bytes and carries only a calendar attestation is allowed "
      "to sit above the authority unrefused — otherwise every build would fail for the hours "
      "between stamping a successor and its anchor, which is the state v8 is in as this goes out. "
      "**That is a convenience rule of exactly the shape the transitional allowance had, and the "
      "transitional allowance swallowed an attack last round.** Attack this one.")
    A("- **v8 was re-stamped several times while being drafted, and the rule licensing that is "
      "stated rather than derived.** §11 says authority attaches at ANCHORING, not at stamping, "
      "so a document that has never governed anything may be revised. Every superseded proof is "
      "retained under a `.superseded-` name and ships in this packet. Decide whether that is a "
      "principled line or a two-hour window in which anything can be quietly rewritten.")
    A("- **A signature says a KEY asserted these bytes, and the fingerprint you will check it "
      "against comes from us.** `check_signature.py --require` refuses a valid signature by any "
      "other key, and prints the fingerprint precisely because this tool cannot establish whose "
      "it is. Key distribution is outside the artifact, and the packet does not solve it.")
    A("- **`--publishing` now enforces v6 §7's last two conditions, and its first version "
      "accepted its own template's placeholder.** `report_to` reading `FILL IN: the URL a "
      "reproducer files at...` passed, because the check refused only \"\", None, TBD and ?; "
      "only the close date was caught, and only because a date must PARSE. Look for the same "
      "shape elsewhere: a gate that tests the SHAPE of a value rather than the claim it makes.")
    A("- **§2c's distribution subset is a new rule with a branch no live input has taken.** It "
      "declares which pinned files a reproducer package contains, and the test is an EQUALITY — "
      "absent must equal the complement — because a skip would make deletion the way to avoid a "
      "digest check. It cannot take effect until v8 anchors, so in THIS package "
      "`check_commitments.py` still refuses. The five rule cases in `test_controls.py` are "
      "exercised against the declaration rather than the authority, which is honest but is not "
      "the same as having run in anger.")
    A("- **Measurement 6 is reported NOT MEASURABLE.** Everything else is a digest or a "
      "timing a stranger can "
      "re-run. That page cannot be checked and says so.")
    # ⛔ THIS WAS LIVE TEXT ASSERTING THE WITHDRAWN INFERENCE, generated into every review packet
    # while v18 §1 said the opposite. My round-5 sweep reported that only historical documents
    # still carried §2c; it grepped for the phrasings it already knew and missed a generator.
    A("- **The independent reproduction does not exist**, and by section 2b we may not produce "
      "one. **v18 §1 withdrew the inference that silence is a result**: if nobody answers the "
      "call we report that nobody did and draw no conclusion from it. A reviewer should check "
      "that the paper holds to that everywhere, including in sentences that only imply it.")
    A("")
    A("## ⛔ What the reviewer should NOT accept without pushing")
    A("")
    A("- that a package running on the machine that built it is evidence of anything beyond "
      "completeness;")
    A("- that the unconstrained runs agreeing three times means unconstrained training is "
      "reproducible — they agreed because nothing was contending;")
    A("- that about +%d%% is *the* cost of determinism. It is the cost of pinning to one "
      "thread rather than requesting %s, on one configuration, at one size -- and which "
      "constraint actually buys identity is a question measurement 4 addresses only for the "
      "reduction shape both arms shared; see PHASE-2-FINDINGS section 10."
      % (round((m1["ratio_of_medians"] - 1) * 100), m1["threads_b"]))
    A("")

    # ⛔ THE CROSS-CHECK WAS DEAD TWICE OVER, AND IT IS WHY THE STALE PACKET SHIPPED.
    #
    #   1. its pattern contained literal BACKSPACE bytes (0x08) where word boundaries were
    #      intended -- a `\b` written into a non-raw string and then saved. It matched nothing,
    #      so the "absent figures" set was always empty and the guard never fired.
    #   2. the name `D` in its refusal was never assigned in this file, so even had it fired it
    #      would have raised NameError instead of reporting -- the same defect fixed in
    #      reproduce_findings.py one round earlier and reintroduced here.
    #
    # A reviewer ran the guard as written over the shipped packet and got the empty set, then ran
    # an ordinary pattern and got {'step 0', 'step 8', '8.0e-06', '4.9e-04'}. The guard's job was
    # to prevent exactly the shipment it permitted.
    #
    # ⚠ A REGEX OVER PROSE IS A PROXY, so this does two things instead of one: it checks the
    # figures, AND it proves at build time that it is capable of failing.
    import re as _re
    _txt = NL.join(L)

    def _figures(s):
        """Numbers that read as measurements: exponentials, percentages, and step counts."""
        pats = (r"(?<![\w.])\d+\.\d+e[-+]\d+(?![\w.])",
                r"(?<![\w.])\d{1,3}\.\d\s?%",
                r"(?<![\w])step -?\d+(?![\w])")
        out = set()
        for p in pats:
            out |= {m.group(0).strip() for m in _re.finditer(p, s)}
        return out

    # ⛔ THE NEGATIVE TEST. A guard nobody has watched fail is indistinguishable from a comment,
    # and this project has now shipped four of those. Inject a figure the findings cannot contain
    # and require the check to notice; if it does not, the guard is broken and the build stops
    # before it can bless anything.
    _canary = "step 99999"
    if _canary in _find or not (_figures(_txt + " " + _canary) - _figures(_txt)):
        raise SystemExit(D + " the packet's cross-check cannot detect an injected figure, so it "
                         "cannot detect a stale one either. Fix the check before building.")

    _absent = sorted(f for f in _figures(_txt)
                     if f not in _find and f.replace(" ", "") not in _find.replace(" ", ""))
    if _absent:
        raise SystemExit(
            D + " this packet prints figure(s) that do not appear in PHASE-2-FINDINGS.md: %s."
            % _absent + NL
            + "  That is how the round-1 and round-2 packets shipped withdrawn claims -- +37%, "
            + "step 8, 83% and 8.0e-06 -- while asserting every figure was measured." + NL
            + "  Either the findings are stale or the packet is. Do not resolve it here.")

    (OUT / "PAPER-B-REVIEW-PACKET.md").write_text(NL.join(L) + NL, encoding="utf-8", newline=NL)
    print("  wrote review/PAPER-B-REVIEW-PACKET.md")
    print("  wrote review/paper-b-review.zip  (%.2f MB, sha256 %s)"
          % (zp.stat().st_size / 1e6, zsha[:16]))
    if dirty:
        print("  " + chr(0x26A0) + " the tree is DIRTY, so the commit named in the packet does "
              "not describe what is in the zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())