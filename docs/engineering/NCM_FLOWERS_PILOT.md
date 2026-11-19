# NCM-assisted Flowers context pilot

This experiment follows WHS [#8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8) and [#9](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/9). Related A2A research is tracked in [#40](https://github.com/SoloMidMiram/md-mdc-Agents-Skills-MCPs-Kagent-A2A-SubAgents/issues/40) and [#41](https://github.com/SoloMidMiram/md-mdc-Agents-Skills-MCPs-Kagent-A2A-SubAgents/issues/41).

## PILOT-02 disposition

**Genuine inference BLOCKED. Recommendation DEFER.** The 22 wheel checksums and the R3 evidence checksums passed. The Quadmath package and a single-provider OpenMP namespace passed static checks. The gate remains blocked on missing binary-to-source and patch provenance for the selected bundled OpenMP library and incomplete mapping of native components in the Torch CPU core. Installer bootstrap remains under review for its vendored dependencies. No candidate installation, import, tensor operation, checkpoint access, or NCM worker execution was performed. Real Flowers quality, incremental token reduction, NCM latency, peak RSS, and model fallback rate are unmeasured. Suspend setup on this configuration.

### Verified locally

- **Quadmath provider.** Ubuntu Resolute amd64 `libquadmath0=16-20260322-1ubuntu1` matched the SHA-256 in the local package index after verification of the Ubuntu-signed index chain. The package's two dependencies are already present on the host. One HTTPS request transferred 155,450 payload bytes at zero monetary cost. After the protocol reserves, 58,564,806 bytes remained in the slice and 2,640,365,401 bytes remained in the aggregate ledger. The lab retains the package and its extracted ELF as inert evidence. Package SHA-256 is `420e777fef436f397a85ddedde53fbb44f92c7ca8e87d581f9d86573859e1aa4`. [Ubuntu package record](https://packages.ubuntu.com/resolute/amd64/libquadmath0)
- **ABI and loader path.** GNU readelf found all 35 versioned Quadmath symbol requirements from Torch's bundled Fortran library and all 38 versioned glibc imports of the new provider in the checked host `libm` and `libc`. The Torch Fortran object's RUNPATH is `$ORIGIN`. The three Torch objects with direct OpenMP dependencies also use `$ORIGIN`. Both OpenMP files export the 26 named GOMP/OMP imports observed in the CPU core. A Bubblewrap probe with trusted Python exposed the original wheel's OpenMP file and a separate read-only Ubuntu Quadmath path. Host OpenMP, the host loader cache, the host home and Windows mounts were absent. Neither candidate library was mapped. This proves visibility in the tested namespace. Installed loader selection, threading behavior and optional loads remain unverified. R3's three unresolved `test_shim` edges are outside the selected runtime roots, and that test binary remains excluded.
- **Native provenance.** The wheel's OpenMP build ID and SHA-256 were recovered. Its ELF lacks a compiler comment section, and its build notes and public release sources did not establish the exact GCC runtime source build or patch set. The CPU core's embedded component-to-binary mapping is still incomplete. These gaps apply to libraries on the intended execution path. Symbol compatibility cannot resolve them. [PyTorch release sources](https://github.com/pytorch/pytorch/tree/v2.15.0/.ci/docker)
- **Installer.** The R3 synthetic proof and per-wheel input controls cover the explicit Python 3.11 prefix under `-I -S`, startup behavior, binary archive type and script basenames. The known index, self-update, archive and entry-point traversal paths are constrained by no index, no egress, wheel-only hash pins and prevalidated basenames. The review did not establish a complete advisory disposition for the pip 24.0 bootstrap's vendored components. The prior synthetic proof remains the extent of execution evidence. [pip traversal advisory](https://github.com/advisories/GHSA-wf93-45jw-7689)

PyTorch's checkpoint advisory explicitly names 2.15.0 as a fixed release. This is externally documented package-level evidence. The fixed CPU wheel and earlier package advisory review do not resolve the binary provenance findings. No redistribution decision was made. Detailed receipts stay in the local lab. [PyTorch checkpoint advisory](https://github.com/pytorch/pytorch/security/advisories/GHSA-v32g-mr63-3j83)

## Corrected synthetic comparison

The [source fixtures](../../tests/fixtures/ncm_flowers_synthetic.json) and [gold references](../../tests/fixtures/ncm_flowers_synthetic_gold.json) are separate. Gold is used only for literal scoring. The extractor ranks source lines by lexical overlap with the query, returns up to two in source order, and falls back to the raw packet when no term matches. Changing gold leaves the extracted packet unchanged. The annotations have no second-reviewer validation.

| Observed measure | A · Raw | B · Unassisted extraction | Historical B · Oracle-assisted |
| --- | ---: | ---: | ---: |
| Facts retained | 33/33 | 18/33 | 25/33 |
| Critical facts retained | 23/23 | 16/23 | 23/23 |
| Total estimated GPT-2 tokens | 1,168 | 939 | 1,007 |
| Total UTF-8 bytes | 3,971 | 3,110 | 3,442 |
| Median per-case token reduction versus raw | — | 21.40% | 14.19% |
| Raw fallbacks | — | 1/8 | 1/8 |

The seven critical misses included a numerical range, care prohibitions, a side of a disagreement, and evidence qualifications. All eight source identities matched. The historical extractor used gold to attach verbatim critical lines, so its perfect critical-fact retention was oracle-assisted. The estimate covers the complete serialized packet, including instruction, query, source identity, content and any protected source lines. Actual agent token use is unmeasured. [Unassisted aggregate](ncm_flowers_unassisted_metrics.json) · [Historical oracle-assisted aggregate](ncm_flowers_synthetic_metrics.json)

## Harness and verification

The optional subprocess adapter is for a separately qualified local worker. The benchmark rejects over-limit input using IDs from the pinned GPT-2 tokenizer with truncation and padding disabled. The 512-token limit comes from the pinned XSum configuration. The worker receives the untruncated IDs, must report the consumed count, and can time out. An actual pinned-tokenizer probe rejected a 604-token synthetic input before worker invocation. Response validation, raw fallback and complete-packet remeasurement are tested with deterministic fakes. Candidate acceptance requires a separate semantic review and ignores the literal score. No real worker was configured. OS isolation and resource caps remain the responsibility of the qualified worker launch. [Pinned XSum configuration](https://github.com/HazyResearch/ncm/blob/c70274273f489abc73832b2b98584a8483b6b203/config/eval/xsum.yaml)

Run `python -m pytest tests/test_ncm_flowers_pilot.py` for the fake-worker tests. Run `python scripts/experiments/ncm_flowers_pilot.py --gpt2-tokenizer LOCAL_TOKENIZER_JSON` for the synthetic comparison. Leave off the tokenizer option for byte and literal-retention measurements. The canonical Chronicle pipeline and the prior WHS paraphrase regression remain outside the change. WHS #8 acceptance is still open.
