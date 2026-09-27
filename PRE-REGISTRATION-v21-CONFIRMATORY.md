# Pre-registration v21 — the confirmed anchor, and the tools round 11 rewrote

*Amends v20. Everything not restated here is unchanged and still governs.*

## 1. ⛔ Why this version exists

Two things, and the first is a change to what the word ANCHORED is allowed to mean.

⛔ **`ANCHORS.json` was the root of trust for the whole tree, and no version commits it.**
`ots_verify` proves a proof is structurally valid and self-consistent with that file; it cannot
prove the file carries the chain's real merkle root, and `check_commitments.py` reports it in the
same run as RETIRED by v10. Two round-11 reviewers moved authority through it independently: one
substituted a merkle root at an existing height and got `anchored() -> True`; the other appended a
row for a block that was never pinned and reached *authority … composed over 17 anchored
version(s)*. The monotonic rule makes the second permitted by design — additions are growth, and
growth is not a violation — so the committed tables constrained only the heights already in them.

⇒ **The word is split, and `in_force()` takes the stronger half.** A block a signed-and-anchored
version names in its own anchor-fact table is CONFIRMED: written down before anyone could choose
it, and beyond the reach of the monotonic rule. A block known only to `ANCHORS.json` is
PROVISIONAL. `anchor_status.py` reports both, which is its job. `in_force()` — the predicate that
moves authority and decides which commitments govern — requires CONFIRMED.

⚠️ **The cost is stated rather than hidden: authority now lags anchoring by one document.** A new
version's block is necessarily newer than any committed table, so the newest anchored version is
always provisional until a later one names its height. v18 and v19 are in exactly that position:
anchored in blocks 966979 and 966981, which no committed table named. **Section 2d below names
them, and they become confirmed the moment this document's own proof anchors.**

⛔ **And six tools were rewritten in round 11 and their pins are stale.** `prepare_anchor.py`,
`check_commitments.py`, `test_controls.py`, `build_review_packet.py`, `anchor_status.py` and
`pin_anchors.py` all changed; v15 pins four of them and v20 pins two at bytes that no longer
exist. A signed document cannot be re-pinned, so the repair is this version.

⚠️ **`pin_anchors.py` is the last of the six and its repair is worth naming.** It asked each
explorer ONCE, so a rate limit or a dropped connection was reported as *no source answered* -- a
sentence about the block rather than about the transport. Three runs of it died that way at
different points while `curl` reached the same host in a second. A source is silent only after
three attempts with backoff now; `MIN_AGREE` and the disagreement rule are untouched.

## 2. ⛔ What was wrong with the gates that failed to notice

⛔ **The composed pin check ran only in the branch this folder is never in.** It lived inside
`if in_force(doc)`, so it fired only when no version was waiting — and one is always waiting while
anyone is drafting. A reviewer mutated `PUBKEY.asc`, which v18 pins and v20 does not, and the gate
printed `v20 pins 3 file digest(s); 3 hold … READY`, rc 0. The control suite's `PUBKEY.asc` attack
had been passing for four rounds on that. **The composed commitment is now checked before any
per-document branch, on every path.**

⛔ **`max(versions())` is the highest document present, not the governing one.** Two more callers
held their own answer: `build_review_packet.py` checked that the archive shipped v20's three pins
while eighteen versions composed thirty, and `anchor_status.py` built its required-proof set the
same way. Both now ask `prepare_anchor.governing_pins()`.

⛔ **The membership declaration was read over the whole document, case-sensitively, and warned
instead of refusing.** Its sibling three lines above had been scoped to section 3's prose two
rounds earlier. A reviewer substituted a row and put one line in section 5, and both declarations
agreed. Both readers now share one scope function, take `[0-9a-fA-F]`, and refuse on a draft.

⛔ **And the distribution subset was located by a hand-written heading.** `### 2c.` is *What the
reproducer package contains* in v18 and **the anchor-fact table in v19**, so the rule read 35
merkle roots as the declared contents of a reproducer package. It is found by SHAPE now — a fenced
block whose every row is a bare path the same document pins — and two such blocks is a refusal
rather than a choice.

### 2a. ⚠️ The numbering, which v18 warned about and v19 did anyway

v18 §3 named this failure six lines above its own tables: *a reader of this document met two
different sections called 2d — the same ambiguity that, in v15, cost two protocol versions when a
renumbered heading silently emptied the fact table.* The reservation of `2a.`–`2d.` was read as
*narrative may not use these numbers* and not as **each number names one table**. This version
restores the second reading: `2d.` is the anchor facts, here as in v15 through v18, and nothing
else uses it.

### 2b. ⚠️ Nothing else moves here

No claim, no threshold, no withdrawal and no reporting sentence changes. This version re-pins five
files and commits two block heights.

### 2d. ⛔ ANCHOR FACTS — monotonic

Each listed height must still carry the listed merkle root; new heights are permitted, and later
anchoring adds rather than contradicts. The last two rows are what make v18 and v19 CONFIRMED.

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
```

## 3. ⛔ What is committed, by DIGEST

⛔ **This section commits exactly 6 file pins.** The number is written here by hand and is not
maintained by any tool, which is the whole of its value: a reader can count the rows and
`prepare_anchor.py` refuses when the two disagree.

⛔ **And the sorted pinned names hash to da74cb8aa7a6e04b09485ad155be80156e2d307ced2ce7e4620aa9c37fcc3294.**
The count fixes cardinality and nothing else. A digest over the sorted names moves when a row is
added, removed **or renamed**, and it fails for a different reason than the count does.

⚠️ `2a.`–`2d.` are RESERVED for the commitment tables in every version since v15 and are not
available to narrative.

### 2c. The six tools round 11 rewrote

```
anchor_status.py                   34fd4726fe8451cf1a50ab8be21beb7e0adf390e69dc98b9bfaa8a0b93a1f9d2
build_review_packet.py             7d007c3cb975dd36bbeeab312f9a28a727b6f4b0318a5b46f68364a1d1397486
check_commitments.py               5535c0764bfc2c1a938dd4d22376c019d84347edc5adcffb4273f79c9f2cc0f6
pin_anchors.py                     d8225f906c10af2c157efdbadcd43506202712b2097a7428aa8bc76ccee96114
prepare_anchor.py                  ae189319b951b0fe4f2ca33aad90ace2e738f2409a816090990ccacd8e554850
test_controls.py                   68a9109e80cda52308879c31236db853696d72f4739f99461590c553557be738
```

## 4. ⚠️ Unchanged

Everything v18, v19 and v20 commit, except the five digests above, continues to govern. The
withdrawal in v18 §1, the reporting sentence in §1d, and v19's argument for the two tools are
untouched by this version.

## 5. ⛔ What this version does NOT do

- It does **not** re-open any decision or number in v18, v19 or v20.
- It does **not** repair the earlier tables. They stay as signed, with pins that no longer describe
  this folder, because that is what happened.
- It does **not** claim `ANCHORS.json` is now trustworthy. It claims the opposite: the file is an
  explorer-sourced assertion, and the two heights in §2d are committed here so that nothing has to
  trust it for v18 and v19 to be in force.
- It does **not** make this document's own block confirmed. That needs the next version, which is
  the property, not a gap in it.
