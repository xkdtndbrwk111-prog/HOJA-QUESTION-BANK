# HOJA game runtime packages (v1)

Read-only runtime copies of the APPROVED units, generated from this repository's approved sources at commit
`9573f91d2845a9667e2540df051f499d937dd94a` by `SMQ-Project-A/experimental/usage-v4-unified/approved-catalog/build_content_packages.mjs`.

- `approved-packages/v1/INDEX.json` lists every package with its byte length and SHA-256.
- The game loads a package only through a URL pinned to a 40-hex commit of this repository and only if the
  downloaded bytes hash to the SHA-256 in its trusted catalog; anything else is rejected.
- 23 units / 732 questions. Do not edit these files by hand: regenerate them from the approved sources.
- Publishing these files does not activate them in the game; activation is a separate, explicit deployment step.
