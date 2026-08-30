# Measurement 6 — NOT MEASURABLE under the implemented design

*Written 30 August 2026, revised the same day after two internal reviews. §6 requires every
measurement to be reported, so this is reported — as unmeasurable, which is a result and not an
omission.*

---

## ⛔ The finding

> **Measurement 6 was not measurable under the implemented design. The pipeline was deterministic
> from inception, so no ordinary baseline existed to be made deterministic and there is no delta to
> measure. No contemporaneous engineering-time record was collected. Retrospective estimates are
> inadmissible.**

⚠️ **The "afternoon", the "two days" and the three failed timing attempts below are PROCESS
HISTORY, not quantitative evidence, and the earlier revision of this page presented them as though
they were the measurement.** Both reviewers said the disclosure was not enough to make it one. It
is not: an estimand that never existed cannot be estimated honestly afterwards, and a number
recalled at the end of the work is a memory wearing a unit.

Everything below is kept because it is true and useful to a reader deciding what this kind of work
costs. None of it is admissible as measurement 6.

---

## ⛔ What this number is, and why it is nearly useless as stated

The pre-registration asks for *"engineering hours to make an ordinary pipeline deterministic"*.
Taken literally, the answer here is **close to zero**, and that answer would be a lie by framing.

The pipeline was **written deterministic from the first line**. Nobody took an existing training
script and hardened it, so there is no before-state to measure a delta against. Reporting "under an
hour" would be true and would invite the inference *therefore determinism is cheap to retrofit*,
which this work does not support in any direction.

⇒ **What can be reported honestly is the cost of the KNOWLEDGE, not the cost of the typing.** Every
control in `train.py` is one line and each exists because something specific went wrong first.

## What the determinism actually consists of

```
the thread pin, before `import numpy`         3 lines
the seed and a single RNG stream              1 line
the data order drawn once, up front           1 line
the corpus assembled in MANIFEST order        4 lines
the environment digest, refusing to run
  if it cannot report what it must           ~30 lines
```

**About forty lines.** An afternoon of typing, and every one of them is obvious *in retrospect*.

## ⚠️ The cost that is real, and it is not hours

Three of those five controls exist because of a failure that had already happened:

| control | what it cost to learn |
|---|---|
| the thread pin, placed **before** the numpy import | the 29 Aug pilot — a separate experiment, run because the question "does thread count matter?" was not obviously worth asking. It partitioned a toy sum four ways. |
| the corpus in **manifest order**, not directory order | not learned here. It is [[substitution-not-corruption]] carried in from another part of this project, where a directory name was mistaken for a provenance. |
| the environment digest **refusing** rather than filling in blanks | the pre-registration's own §2a rule, written before any run, which would otherwise have been a sentence nobody enforced. |

⇒ **The honest form of measurement 6 is: the typing is an afternoon; the knowing is the expensive
part, and it does not scale by hours.** A team that has never seen a threaded reduction change a
digest will not write the pin, will get a plausible model, and will publish it as reproducible —
and no amount of engineering time budgeted in advance produces that line, because the budget is not
what was missing.

## What the measurement DID cost, counted honestly

| | |
|---|---|
| calendar | Phase 1 (corpus) 29 Aug, Phase 2 (pipeline + four measurements) 30 Aug — **two days** |
| commits | 4 |
| the pipeline itself | ~220 lines including comments; the comments are longer than the code and that ratio is deliberate |
| **rework** | **three failed attempts at measurement 1** |

⛔ **The rework is the part worth reporting, because it dwarfed the determinism work.** Making the
training deterministic took an afternoon. Measuring *what that cost* took three attempts:

1. timings taken while a CPU-bound build ran in another window — 7.66 s, 7.59 s, 14.28 s for three
   identical runs;
2. a guard written to prevent exactly that, which checked the machine once, found it quiet, and a
   build started a second later and ran through all seven repetitions;
3. the guard moved to run *between* every repetition, discarding the run rather than annotating it.

⇒ **Making the pipeline deterministic was easy. Measuring it honestly was not**, and if this paper
has a practical lesson for a team trying to reproduce a model, that inversion is probably it.

## ⚠️ The one figure a reader should distrust

Everything else in this paper is a digest, a byte count or a timing a stranger can re-run. **This
page is a memory.** It was written at the end of the work rather than reconstructed months later,
which is the most that can be done for it, and it is still the weakest evidence in the study.

---

Related: [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) §3 · [`PHASE-2-FINDINGS.md`](PHASE-2-FINDINGS.md)
