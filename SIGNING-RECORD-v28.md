# Signing record for protocol v28

Named by v28 §2f as the place where the run over v28's final bytes is recorded. This file is not pinned:
it records, and the next version's §2f names what it records.

## The document signed

`PRE-REGISTRATION-v28-CONFIRMATORY.md`, sha256 `5bfc1abfba964c18763abe704254a428b90f96acd4e918de74d9262d3c035dcd`
(29 October 2026). It was not edited after the run below.

## The control-suite run over the final draft

`python test_controls.py`, run on 29 October 2026 over the tree holding that document, before signing.

```
CONTROL-SUITE-VERDICT.json   sha256 9422e9b7a2e0ccdf73d4ce0fef4e42838c57f6cf09549fa106d78463b616b747
  tree_digest                     175e3cac36282336
  headline                        77 of 77 declared attacks measured; 77 refused, 0 accepted that
                                  should not have been, 0 refused for the wrong reason; 0 not measured
  hygiene_failed                  false
  security_ok                     true
  positive_control_failed         true     (liveness_ok false)
```

The positive control fails for the draft's reasons and no other: `check_commitments.py` reports the five
files v28 repairs (`anchor_status.py`, `check_commitments.py`, `pin_anchors.py`, `prepare_anchor.py`,
`test_controls.py`) as no longer matching v27's pins, and v28 as a document with no proof binding it.
`prepare_anchor.py` reported `v28 pins 30 file digest(s); 30 hold against the files here` and READY.

## Accepted at signing

Blocks 964878 and 964881 stay carried in §2d with no surviving proof in this folder (v28 §2e, as v27 §2e).
`pin_anchors.py --verify` refuses on them, and that is not overridden. The operator signs with this
known.

## Signed and stamped

29 October 2026: signed with key B0145F74B78CF1DA (`PRE-REGISTRATION-v28-CONFIRMATORY.md.asc`, verified Good
signature); the document and its signature stamped with OpenTimestamps on three calendars (alice, bob,
finney), proofs PENDING until a calendar anchors them; `withdrawn_claims.py` regenerated the record.
Next: `python ../../_ots_upgrade.py` once anchored, then `pin_anchors.py --add`, `check_commitments.py`,
and the first post-anchor `test_controls.py`, which is v27's and v28's positive-control check.

## Anchored, and the first post-anchor run

29 October 2026: both proofs carry a Bitcoin attestation (`python ../../_ots_upgrade.py`), block 973704;
`pin_anchors.py --add` pinned it (merkle root matched our proof). `pin_anchors.py --verify` refuses on
964878 and 964881 alone, the two heights accepted above. `check_commitments.py`: all 30 committed files
hash to the digests the anchored protocol pins.

`python test_controls.py`, the first run after the anchor, which is v27's and v28's positive-control check:

```
CONTROL-SUITE-VERDICT.json   sha256 814f9889b6ba7338bd9fddd1690b8f9c91acc844e01874df0bfeddc5739d0876
  tree_digest                     a6f45fd3357f757f
  headline                        68 of 77 declared attacks measured; 68 refused, 0 accepted that
                                  should not have been, 0 refused for the wrong reason; 9 not measured
  hygiene_failed                  false
  security_ok                     true
  liveness_ok                     true
  positive_control_failed         false
```

The nine not measured are the draft-window attacks, which need a draft to exist (v28 §5: the synthetic
draft that would measure them at every tree state is not implemented).
