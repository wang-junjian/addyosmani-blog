# Agentic Engine Optimization (AEO)

> 原文：https://addyosmani.com/blog/agentic-engine-optimization/
>
> 发布日期：2026-04-11

---

*How AI coding agents consume documentation is fundamentally different from how humans do - and if you’re still optimizing only for human readers, you’re leaving a growing share of your audience invisible to your tooling. Docs, CLIs, MCPs, Skills…there’s a whole ecosystem of interfaces that AI agents interact with.*

---

> **Disclosure and context.** I’m a Director at Google Cloud AI, so a few things are worth flagging before you read on. The Lighthouse team in Chrome have shipped an experimental `llms.txt` check ([docs](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt), [coverage](https://searchengineland.com/google-llms-txt-chrome-lighthouse-478246)); independently, the Google Search / Webmaster team have published [their own guidance on SEO and AI agents](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), and Search does **not** officially recommend `llms.txt` as a standard. My position on AEO in this post should be read through a specific lens: my audience here is developers, and for that audience we should fully expect agents to consume docs more and more (vs humans) via agentic coding tools like Claude Code, Gemini CLI, Cursor, and Copilot. Optimizing for that consumption pattern makes sense for developer-facing docs even where it diverges from broader Search guidance aimed at the open web. Treat this as one practitioner’s view from inside the developer-tools world, not a Google-wide recommendation.

I’ve been watching something play out across developer portals that I think deserves more attention than it’s getting.

An engineer opens Claude Code, asks it to implement a spec and hits enter. The agent fetches some of your documentation. It might grab some of what it needs, parse it as raw text, strip the HTML, count the tokens, and either use it as context - or silently discard it because the token count exceeds its context window.

Your analytics recorded nothing useful. Scroll depth was zero. Time-on-page was 400 milliseconds. No link clicks, no tutorial completions, no UI interactions. The funnel you’ve optimized for years showed nothing.

But the agent was absolutely there. It read your docs. And depending on how those docs were structured, it either completed the task successfully - or hallucinated a solution because the content was too token-heavy, poorly structured, or blocked by a misconfigured `robots.txt`.

I’ve started calling the discipline that addresses this **Agentic Engine Optimization**.

---

## What is Agentic Engine Optimization?

**Agentic Engine Optimization (AEO)** is the practice of structuring, formatting, and serving technical content so that AI coding agents can actually use it - not just human readers.

The analogy I keep coming back to is SEO. We spent years learning to optimize for search crawlers and human click patterns. AEO is the same idea, but for a different consumer: AI agents that autonomously fetch, parse, and reason over your content.

The things that matter turn out to be pretty specific:

- **Discoverability** - can agents find your documentation without rendering JavaScript?
- **Parsability** - is the content machine-readable without requiring visual layout interpretation?
- **Token efficiency** - does the content fit within typical agent context windows without truncation?
- **Capability signaling** - does the documentation tell agents what your API *does*, not just how to call it?
- **Access control** - does your `robots.txt` actually let AI traffic through?

If any of these fail, agents either skip your content entirely or produce subtly wrong outputs. The tricky part is you’ll probably never know, because no analytics event fires.

---

## How AI agents actually read your documentation

It’s worth spelling out the behavioral difference here, because it’s bigger than I initially expected.

### The human pattern

A human developer lands on your docs homepage. They navigate to a relevant section. They skim headings, read a few paragraphs, maybe run a code sample in the interactive console, follow two or three internal links, and spend 4–8 minutes in session. Your analytics captures all of it.

### The agent pattern

A [recent research paper](https://arxiv.org/html/2604.02544v1) (Developer Experience with AI Coding Agents) studied HTTP traffic from nine major AI coding agents - including Claude Code, Cursor, Cline, Aider, VS Code, and Junie - fetching developer documentation. The findings were pretty striking.

Agents typically compress multi-page navigation into one or two HTTP requests. Where a human would spend minutes clicking through your documentation hierarchy, an agent issues a single `GET` request, receives the full page, and moves on. The whole concept of “user journey” collapses into a single server-side event.

The practical consequence: every client-side analytics event - scroll depth, time-on-page, button clicks, tutorial completions, link follows, form interactions - becomes invisible. The agent just bypasses all of it.

### The fingerprints of AI traffic

The study also identified distinct behavioral signatures you can use to spot AI agent traffic in your server logs:

| Agent | HTTP Runtime | Pre-fetch Behavior | Signature |
|----|----|----|----|
| Aider | Headless Chromium (Playwright) | On-demand GET | Full Mozilla/Safari user-agent |
| Claude Code | Node.js / Axios | On-demand GET | `axios/1.8.4` |
| Cline | curl | GET + OpenAPI/Swagger sweep | `curl/8.4.0` |
| Cursor | Node.js / got | HEAD probe → GET | got (sindresorhus/got) |
| Junie | curl | Sequential multi-page GET | `curl/8.4.0` |
| OpenCode | Headless Chromium (Playwright) | On-demand GET | Full Mozilla/Safari user-agent |
| VS Code | Electron / Chromium | On-demand GET | Chromium-style with Electron markers |
| Windsurf | Go / Colly | On-demand GET | `colly` |

Beyond coding agents, AI assistant web services (ChatGPT, Claude, Google Gemini, Perplexity) also generate distinct fingerprints when users share URLs in chat interfaces - triggering their own server-side fetches.

Once you know what to look for, you can start segmenting AI agent traffic in your analytics. I was surprised how much of it was already there in my own logs.

---

## The token problem: your docs may be invisible to agents

This is probably the most underappreciated part of the whole picture: **token economics**.

Agents don’t have infinite context. Most have practical limits between 100K–200K tokens, and context management is an active constraint in every task. The paper highlights a concrete example: the Cisco Secure Firewall Management Center REST API Quick Start Guide (Version 10.0) comes in at **193,217 tokens** - nearly 718,000 characters. That single document threatens to consume or exceed most agents’ entire usable context window.

When an agent hits a document that’s too long, a few things can happen - none of them good:

- It may truncate silently, cutting off critical information
- It may skip the document entirely in favor of something shorter
- It may attempt chunking, which adds latency and error surface
- It may fall back to parametric knowledge - i.e., make something up

I think this means **token count is now a first-class documentation metric**. If you’re not tracking token counts for your documentation pages, you’re missing a signal that agents actually use to decide whether to even attempt reading your content.

### Practical token targets

Here’s what seems to work as a rough guide:

- **Quick start / getting started pages**: \< 15,000 tokens
- **Individual API reference pages**: \< 25,000 tokens
- **Full API reference**: chunk by resource/endpoint, not by product
- **Conceptual guides**: \< 20,000 tokens; link to detail rather than embed it

---

## The AEO stack: what to actually build

AEO isn’t a single thing - it’s a layered set of signals and standards. I’ve been thinking of it as a stack, from foundation to surface:

### Layer 1: Access control (`robots.txt`)

This is the agent’s first stop. Before fetching content, many agents check `robots.txt` to determine what they’re allowed to access.

A misconfigured `robots.txt` that blocks known AI crawlers will silently deny agents access to your documentation entirely. No traffic, no errors, no indication anything went wrong. I’ve seen this trip up teams who had no idea their docs were invisible to agents.

The practical steps:

- Audit your `robots.txt` for unintended blocks on AI agent user-agents
- Consider explicitly permitting well-known AI agent patterns (Anthropic, OpenAI, Google, Perplexity crawlers)
- If you need more nuanced control, look at `agent-permissions.json` - an emerging spec that lets you declaratively specify which automated interactions are allowed, rate limits, preferred API endpoints, and more

### Layer 2: Discovery via `llms.txt`

Even if an agent can access your content, it still needs to find the *right* content. This is where `llms.txt` comes in.

I think of `llms.txt` as a sitemap for AI agents. It’s a flat, Markdown-formatted file hosted at `yourdomain.com/llms.txt` that provides a structured directory of your documentation - descriptions and all, so agents can figure out what’s relevant without having to crawl your entire site.

A well-formed `llms.txt` looks something like:

```markdown
# YourProduct Documentation

## Getting Started
- [Quick Start Guide](/docs/quickstart): Install and make your first API call in 5 minutes
- [Authentication](/docs/auth): OAuth 2.0 and API key authentication patterns
- [Core Concepts](/docs/concepts): Data model, entities, and terminology

## API Reference
- [REST API Overview](/docs/api): Base URLs, versioning, pagination, error codes
- [Users API](/docs/api/users): CRUD operations for user management (12K tokens)
- [Events API](/docs/api/events): Event streaming and webhook configuration (8K tokens)

## MCP Integration
- [MCP Server](/docs/mcp): Model Context Protocol server for direct agent integration
```

What makes a good `llms.txt`:

- Descriptions that tell the agent what it will *find*, not just what the page is called
- Token counts per page where useful (so agents can make informed context decisions)
- Organized by task, not by product hierarchy
- Kept under 5,000 tokens itself (it shouldn’t blow the budget just being an index)

### Layer 3: Capability signaling via `skill.md`

`llms.txt` tells agents where things are. `skill.md` tells them what your product can actually *do*.

This is a distinction that I think matters more than it first appears. Instead of an agent having to infer capabilities from prose documentation, `skill.md` surfaces them declaratively - mapping intentions to endpoints and resources.

A `skill.md` for an authentication service might look like:

```markdown
---
name: auth-service
description: Handles user authentication, OAuth 2.0 flows, and session management
---

## What I can accomplish
- Authenticate users via OAuth 2.0 (authorization code, client credentials, PKCE)
- Issue and validate JWT tokens
- Manage user sessions and refresh token rotation
- Integrate with SSO providers (SAML, OIDC)

## Required inputs
- Client ID and Client Secret (from developer console)
- Redirect URI (must be pre-registered)
- Requested scopes (read:user, write:data, admin)

## Constraints
- Rate limit: 1000 token requests per minute per application
- Token expiry: access tokens 1hr, refresh tokens 30 days
- PKCE required for public clients

## Key documentation
- [OAuth 2.0 Guide](/docs/oauth): Full flow walkthrough with code samples
- [Token Reference](/docs/tokens): Token structure, claims, validation
- [Postman Collection](/docs/postman): Ready-to-use request templates
```

This is what lets agents make meaningful decisions - not just fetch documentation, but understand whether your API can even satisfy the user’s intent before spending context budget on a full read.

### Layer 4: Content formatting for agent parsing

Even with perfect discovery and capability signaling, the actual content needs to be agent-readable. A few things I’ve found matter here:

**Serve Markdown, not just HTML.** Many documentation platforms let you access raw Markdown by appending `.md` to a URL or via a query parameter. Make this discoverable. Agents process Markdown with dramatically lower token overhead than HTML (no tag noise, no navigation chrome, no footer cruft).

**Structure for scanning, not reading.** Agents don’t read linearly - they parse structure:

- Use consistent heading hierarchies (H1 → H2 → H3, no skipping)
- Lead each section with the outcome, not the background
- Put code examples immediately after the claim they illustrate
- Use tables for parameter references - they compress better than prose lists

**Kill the navigation noise.** Sidebars, breadcrumbs, and footer links that appear in your HTML are just noise in Markdown/text. Keep them out of the parseable content path.

**Front-load the useful stuff.** The first 500 tokens of any page should answer: what is this, what can it do, and what do I need to get started. Agents have limited patience for preamble.

### Layer 5: Token surfacing

This one is simpler than it sounds but surprisingly high-leverage: surface token counts on your documentation pages. Ideally in both the `llms.txt` index and on the pages themselves (as metadata or a page header).

This gives agents the information they need to make smart decisions:

- “This page is 8K tokens - I can include it fully in context”
- “This page is 150K tokens - I should fetch only the relevant section”
- “This page exceeds my context window - I’ll use the summary from llms.txt instead”

Implementation is straightforward: count characters server-side, divide by ~4 for a rough token estimate, and expose it as a meta tag or HTTP response header.

### Layer 6: “Copy for AI”

This is more of a UX bridge than an infrastructure layer, but I think it’s worth including: the **Copy for AI** button.

When a developer is working inside an IDE with an AI assistant and wants to include documentation as context, they currently copy and paste from rendered HTML - which includes navigation noise, footers, all of it. A “Copy for AI” button that copies clean Markdown to the clipboard is a small thing, but it meaningfully improves the quality of context the agent receives.

Anthropic, Cloudflare, and others have already shipped variants of this. It’s low effort and high signal.

---

## AGENTS.md: the emerging default

One thing worth calling out specifically: `AGENTS.md`.

Just as `README.md` became the default entry point for human developers exploring a repository, `AGENTS.md` is becoming the entry point for AI agents. When a coding agent opens a project, it looks for `AGENTS.md` in the root directory and pulls its instructions into every subsequent task.

I’ve been [writing about this separately](https://addyosmani.com/blog/agents-md/), but the short version is that a good `AGENTS.md` includes:

- Project structure and key file locations
- Direct links to relevant API or service documentation
- Available dev sandboxes and test environments
- Rate limits and constraints the agent should know about
- Preferred patterns and conventions for the codebase
- Links to MCP servers if available

Cisco DevNet has already adopted this as the default file in their GitHub template for open-source projects - newly created projects come with an `AGENTS.md` pre-populated with project-specific content, links to OpenAPI docs, DevNet sandboxes, and test environments.

---

## Monitoring AI referral traffic

One thing you can do right now: start tracking AI referral traffic in your analytics.

Here are the referral sources worth watching:

```text
labs.perplexity.ai/referral
chatgpt.com/(none)
chatgpt.com/organic
link.edgepilot.com/referral
platform.openai.com/referral
perplexity/(not set)
claude.ai/referral
copilot.microsoft.com/referral
gemini.google.com/referral
```

You’ll also want to monitor for the HTTP fingerprints I mentioned earlier - `axios/1.8.4`, `curl/8.4.0`, `got (sindresorhus/got)`, `colly` - to catch direct agent traffic that arrives without a referrer.

Building a proper AI traffic segment gives you the leading indicators for whether any of this work is actually making a difference.

---

## The broader implications for developer experience

I want to step back for a moment, because I think AEO points at something bigger than a technical checklist.

For most of the web’s history, developer portals were designed around human cognitive patterns: progressive disclosure, visual hierarchy, interactive examples, guided tutorials. All of those assume a human is in the loop at every step.

In an agent-heavy world, many of those assumptions break down:

- **Visual hierarchy is irrelevant** - agents read text, not layouts
- **Progressive disclosure becomes an obstacle** - agents want everything at once
- **Interactive examples lose their value** - unless there’s a static/API equivalent
- **User journeys collapse** - a multi-chapter tutorial becomes a single context load

This doesn’t mean human-centered design stops mattering. Humans still read docs. But they increasingly read them *inside an AI assistant’s context* - which means the agent is often the proximate consumer, even when a human is the ultimate beneficiary.

The best documentation going forward will probably need to serve both audiences at once: scannable and well-structured for humans, machine-readable and token-efficient for agents.

---

## AEO audit checklist

Here’s what I’d check if I were evaluating a documentation site’s agent-readiness today:

**Discovery**

- [ ] `llms.txt` exists at root with structured index of all documentation
- [ ] `robots.txt` does not inadvertently block known AI agent user-agents
- [ ] `agent-permissions.json` defines access rules for automated clients
- [ ] `AGENTS.md` exists in code repositories linking to relevant docs

**Content structure**

- [ ] Documentation pages available as clean Markdown (not just rendered HTML)
- [ ] Each page leads with a clear outcome statement in the first 200 words
- [ ] Headings are consistent and hierarchically correct
- [ ] Code examples immediately follow their prose description
- [ ] Parameter references use tables, not nested prose

**Token economics**

- [ ] Token counts are tracked per documentation page
- [ ] No single page exceeds 30,000 tokens without chunking strategy
- [ ] Token counts exposed in `llms.txt` for key pages
- [ ] Token counts available as page metadata (meta tag or HTTP header)

**Capability signaling**

- [ ] `skill.md` files describe what each service/API *does*, not just how to call it
- [ ] Each skill includes: capabilities, required inputs, constraints, key doc links
- [ ] MCP server available for direct agent integration (if applicable)

**Analytics**

- [ ] AI referral sources segmented in web analytics
- [ ] Server logs monitored for known AI agent HTTP fingerprints
- [ ] Baseline established for AI vs. human traffic ratio

**UX bridge**

- [ ] “Copy for AI” button available on documentation pages
- [ ] Markdown source accessible via URL convention (e.g., appending `.md`)

**Tooling**

To help automate some of these checks, I’ve shipped [agentic-seo](https://github.com/addyosmani/agentic-seo) - a lightweight audit tool that scans your site for AEO opportunities. It checks for `llms.txt`, `robots.txt` agent blocking, token counts, Markdown availability, and more. Think of it as Lighthouse, but for agent-readiness.

---

## Where to start

If you’re looking at this list and wondering where to begin, here’s the sequence I’d recommend:

1.  **Audit your `robots.txt`** - ten minutes of work, prevents silent agent lockout
2.  **Add `llms.txt`** - a few hours, immediate discoverability gains
3.  **Measure and surface token counts** - a weekend project with high leverage
4.  **Write `skill.md` for your top 3 APIs** - start with whatever agents are most likely to reach for
5.  **Add “Copy for AI” buttons** - low effort, high signal
6.  **Set up AI traffic monitoring** - gives you the data to justify everything else

---

## Wrapping up

SEO taught us that great content isn’t enough - you have to make it discoverable in the way that matters for the actual traffic patterns of the era. I think AEO is the same lesson, just for a different consumer.

AI coding agents are already a significant and growing share of documentation traffic. They behave fundamentally differently from human readers. And most developer portals aren’t built for them yet.

The teams that move early here will probably have a real advantage: their APIs will be the ones agents recommend, integrate successfully, and come back to. The ones that don’t will see growing gaps between documentation quality and actual agent task success - a silent failure mode that’s genuinely hard to debug.

The good news is that building for agents tends to make documentation better for humans too. The disciplines overlap more than they diverge.

Start with `llms.txt`. Ship a `skill.md`. Audit your `robots.txt`. Measure your tokens. Most of this is a weekend’s worth of work, and the payoff is already real.
