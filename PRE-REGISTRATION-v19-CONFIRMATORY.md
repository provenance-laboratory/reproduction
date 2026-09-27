# Pre-registration v19 — the two tools v18 introduced, argued on their own

*Amends v18. Everything not restated here is unchanged and still governs.*

## 1. ⛔ Why these are not in v18

v18 withdraws a claim, repairs v17's block-finder, and re-pins four digests. It also introduced two
new tools, one of them carrying a **write path into pre-registration documents**. A round-9 reviewer
ruled that bundling wrong, and the argument is v18's own:

> ⛔ **AND THIS VERSION BUNDLES, WHICH §1d ITSELF WARNS AGAINST.** Its best line is that two
> decisions must not be bundled where one can hide the other. … but a future version that bundles
> a governance change with a substantive withdrawal should be split.

**That future version is this one.** v18 §1d refuses to move an anchored date in the same version
that withdraws the claim the date was for, on the ground that *a wholly innocent change would look
identical to a self-serving one*. Applied to §2b, the same standard splits it — and the asymmetry
is what makes it more than symmetry:

```
the withdrawal   SELF-DENYING.   It gives up the study's headline.
--repin          SELF-EMPOWERING. It is a write path into documents that are signed and anchored.
```

Pairing them puts a governance change inside the version a reviewer has every reason to approve,
which is the one configuration in which *we bundled, and here is the disclosure* does the least
work.

⚠️ **The cost v18 cited is not the cost on the table.** §2b said splitting *a version that is
about to be signed would cost more than saying so*. v18 is not signed; it has been redrafted once
already, and the superseded draft is on disk; `prepare_anchor.py` exists to make re-preparing
cheap; and nothing in v18 §1 depends on `--repin` existing.

### 1a. ⛔ `prepare_anchor.py`, and the write path it carries

`--repin` rewrites the digest rows of a pre-registration document. That is a governance change,
because every other route into these documents is closed by construction: they are signed, they are
anchored, and an anchored file whose bytes change is a broken proof.

⇒ **IT IS PERMITTED ONLY WHILE NOTHING HAS SIGNED THE BYTES**, which is what `writable()`
implements. An unsigned version is a draft and correcting a digest in it is editing a draft; the
same edit to a signed document is forgery, and it stays forgery whether or not a calendar has seen
it yet. If the pins of a signed version are genuinely wrong, the honest route is a new version
stating the change and its reason — which is this protocol's own rule for amending an anchored
text, and is the rule this document is an instance of.

⚠️ **The gate was `in_force()` and that was wrong by one step.** `in_force()` means *signed AND
stamped*, so between `gpg` and `_ots_stamp.py` a document had a signature, no proof, and an open
write path. A round-8 reviewer walked through it: they created a signature for v18, touched
`train.py`, re-pinned, and were told to sign a document whose existing signature no longer
verified. The gate is `writable()` now, and the suite attacks it.

### 1b. ⛔ `withdrawn_claims.py`, the generator

`PRE-REGISTRATION.md` §2c states the ecosystem claim plainly, with no marker, and it is
OpenTimestamped — so it cannot be edited, and the survivor is the one that matters. This tool
generates `WITHDRAWN-CLAIMS.md`, an additive record of where a withdrawn claim is still written
down and where to read the withdrawal. Nothing anchored is touched.

⇒ **THE READINGS ARE AN APPEND-ONLY HASH-CHAINED LOG**, the same construction `attempts.py`
already uses in this tree: each entry carries `prev`, the SHA-256 of the previous entry's exact
bytes, and a head file pins the count. A round-9 reviewer promoted every machine-proposed
disposition to *read by a human*, flipped the one anchored carrier to *clean*, and got a clean
exit — the document this tool exists for, erased from the published record, with the doctored tree
passing the step the honest one failed. The per-entry digest defended against the DOCUMENT
changing. Nothing defended against the RECORD OF THE READING changing.

⚠️ **AND IT IS DELIBERATELY NOT PINNED BY THIS VERSION.** `WITHDRAWN-DISPOSITIONS.jsonl` and its
head grow every time somebody reads a file. Pinning them would make each reading a protocol
amendment, which would stop the readings. What protects them is the chain and a stamp on the head,
not a digest in this document.

### 1c. ⚠️ What each is attacked with, by name

v18 §2b's preamble conceded that both tools shipped **unattacked**. Both now carry declared
controls in `test_controls.py`, each asserting a NAMED refusal rather than any refusal:

```
prepare_anchor.py   a pinned PUBKEY.asc changed under the gate
                    re-pin a document that is already signed
                    a second, contradictory pin for one file
                    a digest in a commitment block that no row consumes
                    a pinned file changed and its pin upper-cased
                    a pin whose name leaves the study folder
                    a pin one hex character short

withdrawn_claims.py the anchored carrier flipped to clean in the record
                    the last reading deleted from the end of the log
                    an entry respelled without changing the object
                    the claim restated in a file that is not a .md
```

⛔ **THREE OF THOSE SEVEN PASSED BEFORE ROUND 9, AND THE FIRST OF THEM BLOCKED SIGNING.**
`prepare_anchor.py` kept a second digest grammar, matching `[0-9a-f]` while `check_commitments.py`
— the authority on what these documents commit — has matched `[0-9a-fA-F]` since the round that
found a whole table parsing as zero. Both halves of the local pair were lower-case only, so an
upper-cased pin was missed by the row parser AND by the completeness scan: it did not become a
stray or a refusal, it became nothing, and the tool printed READY over a changed file. The second
parser is deleted; the grammar is imported.

## 3. ⛔ What is committed, by DIGEST

⛔ **This section commits exactly 2 file pins.** The number is written here by hand and is not maintained by any tool, which is the whole of its value: a reader can count the rows, and `prepare_anchor.py` refuses when the two disagree. A round-9 reviewer edited one character of one digest into a shape the parser could not read, and the row left the table taking the total with it — `28 pins; 28 hold … READY`, true of a document that had silently stopped committing a file. A grammar cannot count what it cannot parse, so the count comes from somewhere else.

⚠️ `2a.`–`2d.` are RESERVED for the commitment tables in every version since v15 and are not
available to narrative.

### 2a. The two tools this version introduces

```
prepare_anchor.py                  16838782f245f5ca7c4648770851cb5d840b0a8888465ec7689310e48f2d881b
withdrawn_claims.py                3d06a244f4dfbd2c6e87dacc6ff99d221bd201fb1997a8af9c784dd9b02c7e18
```

⚠️ **Two rows, and that is the point of the split.** Every other instrument this study runs is
pinned by v18, which is where they belong: they are the machinery of a measurement. These two are
the machinery of the PROTOCOL, and a reviewer weighing them is weighing a different question.

### 2b. ⚠️ Nothing else moves here

This version adds no experimental input, changes no measurement, moves no date, and withdraws
nothing. `test_controls.py` carries the controls listed in §1c and is pinned by v18, which re-pins
it as a mechanical consequence of the suite growing.

### 2c. ⛔ ANCHOR FACTS — monotonic

**Every line must remain present and unchanged; new heights may be added and are not a violation.**

```
964534     018d69dc7bf4e2e8a45fdf3a89855b9b7e03027227aa14e596a91dcf320e09b9
964535     ef17461955701f9c1d296245df4ab22a71a7e3e0fd3ceeb7213de12958ba69c5
964549     e863c303c5b515da7544652b29648659c66ff2fa6ffad9fe82ccc975042eb439
964747     8a9766909969f175693a1fd85a7236e3be4d33a95cd4a0bcab3fff2e76e16857
964761     23019c9499bd74096ae1d9c4015bc4f10176900d99cb805e7252011ed7415d37
964762     ff5f6043b9883f8e8830856a16dc52783c66d1185d6ffebab5dbe3598f42c543
964775     ed2dd86c5b3c983d859139542aeced248e1f18ec030ccd550e36286a59f54f5e
964785     8aac2039e614e1557aab7264848c8b0cb1152970f2d5e7fa76170ccdfbf2a587
964789     b73d9657064cb4a9842e18ec1a007bc4702308730257cc378dd56ed3443ec0dd
964812     9cd60bdc0fdc9ba7784f8a4705c22d11b82b081a41d69ff598729522834dbd4a
964815     ac3592ef064ea4e4c7db187954f057550018a38dfa02afc7a2c3d33ad2955b76
964848     5784c7dab006cedba2172ec6cce265b83b1f75c8a27a117f4b2df1165b151d9c
964856     a2c750b72ab68db7602962f230b1e8a236633d5cef8f132fed1547b3ac6aba9e
964878     b9fef3d8dd2fc6b2945cb580525f25beaf5612b7b71e3a1b78799e22f353dce0
964881     45cb82a2d9677e318826afb6fd6f3a6be84b5cf94780ee1487b49097d5293579
964920     7f5a7092d6b342430276b08b492f1f18e8a6fa8ddb55a6245f0d93f6e70e13d3
964922     d876c661233b2de9d92f1dabebf9c1a677570711dbec02b1e5317502b2610fe6
964923     92687073de11e6fd31a71c3f6aa0c75aa60a0950dffa30b80ad91155425f4986
965140     c836cd739ba5bddf491db621fcfe76154d6002cecfb10dd4a72eecd99e039ec6
965142     df6e4b4f68795f65252340e42467d77e8e8c2a44e1e5a4ff40730848aca56eb6
965152     46e025634022f51ac766cc16d8be33c04068c0eb7e7a2f66930e022ca4185ece
965332     c20da71633ebb813cd0f4f78f6059bab6b6b06912a2eb76cc48182acf66a9d35
965333     3d4a2b7fe40ea918d1496985dce09db8395a9559f99c80b7be61b9c259b32266
965458     f4cb09e6fc3350c3ddcf0b4d64d124d1504d94a8b148f92298cf0465fc1513c9
965750     6dde0e9afe57f11f8b833e405d736ae64820acc04ef97d4bfeaffb3d089b949c
965753     a0a8bb7589ecd091de601d52e66639b755285ad688f23b43bc161f8092937586
965767     1a000e0f8b386a3d7b9af7eea508041fc818776605e5be6e5eb3fa108ea5c750
965784     5d65ae5e5a55e51cf1477df815f41cdc3486dfe25e33999361e582bdde0e9c2c
965818     6e9b364e154b594ce72804c6be577f7fb7ae9bf49d941cb71fe9c8bb9d1b2ea8
965831     84f7aba8c1732f40a3b4a6fa6845d0f1e0272bf882760122ff257a23485a3b08
965832     fe0ed8292038251f49661bc2c2674520f23510114b49b7d0089caeb9d2c28855
965840     4a817365b47122ee011d2542c01e677c3dcca3abfa04f01715de02f38bdc7b84
965910     2a7d27ba92ece6f533426c684cc7ab0bbc57a51eed4dc2e332f921a71f3836ec
965912     4c456b1d277b5969250a57052ce30a0b70f4c41cd0659e8f780e4695e3fb2504
965922     e67fe31925653d81ff315c29d2364a5023ebec76de0fc0a6ce347202b3a4edea
```

⚠️ **v18's anchoring block is not in this table yet, and cannot be.** v18 is unsigned as this
is written; the height that anchors it does not exist. `pin_anchors.py` appends it once it does,
and `prepare_anchor.py` refuses to prepare this version while v18 is not in force — because a
version amends the one below it, and anchoring an amendment to a document nobody has signed is the
sequencing mistake this whole protocol is arranged to prevent.

## 4. ⚠️ Unchanged

Everything in v18 and below. In particular §1 of v18 — the withdrawal — stands on its own and is
not reopened here, which is the whole reason these two documents are two documents.

## 5. ⛔ What this version does NOT do

It does not open a write path into a signed document; `writable()` closes that, and §1a says so in
the terms the gate implements. It does not make the readings in `WITHDRAWN-CLAIMS.md` authoritative
— they are one reader's adjudications, chained so that a later reader can tell whether the record
has been rewritten, which is a different and smaller claim. It does not pin the readings.

⚠️ **And it does not claim the scan is complete.** `withdrawn_claims.py` scans every text file in
this tree and requires a human reading of each one a known phrasing appears in. A withdrawal
restated in words nobody anticipated is still possible; the number of files resting on the scan
alone is printed in the generated record rather than left to be assumed, and the hint list is the
thing to extend when one is found.
