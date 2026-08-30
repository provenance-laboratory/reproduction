# Measurement 4 — the second-machine runbook

⛔ **LOCAL ONLY. This file is not published and is not in the reproduction package.** Measurement 4
is *our* comparison of two machines we control. It is **not** the independent reproduction, which
`PRE-REGISTRATION-v3-CONFIRMATORY.md` §2b forbids us from producing ourselves. Nothing here may be
described as independent, and this document deliberately contains **no trained-artifact digest**,
because publishing one before a public commitment exists would void the pre-registration (v3 §6).

⚠️ **Read `PRE-REGISTRATION-v4-CONFIRMATORY.md` first.** It sets five conditions that decide
whether the result can be called a vendor comparison at all. A pair failing any of them is still
reported — labelled `CONFOUNDED`, naming every variable that moved. So a mismatch costs you the
*claim*, not the *run*.

---

## What configuration A already is

The reference arm is on this machine and is already admissible:

```
CPU                       12th Gen Intel(R) Core(TM) i5-1240P
platform                  Windows-11-10.0.26200-SP0
Python                    3.14.3
numpy                     2.5.1
OpenBLAS build config     Haswell MAX_THREADS=24
runtime architecture      Haswell        (observed)
threadpoolctl             3.6.0
reference run directory   runs/tpc-thr-1
```

⭐ **`threadpoolctl` was installed and configuration A was re-run to confirm the observation does
not perturb the measurement — the weights came back bit-identical.** That is why the reference arm
is `runs/tpc-thr-1` rather than `runs/thr-1`: same bytes, but the runtime architecture and
effective thread count are now *observed*, which v4 condition 5 requires of **both** arms.

---

## What the second machine needs, and why each item is there

| Requirement | Why | v4 condition |
|---|---|---|
| An **AMD** CPU | the variable under test | — |
| **Windows 11** | family and major version must match arm A | 1 |
| **Python 3.14.x** | must match to major.minor | 2 |
| **numpy 2.5.1**, exactly | must match exactly | 3 |
| installed from **PyPI wheels** | the wheel carries the same bundled OpenBLAS, so the build-configuration line matches by construction | 4 |
| **threadpoolctl** | without it the runtime architecture and effective thread count are unobserved | 5 |

⚠️ **If the AMD machine cannot run Windows 11, run it anyway.** The comparison will be labelled
`CONFOUNDED` on condition 1 and reported as such. That is a worse result, not a wasted one — and
it is a far better outcome than quietly reporting a vendor claim the design cannot support.

---

## Steps

### 1. On this machine — prepare the transfer

```bash
cd provenance-laboratory/reproduction
python build_package.py
```

Copy `package/` to the AMD machine (USB, or a share). It contains `train.py`, the corpus and its
manifest, and the protocol documents. It contains **no expected digest**: the package is
target-free by design.

### 2. On the AMD machine — install the environment

```bash
python --version                 # must report 3.14.x
python -m pip install numpy==2.5.1 threadpoolctl
python -c "import numpy, threadpoolctl; print(numpy.__version__, threadpoolctl.__version__)"
```

⛔ **Do not use conda, and do not use a system numpy.** Those ship a different BLAS — MKL or a
distribution build — which moves condition 4 and turns the comparison into a library comparison
wearing a vendor label.

### 3. On the AMD machine — verify the corpus arrived intact

The package ships `SHA256SUMS` covering every file in it. Check the transfer against it:

```bash
cd package
python -c "import hashlib,pathlib,sys;bad=[l.split()[1] for l in pathlib.Path('SHA256SUMS').read_text().splitlines() if l.strip() and hashlib.sha256(pathlib.Path(l.split()[1]).read_bytes()).hexdigest()!=l.split()[0]];print('MISMATCH:',bad) if bad else print('all files match SHA256SUMS')"
```

Then confirm the corpus itself re-derives to the committed Merkle root:

```bash
python corpus/build_corpus.py --verify
```

If either check fails, stop. The two arms would not share an input, and `measure_hardware.py`
refuses that comparison rather than producing a meaningless one — but it can only refuse on the
*specification*, not on corrupted bytes carrying the right filename, which is why this step is
here.

### 4. On the AMD machine — run the arm

```bash
python train.py --out runs/amd-thr-1 --threads 1 --seed 20260829
```

⚠️ **`--threads 1` and `--seed 20260829` are not defaults; they are the arm A settings.** Thread
count is a known cause of divergence in this pipeline, so a mismatch makes the pair
`NOT COMPARABLE` — the tool checks this and says so.

Confirm the run observed what condition 5 needs:

```bash
python -c "import json;e=json.load(open('runs/amd-thr-1/run.json'))['environment'];print(e['cpu']);print(e['platform']);print('arch',e['blas_runtime_arch']);print('threads',e['threads_effective'] is not None);print('admissible',e['admissible_for_causal_attribution'])"
```

`admissible` must be `True`. If it is `False`, `threadpoolctl` is not installed in the interpreter
that ran the training — fix that and re-run before copying anything back.

### 5. Copy back

Copy `runs/amd-thr-1/` — both `run.json` and `weights.npz` — to
`provenance-laboratory/reproduction/runs/amd-thr-1/` on this machine.

### 6. On this machine — take the measurement

```bash
python measure_hardware.py --a runs/tpc-thr-1 --b runs/amd-thr-1
```

It prints each of the five conditions with what it observed, the two weight digests, whether they
are bit-identical, and one of three verdicts:

```
ISOLATING       both arms met 1-5 and share an input specification
CONFOUNDED      reported in full, naming the conditions that failed;
                may NOT be cited for a claim about CPU vendor
NOT COMPARABLE  the arms do not share a specification, so the byte
                comparison measures nothing
```

The record is written to `MEASUREMENT-4.json`.

### 7. Report it, whatever it says

⛔ **v3 §6: "any measurement going unreported because it was inconvenient" invalidates the
pre-registration.** All seven measurements are reported whatever they say. Update
`PHASE-2-FINDINGS.md`, which currently records measurement 4 as `NOT DONE`, and rebuild the review
packet.

---

## What an ISOLATING result would and would not establish

⚠️ **It isolates the CPU only among the variables v4 §2 lists.** Microcode revision, BIOS and
firmware settings, kernel scheduling and CPU feature availability beyond the recorded SIMD baseline
are neither held constant nor observed. The honest sentence is *"these two machines, matched on
operating system, Python, numpy and BLAS build, produced the same bytes"* — or did not. It is not
*"CPU vendor determines bit-identity"*, and `measure_hardware.py` writes that limitation into its
own record so the constraint travels with the number.

---

*Governed by [`PRE-REGISTRATION-v4-CONFIRMATORY.md`](PRE-REGISTRATION-v4-CONFIRMATORY.md) §2 ·
Reported in [`PHASE-2-FINDINGS.md`](PHASE-2-FINDINGS.md) · Tool:
[`measure_hardware.py`](measure_hardware.py)*
