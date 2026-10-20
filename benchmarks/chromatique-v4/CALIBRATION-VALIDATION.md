# Additional validation at the published calibration clock

This extension is declared while the first fixed main match is still running,
before inspecting its aggregate score. It does not change the original
schedule or stop rule. The trigger is the source review: Stockfish 17.1's
published strength-setting calibration used **120 seconds + 1 second/move**,
and the original schedule uses shorter clocks.

Run **200 games (100 reversed-color opening pairs)** against Stockfish 17.1
`UCI_Elo=2400`, at **120+1**, with the same one-thread, 32 MiB hash,
no-tablebase and fresh-process controls. The central setting is the one
selected by the original short-clock pilot. It will not be retuned from the
long-match result. A boundary score yields a one-sided/unbounded relative
estimate rather than a result-dependent extension.

The new `anchor` panel is the next 100 distinct positions after the original
four panels in the same checksum-pinned book's deterministic hash ordering.
It is disjoint from all earlier panels. Generate it after the running timed
schedule has finished. The preparation script refuses to alter any existing
panel with different content. Retain all input hashes before launching this
validation match. Its exact schedule is `anchor-schedule.json`.

Compute the same pair-level score, logistic Elo and uncertainty as the main
matches. Report this match separately. Matching the published clock improves
the relevance of the nominal anchor, but the calibration still has different
hardware, opponent pool and approximately 100-Elo source uncertainty. That
source caveat is not a probability distribution or an extra Gaussian error
bar. This remains a conditional Stockfish-setting equivalent, not an awarded
CCRL or human rating.
