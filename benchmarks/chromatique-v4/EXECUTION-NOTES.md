# Execution notes

The target's C++ source and weights remain unchanged from the pinned v4
revision. The initial seven release tests passed. The benchmark's eight focused
tests cover score orientation, opening-pair uncertainty, degenerate samples,
replayed result/color/pair validation, material-offer accounting and exclusion
of mate scores from centipawn loss, and predeclared low/high-loss example
selection. A CLI regression also checks that rejected style reruns preserve
all existing files without starting an engine. Other CLI checks verified
lossless log archiving, rejection of
unfinished runs, and rejection of partial style panels before example judging.

The complete main schedule, sampled opening panels and initial scripts were
committed as `28ce97f` before the first measurement game started. All 168 pilot
games are excluded from the fixed-schedule estimates. The 2200 setting's small
pilot was noisy; the 2400 setting was closest to a 50% score and was selected
as the central reference. The main opponents are its two 200-point neighbors
and Stash 15.3. Fruit's 0/24 pilot is retained, and Fruit is excluded from the
precision matches because it was too strong for an efficient estimate.

The original 2,300-game runner process loaded the code from `28ce97f`.
While it was running, `13dbda1` added an alternate output-directory argument
for later reproductions; the default Fastchess command construction did not
change. Each receipt retains the actual command. The original live process
was not restarted to pick up that CLI change.

Final-schedule games use `restart=on`, confirmed in Fastchess's implementation
to discard and recreate each engine process after a game. This limits state
carryover between openings. Pilot processes were reused. Fastchess printed
warnings for the pilot Stash `Ponder` option, which Stash does not expose;
its search was not given `go ponder`. The final Stash configuration omits
that unsupported option. The runner now checks advertised options before a
new match starts.

A separate research review checked the paired-score standard error,
multinomial pair bootstrap and bounded Hoeffding intervals against primary
sources and found no blocking formula error. It identified mate-to-centipawn
mixing in the initial style implementation. Before any style probes ran, the
script was changed to report mate transitions separately. A focused test
demonstrated the missing behavior and then passed with the correction.
This review is distinct from the final code/results review still required.

The deterministic low/high-loss example-selection rule was committed in
`f36cb72`, after the first main match but before any common-position style
probe existed. It uses the previously unseen probe estimates and has no
source-game-outcome filter. Its timing is separate from the original match
schedule's freeze.

Before any style probes ran, rerun testing exposed writes to the position
manifest and descriptive outputs before the script refused existing probe
evidence. The guard now runs before those writes. The retained expected-failure
logs demonstrate the defect; the updated eight-test suite passes all three
existing-file cases. Tests used temporary fixtures and blocked engine startup.

During timed matches, the agent inspected progress, edited documentation and
scripts, and ran brief focused script tests (under one second of measured
wall time for the last suite). No compiler builds or engine-based style/judge
analysis ran alongside final timed matches. This is the practical execution
interpretation of the protocol's load control; background OS activity, CPU
affinity and thermal conditions were not measured or controlled.

The underlying official Fruit archive returned HTTP 404. The retained source
mirror builds and identifies as Fruit 2.1; byte identity with the original
author archive remains unverified. No current external rating was inferred
from the download failure. The dated CCRL snapshot is context, not a
calibration of this Apple Silicon build or time control.

The complete original 2,300-game schedule passed independent legal replay,
exact opening-pair checks and receipt checksums. It retains one Stockfish time
forfeit and three reported Stash crash/disconnect losses; their underlying
causes remain undiagnosed. No game reached the administrative 300-move limit
(maximum 245). All 200 style source histories/FENs, 400 legal choices,
SAN/check/capture/quiet flags, mate-aware losses and 600 recorded judge PVs were
checked against the source PGN and position manifest. Repeated choices share
a judge search. The three predeclared examples were rejudged at two million
nodes before long-clock matches began; their analysis histories and PVs
passed legality checks.

The four original opening panels remained byte-identical when the new
100-position anchor panel was generated. All five panels are disjoint. The
anchor inputs were committed as `55e879d` before the 120+1 runner started at
2026-10-20 16:00:04 UTC. An explicit macOS idle-sleep assertion was attached to
that runner and verified at 16:06:27 UTC with `caffeinate -i -w <runner PID>`.
Its configured lifetime follows the fixed 400-game runner. Power conditions
were not continuously logged before that assertion; CPU affinity, frequency
and thermals remain uncontrolled.

The first 120+1 match completed at 2026-10-20 18:49:01 UTC with Fastchess
exit status zero. Its 200 PGN result headers and receipt checksum were verified;
all termination tags are normal. The log reports Chromatique W/D/L 171/5/24.
The fixed Stash comparison started immediately afterward. Independent legal
replay and paired intervals for both long-clock matches will run after that
comparison; the final review is still pending.
