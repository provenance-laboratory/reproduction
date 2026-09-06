# Publishing the package — the decisions that must be made in the act

⛔ **Publishing is not a build step.** Section 2c of the pre-registration fixes the reproduction
window's close date *at the moment of publication*, and section 2b binds us from that moment
onward. `build_package.py` therefore stops short of publishing on purpose: everything below is a
decision with a consequence, and none of it should be discovered afterwards.

---

## 1. Two values that do not exist yet, and cannot be defaulted

```
THE ADDRESS      REPRODUCTION-CALL.md says reports go to "the address published with these
                 artifacts". That address has to be a real, open, public place before the
                 sentence is true. A repository issue tracker, with the template already in
                 .github/ISSUE_TEMPLATE/

THE WINDOW       its close date. Section 2c says the null outcome is a RESULT, and a result
                 needs a boundary decided in advance or it becomes "we waited until we got
                 tired". Pick it before publishing, state it in the call, do not move it
```

⚠️ **Moving the close date afterwards would destroy the null result.** If nobody reproduces the
artifact and the window is then extended, the silence stops being a measurement and becomes a
schedule. The date is cheap to choose now and impossible to choose honestly later.

## ✅ BOTH VALUES DECIDED, 7 September 2026 — before publication, as required

```
THE ADDRESS   github.com/provenance-laboratory/reproduction/issues
              commitment.yml            a one-line commitment, filed BEFORE downloading
              reproduction-report.yml   the full report, no field required

THE WINDOW    closes 7 DECEMBER 2026
```

Both are now written into `REPRODUCTION-CALL.md`, which ships **inside** the package — so
`_ots_stamp.py package/SHA256SUMS` in §2 timestamps the close date along with everything else, and
the date is anchored rather than merely asserted.

⚠️ **90 days was chosen against the temptation to pick 11.** A short window costs nothing when
somebody reproduces the artifact quickly — you report the success when it arrives and the date never
mattered. It costs everything in the only outcome that cannot be repaired: silence inside a window
so short that the silence is a fact about the window. ⇒ **The asymmetry is the whole argument, and
there is no case in which the shorter date was better.**

⛔ **The commitment template did not exist until today**, while the report template did. The
protocol's most distinctive instrument — commit before you see the target — had no intake form, so
commitments would have arrived as free text and the count the paper reports would have been a
judgement call. *The mechanism a study is built around is the one most worth checking has a door.*

## 2. Before the bytes leave

```
python check_commitments.py   FIRST. Do the files the protocol pins by digest still hash to
                              those digests? If not, the pre-registration is VOID and nothing
                              below is worth doing
python anchor_status.py       is every REQUIRED proof present, binding its current bytes, and
                              carrying a Bitcoin attestation? A calendar receipt is not an anchor
python build_package.py       assemble. It re-runs check_commitments and refuses if it fails
python verify_package.py      run it as a stranger: sums, no absolute paths, digest matches
python ../../_ots_stamp.py package/SHA256SUMS
                              timestamp the package as published. NOT the same as the corpus
                              proof, which commits the INPUTS; this commits what was OFFERED
```

⛔ **The first two lines are new, and their absence is why they are there.** This checklist
described the act of publishing without running either control that decides whether publishing is
legitimate. `train.py` sat with a digest that did not match its commitment for a day while the
package rebuilt, `verify_package.py` passed, and `SHA256SUMS` was regenerated over the changed
bytes — a checksum derived from what it polices cannot notice a substitution. A checklist that does
not run its own gates is the same object as a pre-registration nothing enforces.

⚠ **`anchor_status.py` requires every protocol document PRESENT ON DISK, plus the corpus manifest.**
It discovers them by projection, so a new version is required the moment it exists and there is no
list to remember to update. A document that exists without a proof is a **failure**, not an
omission, and a governing version missing from the disk entirely is caught by
`check_commitments.governing()`, which selects authority rather than trusting any list.

⛔ **This paragraph used to say the opposite** — that the tool "covers v1 through v5" and that
adding a version "means adding it to that list". The code was repaired as instance thirteen of the
enumeration defect and the prose was not, so the checklist went on instructing a reader to hand-keep
a list the tool no longer has. **A stale instruction to enumerate is how instance N+1 gets made**,
and it survived here precisely because prose is not executed.

⚠️ **Stamp last, and only once the package is final.** A proof over bytes that then change is not
wrong, it is irrelevant — and an irrelevant proof sitting beside a real one is worse than none,
because a reader has to work out which is which. Upgrade it later with `_ots_upgrade.py` once a
Bitcoin block confirms it.

## 3. What must NOT go in

```
our weights.npz          only the digest, in EXPECTED.json. A reproducer holding our file can
                         compare it with itself and never know
any private key          nothing here is signed with the release key; if that changes, the key
                         lives in the cold backup and never in the tree
a named recipient        the call is open. Section 2b: no party approached in a way that is not
                         equally available to everyone
```

## 4. From the moment it is public, two rules bind us

⛔ **We do not assist.** If someone gets stuck, the report saying so is the data. Any help given is
logged and reported, and a run that received help is reported separately from runs that did not.
**This costs us reproductions and is meant to.**

⛔ **We do not characterise anyone's independence.** The paper reports what was filed and at what
public address. A reader opens the thread and judges. Asserting independence on a reporter's behalf
is asserting the thing the reader should be checking.

## 5. What to record on publication day

```
the exact URL of the call and of the report template
the close date, as stated publicly
the package digest and the .ots proof
the commit the package was built from
```

That block goes into the paper. **Silence after it is a finding; silence before it is nothing.**
