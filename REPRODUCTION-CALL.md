# Reproduce this model, and tell us what you got

**We trained a small model and published everything needed to train it again. We are asking anyone
to re-run it and report whether the weights come out bit-for-bit identical.**

You do not need permission, you do not need to succeed, and a failed attempt is the same kind of
result as a successful one.

```
WHERE       github.com/provenance-laboratory/reproduction/issues
            Two templates: a one-line commitment, and a full report

THE WINDOW  closes 7 DECEMBER 2026
```

⛔ **The close date does not move.** It was chosen before the window opened and it is stated here so
that it cannot be chosen afterwards. If nobody reproduces this artifact by 7 December 2026, that
silence is the result we report — and a window extended until a reproduction arrives would not be a
measurement, it would be a schedule. **Reports filed after the close are welcome and will be
reported, but separately, and they do not reopen the window.**

---

## ⛔ First, if you are willing: say so BEFORE you see the target

The protocol ([`PRE-REGISTRATION-v2-CONFIRMATORY.md`](PRE-REGISTRATION-v2-CONFIRMATORY.md) §2)
puts a public commitment **before** the reference digest is published, and the reason is not
ceremony:

> A reference digest published before anyone has committed is a target that reproducers
> self-select against. A commitment made before the target exists cannot be.

So if you intend to try, **file a one-line commitment issue first**, at
`github.com/provenance-laboratory/reproduction/issues`. It costs you nothing, binds you to nothing,
and you may still report whatever you get — including that you gave up.

⚠️ **We are also measuring whether anyone commits.** If nobody does, that is a reported result
about how hard it is to get a deliberately trivial artifact reproduced, and it was written down
before the call went out so that it cannot later look like a consolation prize.

## What you need

```
CPU              any x86-64. GPU is neither needed nor used
RAM              under 1 GB
disk             about 20 MB
time             the training loop takes well under a minute; the download is the slow part
software         python 3 and numpy. Nothing else. No network access during the run
```

## What to do

```bash
# 1. get the package and check it is the package
sha256sum -c SHA256SUMS

# 2. run it. The thread pin is not optional -- it is the constraint being tested
python train.py --out my-run

# 3. compare
#    my-run/run.json carries weights_sha256. Ours is in EXPECTED.json
```

**That is the whole procedure.** If it does not work, that is a result: report it.

## What to report

File a report at `github.com/provenance-laboratory/reproduction/issues` using the **Reproduction
report** template. Fill in whatever you have; **a partial report is worth more than no report**, and
the fields that matter most are the CPU, the thread count and the digest you got.

```
CPU model                       exactly as your OS reports it
logical processors
operating system
python version
numpy version
BLAS and its version            numpy.show_config() prints this
thread environment variables    what OMP_NUM_THREADS etc. were actually set to
weights_sha256 you obtained
whether sha256sum -c passed
anything that went wrong
```

`run.json` from your run contains almost all of this already. **Attaching that file is enough.**

---

## ⛔ Two rules we bind ourselves with, so you know what you are taking part in

**We do not assist.** If you get stuck, we would rather you file the report saying you got stuck
than that we help you past it. Helping would mean we had measured *whether we can make it work with
our help*, which is not the question anyone is asking. **Any assistance we do give will be logged
and reported in the paper, and a run that received assistance will be reported separately from runs
that did not.**

**We do not characterise your independence.** The paper will report what was filed and at what
public address, so a reader can open the thread and judge for themselves. We will not describe any
reporter as independent, or affiliated, or anything else. That is the reader's inference to draw
from the record, not ours to assert on their behalf.

⚠️ **These rules cost us something and are meant to.** They make the result harder to obtain and
harder to dress up. A reproduction study whose author coached the reproducers and then vouched for
their independence measures the author's persuasiveness.

## ⛔ If nobody answers, that is the finding

This was written before the window opened, and it is in the pre-registration
([`PRE-REGISTRATION-v2-CONFIRMATORY.md`](PRE-REGISTRATION-v2-CONFIRMATORY.md) §2, §7) so that it cannot later look like a consolation
prize assembled after silence.

The companion paper measured twelve public model releases against 22 axes and found that
**independent reproduction is satisfied by none of them**. If an artifact published expressly to be
reproduced — a few megabytes, licensing-clean, deterministic by construction, every input hashed and
timestamped, runnable in under a minute on a laptop with no GPU — **also goes unreproduced**, then
the barrier is not cost, not scale, and not licensing. It would be a finding about the ecosystem
rather than about this artifact, and a sharper one than a successful reproduction would have been.

## What we already know, so you are not chasing our bugs

Reported here rather than left for you to discover, because withholding it would waste your time
and measure nothing:

- **Thread count can change the weights, and whether it does depends on your machine.** On ours,
  requesting 1, 2, 4, 8 and 16 threads produced five distinct models. On a reviewer's machine the
  same five requests produced **one** model — their request for 16 was granted as 9. The mechanism
  is the effective *reduction shape*; an environment variable only requests it. That is why the pin
  sits before `import numpy` in `train.py`: OpenBLAS reads those variables at load time, so setting
  them afterwards does nothing at all.
- **The models differ in their bits while agreeing closely on the reported metrics.** Between our
  1-thread and 16-thread runs the relative L2 difference is `2.0e-05`, the final losses agree to
  five decimals (3.21813250 against 3.21812963) and 96.8% of parameters differ. ⚠️ We do **not** claim they are behaviourally
  equivalent — nothing here tested that, and capability testing is out of scope. **If your digest
  differs from ours, the model is probably fine and the artifact is still not reproducible**, and
  both halves of that sentence are the point.
- **Divergence appears at the first step, in every array.** Not at some later step: reduction order
  enters at the first matmul. An earlier draft of ours said "step 8", which was a fact about the
  rounding in our loss file rather than about the model. A reviewer caught it.
- **We have run one machine.** Whether bit-identity survives a different vendor, OS, Python, numpy
  or BLAS build is exactly what we cannot answer alone — and a reviewer's differing digest cannot
  answer it either, because all five of those changed at once.

⚠️ **A digest that differs from ours is a result we want, not a mistake to fix before reporting.**
`verify_package.py` prints a mismatch as a finding and exits successfully, for that reason.

---

*Not money, not financial advice, and not a benchmark. The model is deliberately tiny and its
capability is irrelevant to the question.*
