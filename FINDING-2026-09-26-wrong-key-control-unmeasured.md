# Finding, 26 September 2026 — the wrong-key control has never run

⛔ **`test_controls.py`'s "a valid signature by a key that is not the protocol's" is `unmeasured`,
and has been.** It is the case that would catch an attacker who signs an edited governing document
with their own key. The suite reports:

```
check_signature.py -- a valid signature by a key that is not the protocol's
  ⚠ verify() names the wrong key    unmeasured: gpg could not sign with the throwaway key
```

The suite is right to count this against itself rather than pass it: an unrun control is not a
refused attack. `security_ok` is `false` for this reason alone — **74 attacks were refused and none
passed**, and the suite prints that in its own words: *"THE POSITIVE CONTROL FAILED, AND NO ATTACK
PASSED."* The one counted on the "passed that should not have" line is this hygiene item, not a
breach.

## The cause, reproduced

The throwaway keyring is built correctly and `--quick-gen-key` succeeds. The signing call is:

```
gpg --homedir <tmp> --batch --pinentry-mode loopback --passphrase "" \
    --local-user alt@example.invalid --armor --detach-sign -o <gov>.asc <gov>
```

`<gov>.asc` already exists in the sandbox, having been copied in with the document. In `--batch`
mode gpg refuses to overwrite an existing output file and exits:

```
gpg: signing failed: File exists
```

Reproduced twice outside this tree on a fresh keyring: without `--yes` the call fails with exactly
that message; with `--yes` it writes the signature and the control can run. Adding `--yes` to the
signing call — or unlinking the target first — is the whole of it.

⚠️ **The generation step is not the problem, so the error text points one call too early.** The
message says "could not sign with the throwaway key", which reads as a key or agent fault on this
machine; it is neither. Anyone reading it would look at gpg's configuration rather than at the
output path, and that is where the time would go.

## Why this is not fixed here

`test_controls.py` is pinned by **v22**, at `8249b95f69849159`, and v22 was signed and stamped on
25–26 September and has not anchored yet. Editing the file now would break the pin of a document
that was just put in force, which is the moving-target property v3 exists to remove. The repair is
a protocol version: **v23 re-pins `test_controls.py` at the repaired bytes and says so.**

Until then the state is stated rather than hidden: one control in the suite is unmeasured, the
reason is known and small, and no attack has passed.
