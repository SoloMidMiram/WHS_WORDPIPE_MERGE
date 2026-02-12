# Tools (WHS_WORDPIPE_MERGE)

## make_manifest.py
Generates manifests for files under `_WORK/snapshot`.

### Usage
```powershell
python tools/make_manifest.py --root _WORK/snapshot --out-dir _ARCHIVE/manifests
```

### Outputs
- `_ARCHIVE/manifests/manifest.csv`
- `_ARCHIVE/manifests/manifest.jsonl`

### Notes
- Jalali conversion uses a small pure-Python helper (`tools/jalali.py`).
- Tehran timezone uses `Asia/Tehran` when available; otherwise a fixed +03:30 offset.
