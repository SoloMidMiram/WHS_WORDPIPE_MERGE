# Chronological & Technical Development History for `yt_mkv_downloader.sh` & `YoDwV2.py`

## Introduction

This report reconstructs the evolution of the YouTube‐to‐MKV download
pipeline composed of the Bash script `yt_mkv_downloader.sh` and the
optional orchestration controller `YoDwV2.py`. The chronology and
technical narrative are extracted from the “YouTube Vids + Subtitle
Download Manual – not capability mode” diary (with tracked changes), the
final modularised code, and the author’s comments. The goal is to
understand **how each section of the script evolved**, which problems
were encountered, the decisions behind the modular refactor, and the
lessons learned for future improvement. External citations are used to
support general principles and best practices documented in the diary.

The report contains two tables of contents to aid navigation:

1.  **Chronological table of contents** – lists major dates and events
    in the development history.
2.  **Thematic table of contents** – categorises the history into
    functional themes, aligning with the user‑provided categories
    (metadata normalisation, subtitle handling, muxing, etc.).

------------------------------------------------------------------------

## Chronological Table of Contents

| Date (UTC±0) | Milestone | Relevant modules/functions |
|----|----|----|
| **Pre‑May 2025** | **Early monolithic script**. Script uses a simple `safe_filename` routine to replace spaces and special characters. Logging is ad‑hoc; all logic lives in a single file. | `safe_filename`, `download_video_and_detect_file` |
| **1 Aug 2025** | **First tracked change**. Diary table of contents updated; the author begins formalising a plan to modularise the script. | Outline for modules |
| **7 Aug 2025** | **Major modular refactor (tracked changes)**. New modules are defined for filename normalisation, subtitle handling, muxing and logging. Functions `safe_filename` becomes `normalize_name`; a central logging function (`log`) and `exit_with_log` are introduced. Additional modules such as `fetch_video_metadata`, `validate_mkv_integrity` and `convert_vtt_to_srt` are outlined for future rounds. | `normalize_name`, `prepare_subtitles_and_verify`, `embed_prioritized_subs`, `mux_with_validation`, `exit_with_log`, `log` |

------------------------------------------------------------------------

## Thematic Table of Contents

1.  [I. Early Script Design & Issues](#i-early-script-design--issues)
2.  [II. Metadata & Filename Normalization
    History](#Xf526c6136e649a646b2d8c1f649c57c6dc7e9ab)
3.  [III. Subtitle Deduplication & Conversion
    Challenges](#X86aa12e90ada1191fdd651910cd48d4adeadb6e)
4.  [IV. Muxing Evolution and FFmpeg
    Failures](#iv-muxing-evolution-and-ffmpeg-failures)
5.  [V. Validation Pipelines and Log
    Resilience](#X88a6da5ab91dbb7b3df47b93950528652a67c5b)
6.  [VI. Lessons, Anti‑Patterns and Advice for the
    Future](#X2e16d3ebbd36d1934f5f88cb63deef6dc8f7d14)

------------------------------------------------------------------------

## I. Early Script Design & Issues

### Description

The earliest version of `yt_mkv_downloader.sh` was a monolithic Bash
script that bundled downloading, subtitle extraction, muxing and
housekeeping in a single file. It relied on a home‑grown function
`safe_filename` to strip spaces and punctuation from video titles.
Logging consisted of scattered `echo` statements. The script lacked
robust error handling and functions often mutated global variables,
which made debugging difficult. A summary of early issues from the diary
includes:

- **Naming confusion**: the function `safe_filename` performed string
  trimming, but multiple versions of it were scattered in the file,
  sometimes conflicting.
- **Error propagation**: when `yt-dlp` failed due to restricted videos,
  the script exited silently without preserving logs; there was no
  central logging or timestamping.
- **Cookie extraction overkill**: an experimental path attempted to use
  Selenium headless browsers to extract cookies. The diary noted that
  headless browsers can be detected by websites, leading to blocking or
  CAPTCHAs[\[1\]](https://scrapeops.io/selenium-web-scraping-playbook/python-selenium-make-selenium-undetectable/#:~:text=TLDR%3A%20How%20to%20Make%20Selenium,Undetectable).
  The author eventually abandoned Selenium and recommended exporting
  cookies manually using browser extensions like *Get cookies.txt*.
  External documentation confirms that cookies can grant access to
  restricted videos and are easily exported to a file for
  `yt-dlp`[\[2\]](https://ytdlnis.org/docs/guides/cookies#:~:text=Cookies).
- **Mixing concerns**: the script downloaded video and audio, converted
  subtitles, and muxed them in a linear sequence. There was no
  separation of concerns or modular functions.

### Early Function Snippets

- `safe_filename` – originally trimmed trailing dots and replaced
  non‑ASCII characters. Multiple versions existed, causing confusion.
  Example pseudocode:

<!-- -->

    safe_filename() {
      # remove invalid characters, convert spaces to underscores, trim dots
      local name="$1"
      name="${name//[^a-zA-Z0-9_.-]/_}"
      echo "$name"
    }

- `download_video_and_detect_file` – invoked `yt-dlp` with flags such as
  `--merge-output-format mkv`. The script expected the output file to
  appear in the working directory and used `ls -t` to pick the newest
  file. When videos were restricted, the script failed silently.

### Timeline Commentary

In **early 2025**, the script successfully downloaded public videos but
struggled with age‑restricted or region‑locked content. The diarist
experimented with Selenium to extract cookies but found the approach
brittle because headless Selenium is often detected by
websites[\[1\]](https://scrapeops.io/selenium-web-scraping-playbook/python-selenium-make-selenium-undetectable/#:~:text=TLDR%3A%20How%20to%20Make%20Selenium,Undetectable).
The diary emphasised switching to manual cookie export via browser
extensions[\[2\]](https://ytdlnis.org/docs/guides/cookies#:~:text=Cookies).
These lessons set the stage for the major refactor of August 2025.

------------------------------------------------------------------------

## II. Metadata & Filename Normalization History

### Function and Origin

The `normalize_name` function supersedes the earlier `safe_filename`.
The diary documents this as **Module 1:**
`safe_filename`** → **`normalize_name`. The function aims to produce
file names that are compatible across operating systems while preserving
readability. Key features include:

- **Unicode normalisation**: the function uses `iconv` or `sed` to
  remove non‑printable characters and convert accented characters to
  ASCII.
- **Whitespace & punctuation handling**: spaces and unusual punctuation
  are replaced with underscores. Leading and trailing underscores are
  trimmed.
- **Camel‑case conversion**: an optional `to_camel_case` helper converts
  phrases like `my_video_title` to `MyVideoTitle` when constructing MKV
  names.

### Transformation Path

1.  **Early stage** – multiple definitions of `safe_filename` existed.
    Each trimmed invalid characters slightly differently, leading to
    inconsistent output.
2.  **Aug 7 2025 refactor** – `safe_filename` was consolidated into a
    single function `normalize_name`. The tracked changes highlight
    comments like: “Only **one definition** for `main`, `to_camel_case`,
    `trim_safe_filename`, `normalize_name`” (paraphrased from the
    diary). The refactor centralised all naming logic to one place,
    reduced duplication and improved maintainability.
3.  **Future plan** – the diary proposes generating names based on video
    metadata (e.g., `Uploader_YYYYMMDD_Title`) once
    `fetch_video_metadata` is implemented.

### Problems Encountered

- **Multiple naming rules**: early versions applied different
  transformations depending on the location in the script. For example,
  subtitles were stored under a sanitized base name while MKVs used a
  different pattern. This caused mismatches during muxing.
- **Illegal characters**: some video titles contained characters (like
  emojis or slashes) not handled by the simple `tr` command. The new
  function uses `iconv` to strip unsupported characters.
- **Camel‑case vs underscores**: during refactoring, the author debated
  whether to use camel‑case or underscores. The final solution allows
  both by converting at the call site via `to_camel_case`.

### Tips & Best Practices

- **Centralise sanitisation**: keep a single function for filename
  normalisation. This avoids divergence and ensures consistent output
  across the script.
- **Use external tools**: `iconv` can remove invalid UTF‑8 sequences
  gracefully. `sed` and `tr` are safer for batch replacements than
  manual pattern substitution.
- **Plan for metadata**: storing metadata in JSON or YAML enables
  constructing meaningful file names later. A `fetch_video_metadata`
  module is planned to parse `yt-dlp -j` output.

------------------------------------------------------------------------

## III. Subtitle Deduplication & Conversion Challenges

### Functions

The script handles subtitles in two stages:

1.  `prepare_subtitles_and_verify` – orchestrates the download and
    conversion of subtitle files. It invokes `embed_prioritized_subs`
    and checks whether the expected `.srt` files exist.
2.  `embed_prioritized_subs` – given multiple `.srt` or `.vtt` subtitles
    for a video, this function filters duplicates, prioritises certain
    language codes (e.g., `en`, `en-US`), and renames them consistently.
3.  `convert_vtt_to_srt` – (planned) a helper to convert `.vtt` captions
    to `.srt` format using `ffmpeg` or `iconv`.

### Origins & Evolution

- **Early approach** – the script simply downloaded whatever subtitles
  were available via `yt-dlp --write-sub`. Duplicate or auto‑generated
  subtitles (e.g., `en.vtt` and `en-US.vtt`) were both kept, leading to
  confusion.
- **Refactor impetus** – the diary noted that some videos had up to 20
  subtitle files, many of which were duplicates or auto‑translated. The
  `embed_prioritized_subs` module was introduced to deduplicate by hash
  and prioritise languages. The function logs which subtitles were kept
  and which were discarded.
- **Validation** – `prepare_subtitles_and_verify` ensures that after
  conversion, at least one `.srt` file exists; otherwise it triggers an
  error and logs a message.

### Problems Encountered

- **Duplicate languages**: videos sometimes have both `en.vtt` and
  `en-US.vtt`. Simply keeping one could lose nuanced differences; the
  module therefore hashes the content to detect duplicates before
  discarding.
- **Inconsistent file names**: because the early script did not
  normalise subtitle names consistently, muxing sometimes failed to map
  the right file. This was solved by calling `normalize_name` on
  subtitle base names.
- **VTT to SRT conversion**: `ffmpeg` sometimes produced SRTs with
  overlapping timestamps. The planned `convert_vtt_to_srt` would
  incorporate a custom parser to correct overlapping cues.

### Tips & Best Practices

- **Prioritise human‑edited subtitles**: where multiple subtitles exist,
  favour those labelled “manual” or “CC” over auto‑generated ones.
- **Hash duplicates**: use `md5sum` to detect identical subtitle files
  even if their names differ.
- **Validate after conversion**: ensure at least one subtitle is
  available before proceeding to muxing; otherwise, skip subtitle
  embedding gracefully.

------------------------------------------------------------------------

## IV. Muxing Evolution and FFmpeg Failures

### Function: `mux_with_validation`

This function wraps the `ffmpeg` call that combines video, audio and
subtitles into an MKV container. It also ensures the result is playable
and matches the expected duration.

### Evolution

1.  **Original design** – the script used
    `ffmpeg -i video.mp4 -i audio.m4a -c copy output.mkv` after
    downloading with `yt-dlp --merge-output-format mkv`. However,
    `yt-dlp` can already merge streams when passed
    `--merge-output-format mkv`[\[3\]](https://chuck.is/yt-dlp/#:~:text=Command%20Description%20yt,of%20file%20into%20an%20MKV).
    Calling `ffmpeg` again sometimes corrupted the file because the
    input streams were already merged.
2.  **Bug discovery** – the diary documented an issue where `ffmpeg`
    would reset the position of one input after finishing the other,
    causing mismatched durations. The author created
    `mux_with_validation` to wrap `ffmpeg`, check for errors and
    reattempt with different input orderings. It also calculates file
    duration via `ffprobe` and ensures that the final MKV is not shorter
    than expected.
3.  **Validation** – after muxing, the script calls
    `validate_mkv_integrity` (planned) which uses `ffprobe` to compare
    expected and actual durations. If validation fails, the script logs
    an error and suggests re-downloading.

### Problems Encountered

- **Corrupted MKVs**: double merging via `yt-dlp` and `ffmpeg` produced
  broken files. The fix was to let `yt-dlp` handle the merge or to use
  `ffmpeg` only once, not both.
- **Missing subtitles**: when subtitles were absent, `ffmpeg` would
  still create an MKV but with blank tracks; this caused confusion
  during playback. The new code only adds subtitle streams if they
  exist.
- **Disk space**: large temporary files (video, audio, subs) consumed
  disk space. The refactor introduced cleanup steps to remove temporary
  files after successful muxing.

### Tips & Best Practices

- **Use** `yt-dlp`**'s merge option**:
  `yt-dlp [URL] --merge-output-format mkv` merges audio/video into MKV
  during
  download[\[3\]](https://chuck.is/yt-dlp/#:~:text=Command%20Description%20yt,of%20file%20into%20an%20MKV).
  Only call `ffmpeg` when additional streams (subtitles) must be added.
- **Validate with** `ffprobe`: check the output MKV for expected
  duration and number of streams. Automate retries if mismatches occur.
- **Clean up**: remove intermediate files once the final MKV is
  validated to save disk space.

------------------------------------------------------------------------

## V. Validation Pipelines and Log Resilience

### Logging Functions

During the August refactor, the author introduced a **central logging
mechanism**:

- `log` – accepts a log level (INFO/ERROR) and a message, prepends a
  timestamp, writes to both the console and a log file.
- `exit_with_log` – logs an error message and exits with a non‑zero
  status. It ensures that failure points are captured uniformly.

### Validation Pipeline

- `fetch_video_metadata` (planned) – will call `yt-dlp -J` to retrieve
  JSON metadata. The script can then extract uploader name, upload date
  and other fields to validate downloads.
- `validate_mkv_integrity` (planned) – uses `ffprobe` to verify the
  final MKV has the expected number of streams and durations.
- **Rate‑limiting and concurrency** – the Python controller `YoDwV2.py`
  uses Aiogram middlewares to limit concurrent downloads. It spawns
  asynchronous tasks to run the bash script and returns results to
  Telegram users. The code includes a `debug_context_snapshot` to
  capture environment variables and file lists for debugging.

### Problems & Solutions

- **Non‑atomic logging**: earlier, logs were printed at random points.
  If the script crashed, the log state was lost. The new logging
  functions centralise output and ensure logs survive even if the script
  exits.
- **Weak scope isolation**: functions would modify global variables,
  making it hard to trace errors. The refactor encloses variables within
  functions and uses local scopes.
- **Missing context**: when users reported issues, there was no context
  about the environment. The Python bot adds context snapshots to the
  debug reports, including environment variables and file lists.

### Tips & Best Practices

- **Defensive programming**: anticipate and guard against failure modes.
  A general software engineering principle is to design functions that
  expect inputs to be incorrect and handle them
  gracefully[\[4\]](https://www.conquer-your-risk.com/2023/07/20/the-code-knight-mastering-the-craft-of-defensive-programming/#:~:text=Defensive%20programming%20is%20about%20creating,both%20expected%20and%20unexpected%20issues).
- **Centralised logging**: all messages should funnel through a single
  logger to maintain consistent formatting and preserve ordering.
- **Validate early and often**: checking the integrity of downloads and
  outputs prevents silent corruption.

------------------------------------------------------------------------

## VI. Lessons, Anti‑Patterns and Advice for the Future

The diary emphasises lessons learned during development. Some of these
are general software engineering principles, while others are specific
to the YouTube download domain.

1.  **Avoid overcomplicated solutions**. Using headless Selenium to
    extract cookies was overkill and prone to detection by
    websites[\[1\]](https://scrapeops.io/selenium-web-scraping-playbook/python-selenium-make-selenium-undetectable/#:~:text=TLDR%3A%20How%20to%20Make%20Selenium,Undetectable).
    Instead, manually exporting cookies is simpler and more
    reliable[\[2\]](https://ytdlnis.org/docs/guides/cookies#:~:text=Cookies).
2.  **Use official tool capabilities**. `yt-dlp` can merge streams into
    MKV
    itself[\[3\]](https://chuck.is/yt-dlp/#:~:text=Command%20Description%20yt,of%20file%20into%20an%20MKV);
    avoid redundant calls to `ffmpeg` that can corrupt outputs.
3.  **Embrace defensive programming**. Design functions that handle
    unexpected inputs, return errors clearly and keep the system
    robust[\[4\]](https://www.conquer-your-risk.com/2023/07/20/the-code-knight-mastering-the-craft-of-defensive-programming/#:~:text=Defensive%20programming%20is%20about%20creating,both%20expected%20and%20unexpected%20issues).
4.  **Modularise for maintainability**. Breaking the script into
    well‑named functions (`normalize_name`,
    `prepare_subtitles_and_verify`, `mux_with_validation`, etc.) makes
    it easier to test and reuse components.
5.  **Document and timestamp changes**. The diary’s tracked changes
    provide a clear timeline of modifications. Keeping such records
    helps future maintainers understand why decisions were made.
6.  **Plan for concurrency**. The Python controller introduces rate
    limiting and asynchronous execution to handle multiple download
    requests without overwhelming resources.
7.  **Future Work**. Implement the planned modules
    (`fetch_video_metadata`, `validate_mkv_integrity`,
    `convert_vtt_to_srt`) and integrate them with the Telegram bot.
    Consider adding features like downloading playlists, handling
    retries automatically and producing JSON reports summarising each
    download.

------------------------------------------------------------------------

## Conclusion

The evolution of `yt_mkv_downloader.sh` and its companion controller
`YoDwV2.py` demonstrates a shift from a monolithic, brittle script
towards a modular, robust pipeline. By tracking changes and documenting
lessons learned, the author not only improved the reliability of the
tool but also created a reference for future developers. Key milestones
include the consolidation of filename normalisation, introduction of
subtitle deduplication, improved muxing validation, centralised logging
and asynchronous orchestration. These changes align with best practices
in software engineering and underscore the value of reflective
documentation.

------------------------------------------------------------------------

[\[1\]](https://scrapeops.io/selenium-web-scraping-playbook/python-selenium-make-selenium-undetectable/#:~:text=TLDR%3A%20How%20to%20Make%20Selenium,Undetectable)
Python Selenium - How To Make Selenium Undetectable \| ScrapeOps

<https://scrapeops.io/selenium-web-scraping-playbook/python-selenium-make-selenium-undetectable/>

[\[2\]](https://ytdlnis.org/docs/guides/cookies#:~:text=Cookies) Cookies
\| Guides

<https://ytdlnis.org/docs/guides/cookies>

[\[3\]](https://chuck.is/yt-dlp/#:~:text=Command%20Description%20yt,of%20file%20into%20an%20MKV)
Bringing Sanity to YouTube Video Watching with yt-dlp \| Chuck Carroll

<https://chuck.is/yt-dlp/>

[\[4\]](https://www.conquer-your-risk.com/2023/07/20/the-code-knight-mastering-the-craft-of-defensive-programming/#:~:text=Defensive%20programming%20is%20about%20creating,both%20expected%20and%20unexpected%20issues)
The Code Knight: Mastering the Craft of Defensive Programming - Conquer
your risk

<https://www.conquer-your-risk.com/2023/07/20/the-code-knight-mastering-the-craft-of-defensive-programming/>
