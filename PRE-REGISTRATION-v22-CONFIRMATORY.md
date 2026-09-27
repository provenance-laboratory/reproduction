# Pre-registration v22 — confirming v21, the three doors v21 closed, and round 13

**Status: DRAFT. Unsigned, unstamped, and it governs nothing.** It is written down now
because v21 going in force made three separate things impossible at the same moment, and all
three have the same answer.

## 1. ⛔ Why this version exists

v21 was signed on 19 September 2026 and its proof landed in Bitcoin blocks **967728** and
**967736**. That is the outcome the protocol wants, and it immediately closed three doors:

1. **v21 cannot confirm itself.** `confirmed()` requires a committed fact from a version
   *strictly newer* than the document — the repair round 12 made after a reviewer showed the
   ordering lived in the prose and not in the code. So v21 is ANCHORED and PROVISIONAL, and
   only a later version's §2d can make it CONFIRMED. **§2d below is that.**
2. **Every tool that needs repair is pinned by v21**, and `writable()` refuses a signed
   document. That is round 12's other repair working: before it, deleting a `.asc` reopened a
   stamped document to rewriting. The honest route is a new version, and this is it.
3. **`test_controls.py` mutates a DRAFT** and there was none. It did not quietly skip; it
   raised *"no version whose declarations are checked carries a pin row … this attack tests
   nothing either way"* and took the suite down. A control that cannot run must say so, and
   it did.

⚠️ **None of these is a defect.** Each is a gate holding. They are recorded together because
a reader who meets them one at a time will think something is broken.

4. **Round 14 then found, in the round-13 repairs, an authority rule that did not require a
   signature, a verifier that refused the protocol's own signing subkey, a proof filter that was
   still a filename test, and a verdict bound to the wrong tree (§2l–§2o); the round-14 read then
   asked that the key file be pinned by the governing version (§2p), and the round-15 read that
   every inherited pin be restated by it (§2q). Round 13 had
   demonstrated three bypasses and two weaker seams against v21's tools**, all
   at the boundary between *cryptographically valid* and *valid for this protocol's state*:
   a valid signature by the wrong key granted the signed-successor exemption; a proof renamed
   under this study's own `.superseded-` convention reopened a stamped document to rewriting;
   the `distribution-subset` reader read a sentinel a renderer would not, and missed one it
   would; the signature cache could be fooled by a same-size byte flip in one process; and the
   committed-fact map applied none of `governing()`'s acceptance checks. §2g–§2k record each,
   and this version commits the repaired tools.

5. **Rounds 16 and 17 then read this draft itself.** On 24 September a cold reader found a
   READY gate that accepted a forged restatement, two parsers composing two different
   histories, a third proof filter still deciding by filename, and a cause printer naming the
   wrong cause. On 25 September a second reader found the repair of that third filter taking
   the FIRST proof-shaped sibling it met — one planted file demoted the governing version
   with no refusal — and six sentences in this document that were false or stale against the
   tree. **§2r records both reads, and this version commits the tools they moved.**

## 2. ⛔ What was wrong, and is repaired under this version

Eighteen defects in tools v21 (and earlier versions in force) pin — eleven in §2e–§2o and seven
more in §2r — two defects in this draft's own text, which §2r also records (§3b's subset
declaration, and six sentences that were false or stale against the tree), and two restatements
(§2p, §2q). **Each was stated in this draft
before it was repaired**, because a draft is where a change is proposed and a signature is where
it is committed. §2e and §2f were written on 19 September; §2g–§2k on 20 September from the
round-13 review; §2l–§2o on 23 September from the round-14 review of the round-13 repairs; §2p on 24 September
from the round-14 read; §2q on 24 September from the round-15 read; §2r on 24 September
from the round-16 read, and extended on 25 September by the round-17 read.

### 2e. ⛔ `prepare_anchor.py` names a cause that is not the cause

With v21 signed, stamped and anchored, the tool prints:

```
⚠ v21 is NOT in force: its proof carries no Bitcoin attestation yet -- a calendar has
  receipted it and no block has carried it. Run `python ../../_ots_upgrade.py` once a block has.
```

**The proof carries two Bitcoin attestations and both blocks are pinned.** The real reason is
the one this document exists to fix: nothing newer commits its heights. `_why` was rewritten in
round 12 to report the three signature states, and its final branch still assumes the only
remaining reason is a missing attestation — while the same round's `confirmed()` repair created
a fourth. **Two changes to one file in one round that needed to agree and did not.** The tool
tells the operator a false cause and prescribes a remedy that does nothing, which is the
failure this project has named before.

**Repaired under this version:** `_why` has the fourth branch — *anchored, and PROVISIONAL: no
committed anchor-fact table names that block yet; nothing to run here* — and a round-13
reviewer confirmed the false cause fired exactly as described before the repair.

### 2f. ⛔ `pin_anchors.py` declares a timeout that does not bound the request

`_HTTP_TIMEOUT = 15`. Measured against the three sources while pinning v21's blocks:

```
blockstream        0.9s  HTTP 200
mempool          140.1s  urlopen error timed out
blockchain.info    2.5s  HTTP 200
```

A request asked to stop at 15 seconds returned at 140. With three tries and backoff that is
roughly seven minutes per block spent on one unreachable source, and the run rebuilds the whole
file or nothing, so pinning **two** new blocks cost a re-fetch of **forty-one** over five hours.
The redundancy worked — `MIN_AGREE=2` and `MIN_FAMILIES=2` were satisfied without the dead
source — so this is a cost defect, not a correctness one. **The number says 15 and the
behaviour is 140, and a declared bound that does not bind is the kind of claim this tree exists
to refuse.**

**Repaired under this version, and not by retiming.** A round-13 reviewer named the disease:
pin and verify were one whole-file act, so adding two blocks re-fetched forty-one. The tool now
has two acts and refuses to run with neither flag: `--add` fetches and appends only the blocks
our proofs name that are not yet pinned, under the same two-operator, two-family agreement rule
as everything else; `--verify` re-fetches every pin and is the act anything trusts. The timeout
is unchanged — the platform did not honour it, and a smaller number would not change that.

### 2g. ⛔ `signed()` accepted a valid signature by the wrong key

`check_signature.verify()` answered *does some key gpg knows make a valid signature*, and
`prepare_anchor.signature_state()` read that as *does the protocol's key stand behind this*.
The fingerprint comparison lived only in `check_signature.py --require`, in `main()`. A reviewer
generated a second key, imported it beside `PUBKEY.asc`, signed this draft with it, and got
`signature_state -> ok` — the signed-successor exemption — while `--require` rejected the same
file. Two definitions of *signed* in one tree, one level up from round 12's empty-file finding:
not *is there a signature* but *whose*.

**Repaired:** `ok` means signed by the primary key in `PUBKEY.asc` — the file this tree pins —
inside `verify()` itself, so every caller gets one answer; any other valid signature is `BAD
(WRONG KEY)`. The required fingerprint is read from the key file, never typed. A control signs
the draft with a throwaway key in a sandbox keyring holding both keys, and must be refused by
name.

### 2h. ⛔ `writable()` read a filename where it promised *nothing has ever committed these bytes*

`stamped()` was `<doc>.ots` exists. A reviewer took v20, deleted the `.asc`, renamed the proof
to `v20.md.ots.superseded-attack` — this study's own convention for retired proofs — edited a
tool and ran `--repin`: `signed=absent stamped=False writable=True`, three rows re-pinned, exit
0. The evidence was not destroyed; it sat in the directory under a historical suffix.

**Repaired:** `stamped()` is projected over every proof-shaped file beside the document, whatever
it is called: a file whose OpenTimestamps header commits to `sha256(doc)` is a commitment to
these bytes, current or superseded. The header parse is `ots_verify.commits`, the tree's one
proof reader. Two controls now cover *delete the signature* and *delete it and rename the
proof*, both against the highest version that really carries a proof over its own bytes
(the old control targeted the draft and fabricated a sibling's proof beside it, which tested
presence of a file and not the case that matters).

### 2i. ⛔ the `distribution-subset` reader was a regex over a language that is not regular

Two reviewers, two directions. A sentinel fence nested inside a four-backtick fence is literal
text to a CommonMark renderer and was a declaration to the regex. A sentinel indented two
spaces — natural under a list item — is a fence to the renderer and was nothing to the regex,
which then **fell through to the shape rule it had replaced** and returned an ordinary code
example as the declared subset. Author and tool held different subsets of one anchored
document. And on the live tree the sentinel was used by nothing: v21 declares no subset, and
v18's block predates the sentinel.

**Repaired:** the reader is a fence scanner that walks the document as CommonMark does — up to
three spaces of indent, backtick or tilde fences, a closing fence of the same character at
least as long, no fence opening inside content. The shape fallback is deleted: a document
declares a subset with the sentinel or declares none. A near miss — the sentinel on a
fence-shaped line the scanner did not open: nested, blockquoted, indented four spaces, trailing
text in the info string — is a **refusal**, never a silent demotion. This version carries the
sentinel form (§3), so the branch that runs is the branch the controls exercise.

### 2j. ⚠️ the signature cache was keyed on mtime and size

A byte flipped inside the armoured body, same length, mtime put back, in the same process after
`ok` was cached: `ok`. Narrow — one process, one caller — and precisely the gap the cache's own
comment claimed not to have. **Repaired:** the key is the SHA-256 of both files' bytes, which is
what *memoised on the bytes* means; a control performs the flip.

### 2k. ⚠️ `_committed_heights` applied none of `governing()`'s acceptance checks

It read anchor facts off any signed and anchored version, with none of the RELABELLED /
UNVERSIONED / NO-TABLE rules the authority rule applies. The signature requirement of §2g is
what stood between that and a forgery, and one lock that is one keyring is one lock.
**Repaired:** only documents `governing()` accepts may supply committed facts; a tree
`governing()` refuses commits nothing.

### 2l. ⛔ `governing()` selected anchored documents and never asked who signed them

A round-14 reviewer created a `PRE-REGISTRATION-v23-CONFIRMATORY.md` with no signature and no
proof, made only the selector's `anchored()` predicate answer true, and got `highest selected:
(23, ...)`. `in_force()` is `signed() and confirmed()`; the code that composes commitment
authority applied neither. Stamping is free — a calendar receipt and, in hours, a Bitcoin
attestation can be had over any bytes — so an anchored unsigned successor is a draft with a
timestamp, and the authority rule was letting a timestamp stand in for a signature. **One
predicate answered *anchored* and another answered *in force*, and they were not the same
predicate.**

**Repaired:** a version is eligible to govern only if `check_signature.verify` — the verifier
§2g made answer *whose* — says the protocol's key stands behind it; an anchored document it does
not is rejected by name as UNSIGNED, and above the selected authority it blocks the tree exactly
as a stripped signature (MISSING) does. A control reproduces the reviewer's setup in process.

### 2m. ⛔ a signing subkey of the protocol's key read as WRONG KEY

§2g compared the fingerprint gpg's `VALIDSIG` names first — the *signing* key — with the one
fingerprint `required_fingerprints()` kept, the primary's, and stopped reading at the primary. A
signature made with a signing subkey of the protocol's own key therefore verified and was refused:
*WRONG KEY: a valid signature by <subkey>, and the protocol's key is <primary>*, while the same
`VALIDSIG` line carried the primary's fingerprint in its last field. Not live today — the key in
`PUBKEY.asc` has no subkey — and total the day the operator rotates to one, which is ordinary
key hygiene. **Repaired:** every fingerprint in the key block is required (the primary and each
subkey it certifies), and `verify()` accepts a signature whose signing key OR whose reported
primary is in that set. A control generates a key with a signing subkey in a sandbox, signs with
the subkey, and must get `ok`; with the primary, `ok`; with another key, `BAD`.

### 2n. ⛔ `stamped()` was still a filename test, one convention over

§2h's projection kept a filter: `".ots" in name`. A reviewer renamed a real proof to
`...md.timestamp-retired-20260904` and `stamped()` said false with the commitment still in the
directory, parseable by the tree's own reader. "Whatever it is called" meant "whatever it is
called, as long as it is called *.ots*". **Repaired:** every sibling file is read; the first
bytes decide whether it is a proof (the OpenTimestamps magic) and the header parse decides
whether it commits to these bytes. A name decides nothing. A control renames the proof of the
highest stamped version to a name with no `.ots` in it and must still find the document stamped.

### 2o. ⛔ the verdict was bound to a tree nobody receives

Round 13 bound `CONTROL-SUITE-VERDICT.json` to a `tree_digest` the packet builder recomputed —
over the SOURCE tree, where the comparison is tautological. The digest walked everything under the
folder (`review/`, `runs/`, scratch) while the archive ships a declared projection, and the
builder wrote `REVIEW-COMMANDS.json` into the archive after the verdict was sealed: the shipped
verdict said one tree and a reviewer's pristine extraction hashed to another, and the
withdrawn-claims record described 139 text files where the extraction held 140. The third round
running of *the verdict disagrees with the shipped tree*, inside the repair for it.
**Repaired:** `tree_digest` is over the shipped projection (`build_review_packet.shipped_rels`,
one function), minus the two files that are measurements about the tree; the builder extracts
its own archive and requires the digest recomputed there to equal the verdict's, deleting the
archive otherwise; `REVIEW-COMMANDS.json` sits under `review/`, the directory every projection
over this tree excludes by one declaration, so it describes the tree without being counted in it.

### 2p. ⚠️ the key file that decides whose signature counts was pinned by v18 and by no version since

A round-14 reviewer appended a second primary to `PUBKEY.asc` and its signatures read `ok`, then
checked what commits that file: v8–v18 pin it, v19, v20 and v21 do not, and the governing version
is v21. The tamper is caught today because `check_commitments.py` composes every anchored
version's table and inherits the v18 pin -- but that holds only because no version retired the
path, and a version that did would leave `verify()` trusting an uncommitted file. **The trust
file for *whose signature counts* is committed here by the version that governs**, as a ninth
row of §2c, rather than by a table six versions old.

### 2q. ⚠️ the governing version should restate what it enforces

A round-15 reader applied §2p's own argument one step further: the 21 paths the composed history
pins and v22 did not restate -- `train.py`, `reproduce_findings.py`, the corpus, the measurement
scripts, `withdrawn_claims.py`, the run record -- are enforced by inheritance from the earlier versions in force that pin them,
which is the situation §2p closed for `PUBKEY.asc`. Composition enforces them today (the reader
tampered with `reproduce_findings.py` and was refused); it enforces them only until some version
retires a path. **v22 restates every one of them at its current bytes**, which are the bytes the
inherited pins already require, so this changes what is enforced not at all and changes who
commits it: the version that governs.

### 2r. ⛔ the round-16 and round-17 reads of this draft: a READY that did not restate, three filename tests, and a proof-shaped sibling that read first

A cold reader of the round-16 packet, on 24 September, found four things in the tools this draft
pins and one in its own text. Each is repaired under this version:

- **`prepare_anchor.py` said READY for a forged restatement.** A line appended to the training script and
  its new digest written into this draft's row printed *re-pinned at these exact bytes by v22,
  THE UNSIGNED DRAFT IN HAND* and READY. A restatement (§2q) changes what is enforced not at all,
  so its row must carry the digest the versions in force already give the path; a row that differs
  is a forged pin or an unstated repair, and the gate refuses it by name. A repair is a row this
  document names in §2e–§2o or here.
- **Two parsers, two composed histories.** `prepare_anchor.py` read only the fences under its own
  §3 and printed that ten versions "pin nothing" while `check_commitments.py` read their tables. The
  pairs now come from the one reader `check_commitments.commitments()`, in both tools.
- **`check_commitments.anchored()` was a filename test**, one tool over from §2n: a version whose
  signature was deleted and whose proof was renamed read as a DRAFT and demoted authority without
  a refusal. The proof is now found by the same projection `stamped()` uses. A document whose proof is
  present while its signature is absent reads ANCHORED **and UNSIGNED**, and UNSIGNED is what
  blocks (§2l). MISSING is the other case — a signature present with its proof gone — and a
  draft is the state with neither. (The round-17 read measured all three; the first cut of
  this bullet named the wrong one.)
- **The cause printer named the wrong cause** for a truncated proof and a substituted root ("no
  Bitcoin attestation yet -- run the upgrade"). A file that does not parse as a proof of these
  bytes is reported as not a proof, and not pending.
- **§3b of this draft declared a four-file distribution subset that could run in no distribution**
  and counted the rest as "five", a number from an earlier draft. This version declares no subset;
  §3b says why.

Also from that read: `anchor_status.py` no longer walks `review/` for superseded proofs; the
builder's note on block 967531 says what `ANCHORS.json` carries; a document that declares two
subset blocks is recorded by the suite as refused rather than ending the suite; and
`WITHDRAWN-CLAIMS.md` was regenerated so `withdrawn_claims.py --check` describes this folder.

**Then the round-17 read of the same archive, on 25 September, found three more in the same tools
and six sentences in this document.** Each is repaired under this version:

- ⛔ **`check_commitments.anchored()` projected over every proof-shaped sibling and then took the
  FIRST one and stopped.** The reader wrote a small, valid OpenTimestamps proof over v21's exact
  bytes carrying only a calendar receipt, named so it sorts before the real proof, and dropped it
  in the folder. v21 read PENDING with its Bitcoin-attested proof unread one file along; PENDING
  did not block, so authority rolled back from v21 to v20 in silence and `prepare_anchor.py` still
  printed READY. Fixing instance N — *a name decides nothing* — had built instance N+1: *the FIRST
  thing found decides*. ⇒ **The strongest commitment decides, not the first one found.** The
  projection now lives in one place, `ots_verify.py`, and every proof-shaped sibling is read:
  ANCHORED wins if any of them verifies against the pinned chain, and among the rest a file that is
  not a proof of these bytes outranks a receipt, because refusing is the safe direction. The verdict
  names the file that answered it, which the demotion did not. And PENDING joins the blocking states
  for the state that is an attack rather than a wait: a document whose own proof names no block
  while a proof of its own signature is still anchored in one has had an attestation taken off it.
  A freshly stamped successor has no such witness and is left alone, so the tree stays green while
  it waits for its block. A suite case plants the reader's exact fixture, twice.
- ⚠️ **The blocking refusal named one cause for four states.** It said *its proof is not a proof*
  for a document whose proof had just been read as ANCHORED and whose signature was the thing
  missing, and then cut the real reason off at sixty characters, mid-word, leaving an unbalanced
  bracket. §2l added UNSIGNED to that set and did not touch the sentence that reports it — §2e's
  defect, one tool over, for the third time in this archive. ⇒ The message branches on the state,
  and the reason is clipped at a word or not at all.
- ⚠️ **`anchor_status.py` was still finding proofs by filename**, `<doc>.ots`, the third tool in
  this tree to ask *is there a proof of these bytes*. §2n repaired one and the bullet above repaired
  the second; a reporting tool left deciding by name reports NO PROOF for a commitment sitting in
  the folder under another name. It fails closed, so it was a wrong report and not a bypass, and a
  report that is wrong about the tree is still wrong. ⇒ It uses the same projection, from the one
  place that projection now lives.
- ⚠️ **Six sentences in this document were false or stale against the tree**: §2's date line
  attributed §2p to the round-15 read while §1 and §2p's own body say round 14; §2's count of
  defects excluded §2r; §2's date enumeration stopped at §2q; §5's caveat named §2e–§2o and not
  §2r; §1 did not mention the round-16 read at all; and the third bullet above described the
  measured state as MISSING when it is ANCHORED and UNSIGNED. All six are corrected here.

**What the repaired paths were pinned at before this version.** A repair is a row whose digest the
versions in force do not give, and the READY gate exempts it because this document names it. So the
transition is written down, old beside new, rather than merely exempted:

- `anchor_status.py` — v18 pins 2e52e4bea1d0fbbc…, this version pins 886f615899d22181…; v21 restates it as 34fd4726fe8451cf…
- `build_review_packet.py` — v20 pins 2469310ef7beaa00…, this version pins 4725520c72229eac…; v21 restates it as 7d007c3cb975dd36…
- `check_commitments.py` — v18 pins 94c3346085fbe974…, this version pins c2532c98dbba0950…; v21 restates it as 5535c0764bfc2c1a…
- `check_signature.py` — v18 pins 04c16bee058b27ef…, this version pins 46bed0e0d35f1c19…
- `ots_verify.py` — v18 pins 15ca911511c6c8af…, this version pins 2c5676b0518aca1b…
- `pin_anchors.py` — v18 pins 98ef5a2074803888…, this version pins ca5e9d207b77f87b…; v21 restates it as d8225f906c10af2c…
- `prepare_anchor.py` — v20 pins 0937087c9dc3f66e…, this version pins 687e0d5a03154697…; v21 restates it as ae189319b951b0fe…
- `test_controls.py` — v20 pins cf2e339a5fbe0f51…, this version pins 8249b95f69849159…; v21 restates it as 68a9109e80cda523…
- `PUBKEY.asc` — v18 pins 88f9a69659c87a89… and this version pins the same bytes; §2p's
  reason for re-pinning it is that no version since v18 does, not that it changed.

Each digest is the first sixteen hex characters, as `prepare_anchor.py` prints them; the full rows
are in §2c and in the version named. The left column is the pin **the versions in force** give the
path, which is the value the READY gate compares a restated row against — v21 is signed and
anchored and no later table has confirmed it yet, so it is not among them, and where it restates a
path at other bytes that value is given too.

### 2d. ⛔ ANCHOR FACTS — monotonic

Each listed height must still carry the listed merkle root; new heights are permitted, and
later anchoring adds rather than contradicts. **The last two rows are what make v21
CONFIRMED**, and they are the whole reason this section is not simply v21's copied forward.

```
964534  018d69dc7bf4e2e8a45fdf3a89855b9b7e03027227aa14e596a91dcf320e09b9
964535  ef17461955701f9c1d296245df4ab22a71a7e3e0fd3ceeb7213de12958ba69c5
964549  e863c303c5b515da7544652b29648659c66ff2fa6ffad9fe82ccc975042eb439
964747  8a9766909969f175693a1fd85a7236e3be4d33a95cd4a0bcab3fff2e76e16857
964761  23019c9499bd74096ae1d9c4015bc4f10176900d99cb805e7252011ed7415d37
964762  ff5f6043b9883f8e8830856a16dc52783c66d1185d6ffebab5dbe3598f42c543
964775  ed2dd86c5b3c983d859139542aeced248e1f18ec030ccd550e36286a59f54f5e
964785  8aac2039e614e1557aab7264848c8b0cb1152970f2d5e7fa76170ccdfbf2a587
964789  b73d9657064cb4a9842e18ec1a007bc4702308730257cc378dd56ed3443ec0dd
964812  9cd60bdc0fdc9ba7784f8a4705c22d11b82b081a41d69ff598729522834dbd4a
964815  ac3592ef064ea4e4c7db187954f057550018a38dfa02afc7a2c3d33ad2955b76
964848  5784c7dab006cedba2172ec6cce265b83b1f75c8a27a117f4b2df1165b151d9c
964856  a2c750b72ab68db7602962f230b1e8a236633d5cef8f132fed1547b3ac6aba9e
964878  b9fef3d8dd2fc6b2945cb580525f25beaf5612b7b71e3a1b78799e22f353dce0
964881  45cb82a2d9677e318826afb6fd6f3a6be84b5cf94780ee1487b49097d5293579
964920  7f5a7092d6b342430276b08b492f1f18e8a6fa8ddb55a6245f0d93f6e70e13d3
964922  d876c661233b2de9d92f1dabebf9c1a677570711dbec02b1e5317502b2610fe6
964923  92687073de11e6fd31a71c3f6aa0c75aa60a0950dffa30b80ad91155425f4986
965140  c836cd739ba5bddf491db621fcfe76154d6002cecfb10dd4a72eecd99e039ec6
965142  df6e4b4f68795f65252340e42467d77e8e8c2a44e1e5a4ff40730848aca56eb6
965152  46e025634022f51ac766cc16d8be33c04068c0eb7e7a2f66930e022ca4185ece
965332  c20da71633ebb813cd0f4f78f6059bab6b6b06912a2eb76cc48182acf66a9d35
965333  3d4a2b7fe40ea918d1496985dce09db8395a9559f99c80b7be61b9c259b32266
965458  f4cb09e6fc3350c3ddcf0b4d64d124d1504d94a8b148f92298cf0465fc1513c9
965750  6dde0e9afe57f11f8b833e405d736ae64820acc04ef97d4bfeaffb3d089b949c
965753  a0a8bb7589ecd091de601d52e66639b755285ad688f23b43bc161f8092937586
965767  1a000e0f8b386a3d7b9af7eea508041fc818776605e5be6e5eb3fa108ea5c750
965784  5d65ae5e5a55e51cf1477df815f41cdc3486dfe25e33999361e582bdde0e9c2c
965818  6e9b364e154b594ce72804c6be577f7fb7ae9bf49d941cb71fe9c8bb9d1b2ea8
965831  84f7aba8c1732f40a3b4a6fa6845d0f1e0272bf882760122ff257a23485a3b08
965832  fe0ed8292038251f49661bc2c2674520f23510114b49b7d0089caeb9d2c28855
965840  4a817365b47122ee011d2542c01e677c3dcca3abfa04f01715de02f38bdc7b84
965910  2a7d27ba92ece6f533426c684cc7ab0bbc57a51eed4dc2e332f921a71f3836ec
965912  4c456b1d277b5969250a57052ce30a0b70f4c41cd0659e8f780e4695e3fb2504
965922  e67fe31925653d81ff315c29d2364a5023ebec76de0fc0a6ce347202b3a4edea
966979  d154bdb8cfe1926a12a668599b409bc32fde8cb301ff670b9077587dcc4b294c
966981  febf47418ab2295a9531814e72e716a74ad1cdf853d90cb064be963b75676db0
967137  fbbe69eb9f9f39133822c0be9eae5fd2c6b16f93c4cbab0d1de3efb508d669d7
967140  58b46a7bd1b5813a1b30644c25815d37b298a3532ba893c6e3dc93eab7999088
967150  f099824f9d0fdece911e67d6380e08b6ffe2fe0b0952e398229f4b0cba5acbc6
967728  57aff597b9004136ea9de160d284ba8cd1c59f8ac72aa400210c82a497c99d03
967736  a27c668a4d320942f8cb3906efbfefefaedda9d760d5d52bdb74f7a7e0f1a0d4
```

## 3. ⛔ What is committed, by DIGEST

⛔ **This section commits exactly 30 file pins.** The number is written here by hand and is not
maintained by any tool, which is the whole of its value: a reader can count the rows and
`prepare_anchor.py` refuses when the two disagree.

⛔ **And the sorted pinned names hash to 968b5635c5e00e030a6f12da305fdae3b977327e5adfa484331cd48888f3926e.**
The count fixes cardinality and nothing else. A digest over the sorted names moves when a row
is added, removed **or renamed**, and it fails for a different reason than the count does.

⛔ **And READY is a narrower statement than it sounds.** `prepare_anchor.py` prints READY when
every row matches the file on disk **and** every restated row carries the digest the versions in
force already give that path. For the nine rows this version names as repairs — the six tools v21
pins, plus the two v18 pins that §2g and §2h changed, plus the key file — only the first half is
checked, because the gate cannot know what repaired bytes are supposed to be. Somebody has to have
read those nine diffs; the tool cannot, and the old digest beside the new one at the end of §2r is
there so the transition is at least declared. READY is not a statement about whether the repairs
are right.

⚠️ `2a.`–`2f.` are RESERVED for the commitment and repair tables and are not available to
narrative.

### 2c. The eight tools, the key, and every other path the composed history pins, at the bytes this version commits

⚠️ Six rows restate v21's pins at the repaired bytes (`check_commitments.py`, `prepare_anchor.py`, `pin_anchors.py`, `anchor_status.py`, `test_controls.py`, `build_review_packet.py`; §2e–§2o and §2r say what changed); two rows — `check_signature.py` and
`ots_verify.py` — are pinned by earlier versions in force and are re-pinned here because
§2g and §2h changed them; one row, `PUBKEY.asc`, is pinned by v18 and by no version since, and
is pinned here directly for the reason §2p gives; the remaining 21 rows restate, at their current
bytes, every path the composed history of anchored versions pins and no version has retired, for the
reason §2q gives. Every digest below was written by `--repin` on this unsigned draft, never typed.

```
PUBKEY.asc                         88f9a69659c87a898c6a4408d28e69520306b6916744642f60519469cbb24273
anchor_status.py                   886f615899d22181a0000223776c6ff3bbe33962e45dcd7e5471688fdd286d7c
build_review_packet.py             4725520c72229eac2fc31b547aefcb493c81168a42a8b1f4ef34143d22f0e8f0
check_commitments.py               c2532c98dbba0950fdc53b4fc4d289d0f70267e1c427ed617e5a7000aa20ea23
check_signature.py                 46bed0e0d35f1c192ad984f7be470a5acefe624e33d5f3ea5e11f2259728fff3
ots_verify.py                      2c5676b0518aca1b36af6899b71a326c73a5253e6593a7cc1f1ea266ea7290ee
pin_anchors.py                     ca5e9d207b77f87b6fef84ae322e03aab12bd1eea8b905fd62c9b5e107173d90
prepare_anchor.py                  687e0d5a03154697bfc14bb71d28a7910953546c01c46e2a771175a20ad51026
test_controls.py                   8249b95f698491591c9381c0430be589c4f1a6e6e93e9d46fa828b720c531375
DISTRIBUTION-PLAN.md               6a1851278f20a89328cd5ffccb0359ee97d0ebbfc6e39147feea3b734fb2cb89
HOW-TO-RECHECK-THE-ANCHORS.md      403526de7aeaa22a73ddcc0df24350898a43a455beb97357c63e1f1d21d04233
REPRODUCTION-CALL.md               803e1047c9fcb186be4b4c5f8d16966db4ee4a9a00e252e42a8f01eb1d38ac83
attempts.py                        1edee542a8ecfa974694a8dbc807b706bb0b0aaf767cf3213f002ffed70f36ab
build_package.py                   0c50cc172500f62c0363f124fef3e9b494e8f8ef5b3532e9371c5ae927000f9c
capture_exposure.py                4a3cd9c235b499dff5430731c0fe867147ad799d7e6b3512febd9587feb1a90d
corpus/MANIFEST.json               fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py             2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json                7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30
corpus/verify_shipped.py           943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
exposure/exposure-2026-09-07.json  837fb43a3f9f5ddeddcd06372759c796d2df91ba958d12b269b0de2c7ccb2624
measure_cost.py                    4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py              d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_hardware.py                9686200fc21b08e1ef0cfeb14f7ecda9733bc34296e0318b7e63c4f390b6effc
measure_storage.py                 1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
reproduce_findings.py              d9c6be8882464a59e054d525b6e9970c02bb4f4b34be584cc403826cd0b39f25
runs/det-1/run.json                97a0318343b2fa60a072fd4339520b124c13e1b3fab62a5148dc5a8f60e2d816
seed_sensitivity.py                1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
train.py                           ebd61532782573a04aca8ab5d526ab6d233c450963ac111460f2d5d86f81d2fe
verify_package.py                  ed4d6d2a179169720fba28ef59769dc14e59cf9d207d617ad0c4aa75e32d0410
withdrawn_claims.py                3d06a244f4dfbd2c6e87dacc6ff99d221bd201fb1997a8af9c784dd9b02c7e18
```

### 3b. ⛔ What the reproducer package contains, of the files this version pins

**This version declares no distribution subset.** v18 §2c lists a nine-file reproducer package;
the round-15 read of a draft of this section found that the four-file subset it declared could
run in no distribution: every version reads `PUBKEY.asc` to decide whose signature counts, and the
tools import one another (`check_commitments.py` imports `ots_verify` and `pin_anchors`;
`prepare_anchor.py` imports `check_commitments`; `test_controls.py` imports `prepare_anchor`,
`attempts`, `build_review_packet` and `withdrawn_claims`), so a distribution that carried the four
alone could neither verify its own authority nor start. The subset rule (§2i) stays in the tools
for a version that ships a closed package; under this version the only distribution the rule
recognises is the whole shipped tree, in which nothing pinned is absent.

## 4. ⚠️ Unchanged

The study, its measurements, the reproduction call and its window closing **7 December 2026**,
and every claim v18 §1 withdrew. Nothing here reopens any of them.

## 5. ⛔ What this version does NOT do

- It does **not** make itself authority. It is a draft; it is unsigned; `in_force()` is false
  and will stay false until it is signed, stamped and confirmed by a version after it.
- It does **not** assert that v21's blocks are correct because this document names them. They
  are checkable offline against one merkle root per block, which is what §2d is for.
- It does **not** repair §2e–§2o and §2r by being written. Those are edits to files, made against
  this draft while it is still writable, and committed by signing it.
