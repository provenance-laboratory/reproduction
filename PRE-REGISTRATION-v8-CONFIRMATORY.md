# Pre-registration v8 — a proof that was never parsed, and a record whose clock ran backwards

⛔ **v3 governs, v4 amends measurement 4, and this version replaces v6 §2a, v6 §2b and v7 §3.**
Where this document is silent, v7, v6, v4 and v3 govern in that order.

## 1. What round 5 found

Two reviewers, working independently, built the same forty-byte file:

```
SHA256(document) || \x05\x88\x96\x0d\x73\xd7\x19\x01
```

⇒ **It was accepted as an OpenTimestamps proof.** It moved authority in `check_commitments.py`,
and with it a substituted `train.py` passed with exit 0. `ots info` on the same file says *"is not a
timestamp file"*. Every anchor check in this project decided whether a proof was a proof by
searching it for two byte strings — the document's digest, and the eight-byte Bitcoin attestation
tag — so a file containing exactly those two byte strings and nothing else was believed.

⚠️ **Round 4 found this attack and the repair did not fix it.** A round-4 reviewer passed 35 bytes
of junk containing the tag. The repair added *binding* — requiring the document's own digest to be
present — and never added *parsing*. So the next reviewer supplied 40 bytes containing both strings
and was believed again. **Two rounds, one defect, because the repair addressed the instance instead
of the class: a proof is a structure, and looking for bytes inside it is not reading it.**

## 2. ⛔ What is committed, by DIGEST — replacing v6 §2a, v6 §2b and v7 §3

### 2a. Experimental inputs

```
train.py                   f44a74f0dcd4e9588bd821b85cf9639188051332ee1c707ae675c8b48dec5b49
corpus/MANIFEST.json       fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py     2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json        7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30
```

⚠️ **`train.py` moves from `22cbfeb7` for two recording defects, and the weights do not change.**

- **`started_utc` was captured after training finished.** A reviewer measured it: shell before
  09:12:38, recorded *"started"* 09:12:42, shell after 09:12:42, wall clock 3.8s. The only field in
  the record that says *when* was wrong by the duration of the run, and its name asserted the
  opposite of what it held.
- **The package binding bound whichever package happened to exist.** In the source tree it recorded
  a stale package whose `train.py` was a different pipeline; inside an extracted package it looked
  in the wrong place and recorded nothing. It now locates the manifest, compares that manifest's
  own entry for `train.py` against the digest of the file executing, and **records a refusal rather
  than a digest** when they disagree. A package that does not contain the pipeline being run is not
  evidence about that run.

⇒ **The trained weights are `a4afb5c86dd88ae5ce7a475d448ee6bab18f6bc4e3c6c59721511f98f1c23d38`
under both `22cbfeb7` and `f44a74f0`, verified by running both.** No result in the paper changes.
What changed is that the record now says something true about when the run began.

### 2b. Instruments and gates

```
anchor_status.py           a98181d1e7229de6d8b136714c8c59f051df8d03f5849de0d4cb51d8000dec33
build_package.py           043a7044c579fdcac48781e7448ea7867b646ba651a828bc605ad2b959a0783f
check_commitments.py       1bf24d7dc245ababe69f7d3bec4a38a3ef0e5374bb11fa3e35b6db0a8a435f50
check_signature.py         4bf4cb00274891f7bf633e819bcbd144e8b9df56ac6c430b405fd748deb59614
corpus/verify_shipped.py   943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
measure_cost.py            4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py      d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_hardware.py        36dd832bd5cdbd4b97961fb356943686a54becaea020def6387298280d6cff94
measure_storage.py         1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
ots_verify.py              a2e06b83c25dc70aec9722605d4e2a6cf958528b14fede2b8aeffbc68a961368
reproduce_findings.py      78d570f5df51245e5d9a9b2ddeb75ef5e22cda283a06e64383ca383b80827bbf
seed_sensitivity.py        1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
test_controls.py           6116aeec9e675f2ae89ed851b423f58a6dea6b5e59ca22349b24a868e3b385af
verify_package.py          bf88fd51fe247bebcd6769645eeb570f6381983decdd5867a94c04a4a5a6c87d
```

⇒ **Fourteen, up from twelve.** Six unchanged from v7; `ots_verify.py` and `check_signature.py` are
new; four move for the repairs in §3–§5.

### 2c. ⛔ What the reproducer package contains

```
train.py
corpus/MANIFEST.json
corpus/build_corpus.py
corpus/sources.json
check_commitments.py
ots_verify.py
check_signature.py
test_controls.py
corpus/verify_shipped.py
```

⛔ **Since v6 pinned the instruments, the package has shipped a control that could not pass inside
the package.** v6 pins sixteen files; the reproducer's package deliberately contains nine of them,
because the measurement and build instruments are ours and are not part of what a stranger is asked
to run. So a reproducer following the documented instruction saw **nine `MISSING` lines and a
refusal, on an untampered package.**

⚠️ **It went unnoticed because every gate ran the checker against the SOURCE tree.** Nothing ever
ran it where a reproducer runs it — the same shape as the round-3 defect where controls were
described in prose instead of executed, one directory over.

⇒ **The rule is an equality, not a skip.** "Ignore files that are not there" would be the absence
defect again, in the checker whose own version is about absences, and deleting a file would become
a way to avoid its digest being checked. The absent set must be **exactly** the pinned set minus the
subset declared above: one file missing from the subset, or one absence outside the complement, and
the check refuses.

## 3. Proofs are parsed now

`ots_verify.py` walks the actual serialisation — magic header, version, the file-hash operation and
its digest, then the operation tree — and **evaluates** each operation rather than skipping over its
arguments, so the attestation's merkle root is computed from the document's own bytes and reported.
It fails closed on any byte it does not recognise.

⚠️ **An earlier draft of this module parsed the structure without evaluating it, and a byte flipped
inside an append argument still passed** — the shape was intact and the path merely led somewhere
else. That is the same defect as substring-instead-of-parse, one level in, and it was caught by
testing the module rather than by reading it.

The seven genuine proofs in this tree are accepted with their block heights (964534, 964535, 964549,
964761, 964762, 964775, 964785, 964789, 964812, 964815, 964848). These are refused:

| attack | why it is refused now |
|---|---|
| the 40-byte forgery above | no magic header — not a proof file at all |
| 35 bytes of junk containing the tag | no magic header |
| the document's digest alone | no magic header |
| a **real, valid, Bitcoin-anchored** proof over a *different* document | commits to other bytes |
| a real proof, truncated | runs off the end of the file |
| a real proof with bytes appended | trailing bytes after the proof ended |

⚠️ **What a pass still does not mean.** It does not contact a node or a calendar, so it does not
confirm that the named block exists or that its merkle root matches. It establishes that the file
*is* an OpenTimestamps proof, that it commits to *these* bytes, and that it carries a Bitcoin
attestation naming a height. Confirming the path against a chain is a network operation and stays in
the publication checklist.

## 4. ⛔ An anchor answers WHEN, never WHO

A reviewer stated the gap in one sentence: **stamping is free, public and unilateral.** Anyone with
write access to this directory can compose a successor document, stamp it, wait two hours, and hold
a proof indistinguishable from ours. Until now, timestamping was the whole of these documents'
authenticity story.

```
the anchor      these bytes existed no later than Bitcoin block N       WHEN
the signature   this key asserts these bytes                            WHO
together        this key asserted these bytes before block N            WHEN + WHO
```

⇒ `check_signature.py` verifies a detached OpenPGP signature over every protocol document present,
**derived by globbing rather than from a list** — a hand-kept list would go stale exactly when a new
version was written, which is when the check matters. It parses gpg's machine-readable status
output, not its prose: *"Good signature"* is printed for untrusted keys too, and the exit code is 0
for an expired one.

⚠️ **A signature alone would be weaker than the pair, which is why it does not replace the anchor.**
Signing is as unilateral as stamping and can be backdated freely; it is the anchor that fixes the
signature in time. And a valid signature says a *key* asserted these bytes — whether that key is
whose you think is a question about key distribution that this tool cannot answer, so it prints the
fingerprint for checking against a channel that does not come from us.

**Signatures gate publication, not review.** Unsigned documents exit 2, which `--publishing` treats
as fatal and a review build does not.

## 5. Absence is not agreement — at the premise this time

Round 4 found six pairs granted `ISOLATING` that should not have been, all of the form *a control
satisfied by the ABSENCE of the thing it checks*. Round 5 found five more, and **where they landed
is the point**:

| attack | verdict before |
|---|---|
| both arms' `spec` absent | `MATCHED-STACK CROSS-MACHINE` |
| both arms' `corpus_merkle_root` absent | `MATCHED-STACK CROSS-MACHINE` |
| both arms' `threads_requested` absent | `MATCHED-STACK CROSS-MACHINE` |
| both arms' `python` absent | `MATCHED-STACK CROSS-MACHINE` |
| one arm's CPU absent | crashed on a `None` slice |

⛔ **Round 4's absences were repaired one at a time inside `conditions()`. These four are read by
the same-input gate ABOVE it** — the gate deciding whether the comparison is a comparison at all —
where `a.get(k) != b.get(k)` is *false* when neither arm states `k`. **Deleting the field that says
the two runs asked the same question made the pair look more comparable, not less, and returned the
strongest verdict the tool can issue.** Repairing instance N where it appears is how instance N+1
gets made.

⚠️ `python` failed a second way: `str(None).split(".")` is `["None"]`, so two absent Pythons
compared equal *and truthy* as the string `"None"`. A guard that tests truthiness after stringifying
tests the truthiness of the word None.

⇒ Every comparison in `measure_hardware.py` now routes through one `_agree()` helper for which
absence — on either side, in either direction, including `""`, `"None"` and `"?"` — is never
agreement. **It does not project over the record's keys**, so a field nobody thought to guard is
still unguarded; the defence is only that adding an unguarded comparison now takes deliberate effort
instead of being the default.

⚠️ **Condition 0 is renamed from *"the two arms are DIFFERENT machines"* to *"the arms report
DIFFERENT CPU identities"*,** because comparing two self-reported strings is not observing two
machines: two hosts of one model report the same string, and a copied record reports its source's.

## 6. `--publishing` enforces what v6 §7 promised

v6 §7 listed two conditions as *"not yet enforced in code… so the gap is a commitment rather than a
discovery"*. ⛔ **A declared gap is still a gap**; the disclosure converted a defect into a
disclosure and left the build publishing a target nobody had committed to. Both are enforced now:

- publishing `EXPECTED.json` requires an **anchored** protocol document to govern
- publishing requires a `REGISTRATION.json` recording a **reporting address** and an **open close
  date**, since v3 §7 promises everything filed by the close date is reported — unfalsifiable
  without a date, unreachable without an address

⛔ **And `--publishing` did not travel.** `build_package.py` invoked `check_commitments.py` with no
arguments even on a publishing run, so the checker's strict path — the one refusing to publish while
a newer version is stamped and unanchored — existed, was tested, and was unreachable from the only
tool that calls it.

## 7. ⛔ Two more lists that should not have been lists — and v7 paid for one of them

`anchor_status.py` held the protocol documents that must be anchored as a hand-kept list.
`build_package.py` held every protocol document and its proof the same way.

⚠️ **v7 recorded editing one of those lists as a cost of v6's rule.** Its §3 says `anchor_status.py`
and `build_package.py` moved *"only because they must NAME this document — a version cannot be
required or shipped by tools that do not know it exists"*. That sentence is the defect stated as
though it were a law of nature. **A version cannot be required by tools that do not know it exists
only if the tools are told rather than allowed to look.**

⇒ This is instance **thirteen** of the same shape, and the notable part is where it was found: v7
existed *because* of an enumeration defect in `test_controls.py`, and paid for it by editing two
enumerations instead of removing them. **Fixing instance N by enumerating is how instance N+1 gets
made.** Both now project over `PRE-REGISTRATION*.md` on disk.

⚠️ **The old comment had a real argument, and it is kept.** It read: *"EXPLICIT, because 'whatever
is on disk' is how a missing governing document passed."* That is true, and globbing alone would
reintroduce it — so the projections **fail closed**: a document present without a proof is an error
that stops the build, not an omission, and authority is still selected by
`check_commitments.governing()` rather than by either list.

## 8. A status string got richer and a comparison silently stopped matching

`check()` in `anchor_status.py` was changed to report real block heights, so it began returning
`"ANCHORED [964761, 964762]"` where it had returned `"ANCHORED"`. Its caller still read
`ok = st == "ANCHORED"`.

⇒ **Nine anchored documents were reported as failures**, in the same edit that made the tool more
informative. It failed **closed**, which is the only reason it was caught within a minute — and the
obvious quick fix, `"ANCHORED" in st`, would have failed **open** and matched `"NOT ANCHORED"` too.
The verdict is a separate boolean now, so what is printed cannot move what is decided.

## 9. ⛔ Destroying a proof made the checker check LESS, and pass

Once `ots_verify.py` was refusing forged proofs, the control suite found the attack **behind** the
one it was written for. Forging v6's proof does not promote anything — the parser refuses it
correctly and v6 simply drops out of the candidate set. **Authority then falls back to v5.**

```
v6 pins 16 files          forge v6's proof          v5 pins 4 files
                    ─────────────────────────>      all 4 still match
                                                    exit 0
```

⇒ **The attack does not defeat the proof check. It defeats the SELECTION RULE**, by removing the
strongest candidate so that a weaker table governs. A smaller table is not a smaller authority; it
is a different one. Three variants — forging, truncating, and appending to the governing proof —
all passed this way, and only the *deletion* variant was caught, by an unrelated path.

⚠️ **The fix cannot simply refuse every unanchored document above the authority**, or the project
stops functioning: for the hours between stamping a successor and its anchor, a legitimately pending
document sits above the version in force — which is the state this very document is in as it is
written. So `anchored()` now returns a **state**, and the rule distinguishes them:

| state above the authority | meaning | verdict |
|---|---|---|
| `PENDING` | parses, commits to these bytes, waiting on Bitcoin | allowed — this is the normal transition |
| `TAMPERED` | not a proof, or over other bytes | ⛔ refused: someone removed the table that would have governed |
| `MISSING` | no proof at all | ⛔ refused, same reason |

⚠️ **`PENDING` is a value, not a phrase matched in the reason text.** Deciding this by searching the
explanation for the word "pending" would be the substring defect for the third time in one document.

## 10. Instance fourteen, found by trying to use the convention it hard-coded

`anchor_status.py` recognised retired proofs by a list of the **two suffixes that happened to
exist**. Retiring a proof under any new name would have made it an unrecognised extra — reported as
clutter rather than as the record it is.

⇒ Switching it to the documented pattern (`.superseded-` followed by something that says what it
binds) immediately surfaced **six retired proofs already in this tree that the list did not know
about**, including `PRE-REGISTRATION-v6-CONFIRMATORY.md.ots.superseded-pre-transitional-fix`. The
enumeration was not a latent risk; it had already been wrong for some time, silently.

## 11. ⚠️ This document was re-stamped while it was being drafted, before it anchored

Sections 9 and 10 were written **after** v8 was first stamped and signed, because the control suite
found §9's attack minutes later, and §10 was found while retiring the proof for §9. Every superseded
proof is retained beside this file under a `.superseded-` name recording what it binds:

```
python anchor_status.py        lists them, and they are in the package
```

⇒ Each binds an earlier draft and **none of them binds this file** — that failure to bind is the
fact they exist to record. The count is deliberately not written here, because a number typed into
a document is a claim that goes stale the next time; the directory is the record.

⚠️ **State the rule, because the alternative reading is that stamped documents can be quietly
edited.** Authority attaches at **anchoring**, not at stamping. Before a document anchors it has
never governed anything, and revising it is drafting; after it anchors, a change costs a new
version, as v7 records paying. What makes this safe is not the timing but that **the superseded
proof stays in the tree under a name that says why** — the same convention already applied to v2,
v3, v4 and v6 in this directory, which is how §10's six were found.

## 12. The control suite

**11 attacks → 25**, five of them against the proofs themselves,, all refused, with both positive controls still passing. The suite is in the
package and in the publication gate.

## 13. What this version does NOT do

⚠️ **The measurement-4 pair remains DESCRIPTIVE under v6 §6, and this version does not promote it.**
The existing pair was produced by `22cbfeb7`. A confirmatory pair requires a fresh run on both
machines under this document once it is anchored.

⚠️ **It does not claim the parser is a chain check**, or that a signature establishes identity, or
that `_agree` closes the absence class. Each of those would be the kind of overclaim this version
exists to remove.

## 14. What would invalidate this version

Everything in v3 §6, v4 §3 and v6 §7, with §2a, §2b and the two formerly unenforced conditions
replaced by §2 and §6 above, plus:

- accepting a timestamp proof without parsing it
- publishing a protocol document that carries no valid signature by the committed key
- reporting a cross-machine claim from a pair whose same-input fields are absent rather than equal
- any check that decides a verdict by comparing a human-readable status string
- any tool that requires a hand-kept list of protocol documents rather than discovering them
- selecting authority from a lower version while a higher one's proof is destroyed rather than pending
- a distribution whose absent files are not exactly the complement of §2c

⚠️ **Three protocol versions in four days is the cost of committing instruments, and it is being
reported rather than smoothed over.** v6 said that if the rule ever became an excuse for not
repairing a checker it had failed and should be reported as failing. It has not become that yet —
but the honest reading of v7 and v8 is that the repairs are arriving faster than the anchors, and
the defence is that each version has to justify itself in prose a reviewer reads.

---

*Replaces: v6 §2a, v6 §2b, v7 §3 · Alongside: [`v3`](PRE-REGISTRATION-v3-CONFIRMATORY.md),
[`v4`](PRE-REGISTRATION-v4-CONFIRMATORY.md), [`v6`](PRE-REGISTRATION-v6-CONFIRMATORY.md),
[`v7`](PRE-REGISTRATION-v7-CONFIRMATORY.md) · Enforced by
[`check_commitments.py`](check_commitments.py), [`ots_verify.py`](ots_verify.py),
[`check_signature.py`](check_signature.py) and [`test_controls.py`](test_controls.py)*
