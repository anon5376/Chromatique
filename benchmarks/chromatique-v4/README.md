# Chromatique v4: playing strength and style

**Measurements are in progress. No final playing rating or style verdict is
published yet.** Completed PGNs and run receipts are retained in
[`results/`](results/); final results require complete schedules, independent
PGN replay, statistical analysis and review.

## What is measured

The target is unmodified revision
[`4d462c8f`](https://github.com/lusolitaire-dot/Chromatique/tree/4d462c8f7883f4e08d3d0e151de0374a6150ea22),
with its bundled v4 model, learned policy enabled and full-strength settings.
Chromatique's inherited `UCI_Elo` control is disabled; it does not calibrate
the replacement evaluator. Puzzle ratings are not playing ratings.

The measured host is an Apple M5 Pro with 15 logical CPUs and 24 GiB RAM,
running macOS 27.0.1. Builds use Apple Clang 21. Each engine uses one search
thread and 32 MiB hash where supported, with pondering and tablebases off.
Six games run concurrently. Fresh engine processes start every measurement
game. Source revisions, binary/model/network hashes, build commands and
hardware are in [`data/environment.json`](data/environment.json); actual
commands and input hashes are in each `.run.json` receipt.

## Fixed match design

| Purpose | Opponent(s) | Games | Initial time + increment |
|---|---|---:|---|
| Main strength | Stockfish 17.1 settings 2200, 2400, 2600 | 400 each | 5 seconds + 0.05 seconds/move |
| Independent engine | Stash 15.3 | 400 | 5 + 0.05 |
| Local calibration checks | SF2200–SF2400, SF2400–SF2600, Stash–SF2400 | 200 each | 5 + 0.05 |
| Clock sensitivity | SF2400 | 100 | 30 + 0.3 |
| Separate long-clock validation | SF2400 and Stash 15.3 | 200 each | 120 + 1 |

The original 2,300-game schedule was committed before the first measurement
game. A separate 168-game selection pilot is retained and excluded from all
fixed-schedule estimates. Its closest-to-even setting, SF2400, became the
central reference; Fruit's 0/24 pilot was too strong for efficient precision
matches. The two 120+1 extensions total 400 games. Their source-based triggers
and prospective declaration times are documented in
[`CALIBRATION-VALIDATION.md`](CALIBRATION-VALIDATION.md).

Every opening is played twice with colors reversed. The checksum-pinned
CC0 Stockfish `8moves_v3` book supplies 16-ply histories. Deterministic hash
ranking selects distinct final positions without reference to Chromatique's
choices or outcomes. Pilot, main, bridge, slower and anchor panels are
disjoint; the same main panel is reused across main opponents. Color pairing
does not establish that individual starting positions are evaluation-balanced.

No score-based resignation or draw adjudication is used: the engines' scores
have different meanings. Rule draws and a declared 300-move administrative
draw limit apply. Genuine clock losses, crashes and illegal moves stay in the
result. The runner uses a 100 ms time margin and refuses changed or unfinished
existing artifacts. Compiler builds and engine-based judging run outside
timed matches; practical load-control limits are recorded in
[`EXECUTION-NOTES.md`](EXECUTION-NOTES.md).

## Elo and uncertainty

For score fraction `s = (wins + draws/2) / games`, the reported relative
logistic Elo is `400 log10(s / (1-s))`. The sampling unit is a complete
opening pair. Its normalized score is one of `0, 0.25, 0.5, 0.75, 1`; five
counts preserve the full pentanomial distribution.

The primary 95% interval uses the unbiased variance of those pair scores,
a normal interval for their mean, and transformed Elo endpoints. A seeded
20,000-resample pair bootstrap supplies a sensitivity check. A conservative
Hoeffding interval is also retained for every match and replaces the primary
interval when empirical variance is zero. Boundary Elo estimates remain
unbounded. These are individual, conditional intervals, not simultaneous
coverage across all opponents or a measure of external calibration error.
Shared openings correlate opponent-specific results, so nominal anchors are
not pooled as independent ratings. See [`PROTOCOL.md`](PROTOCOL.md) and
the [primary methodology sources](SOURCES.md).

Independent replay checks every recorded legal move, rules-terminal result,
opponent, time control, complete opening history and exact reversed-color
pair count. It verifies receipt and PGN/book checksums before recomputing
W/D/L, color splits, terminations, pair counts and confidence intervals.

## External rating limits

Stockfish 17.1 inherits the polynomial from a historical Stash calibration
at 120+1. No fresh calibration specific to 17.1 was located. The old fit's
roughly 100-Elo discrepancy with CCRL is historical context, not a present
uncertainty bound. A nominal setting plus our relative Elo is a conditional
Stockfish-setting equivalent.

CCRL's list computed on 2026-10-17 rates **Stash 15.3 64-bit at 2174,
+19/−19 (95%), from 982 games**. Its official archive dates those games to
May 2020 and omits their time controls. Present scaled 2+1 policy does not
establish their historical clock or hardware. Tested-binary identity and
equal strength with our same-release ARM64 build are unverified. CCRL uses
BayesElo; this study uses a logistic score transform. Adding our match delta
to 2174 assumes transfer across models, builds, clocks and pools. Keep the
published rating interval separate from our match interval; the remaining
transfer uncertainty is unknown. [Primary references and capture
provenance](SOURCES.md), [structured source receipt](data/rating-sources.json).

Neither comparison awards Chromatique a CCRL, human FIDE or online rating.

## Evaluating the romantic-style claim

The fixed main PGNs supply descriptive check, capture, quiet-move and
material-deficit rates after the forced book moves, plus game-length and
queenless-game context. They do not isolate style from differing positions,
opponent strength or forced defense.

A separate common-position panel selects at most one eligible position per
central-match opening pair, using the predeclared hash/ply rule. Both engines
choose from the identical board and full history with 0.25 seconds each.
Full-strength Stockfish 17.1 judges the position and each distinct choice at
200,000 nodes per search. Checks, quiet moves, material-offer proxies and
estimated evaluation loss are compared in opening-paired observations.
Mate-valued searches are retained separately from ordinary centipawn losses.

The offer proxy measures exposure of a non-pawn to a legal capture, allowing
an immediate recapture; it can include an already hanging piece. Low estimated
judge loss does not prove intent, soundness or a sacrifice. The predeclared
two lowest-loss and one highest-loss target offer examples receive separate
two-million-node inspection, without filtering source-game outcomes. All
histories, moves and analysis continuations are retained. These examples are
selected illustrations, not a sacrifice success rate.

The judge shares Stockfish's evaluation family with the comparator. Probe
positions come from Chromatique's central-match trajectories, omit checks and
positions with few legal choices, and use a different clock from the games.
Style comparisons are exploratory and have no multiple-comparison correction.
Quiet moves alone cannot establish positional understanding; a neural
evaluator's lack of a hand-written material term cannot establish “zero
positional play.”

## Reproduce and inspect

[`REPRODUCING.md`](REPRODUCING.md) gives setup, match, replay, style and
example-inspection commands, with fresh output directories for new matches.
The scripts use only the repository's declared Python development
requirements. External UCI engines and Fastchess are local benchmark tools;
their source trees and binaries are not redistributed here. PGNs remain
plain text. After all matches finish, completed logs and recovery states will
be retained in lossless gzip archives with raw/compressed checksums and
verified roundtrips.

Rerunning the same wall-clock searches need not reproduce the same moves.
Reproducibility means pinned inputs, explicit controls, complete retained
evidence and rerunnable calculations.
