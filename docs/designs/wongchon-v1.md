# Design: wongchon version 1

Author: Vasapol Rittideah

Status: `Draft`

Intent: [`docs/intents/wongchon-v1.md`](../intents/wongchon-v1.md)

## Context

The intent of version 1 states what the plugin must do: it takes each change of a project through the intent, design, build, and verify stages, and the maintainer approves each gate when they merge its pull request (PR). This design states how the plugin does it. It also answers the open questions of the intent and the open questions that the [Roadmap](../../ROADMAP.md) gives to the design phase.

Phases 0 to 2 of the roadmap are done. This repository has the conventions in `docs/conventions/`, the `intent` skill, the Git guard hook, and a CI gate. The Decisions section of the roadmap holds each decision of this design with its rejected options, so this design links those decisions and does not repeat them.

## Stages and artifacts

Each stage commits its artifacts in 1 folder for each kind of artifact, as the [Stage artifacts](../../ROADMAP.md#decisions) decision of the roadmap states. All files of 1 change have the same change name, so a reader finds them with the name.

| Stage | Artifact | Path | Gate |
| --- | --- | --- | --- |
| Intent | The intent | `docs/intents/<change>.md` | The owner merges the PR of the intent. |
| Design | The design, and 1 architecture decision record (ADR) for each decision that rejects options | `docs/designs/<change>.md` and `docs/adr/<number>-<decision>.md` | The owner merges the PR of the design. |
| Build | The plan, and then the code and its tests | `docs/plans/<change>.md` | The owner merges the PR of the plan. Then each task of the plan reaches `main` in its own PR. |
| Verify | The verification evidence | `docs/evidence/<change>.md` | The owner merges the last PR of the change, which adds the evidence. |

- Write the change name as lowercase words and numbers separated by single hyphens, as the [Intent](../conventions/intents.md) conventions state.
- Give intents, designs, and plans a Status line with the values `Draft` and `Approved`. The status states only the approval of the artifact. Git history and the merged PRs state the progress of the change, so no artifact has a status such as `Implemented` or `Complete`.
- Link each artifact to the artifact of the stage before it. A design links its intent, a plan links its design, and the evidence links its plan.
- Write the evidence against the success criteria of the intent. A small change has no intent, so its evidence uses the acceptance criteria of its plan.

## Design artifact

A design states how to build the change that its intent describes. The design convention, which the next PR of phase 3 adds, fixes the sections. This design shows the content that the convention starts from:

- The parts of the change, how they connect, and the interfaces between them
- The decisions of the change, with a link to the ADR of each decision that rejects options
- The answers to the open questions of the intent, or the stage that decides each question
- The check that enforces each rule of the change, or the follow-up task that adds the check
- The order of the work, which the plan of the build stage turns into tasks
- The open questions for later stages

A design does not repeat what the intent states, such as the problem, the success criteria, or the scope.

## Project documents

A project has these documents at its root, as the [Project documents](../../ROADMAP.md#decisions) decision of the roadmap states:

| Document | When it exists | Content | Writer | Check |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | From the setup command | The rules that apply to all work in the project, in at most 200 lines, and links to the conventions and the other project documents. `CLAUDE.md` is a symbolic link to it. | The setup command, and then each PR that changes a rule | A line count check in CI, from the build phase |
| `CONSTRAINTS.md` | From the design stage of the first change | The quality bar of the project. Each rule names the command that checks it. | The design stage, with the `constraint-driven-development` skill | The review gate blocks a change that lowers the bar. |
| `ARCHITECTURE.md` | After the build stage of the first change | The parts of the project, how they connect, the reasons, and the rules. It lists no folders or versions. | The design stage plans it. The reasons and rules move into the file after the build. | Each rule has a deterministic check in the stack of the project. Reviewers ask for a check when a rule has none. |
| `GLOSSARY.md` | From the first change that uses a term of the domain of the project | Each term that the code does not explain | The design stage, and then each PR that adds or changes a term | Each PR that adds or changes a term updates the file. |

The design phase writes the conventions of `CONSTRAINTS.md` and `GLOSSARY.md`. The build phase writes `ARCHITECTURE.md` for this repository, as the roadmap states.

## Decision records

The design stage records decisions in ADRs, as the [Decision records](../../ROADMAP.md#decisions) decision of the roadmap states.

- Save each ADR as `docs/adr/<number>-<decision>.md`. The number has 4 digits, and each new ADR takes the next number.
- Open the PR of an ADR with the status `Accepted`. The merge of the PR accepts the ADR.
- Do not edit an accepted ADR. To change a decision, write a new ADR that supersedes it, and change only the status line of the old ADR.
- In this repository, move each decision of the roadmap that has rejected options into an ADR, in a separate PR after the ADR convention. Then the Decisions section of the roadmap only links the ADRs.

## Small changes

A change that fits in 1 PR skips the intent and design stages and starts at the build stage, as the [Small changes](../../ROADMAP.md#decisions) decision of the roadmap states. CI enforces the rule with 2 checks:

- If a plan links no intent, the plan has exactly 1 task, which is 1 PR.
- If a PR belongs to a change without an intent, the PR does not change `docs/adr/`, `ARCHITECTURE.md`, or `CONSTRAINTS.md`. A change to these files is a design decision, so it needs the design stage.

The owner can still take any change through all stages. The build phase adds these checks, because they read plans.

## Setup command

A project runs `/wongchon:setup` 1 time, as the [Setup command](../../ROADMAP.md#decisions) decision of the roadmap states. The skill sets `disable-model-invocation: true`, so only a person starts it. It does these steps:

1. Make sure that the project has Git, the GitHub CLI, and a GitHub remote.
2. Ask the owner for the facts of the project, such as the commit scopes and the build and test commands.
3. Write `.wongchon/config.json` with these facts.
4. Create `AGENTS.md`, or add the rules of the framework to an existing `AGENTS.md`. Create `CLAUDE.md` as a symbolic link to it.
5. Create the GitHub labels of the [GitHub label](../conventions/github-labels.md) conventions.
6. Open a PR with these files.

The setup command does not install hooks. Claude Code registers the hooks of a plugin when it loads the plugin. The setup command does not write `CONSTRAINTS.md` or `ARCHITECTURE.md`, because a greenfield project has no stack and no check commands yet.

## Stage gate

A CI job named `Stage gate` blocks the merge of an artifact that the owner did not approve, as the [Stage gate](../../ROADMAP.md#decisions) decision of the roadmap states.

- The job reads each intent, design, and plan that the PR adds or changes, and fails when its status is not `Approved`.
- The agent changes the status to `Approved` only after the owner approves the artifact in the chat or in a review of the PR, as the intent convention states.
- The ready rule of the [Pull request](../conventions/pull-requests.md) conventions requires passing CI, but this job fails until the owner approves. The rule therefore excludes the `Stage gate` job, and only that job.
- The job runs 1 Python script with the standard library only. The build phase adds the checks of small changes to the same script.

## Plugin layout

The plugin lives in `plugin/`, and the marketplace at the root of this repository points to it, as the [Plugin layout](../../ROADMAP.md#decisions) decision of the roadmap states. The build phase creates this layout and moves the files.

```text
.claude-plugin/marketplace.json    marketplace, with the source ./plugin
plugin/
  .claude-plugin/plugin.json       manifest, with the ponytail dependency
  skills/<skill>/SKILL.md          stage skills and bundled third-party skills
  hooks/hooks.json                 hook registration
  hooks/git_guard.py
  scripts/                         CI checks, such as the Stage gate script
  conventions/<name>.md            conventions, which the skills read
AGENTS.md, ROADMAP.md, README.md   files of this repository only
ARCHITECTURE.md                    from the build phase
docs/intents/, docs/designs/, docs/plans/, docs/evidence/, docs/adr/
evals/                             sample projects of the eval suite
.claude/, .wongchon/, .github/
```

- Put each file that a skill reads in another project under `plugin/`. The install copies only the plugin folder, so a file outside it does not reach the project.
- Link a convention from a skill with `${CLAUDE_PLUGIN_ROOT}/conventions/<name>.md`. Claude Code replaces the variable with the install folder of the plugin.
- Keep the template of each artifact in the Template section of its convention, as the intent convention does. The plugin has no separate folder for templates.
- Declare the `ponytail` plugin in the `dependencies` field of `plugin.json`. The `ponytail` plugin comes from another marketplace, so the marketplace of this repository lists that marketplace in `allowCrossMarketplaceDependenciesOn`.
- Load the skills of the plugin in this repository through symbolic links in `.claude/skills/`, as today.

## Skills

Each stage skill has the name of its stage, as the [Stage skill names](../../ROADMAP.md#decisions) decision of the roadmap states. A user calls it with the namespace of the plugin, such as `/wongchon:design`.

| Skill | Stage | Phase |
| --- | --- | --- |
| `intent` | Intent | 2 |
| `design` | Design | 3 |
| `plan` and `build` | Build | 5 |
| `verify` | Verify | 6 |
| `setup` | Before the first change | 5 |

- Keep the name `verify` for the skill of the verify stage. Claude Code has a built-in `/verify` skill that builds and runs an app. The `wongchon:verify` skill can use it as 1 step when it collects evidence.
- Copy and rewrite the skills of agent-skills in the phases that the Skills from agent-skills section of the roadmap states.

## Order of the work

Phase 3 delivers these PRs in this order. Each PR is 1 reviewable change.

1. This design, written by hand from the intent
2. The design convention, from this design
3. The ADR convention
4. The ADRs of this repository, moved from the Decisions section of the roadmap
5. The conventions of `CONSTRAINTS.md` and `GLOSSARY.md`
6. The `Stage gate` CI job, and its exception in the ready rule of the pull request conventions
7. The copies of `spec-driven-development`, `api-and-interface-design`, `documentation-and-adrs`, and `constraint-driven-development`, rewritten for the design stage
8. The `design` skill

The build phase creates the plugin layout, moves the files into `plugin/`, adds the setup command, and adds the checks of small changes.

## Answers to the open questions of the intent

| Question of the intent | Answer |
| --- | --- |
| Where does a project keep the artifacts of each stage? | In 1 folder for each kind of artifact. See Stages and artifacts. |
| Which deterministic rule decides that a change is small enough to start at the build stage? | Its plan has 1 task, and its PR does not change `docs/adr/`, `ARCHITECTURE.md`, or `CONSTRAINTS.md`. See Small changes. |
| Which project documents does the framework require besides `ARCHITECTURE.md`? | `AGENTS.md` and `CONSTRAINTS.md`, and `GLOSSARY.md` when the project has a term of its domain. See Project documents. |
| What are the name and the steps of the setup command? | `/wongchon:setup`, with the steps in Setup command. |
| Who changes the status of an intent to `Approved`, and which CI check blocks the merge of an intent that has another status? | The agent, after the owner approves. The `Stage gate` CI job blocks the merge. See Stage gate. |

## Open questions

The build phase decides these questions:

- How does the CI of a project run the checks of the plugin, such as the `Stage gate` job? A possible answer is a workflow that the setup command writes, which checks out this repository at the installed version.
- Does a link with `${CLAUDE_PLUGIN_ROOT}` in a skill open a convention outside the folder of the skill? The documentation implies it, but nobody tested it.
- Does Claude Code install the `ponytail` plugin from another marketplace as a dependency, as the documentation states?

The maintainer decides this question in the review of this design:

- The Steering Claude Code article puts the folder layout of a project in `CLAUDE.md`. The Best practices for Claude Code page calls this advice out of date, because Claude reads the code. This design follows the Best practices page, as the Project documents decision of the roadmap already does.

## Answers

| Question | Reply |
| --- | --- |
| Where does a project keep the artifacts of each stage: 1 folder for each change, or 1 folder for each kind of artifact? | 1 folder for each kind of artifact: `docs/intents/`, `docs/designs/`, `docs/plans/`, and `docs/evidence/`, with ADRs in `docs/adr/`. |
| Which project documents does the framework require besides `ARCHITECTURE.md`? | `AGENTS.md` and `CONSTRAINTS.md`. `GLOSSARY.md` is optional, and a project creates it with its first term of the domain. |
| How does the design stage use ADRs? | ADRs go in `docs/adr/<number>-<decision>.md`. An ADR opens as `Accepted`, and the merge accepts it. An accepted ADR changes only when a new ADR supersedes it. The roadmap decisions with rejected options move into ADRs in a separate PR after the ADR convention. |
| Does the skill of the verify stage keep the name `verify` next to the built-in `/verify` skill? | Yes. Users call it as `/wongchon:verify`, and it can use the built-in skill to run the app. |
| What is the layout of the plugin? | The plugin lives in `plugin/`, and the marketplace at the root points to it. The skills, hooks, scripts, and conventions move into `plugin/` in the build phase. |
| Do you accept the changes to the Skills from agent-skills table? | Yes. `constraint-driven-development` moves to the design phase, `accessibility-engineering` joins the verify phase, the design phase copies only the parts of `spec-driven-development` about how to build and the ADR part of `documentation-and-adrs`, and `planning-and-task-breakdown` stays in the build phase. |
| Which deterministic rule decides that a change is small? | A change without an intent has a plan with 1 PR, and that PR does not change `docs/adr/`, `ARCHITECTURE.md`, or `CONSTRAINTS.md`. |
| What are the name and the steps of the setup command? | `/wongchon:setup`, which only a person starts. It checks for Git, the GitHub CLI, and a remote, asks for the facts of the project, writes `.wongchon/config.json`, creates or extends `AGENTS.md` with the `CLAUDE.md` link, creates the labels, and opens a PR. The plugin brings its hooks, and the design stage of the first change writes `CONSTRAINTS.md`. |
| Who changes the status to `Approved`, and which CI check blocks the merge? | The agent, after an explicit approval of the owner. A `Stage gate` CI job fails while an intent, design, or plan of the PR is not `Approved`, and the ready rule of the PR conventions excludes only that job. |

## References

| Source | What this design takes from it | Parts read only in a summary |
| --- | --- | --- |
| The 02 Design section of [The AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook) | The design answers the open questions of the intent or carries them forward, and a person decides the gate | The whole article, which the fetch tool returned only as a summary |
| [Steering Claude Code](https://claude.com/resources/articles/steering-claude-code-skills-hooks-rules-subagents-and-more) | `CLAUDE.md` as an index to other files in at most 200 lines, procedures in skills, and rules that must always hold in hooks | The embedded timeline and the map of hook events |
| [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) | Write in project documents only what the code does not show. Give a side-effect skill `disable-model-invocation: true`. | None |
| The [plugins reference](https://code.claude.com/docs/en/plugins-reference), [plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies), and [skills](https://code.claude.com/docs/en/skills) pages of the Claude Code documentation | The plugin layout, the copy of only the plugin folder at install, `${CLAUDE_PLUGIN_ROOT}`, the `dependencies` field, the namespace of plugin skills, the built-in `/verify` skill, and the hooks of a plugin | The last part of the skills page, and most of the hooks page |
| [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) by Michael Nygard | 1 numbered ADR for each decision, and a new ADR that supersedes an old one instead of an edit | None |
| [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/) by Malte Ubl | A short design for a small change, and no design when a change has no trade-offs | None |
| The skills of [agent-skills](https://github.com/addyosmani/agent-skills) at version 0.6.17 | The phase of each skill, the ADR sections of `documentation-and-adrs`, and the parts of `spec-driven-development` about how to build | 20 of the 26 skills, which the agent read only by their descriptions, headings, and paths |
