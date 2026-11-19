# WHS-AI-01 Chronicle context packs

The experimental exporter will read an existing Chronicle run and compare full raw context (A), the frozen PR #12 extractor (B0), and structural retrieval (B1). Its output is a derived research artifact. Existing Chronicle survivor identities and source locators remain authoritative.

The run manifest alone carries no source byte digests. The experiment therefore requires a trusted receipt that pins both the run artifacts and original source bytes. A receipt must be captured from known inputs and reviewed outputs. Minting hashes from an unknown or stale run cannot establish provenance.

The benchmark keeps gold separate from retrieval. Tune on a designated synthetic partition, freeze B1, and score a separate holdout. Report all raw fallbacks, refused provenance, complete-packet estimates and remaining limits. Published evidence is synthetic only.
