# Pre-registration v20 — re-pinning three tools edited after v18 and v19 were signed

*Amends v19. Everything not restated here is unchanged and still governs.*

## 1. ⛔ Why this version exists: a sequencing mistake, recorded rather than tidied away

v18 was signed at 19:50 and stamped at 19:55 on 14 September 2026. `build_review_packet.py` — a file
v18 commits by digest — was edited at 20:40, fifty minutes later. `test_controls.py`, also pinned by
v18, and `prepare_anchor.py`, pinned by v19, were edited during round 10's repairs.

⛔ **`prepare_anchor.py`'s own opening docstring says a version must be signed AFTER the tooling is
final, and that is the rule that was broken.** A round-10 reviewer found it from the covering letter
rather than from the tree, because the letter said *the packet builder refused three times while
assembling this* — which is the file being edited after the document pinning it had been signed.

⚠️ **A signed document cannot be re-pinned and must not be.** `--repin` is refused on anything that
carries a signature, correctly: re-pinning would rewrite a commitment somebody has already attested
to. The repair for a broken pin on a signed version is a NEW version that pins the current bytes,
which is this one.

⚠️ **v18 and v19 keep their broken pins, and that is deliberate.** The history of a sequencing
mistake is worth more than a tidy tree. Anyone checking those two documents against this folder will
find the three files below do not match, and the reason is here.

## 2. ⛔ What was wrong with the gate that failed to notice

This was not caught by the tool that exists to catch it, and the reason is worth committing.

⛔ **`in_force()` was `signed() and stamped()` — the existence of two files beside the document.**
`main()` returned 0 the moment that was true, so every repair round 9 made to the commitment grammar
was dead code in the shipped state: the imported parser, `_NEAR_PIN`, `_inside()`, the declared
count. None of it executed. In the same tree, in the same minute, `anchor_status.py` reported
`pending (calendar only)` under its own printed rule that no document may say ANCHORED until that
list is empty.

⇒ **`in_force()` is now signed AND anchored**, where anchored means a proof that carries a Bitcoin
attestation whose block is pinned in `ANCHORS.json` — parsed by `ots_verify`, the parser
`anchor_status.py` already uses, rather than a second opinion written for this.

⇒ **And being in force no longer ends the check.** Every version in force has its pins verified, and
the current commitment for a file is the pin given by the HIGHEST in-force version that names it —
so an amendment supersedes an earlier row, while a file nobody has re-pinned still answers to the
version that did.

## 3. ⛔ What is committed, by DIGEST

⛔ **This section commits exactly 3 file pins.** The number is written here by hand and is not
maintained by any tool, which is the whole of its value: a reader can count the rows and
`prepare_anchor.py` refuses when the two disagree.

⛔ **And the sorted pinned names hash to 0c49fe43fe340e24d2d3455bb69badcc1fc3cc1444d5f3ec860db266a5e936a5.**
The count fixes cardinality and nothing else. A round-10 reviewer substituted `PUBKEY.asc` out of
v18's table and `./train.py` in, with train.py's real digest: total still 28, declared still 28, and
**the key every detached signature in this tree verifies against was no longer committed.** A digest
over the sorted names moves when a row is added, removed **or renamed**; it is recomputable by eye
with `sha256sum`, and it fails for a different reason than the count does.

⚠️ `2a.`–`2d.` are RESERVED for the commitment tables in every version since v15 and are not
available to narrative.

### 2a. The three tools edited after their pinning version was signed

```
build_review_packet.py             2469310ef7beaa00cf5bade112e20e8c7096a25f66d304267badc99a3da47b09
prepare_anchor.py                  0937087c9dc3f66e840c812bd90b6d70fb63fd964b3aeb52c4c9c284eef42656
test_controls.py                   cf2e339a5fbe0f517d982703a6c3f8a20f864efd4fc67ccc00191dd0d258a687
```

## 4. ⚠️ Unchanged

Everything v18 and v19 commit, except the three digests above, continues to govern. The withdrawal
in v18 §1, the reporting sentence in §1d, and v19's argument for the two tools are untouched by this
version.

## 5. ⛔ What this version does NOT do

- It does **not** re-open the decision v18 records, or any number in it.
- It does **not** repair v18's or v19's tables. They stay as signed, with pins that no longer
  describe this folder, because that is what happened.
- It does **not** claim the sequencing rule is now enforced by anything other than a person reading
  this before signing. The gate reports a broken pin; it cannot stop an edit made after a signature.
