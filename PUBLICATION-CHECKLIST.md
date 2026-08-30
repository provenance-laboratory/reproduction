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

⚠ **`anchor_status.py` covers v1 through v5 and the corpus manifest.** Adding a protocol version
means adding it to that list; that is deliberate, and it is the reason a missing governing document
fails loudly instead of passing as an empty success.

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
