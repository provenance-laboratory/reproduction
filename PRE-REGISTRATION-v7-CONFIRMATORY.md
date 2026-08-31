# Pre-registration v7 — the first time v6's rule cost something, and it was paid

⛔ **v3 governs, v4 amends measurement 4, v6 commits the instruments, and this version replaces
v6 §2b only.** One digest changes. Where this document is silent, v6 and v3 govern.

## 1. What happened, within hours of v6 anchoring

v6 §2b committed twelve instrument and gate scripts by digest, and said this about the cost:

> *"Every repair to a checker now requires a new anchored version. That is deliberate — round 4
> exists because a checker was repaired between rounds and nothing recorded which one produced
> which result — and it will make this project slower. If that becomes an excuse for not repairing
> a checker, the rule has failed and should be reported as failing, not quietly relaxed."*

⇒ **v6 anchored at Bitcoin blocks 964812, 964815 and 964848. Within the hour, `test_controls.py`
needed a repair, and making it voided the pre-registration.** This document is the record of paying
that cost rather than relaxing the rule.

## 2. The defect that forced it, which is the one this project keeps making

`test_controls.py` carries the attack *"delete the governing document's proof"*. It deleted
`PRE-REGISTRATION-v5-CONFIRMATORY.md.ots` **by name**.

⛔ **The moment v6 anchored and became authority, that attack stopped attacking anything.** It
removed a *superseded* document's proof, the checker correctly carried on with v6, and the control
reported the attack as REFUSED — a control that passes because the thing it names is no longer the
thing that matters. It had silently stopped testing the property it exists to test.

⚠️ **This is the enumeration defect, inside the file written to catch enumeration defects.** A test
that names a version rather than deriving the governing document goes stale exactly when the
protocol advances, which is the one moment its result is load-bearing. The same shape has now
appeared in a check-method registry, a coverage denominator, a workflow block, a deposit file list,
a packet's send list, a path-shortening rule applied per host — and now in the control suite.

⇒ Both attacks in that file now **derive** the governing document from `check_commitments.governing()`
instead of naming a version. The suite went from 10 refused with one false pass, to 11 refused.

## 3. ⛔ What is committed, by DIGEST — replacing v6 §2b

```
check_commitments.py       2089c5bd7322717ca0e587ba3c23690fefd1c8dbf8f065496500e25949b7e638
anchor_status.py           02f7d89144f1e26c3b4ee0cc006a9e617601d06e136771411df93b907d442614
measure_hardware.py        369f987e25d95f8df95928015574cf5898697354530ba963ab22860b780acc24
measure_cost.py            4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py      d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_storage.py         1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
seed_sensitivity.py        1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
build_package.py           03314126c0b4b975aae3fff31c9549503d8b644610d31910de10608cff762c82
verify_package.py          bf88fd51fe247bebcd6769645eeb570f6381983decdd5867a94c04a4a5a6c87d
test_controls.py           7a294609c03b46fb3bcecac29d6570b11bb6cbe5a19e8b8be21c57e9d555b075
corpus/verify_shipped.py   943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
reproduce_findings.py      78d570f5df51245e5d9a9b2ddeb75ef5e22cda283a06e64383ca383b80827bbf
```

⇒ **Nine of the twelve are unchanged from v6.** `test_controls.py` moves for the repair in §2; `anchor_status.py` and `build_package.py` move only because they must NAME this document -- a
version cannot be required or shipped by tools that do not know it exists. v6 §2a's experimental
inputs are untouched and are not restated here.

## 4. What this version does NOT do

⚠️ **It does not weaken the rule, add an exemption for test files, or introduce a category of
"minor" change.** Each of those was available and each would have made the next repair invisible.
The rule's whole value is that it has no exceptions to argue about, and a first exception granted
to the author's own convenience, hours after the rule was written, would be worth less than no rule.

⚠️ **It does not claim the cost is small.** Two protocol versions in one day, each requiring a
stamp and a wait for a Bitcoin attestation, for one repair to one test file. That is the real price
of committing instruments, and a reader deciding whether to adopt this practice should see the
price rather than only the principle.

## 5. What would invalidate this version

Everything in v3 §6, v4 §3 and v6 §7, with §2b's digest table replaced by §3 above.

⚠️ **And one thing to watch, stated because it is the likeliest way this fails.** If protocol
versions begin appearing faster than reviews do, the anchoring will stop meaning "committed before
the data" and start meaning "committed before the last edit". The defence is not a rule; it is that
each version has to justify itself in prose that a reviewer reads, as this one does.

---

*Replaces: v6 §2b · Alongside: [`PRE-REGISTRATION-v3-CONFIRMATORY.md`](PRE-REGISTRATION-v3-CONFIRMATORY.md), [`v4`](PRE-REGISTRATION-v4-CONFIRMATORY.md), [`v6`](PRE-REGISTRATION-v6-CONFIRMATORY.md) · Enforced by [`check_commitments.py`](check_commitments.py) and [`test_controls.py`](test_controls.py)*
