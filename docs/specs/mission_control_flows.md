# Mission Control Flows And Information Hierarchy

## Purpose

This document defines how mission control should present Relaytic to humans and external agents once the workspace-first continuity layer exists.

The goal is not to add more panels. The goal is to make Relaytic legible on first contact and durable across multi-run work.

## Primary design rule

Humans should feel oriented.

External agents should feel unblocked.

Both should see the same truth, but rendered differently.

## Always-visible information

Mission control should always surface:

- current workspace
- current run
- current stage
- current mode
- current recommended next move
- confidence posture
- unresolved count
- review requirement
- active capability posture

These items should be visible without drilling into raw artifacts.

## Human-first hierarchy

The human surface should prioritize:

1. what Relaytic is doing now
2. what Relaytic believes now
3. what Relaytic recommends next
4. what the user can do next
5. what would change Relaytic's mind
6. what happened previously in this workspace

The human surface should never assume repo literacy.

## Agent-first hierarchy

The agent surface should prioritize:

1. current result contract
2. current next-run plan
3. current workspace state
4. active learnings posture
5. trace and adjudication posture
6. command or tool affordances

The agent surface should be terse, artifact-first, and command-usable.

## Required human flows

### First-time human

The first-time human flow must make clear:

- what Relaytic is
- that it needs data
- what kinds of objectives it accepts
- how to continue after a run finishes

### Returning human

The returning human flow must make clear:

- which workspace they are in
- what changed since the last run
- what Relaytic currently recommends
- whether the right move is same data, add data, or start over

### Stuck human

The stuck flow must make clear:

- what is missing
- what Relaytic can do without more input
- what one action would unblock progress fastest

### Post-run human

The post-run flow must make clear:

- what Relaytic found
- how confident it is
- what remains unresolved
- what the next recommended move is
- how to continue from the same workspace

## Required agent flows

### First-time external agent

The agent flow must make clear:

- which handbook to read
- which artifacts are canonical
- which commands or tools are available
- how to continue an existing workspace

### Continuing external agent

The agent flow must make clear:

- current workspace state
- current result contract
- next-run plan
- active governed learnings
- trace or adjudication posture if relevant

## Required user actions

Mission control should make these actions explicit:

- continue on same data
- add data
- start over
- ask why Relaytic believes this
- ask what would change its mind
- inspect learnings
- reset learnings
- inspect trace
- inspect benchmark or incumbent posture

## Information layering

The mission-control hierarchy should be:

- `top bar`: current workspace, stage, mode, next move, confidence
- `primary card`: result contract summary
- `secondary cards`: unresolved items, next-run options, learnings posture, trace/eval posture
- `advanced views`: branch replay, detailed traces, artifact tree, raw reports

Humans should not land in an advanced view first.

## Report handoff

After a run completes, mission control should always point both humans and agents to:

- the differentiated report for their role
- the canonical result contract
- the next-run options
- the current workspace state

## Anti-patterns

Mission control must not:

- show different next moves in different surfaces
- hide unresolved items behind overly optimistic prose
- treat the current run as if prior runs do not exist
- require report scraping to continue a workspace
- expose agent-facing terseness as the default human experience
