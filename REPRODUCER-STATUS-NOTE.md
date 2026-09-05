# Reproducer status — decided before the call, not after

*5 September 2026.*

⛔ **This has to be settled before `REPRODUCTION-CALL.md` is published.** §2b's whole design is that
nobody is approached in a way not equally available to everyone; a party whose status is worked out
*after* it files is a party whose status was worked out to suit the result.

⚠️ **No party is named in this file, and none will be named in a paper, a deposit or a repository.**
A filing is public at the address it is filed to; whoever files signs their own filing there. This
document is a rule about what we may write, not a record of who anybody is.

---

## 1. What §2b actually says

Three rules, and none of them bars anyone from filing:

```
WE DO NOT ASSIST                 a reproducer receives the published package and nothing else.
                                 Any assistance of any kind is LOGGED AND REPORTED, and an
                                 assisted run is reported separately from unassisted runs

WE DO NOT CHARACTERISE           the paper reports what was filed, by whom, at a public address
INDEPENDENCE                     a reader can open. It will NOT assert that a reproducer is
                                 independent -- that is the reader's judgement, not ours

NO PRIVATE APPROACH              the re-run is solicited by a public, open request, "with no
                                 party approached in a way that is not equally available to
                                 everyone"
```

⇒ **Every report is reported.** §2b says so directly: *"A failed reproduction is data. A
reproduction that diverges is measurement 5. A reproduction we dislike is still in the paper."*

## 2. ⇒ The rule that follows, and it is short

**Report the filing and the address. Assert nothing about the filer.**

```
WRITE      "a report was filed by <the handle that filed it> at <URL>", and let the reader
           open the thread

DO NOT     write "independent" about any specific filer. Not once, not in a caption, not in
WRITE      an abstract. §2b forbids it and the forbidding is the point

DO NOT     count a filing toward the gap Paper A measured, unless the filing itself is what
COUNT      closes it in a reader's judgement rather than in ours
```

⚠️ **The second and third are different obligations and both are needed.** Never writing the word is
not sufficient on its own: a paper whose central claim is about *independent* reproduction, which
reports a filing and moves on, has made the claim by arrangement rather than by assertion. **The
protection is in what the paper counts, not only in what it says.**

## 3. What such a filing is genuinely good for

**Finding out whether a stranger can run the package at all.** That risk is real and has already
bitten once: v2's §2a gate refused conda/MKL, macOS Accelerate and plain OpenBLAS outright, so
three honest installs could have filed nothing but *"I could not run it"* — which §2c would then
have scored as an ecosystem finding about our own gate.

```
a run that FAILS      extremely valuable, costs nothing in credibility, and is the outcome we
                      are least able to produce ourselves -- we know too much about the package

a run that DIVERGES   measurement 5, reported

a run that MATCHES    evidence the package works. Whether it is evidence for the headline is
                      the reader's call, from the thread, which is exactly §2b's design
```

⇒ **Diagnostic value is certain; evidential value is the reader's to assign.**

## 4. The order, which is the part that matters

```
1  publish REPRODUCTION-CALL.md, with the public address and the close date
2  anyone who wishes to file, files against that public call
3  the paper reports what was filed and where, and characterises nobody
```

⛔ **Not: arrange a run, then publish a call it can be said to have answered.** That is the private
approach §2b prohibits, and the fact that it would be easy to describe afterwards as *"filed
against the call"* is precisely the reason to fix the order in advance.

## 5. ⚠️ And one thing that is now true of every reproducer

The reference weights digest has been public in the repository since v5 — see
`FINDING-2026-09-05.md` §3. **Any party filing after that date could in principle have known the
target before starting.** That is a limitation on what *any* matching result can support, and it
must be disclosed whatever the window produces.

---

*Nothing here is executed. `REPRODUCTION-CALL.md` has not been published, the address and close date
do not exist yet, and the commitment gate is currently refusing — see `FINDING-2026-09-05.md`.*
