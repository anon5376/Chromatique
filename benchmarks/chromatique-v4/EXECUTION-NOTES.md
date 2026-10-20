# Execution notes

The target's C++ source and weights remain unchanged from the pinned v4
revision. The initial seven release tests passed. The benchmark's six focused
tests cover score orientation, opening-pair uncertainty, degenerate samples,
replayed result/color/pair validation, material-offer accounting and exclusion
of mate scores from centipawn loss.

The complete main schedule, sampled opening panels and initial scripts were
committed as `28ce97f` before the first measurement game started. All 168 pilot
games are excluded from the fixed-schedule estimates. The 2200 setting's small
pilot was noisy; the 2400 setting was closest to a 50% score and was selected
as the central reference. The main opponents are its two 200-point neighbors
and Stash 15.3. Fruit's 0/24 pilot is retained, and Fruit is excluded from the
precision matches because it was too strong for an efficient estimate.

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
