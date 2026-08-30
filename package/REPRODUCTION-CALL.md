# Reproduce this model, and tell us what you got

**We trained a small model and published everything needed to train it again. We are asking anyone
to re-run it and report whether the weights come out bit-for-bit identical.**

You do not need permission, you do not need to tell us in advance, and you do not need to succeed.
**A failed reproduction is the same kind of result as a successful one and is reported the same
way.**

---

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

File a report at the address published with these artifacts. Fill in whatever you have; **a partial
report is worth more than no report**, and the fields that matter most are the CPU, the thread
count and the digest you got.

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
([`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) §2c) so that it cannot later look like a consolation
prize assembled after silence.

The companion paper measured twelve public model releases against 22 axes and found that
**independent reproduction is satisfied by none of them**. If an artifact published expressly to be
reproduced — a few megabytes, licensing-clean, deterministic by construction, every input hashed and
timestamped, runnable in under a minute on a laptop with no GPU — **also goes unreproduced**, then
the barrier is not cost, not scale, and not licensing. It would be a finding about the ecosystem
rather than about this artifact, and a sharper one than a successful reproduction would have been.

## What we already know, so you are not chasing our bugs

Reported here rather than discovered by you, because withholding it would waste your time and
measure nothing:

- **Thread count alone changes the weights.** On our machine, `threads=1,2,4,8,16` produced five
  distinct models. That is why the pin is in `train.py` before `import numpy` — OpenBLAS reads
  those variables at load time, so setting them later silently does nothing.
- **The models differ in their bits and not in their behaviour.** Between our threads=1 and
  threads=16 runs, the relative L2 difference is about `8e-06` and the final loss agrees to seven
  significant figures, while 83% of parameters differ. **If your digest differs from ours, the model
  is probably fine and the artifact is still not reproducible.** Both halves of that sentence are
  the point.
- **We have only run configuration A** — one Intel hybrid-core laptop. Whether bit-identity survives
  a different vendor or a different instruction set is exactly what we cannot answer alone.

---

*Not money, not financial advice, and not a benchmark. The model is deliberately tiny and its
capability is irrelevant to the question.*
