# Pre-registration v23 — confirming v22, and three repairs to the control suite

**Status: DRAFT. Unsigned, unstamped, and it governs nothing.** It is written down now because
v22 going in force stopped the control suite, and because making it run again surfaced a second
control that does not run either.

## 1. ⛔ Why this version exists

v22 was signed on 26 September 2026 and its proof landed in Bitcoin block **968668**. That is the
outcome the protocol wants, and it carries the consequence an anchoring carries:

1. **v22 cannot confirm itself.** `confirmed()` requires a committed fact from a version
   *strictly newer* than the document. So v22 is ANCHORED and PROVISIONAL, and only a later
   version's §2d can make it CONFIRMED. **§2d below is that.**

2. **And this time the suite could not say so.** v22 §1.3 recorded that `test_controls.py`
   mutates a DRAFT, that with every version anchored there is none, and that the control
   *"did not quietly skip; it raised … and took the suite down"* — filed there as a gate holding
   rather than a defect. The first half is right and stays right. The second half is the defect:
   **saying "this case tests nothing" should not cost the thirty controls behind it.**
   `_declaration_target`'s own comment already states the rule — *"A VERSION WHOSE DECLARATIONS
   ARE CHECKED BUT WHICH CARRIES NO PIN TABLE IS SKIPPED, NOT ASSERTED ON … round 9's exact
   failure, where one crash took five controls with it"* — and the empty-candidate branch was the
   one case that still raised. §2s repairs it.

3. **Repairing that surfaced a control that does not run.** With the suite reaching its end,
   `p_wrong_key_signature` reported `unmeasured`. The cause is not cryptographic: gpg writes the
   detached signature to a path that already exists, and `--batch` declines to overwrite it.
   **So the case that catches a valid signature by a key that is not the protocol's — the bypass
   v22 §2g repaired — is not exercising that repair.** §2t. A second control signs the same way
   and carries the same flag here.

⚠️ **What this version does not yet know, stated rather than implied.** Editing a pinned file makes
the baseline fail, and the suite scores nothing once it does. The repairs below are committed on
three pieces of evidence: the run now reaches its verdict instead of aborting, the eight
`_declaration_target` cases report themselves `unmeasured`, and the in-process wrong-key check now
runs and refuses a valid signature by `C5647997F3D40D1D`. What the thirty baseline-gated attacks
say is not established while the baseline fails. That order follows from the protocol, and naming
it is better than implying a measurement nobody holds.

## 2. ⛔ What was wrong, and is repaired under this version

### 2s. ⛔ an unmeasurable control ended the run instead of reporting itself

`_declaration_target` raised `AssertionError` when no checked version carried a pin row. Nothing
catches that — `_Unmeasurable` is the type this suite handles — so the run stopped inside
`p_duplicate_pin`, and roughly thirty controls after it, including the positive control, did not
execute. The condition is reached by a tree in which **every version is anchored**, which is the
state the protocol exists to produce.

⇒ The branch now raises `_Unmeasurable`, carrying the same sentence. Eight cases in that family
report `unmeasured` and the run continues to its verdict. **The healthy state of the tree is no
longer the one state the suite cannot measure.**

### 2t. ⛔ the wrong-key control reports itself unmeasured

`p_wrong_key_signature` builds a throwaway keyring, signs the governing document with a key that is
not the protocol's, and expects the refusal. Its signing call writes to `<gov>.asc`, which is
already in the sandbox beside the document it signs. `--batch` gpg refuses to overwrite an existing
output file and exits `signing failed: File exists`; the setup raises `_Unmeasurable`, and the
control is reported unmeasured rather than run. Reproduced twice on a fresh keyring outside this
tree: without `--yes` the call fails with exactly that message; with `--yes` it writes the
signature.

⚠️ **How far back this reaches, with the bound stated.** The repository holds 13 revisions of
`test_controls.py`, and a search over all of them finds the flag in none. That is a statement
about this repository's history and the condition on this machine, not about every run anyone
has made: the call fails when the output path is already present, and whether it was present on
each past run is not something this document establishes.

⚠️ **The error text points one call too early.** *"gpg could not sign with the throwaway key"* reads
as a key or agent fault on the machine, and a reader would go looking at gpg's configuration. The
fault is the output path. The comment at the call site now says so, because the next reader will
have the same first thought.

⇒ `--yes` is added at both throwaway-keyring call sites — `p_wrong_key_signature` and the signing
subkey control, which writes `-o <doc>.asc` the same way and carried the same hazard. The
in-process half of the first now runs and refuses: *"verify() names the wrong key, not merely a bad
one"*.

### 2u. ⚠️ a verdict could outlive the run that produced it, on the hand path

`build_package.py` is defended, and was defended before this round: it unlinks
`CONTROL-SUITE-VERDICT.json`, issues `CONTROL_SUITE_NONCE`, and validates the nonce and the tree
digest **before** it branches, on every path. That is round 11's repair together with the later fix
that moved those checks out of `if returncode != 0`. None of it is changed here, and the packaged
path is not exposed to what follows.

The residual is the path `OPERATOR-ACTIONS.md` actually instructs: `python test_controls.py`, run
by hand. On that path nothing removed the previous verdict, so a run that crashed left the last
run's JSON in place, with no timestamp and nothing saying which tree it described. ⚠️ **This was
found by making exactly that mistake** — reading a verdict written 48 minutes and one anchoring
earlier, and very nearly reporting it as this tree's result. Its `nonce` was `""`, which is the
mechanism saying the verdict was not the reader's to use.

⇒ `main()` removes the verdict before the run, so absence means *no verdict* by hand as it already
does under the gate.

### 2d. ⛔ ANCHOR FACTS — monotonic

Each listed height must still carry the listed merkle root; new heights are permitted, and
later anchoring adds rather than contradicts. **The last row is what makes v22
CONFIRMED**, and it is the whole reason this section is not simply v22's copied forward. The
two rows above it, which v22 added to confirm v21, stay exactly where they are: the rule for this
table is that it grows, and every height v22 carried is carried here.

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
968668  62e24a1b11ad70b4aedc31f2eca6d15eec594db333f747ed994b2faa008f8688
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

⚠️ **One row moves: `test_controls.py`.** §2s–§2u say what changed in it and why. The other
29 rows restate, at their current bytes, every path the composed history of anchored versions
pins and no version has retired — the same discipline §2q introduced, for the same reason. The
declared count stays 30 and the digest over the sorted names is unchanged, because no row is
added, removed or renamed here; exactly one digest moves. Every digest below was written by `--repin` on this unsigned draft, not typed by hand.

```
PUBKEY.asc                         88f9a69659c87a898c6a4408d28e69520306b6916744642f60519469cbb24273
anchor_status.py                   886f615899d22181a0000223776c6ff3bbe33962e45dcd7e5471688fdd286d7c
build_review_packet.py             4725520c72229eac2fc31b547aefcb493c81168a42a8b1f4ef34143d22f0e8f0
check_commitments.py               c2532c98dbba0950fdc53b4fc4d289d0f70267e1c427ed617e5a7000aa20ea23
check_signature.py                 46bed0e0d35f1c192ad984f7be470a5acefe624e33d5f3ea5e11f2259728fff3
ots_verify.py                      2c5676b0518aca1b36af6899b71a326c73a5253e6593a7cc1f1ea266ea7290ee
pin_anchors.py                     ca5e9d207b77f87b6fef84ae322e03aab12bd1eea8b905fd62c9b5e107173d90
prepare_anchor.py                  687e0d5a03154697bfc14bb71d28a7910953546c01c46e2a771175a20ad51026
test_controls.py                   71ef87194d6f563442a6630bcc74018dbc0d79f176d3cbfce4f3d941cc79a5f0
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
- It does **not** assert that v22's block is correct because this document names it. It is
  checkable offline against one merkle root per block, which is what §2d is for.
- It does **not** repair §2s–§2u by being written. Those are edits to `test_controls.py`, made
  against this draft while it is still writable, and committed by signing it.
- It does **not** report what the repaired suite measures. Editing a pinned file makes the
  baseline fail, and the suite scores nothing once it does — *"the baseline does not pass, so
  nothing below is measured"*. That is the gate working, and it is why a measurement of the
  repaired suite is available only once this version is in force.
