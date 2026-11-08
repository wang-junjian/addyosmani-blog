# The Intent Debt

> 原文：https://addyosmani.com/blog/intent-debt/
>
> 发布日期：2026-06-05

---

*Technical debt lives in your code. Cognitive debt lives in your head. Intent debt lives in the artifacts you may have never wrote: the goals, constraints, and rationale for why the system is the way it is. If you’re lucky, some of this exists scattered in team documents or discussions, but it’s likely incomplete. It’s the one kind of debt your agents can’t pay down for you, and agentic engineering makes it the most expensive.*

---

## Three places debt can live

Margaret-Anne Storey’s [Triple Debt Model](https://arxiv.org/abs/2603.22106) is a clean way to think about software health. The three models of debt are technical, cognitive, and intent.

**Technical debt lives in the code.** It’s the accumulation of implementation choices that make the system harder to change later: the tangled module, the shortcut you took under deadline, the abstraction that leaked. We’ve understood this one for decades. You feel it coming through slow builds, fragile tests, and the dread of touching one particular file.

**Cognitive debt lives in people.** It’s the erosion of shared understanding, the gap between how much code exists and how much any human understands. I’ve been calling this comprehension debt. It builds up when the system grows faster than the team’s mental model of it. Your code can be pristine and you can still carry crippling cognitive debt, because nobody understands the pristine code either.

**Intent debt lives in artifacts.** It’s the absence or erosion of the *externalized* rationale, goals, and constraints that explain why the system is the way it is. The key word is externalized. The rationale has to be written down where a teammate, a future you, or an agent can read it, not held in your head. When intent debt runs high, the system drifts from what you meant it to do, and nobody can say when it diverged or why.

These three are independent, which took me a while to internalize.

You can have low technical debt and high intent debt. You can understand a system completely yourself (no cognitive debt for you) while its intent exists nowhere outside your skull (enormous intent debt for everyone else).

From the inside they feel alike, but each one bills you separately.

## Why intent debt is the one agents can’t help with

AI generates code faster than ever, which makes technical debt cheaper to take on and cheaper to pay down. Point an agent at a tangled module and it’ll refactor it.

Cognitive debt recovers too, more easily than most engineers expect. When you don’t understand a chunk of the system, you ask the agent to explain it. You rebuild part of the lost mental model on demand, because the code still exists and the model can read it back to you.

Intent is different. **An agent can’t generate intent, because intent is the one input that has to come from you.** A model can infer a plausible rationale from the code, the same way you can guess why a previous engineer did something. A guess about intent isn’t the intent. The model doesn’t know whether that 300ms debounce was a deliberate UX decision, a benchmark result, or a number someone typed once and never revisited. It will invent a confident-sounding reason, which is worse than admitting it doesn’t know.

Of the three debts, intent debt is the only one where the agent can’t bail you out. It can write the code and restore your comprehension. The *why* is the one thing it can only fabricate.

## Agents make the un-written cost compound much faster

Teams got away with high intent debt for years because we carried it in our head and old docs.

When a new human joined a team, you didn’t write everything down, because they picked up intent over time: hallway conversations, code review comments, “oh, we don’t do it that way because of an incident in 2023.” Knowledge moved person to person and built up. The engineer who’d been there four years was the intent documentation, expensive and lossy, but it worked.

Agents break that model. Bringing agents onto a team doubles its size overnight with junior people who have no long-term memory. **An agent starts most sessions cold.** It carries none of the tacit intent your humans built up over years. Whatever you haven’t externalized into an artifact it can read, it doesn’t have.

That changes the economics of *not writing things down*. Un-externalized intent used to cost you once in a while, at onboarding or after someone left. Now you pay it every session, multiplied by every agent you run.

Picture the 20 agents you’re so excited to parallelize. Each one is a teammate who has never met you, can’t read your mind, and will fill any gap in your intent with a plausible guess. The orchestration tax I [wrote about](https://addyosmani.com/blog/orchestration-tax/) is partly an intent-debt tax. Much of what makes managing many agents exhausting is re-supplying the intent you never wrote down.

## The other half of the comprehension debt argument

When I wrote about [comprehension debt](https://addyosmani.com/blog/comprehension-debt/), I made a point I want to revisit, because intent debt sharpens it.

I argued that detailed specs aren’t a complete answer. Translating a spec into working code involves a huge number of implicit decisions no spec ever captures, and a spec detailed enough to *be* the program is the program in a slower language. I still believe that.

Intent debt is the complementary truth.

Being unable to capture *all* intent is no license to capture *none* of it. The implicit decisions an agent now makes on your behalf, the ones a spec will never enumerate, are the decisions whose rationale evaporates if you don’t record at least the load-bearing ones. You can’t write down everything.

You do have to write down the *why* behind the choices that would be expensive to get wrong, because nobody will reconstruct those later.

Comprehension debt warns you not to trust that code is correct because it exists.

Intent debt warns you not to trust that the *reason* survives because the code does. Code is the answer; the intent was the question it was meant to solve. AI is brilliant at producing answers to questions you forgot to write down.

## What high intent debt looks like

Intent debt rarely shows up as friction. It shows up as a particular kind of helplessness.

- An agent “fixes” a bug by deleting a guard clause, and nobody can say whether that guard was load-bearing or leftover, because no doc or commit message ever recorded why it was there.
- A refactor changes a behavior users depend on. The review passed because the diff looked clean and the tests were green, but the tests only encoded the previous behavior, never the intent.
- You ask why two services talk over a queue instead of a direct call, and the honest answer is “an agent suggested it and it seemed fine.” That answer is intent debt, already accruing interest.

If you’ve felt the [cognitive surrender](https://addyosmani.com/blog/cognitive-surrender/) version of this, defending a design choice you can’t reconstruct, intent debt is the team-scale, written-down version of the same hole.

Surrender is about your own posture in the moment. Intent debt is what a hundred of those moments leave in the repo for the next person and the next agent to inherit.

## Paying it down: externalize intent as a first-class artifact

Almost everything I’ve been writing about for the last few months turns out to be intent-debt management. I didn’t have the word for it. The move is the same each time: **take the intent out of your head and put it somewhere an agent can read.**

**Write the spec for the intent, not the implementation.** A [good spec](https://addyosmani.com/blog/good-spec/) captures the goals, the constraints, the non-negotiables, and an explicit definition of *done* (fast, accessible, secure, delightful, beyond “functionally correct”). The spec carries the intent the code can’t carry on its own.

**Treat AGENTS.md as your intent ledger, not your config.** It’s why I keep saying [stop using /init](https://addyosmani.com/blog/agents-md/). An auto-generated file describes what the code is. An intent file describes what the team means: the conventions, the “we don’t do it this way because,” the constraints invisible in any single file. Agents can’t infer that, and they need it most.

**Capture decisions where they happen.** Lightweight [decision logs](https://addyosmani.com/blog/automated-decision-logs/) (ADRs) are pure intent-debt paydown. Recording *why* at the moment you decide costs almost nothing. Reconstructing it eight months later, after the person who knew has moved teams, costs a fortune. Agents have made logging cheaper than ever, so the old excuse is gone.

**Make the learning loop write intent back down.** I’ve argued for [self-improving agents](https://addyosmani.com/blog/self-improving-agents/) that update a learnings file at the end of a session. The same loop is an intent-debt pump running in reverse: every mistake whose root cause you record, every “we tried X and it didn’t work because Y” is intent that would otherwise have lived only in your memory of a bad afternoon.

None of these are new tools. They’re the discipline of refusing to let the *why* exist only in your head, in an era where your head is no longer where most of the work happens.

## Where the value moved

For a long time, the scarce, valuable thing in software was the ability to produce a correct implementation. Code was expensive, so we optimized for writing it.

AI made code cheap, and comprehension is recoverable. Intent, the goals and constraints and reasons, is the one input that still has to originate with a human. It’s also the one we’re worst at externalizing, because for decades we got away with carrying it in our heads.

That worked when the team was a handful of people who could absorb intent over years of shared context. It does not work when half the team is agents that start every session as strangers.

Technical debt makes your system hard to change. Cognitive debt makes it hard to understand. Intent debt makes it hard to know whether the system still does what you wanted, and it’s the only one of the three your agents can’t pay back for you. That part stays with you. Write down the why, because it’s becoming the most valuable thing you can leave in the repo.
