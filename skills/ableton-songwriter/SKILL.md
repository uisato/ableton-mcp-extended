---
name: ableton-songwriter
description: Professional songwriting workflow for Ableton: structured intake, production brief, composition/arrangement execution, plugin-aware instrument loading, quick mix, QA, and revision handoff.
---

# Ableton Songwriter

## Objective
Convert an open-ended songwriting request into a playable, editable Ableton draft with:
- coherent song form,
- intentional section contrast,
- viable instrumentation choices,
- and a minimal but professional gain/mix baseline.

This skill optimizes for production momentum and clean revision cycles, not final mastering.

## Use This Skill When
- The user asks to compose, arrange, rewrite, or “start a song” in Ableton.
- The user gives broad direction and expects structured clarification.
- The user wants a practical draft with a fast polish pass.

## Do Not Use This Skill When
- The task is purely technical/debugging (no songwriting intent).
- The user only asks for a single isolated operation (for example, “rename track 3”).
- The user explicitly asks for free-form brainstorming with no DAW execution.

## Operating Standards
- Keep decisions explicit and traceable in a compact production brief.
- Resolve high-impact unknowns first; avoid over-questioning.
- Protect user project state (never destructive by default).
- Prefer repeatable arrangement patterns over novelty for first drafts.
- Keep the first pass modular so sections can be swapped or extended quickly.

## Workflow
1. Parse request and extract fixed constraints.
2. Run targeted intake for missing high-impact decisions.
3. Emit production brief and proceed unless user asks to review first.
4. Build section foundations (rhythm, harmony, hook) in Session or Arrangement.
5. Arrange into form with section contrast and transitions.
6. Apply quick mix baseline and playback-ready positioning.
7. Return structured handoff with revision options.

## Intake Protocol
- Use MCQ format with `1. 2. 3.` numbering when clarification is needed.
- Ask exactly 3 questions first; ask at most 2 follow-ups.
- Skip any item already answered by user constraints.
- If user asks for speed, ask only:
  - genre family,
  - energy target,
  - section length target.
- Use [intake-mcq.md](references/intake-mcq.md) for full option bank.
- If structured input tooling is available, use it; otherwise ask plain-text MCQ.
- Always include one safe default option.

## Production Brief Contract
Before building, output a concise brief in this schema:

```md
Production Brief
- Genre/Reference:
- Mood/Intent:
- BPM/Groove:
- Key/Mode:
- Song Form:
- Section Lengths:
- Instrument Priorities:
- Vocal Plan:
- Mix Target:
- Constraints/Do-Not-Do:
```

Proceed automatically after brief unless user requests approval gate.

## Build Standards in Ableton

### 1) Session Setup
- Set tempo immediately from brief.
- Select one template from [song-recipes.md](references/song-recipes.md).
- Name tracks by role, not instrument brand (example: `Lead Synth`, `Drum Bus`).
- Keep routing simple on first pass; avoid deep bus complexity.

### 2) Instrument Strategy
- Try user-owned external plugins when relevant and available.
- If external plugins are unavailable, fallback to stock devices and state fallback.
- For electronic/hybrid leads, prioritize modern synth clarity before layering.
- For acoustic-forward requests without audio assets, use MIDI placeholders with clear naming.

### 3) Composition Strategy
- Build at least two distinct sections (A/B) with different density and contour.
- Ensure each section has:
  - rhythmic anchor,
  - harmonic movement,
  - top-line hook or motif.
- Keep early motifs short and memorizable; avoid over-ornamentation.

### 4) Arrangement Strategy
- Minimum draft length: 16 bars unless user requests shorter.
- Preferred default: 32 bars with intro + A + B.
- Add transitions at section boundaries (drum fill, riser, filter move, dropout).
- Place cue points at major sections for fast iteration.

### 5) Quick Mix Baseline
- Set faders for immediate readability (no clipping on master).
- Keep low-end mono/center-aligned.
- Apply light panning/width to support layers only.
- Use conservative dynamics control for punch, not loudness.
- Leave headroom for later mix/master passes.

### 6) Playback Behavior
- Set playhead to first actionable section start.
- Do not start playback unless user asks.

## Plugin-Aware Policy
- If plugin listing/loading tools exist, check availability before assuming plugin usage.
- When user asks for named plugin loading, prefer exact match if ambiguity exists.
- If multiple close matches exist, request specificity instead of guessing.
- If loading fails, continue with best available substitute and report it clearly.

## Guardrails
- Never delete/overwrite user material without explicit confirmation.
- If set already contains substantial content, ask whether to append or replace target region.
- If operations are blocked by platform rules (for example, final track deletion), stop retry loops and state constraint.
- Keep progress updates brief and factual.

## Quality Checklist (Before Handoff)
- Section contrast is audible (A vs B not redundant).
- Track naming is clear and role-based.
- No obvious timing/form misalignment across section boundaries.
- Master output is not clipping.
- User constraints have been respected or explicitly called out as unmet.

## Handoff Format
Return a short structured recap:
- What was built (sections, bars, key tracks).
- What plugins/instruments were used (including fallbacks).
- Current limitations/assumptions.
- 2-4 concrete revision options.

## Revision Loop Rules
- On revision requests, preserve successful sections and change only requested scopes.
- Reuse existing motif/harmony where possible to maintain identity.
- If revision alters core brief dimensions (genre, BPM, key), emit updated brief first.

## Worked Example

### Example User Request
`Write a modern melodic house idea with emotional chords and a strong drop. Keep it club-ready but not too aggressive.`

### Example Intake (3 Questions)
1. Groove focus:
`1.` Four-on-the-floor house bounce (Recommended)  
`2.` Straighter driving pulse  
`3.` More syncopated / broken feel

2. Harmonic color:
`1.` Minor + warm tension chords (Recommended)  
`2.` Brighter major/uplifting  
`3.` Darker/minimal harmony

3. Draft size:
`1.` 32 bars (Recommended)  
`2.` 16 bars quick sketch  
`3.` 64 bars extended draft

### Example Production Brief
```md
Production Brief
- Genre/Reference: Melodic House (modern, emotional)
- Mood/Intent: Uplifting tension with controlled energy
- BPM/Groove: 124 BPM, 4-on-the-floor bounce
- Key/Mode: F# minor
- Song Form: Intro -> A groove -> B/drop
- Section Lengths: 8 + 8 + 16 (32 bars total)
- Instrument Priorities: Kick/bass lock, emotional chord stack, lead hook, top percussion
- Vocal Plan: No vocal in v1 (instrumental motif only)
- Mix Target: Club-ready draft with headroom preserved
- Constraints/Do-Not-Do: Avoid harsh high-end and over-compression
```

### Example Build Plan (Ableton Actions)
1. Set tempo to 124 BPM.
2. Create/prepare role tracks:
- `Kick`, `Bass`, `Chord Stack`, `Lead Hook`, `Top Perc`, `FX`, `Atmos`, `Reference Bus`.
3. Load instruments/effects:
- Prefer external synth for `Chord Stack` and `Lead Hook` if available.
- Fallback to stock synth + utility processing if plugin unavailable.
4. Write section A (8 bars):
- establish kick+bass groove and core chord rhythm.
5. Write section B/drop (16 bars):
- increase density, widen support layers, strengthen hook rhythm.
6. Add transitions:
- riser, fill, or filter move between A and B.
7. Place cue points:
- `Intro`, `A`, `Drop`.
8. Quick mix baseline:
- gain balance, low-end mono, prevent master clipping.

### Example Handoff
```md
Built
- 32-bar melodic house draft in F# minor at 124 BPM.
- Sections: Intro (8), A groove (8), Drop (16).
- Core tracks: Kick, Bass, Chord Stack, Lead Hook, Top Perc, FX, Atmos.

Sound Choices
- Lead/chords used [plugin name] with fallback to [stock device] where needed.

Current Constraints
- No vocal yet; arrangement optimized for instrumental draft.

Revision Options
1. Make drop more aggressive (drum/bass density + transient emphasis).
2. Make it more emotional (longer chord sustains + softer top end).
3. Extend to 64 bars with breakdown + second drop.
4. Add vocal chop motif in section B.
```

## References
- Intake prompts and option bank: [intake-mcq.md](references/intake-mcq.md)
- Genre defaults and templates: [song-recipes.md](references/song-recipes.md)
