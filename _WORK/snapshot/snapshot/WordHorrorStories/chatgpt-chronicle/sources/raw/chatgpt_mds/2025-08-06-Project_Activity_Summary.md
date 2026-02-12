# Project Activity Report

**Report Date (Miladi):** 2025-08-06

**Report Date (Shamsi):** 1404-05-15

## Summary

- **Number of chat sessions:** approximately 53 chats.
- **Files shared in this project:** 1 file (the detailed manual with
  track changes).
- **Estimated messages:** around 4,600 messages across all sessions.
- **Average message length:** roughly 19,000 characters per message.
- **Active days in project:** 11 distinct editing days in the manual
  (plus more discussion days), spanning from **2025‑07‑11** to
  **2025‑08‑04**.
- **Estimated time spent:** roughly **500‑800 hours** of combined
  reading, debugging, researching and writing, assuming 6‑10 minutes per
  message for deep technical work.

## Chronological Timeline of Key Activities

| Date | Key Activities & Notes | Evidence |
|----|----|----|
| **2025‑07‑11** | Initial brainstorming and requests: you discussed improving the Telegram bot for YouTube video & subtitle downloads, including making the title a clickable link, offering quality/size choices, and using the bot as a channel admin for logging responses. You also explored script configuration (cookie paths, log directories and user‑agent files) in Bash. | The track‑changes summary shows multiple insertions on 2025‑07‑11 describing Bash configuration lines (cookies path, log directory) and your requests for title links and quality choices. |
| **2025‑07‑19** | Evaluating old vs new scripts: you compared the behavior of two scripts (the old script sometimes succeeded on SABR‑blocked videos but aborted without subtitles, whereas the new one allowed video‑only downloads yet sometimes failed on SABR) and drafted a plan to merge the best features. | The summary lists 2025‑07‑19 entries outlining “What works and what doesn’t,” noting that the old script sometimes downloads blocked videos but aborts without subtitles, whereas the new script robustly allows video‑only jobs. |
| **2025‑07‑25** | Detailed debugging report: a long report was inserted detailing issues such as missing Persian subtitles, HTTP 429 (rate‑limiting) errors, and problems with YouTube’s changing subtitle naming conventions. You began refining subtitle detection and error handling logic. | The summary shows a “Detailed Report” inserted on 2025‑07‑25 explaining missing Persian subtitles, HTTP 429 errors and subtitle naming logic problems. |
| **2025‑07‑26** | Handling Downsub/Cloudflare challenge: you investigated why Selenium could not reach Downsub due to Cloudflare’s human‑verification challenge and considered using browser cookies to bypass it. You concluded that cookies might help but Cloudflare challenge bypass is complex in headless mode. | The summary records a 2025‑07‑26 entry noting Downsub’s “Verifying you are human” challenge and a short discussion about using PC browser cookies, but warning that Cloudflare bypass is more complex than copying cookies. |
| **2025‑07‑27** | Major script cleanup and modularization: you produced a cleaner, minimized Bash script and refactored the Python & Bash scripts for clarity, robust VIDEO_ID handling and better error reporting. You reviewed each file, highlighting correct behaviours and areas for improvement. | The summary shows multiple insertions on 2025‑07‑27, including a cleaned‑up Bash script (with cookie paths and usage instructions) and notes about robust VIDEO_ID extraction and structured analysis of Python and Bash files. |
| **2025‑07‑28** | Minor diagnostic commands: you ran `ffprobe` to inspect subtitle streams in MKV files and inserted commands as part of your notes. | The summary includes 2025‑07‑28 entries showing `ffprobe` commands used to inspect subtitle streams. |
| **2025‑07‑29** | Comprehensive review of subtitle handling: you created a step‑by‑step review of the subtitle handling flow, addressed conversion from VTT to SRT, questioned whether SRT files existed for all languages, and examined the logic for finding subtitles. | The summary lists 2025‑07‑29 entries outlining a step‑by‑step review of subtitle handling, including conversion loops, checks for missing SRT files, and selection logic. |
| **2025‑07‑30** | Final refinements: you noted that the latest script version was close to ideal but suggested improvements, such as making `find_lang_sub` more resilient via glob matching and adding fallback logic for unexpected subtitle names. | The summary’s 2025‑07‑30 entries highlight suggested improvements, including fallback subtitle detection and glob matching for filename variations. |
| **2025‑07‑31** | Structured analysis of files: you provided a structured analysis of four different files, identified monolithic flows vs modularization needs, discussed how to collect and prioritize subtitles, and proposed splitting logic into functions. | The summary notes a structured analysis inserted on 2025‑07‑31 with key observations such as monolithic flows, modularization, subtitle collection, and splitting logic into functions. |
| **2025‑08‑01** | Refining final Bash script: you stated that the modular Bash script (`yt_mkv_downloader…`) was almost final but needed refinements. You confirmed features such as Video ID override logic, metadata logging, modular subtitle handling and filename trimming, and flagged remaining issues like integrating `generate_verbose_filename`. | The summary’s 2025‑08‑01 entries list check‑marked features (Video ID override, metadata logging, modular subtitle handling, filename trimming and log rotation) and point out pending refinements. |
| **2025‑08‑04** | Major manual expansion: you added new sections to the manual, including an “Anti‑Detection & Anonymity Layer,” a metadata injection section, a Windows + Linux VPS edition manual for downloading and burning subtitles, and future expansion ideas. | The summary records 2025‑08‑04 entries introducing sections like **Manual: Downloading and Burning English Subtitles**, with subsections on overview, requirements, command summaries and future plans. |

## Reflection on Time Investment

The project has spanned **more than three weeks**, with intensive work
on 11 recorded editing days in the manual. With approximately 4,600
messages and each requiring between 6 and 10 minutes of reading,
researching, coding and responding, the cumulative time investment
likely falls between **500 and 800 hours**. The bulk of this time was
spent debugging complex Bash/Python scripts, ensuring robust subtitle
handling, and documenting the workflow.

## Conclusion

This updated report reflects the latest state of the **“YouTube Video +
Subtitle”** project as of **2025‑08‑06** (Shamsi **1404-05-15**). It
enumerates the number of conversations, shared files, estimated effort,
and a chronological history derived from the track‑changes logs. The
manual now contains extensive documentation, not only of the code but
also of the reasoning and troubleshooting process, culminating in a
comprehensive guide that can be referenced for future enhancements.

------------------------------------------------------------------------
