# Pre-registration — what reproducibility costs

**Written and OpenTimestamped before the first training step, and before any measurement exists.**

⛔ **This document exists so that the result cannot be a retrofit.** The expected outcome is written
below, in advance, including the outcome in which the experiment *fails to achieve what it set out
to achieve* — because that failure is the more interesting result and would otherwise look like a
story assembled after the fact.

---

## 1. The claim to be measured

> **Bit-identical reproduction of a trained model from a published specification: is it achievable,
> and what does it cost?**

Everyone assumes it is possible in principle and too expensive in practice. **Neither half has been
measured cleanly on a worked example.** That gap is the paper.

This is the second of a pair. Paper A — *What a Model Release Lets You Check* — established the
standard by measuring twelve releases against 22 axes and found that **eight of those axes are
satisfied by none of them**: corpus digests, a commitment made before training, weights signing,
weights timestamping, and independent reproduction of either kind. Paper A measures the gap. **This
paper is an attempt to close it once, on a deliberately tiny artifact, and to report what that
cost.**

⇒ In this order the two are one argument. In the other order they are two disconnected papers.

## 2. Protocol, fixed in advance

```
model        DELIBERATELY TINY, under 100M parameters. Scale is not the point and actively
             obscures it. Capability is irrelevant and will not be benchmarked
corpus       small, fixed, and REDISTRIBUTABLE. Licensing-clean at the outset, because a corpus
             we cannot redistribute makes the replication package impossible -- the thing the
             paper is about
commitment   the corpus Merkle root is published AND OpenTimestamped BEFORE the first training
             step. The proof is a Bitcoin block, as with this project's other pre-registrations
pipeline     deterministic by construction: fixed seeds, fixed data order, pinned kernels,
             deterministic reductions, pinned environment digest
publication  corpus manifest + code + seeds + environment digest + weights, each hashed and signed
check        AN INDEPENDENT PARTY re-runs and compares weights BIT FOR BIT
```

⚠️ **The independent reproduction is the contribution.** Determinism claimed by the party that
built the pipeline is not evidence. Without a second party this is a blog post, and the second
party must be secured *before* training starts, not recruited afterwards to bless a result.

## 3. The measurements

These are the paper, not the model.

```
1  wall-clock overhead of determinism vs the same run unconstrained     <- the headline cost
2  storage and bandwidth overhead of the manifest and artifacts
3  does bit-identity hold on IDENTICAL hardware?
4  does bit-identity hold on DIFFERENT hardware?
5  if not: the divergence magnitude, and the first layer/step where it appears
6  engineering hours to make an ordinary pipeline deterministic         <- honest, self-reported
```

## 4. ⛔ The expected finding, written BEFORE the experiment

**Bit-identity across different hardware will probably fail.** The reasons are principled rather
than incidental:

- floating-point addition is not associative, so **reduction order changes the result**
- kernel selection varies by architecture and by library version
- non-deterministic atomics are the default in fast kernels

**If that is what happens, it is not a failed experiment. It is the result**, and a sharper one
than success would have been:

> **Bit-identical reproduction is achievable same-hardware and not across hardware. Verifiable model
> provenance therefore requires either hardware pinning or a stated numerical tolerance — and a
> tolerance is a weaker guarantee that must be quantified, not waved at.**

That reframes the field's casual use of the word *reproducible*.

⇒ **The paper is written to be publishable under either outcome, and this paragraph is why.** If
bit-identity holds across hardware, the finding is that it is achievable and here is its cost. If
it does not, the finding is that the word has been doing work it cannot support. Both were
committed to in advance; neither is a rescue.

## 5. What this paper will decline to do

- **No model-quality claim.** The model's capability is irrelevant and benchmarking it would be
  scope creep into the thing Paper A explicitly refuses to measure.
- **No recommendation.** Paper A measures the gap and declines to prescribe. This one measures a
  cost and declines to say who should pay it.
- **No generalisation from one artifact.** A single worked example bounds nothing. It establishes
  that a number exists and what it was, once, under stated conditions.

## 6. What would invalidate this pre-registration

Stated so that a reader can hold the finished paper against it:

- changing the model or corpus after training has begun, without recording the change and its date
  here
- reporting bit-identity without an independent party's re-run
- reporting a tolerance without quantifying it
- benchmarking the model's capability anywhere in the paper
- any measurement in section 3 going unreported because it was inconvenient

**All six measurements are reported whatever they say.** A measurement omitted is a result.

---

⚠️ **Status at signing: nothing has been trained.** No corpus has been fixed, no model has been
built, no measurement exists. This document is the whole of the commitment.

**NOT a product, and not a recommendation.**
