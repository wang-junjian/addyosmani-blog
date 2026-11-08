# The Agent Stack Bet

> 原文：https://addyosmani.com/blog/the-agent-stack-bet/
>
> 发布日期：2026-04-18

---

Peek under the hood of most “production agents” shipping today and you won’t find intelligence. You’ll find custom plumbing, fragile session logic, shared service accounts, and a security model held together by hope. This can be so much better.

If you’ve spent the last 18 months putting agents into production, you already know the models and tools have gotten *dramatically* better. You also know the problems that are still burning your on-call rotation are not problems you can prompt your way out of. We are running into a **stack ceiling**, and it is quietly creating a **governance** and **reliability gap** that the next generation of agentic systems cannot grow through.

Right now the industry is living with what I’d call *excessive agency*: **autonomous systems given broad permissions to get things done**, then left to discover - at runtime, in production - that a schema drifted, an API changed, or a downstream service started returning PII it wasn’t supposed to. Agents mark tasks “complete” while leaving a trail of corrupted state behind them. The humans find out on Monday.

This is not a failure of the people building agents. It is a failure of the stack they’re building on.

Here are the four architectural bets I think every serious team has to make in the next twelve months.

## 1) Agents need identities, not shared credentials

Every engineer who has shipped agents to production knows this specific flavor of dread: you have agents doing useful work, and effectively zero visibility into which tools they touched, which data they moved, or which credentials they used to do it. I call this *governance debt* - the silent accumulation of security and audit risk that eventually forces a full rewrite, usually right after the first incident that reaches the CISO.

The root cause is that most agents today are ghosts. They don’t have identities. They borrow a service account, inherit a human’s OAuth token, and “promise” - in application code, in a prompt - to stay inside the lines. In a real enterprise environment, a promise in a prompt is not a policy.

**My bet is that agent identity has to move from the application layer down into the platform layer.**

The difference is between bolted-on vs. embedded security. Bolted-on looks like middleware in front of every tool call, politely asking the agent to behave: easy to bypass, expensive in latency, and invisible to your existing IAM. Embedded looks like a badge reader welded into a steel frame. The agent has a distinct, unforgeable identity recognized at the network and platform level, and policy is enforced at the source. If the agent reaches for a database it isn’t cleared for, the connection never opens. No middleware, no vibes.

Done right, this turns “a fleet of liabilities” into something that looks a lot more like a managed workforce: every action attributable, every permission auditable, every agent revocable with one call.

## 2) Agents need universal context, not scraped windows

Context management is a tax every builder is currently paying. Teams are burning a huge share of their engineering hours (and tokens) on undifferentiated plumbing - custom serialization, bespoke session stores, hand-rolled memory layers - just to keep an agent from forgetting its mission halfway through a multi-step task.

Worse, the context agents *can* get their hands on is usually siloed. A browser-based agent can see the open tab. A desktop wrapper can see the files a user happened to drag in. Neither of them can easily reason across the systems where the business actually lives - the CRM, the ERP, the data warehouse, the ticketing system, the transcripts, the project plans - at the same time.

**Agents need universal context that integrates at the platform level.** If we don’t fix this, we should be honest that the ceiling of agentic AI is “slightly better spreadsheet autocomplete,” and we should stop writing vision pieces about it.

# 3) Agents need to survive your laptop closing

Here’s the uncomfortable version of this: a lot of what ships today as “an agent” isn’t yet ready to deploy across a business.

I want to be precise, because the frontier has genuinely moved in the last six months. Environments like Claude Code, OpenClaw, and similar platforms are capable - persistent task state, scheduled execution, multi-agent coordination, and long-running sessions that survive disconnects are no longer aspirational. These are not toys. The question has moved on.

The question now is whether an agent can run for a week instead of an hour. Whether it can cross three handoffs, two credential rotations, and an approval gate without a human babysitting the session. Whether the work it did on Tuesday is auditable on Friday by someone who wasn’t in the room. A session that survives a dropped WebSocket is table stakes. A mission that survives a quarter is the bar enterprises actually need.

Real work doesn’t fit in a session, and most of it doesn’t fit in a day either. A procurement workflow spans weeks and a dozen handoffs. A compliance audit runs for a month. An incident investigation outlives three on-call rotations.

**Most agents today hit a hard ceiling - sometimes time-based, sometimes token-based, sometimes governance-based - and when they hit it, the mission fails and a human picks up the pieces from wherever the transcript ended.**

Enterprise-grade autonomy requires durable, cloud-native execution with a much higher floor than “the session stayed up.” Concretely, that means:

- **State** and **checkpointing** that survives restarts, disconnects, redeploys, and model version changes by default - not bolted on with a local Redis and a prayer.
- **Context that outlives the window**: long-horizon memory, summarization, and handoff between agent instances, so a multi-week task doesn’t die because a single run exhausted its tokens.
- **Missions that outlive sessions**: agents that stay on the job across days, handoffs, and credential rotations, with an auditable trail of what happened while you were asleep.
- **First-class human-in-the-loop primitives,** so the agent can pause and ask for permission to do something new instead of silently deciding it has the authority.

Persistence with guardrails. That’s the bar. Anything less and you’re building demos that happen to run for a long time.

# 4) Agents need platforms

The pattern I see most often in strong teams is the saddest one: brilliant engineers draining their bandwidth into stack problems that do not differentiate their product. Custom memory. Bespoke eval harnesses. Homegrown observability. Handwritten retry logic. A tracing system that almost works. None of this is the hard part of the agentic era, and none of it is what your users are paying you for.

The real value lives in domain reasoning and business logic - the judgment calls that are specific to your company, your customers, your regulatory environment. Everything underneath should be the platform you *build on*, not the plumbing you *build*.

This is why the maturation of open primitives matters right now. Open-source orchestration frameworks exist precisely so the scaffolding isn’t locked behind any single vendor’s roadmap. The model that worked for cloud compute, containers, and CI/CD - start local on open primitives, graduate to a managed platform when you’re ready to scale - is the model agent platforms need to copy.

**Teams should be able to prototype on their laptop with the same building blocks they’ll run in production, and cross that boundary without a rewrite.**

That’s the engineering standard that lets teams stop fighting plumbing and get back to the product.

## The five-year horizon

The teams that pull ahead in the next five years will not pull ahead by being smarter at writing boilerplate. They’ll pull ahead by **choosing the right agent foundation** and spending their engineering hours on the problems ***only they can solve***.

Every month spent rebuilding the common stack - identity, context, persistence, orchestration - is a month not spent on the logic that actually makes your agents worth deploying.

**The agent stack has to become a solved problem.** The only real question is whether you want to solve it yourself, again, or build on a foundation that was engineered for agents from the ground up.

My bet is on the latter. I think yours should be too.
