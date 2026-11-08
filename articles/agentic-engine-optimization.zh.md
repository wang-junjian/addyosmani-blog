# 智能体引擎优化（AEO）

> 原文：[Agentic Engine Optimization (AEO)](https://addyosmani.com/blog/agentic-engine-optimization/)
>
> 发布日期：2026-04-11

---

*AI 编码智能体消费文档的方式，与人类有着根本性的不同——如果你仍然只为人这一侧的读者做优化，你就在把越来越多的受众放到了你的工具看不见的地方。文档、CLI、MCP、技能……AI 智能体与之交互的界面，已经是一整个生态。*

---

> **披露与背景。** 我是 Google Cloud AI 的总监，所以在你继续往下读之前，有几件事值得先说清楚。Chrome 里的 Lighthouse 团队已经上线了一项实验性的 `llms.txt` 检查（[文档](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt)、[覆盖情况](https://searchengineland.com/google-llms-txt-chrome-lighthouse-478246)）；另外，Google Search / Webmaster 团队已经发布了[他们自己关于 SEO 与 AI 智能体的指引](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)，而 Search **并不**正式推荐把 `llms.txt` 当作标准。我在本文中对 AEO 的立场应当通过一个特定的镜头来读：我这里的受众是开发者，而对这个受众来说，我们应当完全预期智能体会越来越多地（相对人类）通过 Claude Code、Gemini CLI、Cursor、Copilot 这类智能体编码工具来消费文档。即便这与面向开放网络、更广泛的 Search 指引有所分歧，为这种消费模式做优化，对面向开发者的文档也是合理的。请把这当作来自开发者工具世界内部的一位实践者观点，而不是 Google 全公司的建议。

我一直在开发者门户上观察着一些事，我觉得它值得比现在更多的关注。

一位工程师打开 Claude Code，要求它实现一份规格，然后按下回车。智能体抓取了你的一部分文档。它可能拿到了自己需要的部分，把它当纯文本解析、剥掉 HTML、数了数 token，然后要么把它当上下文用——要么因为 token 数超出上下文窗口而悄悄丢弃。

你的分析工具什么都没记录到有用的东西。滚动深度是零。页面停留时间是 400 毫秒。没有链接点击，没有教程完成，没有 UI 交互。你优化了多年的那个漏斗，什么都没显示。

但智能体确实来过。它读了你的文档。而取决于那些文档是怎么组织的，它要么成功完成了任务——要么因为内容 token 太重、结构太差，或者被一个配置错误的 `robots.txt` 挡住，而幻觉出了一个方案。

我已经开始把应对这件事的这门手艺叫作**智能体引擎优化**。

---

## 什么是智能体引擎优化？

**智能体引擎优化（AEO）** 是一门实践：对技术内容进行结构化、格式化与投递，让 AI 编码智能体真正能用上它——而不只是人类读者。

我反复回到的类比是 SEO。我们花了很多年学习为搜索爬虫和人类点击模式做优化。AEO 是同一个想法，但面向一个不同的消费者：那些自主抓取、解析并推理你内容的 AI 智能体。

真正重要的东西最后发现相当具体：

- **可发现性**——智能体能不渲染 JavaScript 就找到你的文档吗？
- **可解析性**——内容在不依赖视觉布局解读的前提下是机器可读的吗？
- **token 效率**——内容能装进典型智能体的上下文窗口而不被截断吗？
- **能力信号**——文档有没有告诉智能体你的 API *能做什么*，而不只是怎么调用它？
- **访问控制**——你的 `robots.txt` 真的放 AI 流量进来了吗？

这几点只要有一样不达标，智能体要么完全跳过你的内容，要么产出微妙地错误的结果。棘手的地方在于你大概永远不会知道，因为没有任何分析事件会触发。

---

## AI 智能体实际上是怎么读你的文档的

这里的行为差异值得说清楚，因为它比我最初预期的更大。

### 人类的模式

一个人类开发者落到你的文档首页。他导航到一个相关的章节。他扫一遍标题，读几段，也许在交互式控制台里跑一个代码示例，跟着两三个内部链接，然后总共待上 4–8 分钟。你的分析工具把这些全都记录下来了。

### 智能体的模式

[最近的一篇研究论文](https://arxiv.org/html/2604.02544v1)（Developer Experience with AI Coding Agents）研究了九个主流 AI 编码智能体抓取开发者文档时的 HTTP 流量——包括 Claude Code、Cursor、Cline、Aider、VS Code 和 Junie。结论相当惊人。

智能体通常把多页导航压缩成一两次 HTTP 请求。在一个人类会花几分钟点过你的文档层级的场合，智能体发一个 `GET` 请求、收到整页、然后就走。整个「用户旅程」的概念塌缩成一次服务端事件。

实际的后果是：每一个客户端分析事件——滚动深度、页面停留时间、按钮点击、教程完成、链接跟随、表单交互——都变得不可见。智能体直接绕过了这一切。

### AI 流量的指纹

这项研究还识别出了你可以用来在服务器日志里发现 AI 智能体流量的独特行为签名：

| 智能体 | HTTP 运行时 | 预取行为 | 特征指纹 |
|----|----|----|----|
| Aider | 无头 Chromium（Playwright） | 按需 GET | 完整的 Mozilla/Safari user-agent |
| Claude Code | Node.js / Axios | 按需 GET | `axios/1.8.4` |
| Cline | curl | GET + OpenAPI/Swagger 扫查 | `curl/8.4.0` |
| Cursor | Node.js / got | HEAD 探测 → GET | got（sindresorhus/got） |
| Junie | curl | 顺序多页 GET | `curl/8.4.0` |
| OpenCode | 无头 Chromium（Playwright） | 按需 GET | 完整的 Mozilla/Safari user-agent |
| VS Code | Electron / Chromium | 按需 GET | 带 Electron 标记的 Chromium 风格 |
| Windsurf | Go / Colly | 按需 GET | `colly` |

除了编码智能体，AI 助手类 Web 服务（ChatGPT、Claude、Google Gemini、Perplexity）在用户于聊天界面里分享 URL 时也会产生独特的指纹——触发它们自己那一侧的服务端抓取。

一旦你知道该找什么，你就可以开始在分析工具里切分 AI 智能体流量了。我很意外我自己的日志里已经有多少。

---

## token 问题：你的文档可能对智能体不可见

这大概是整幅图景里最被低估的部分：**token 经济学**。

智能体没有无限的上下文。大多数实际限制在 100K–200K token 之间，而上下文管理在每一个任务里都是活跃的约束。论文里举了一个具体的例子：Cisco Secure Firewall Management Center REST API Quick Start Guide（Version 10.0）全文是 **193,217 个 token**——将近 718,000 个字符。仅这一份文档就足以吃掉或超过大多数智能体整个可用的上下文窗口。

当一个智能体撞上一份太长的文档，可能发生几件事——没有一件是好事：

- 它可能静默截断，把关键信息切掉
- 它可能完全跳过这份文档，改去用更短的
- 它可能尝试分块，这增加了延迟和出错面
- 它可能退回到参数化知识——也就是，编一个

我认为这意味着 **token 数现在是一项一等的文档指标**。如果你没有在追踪文档页面的 token 数，你漏掉了一个智能体真正会用来决定要不要尝试读你内容的信号。

### 实用的 token 目标

下面这些作为粗略的参考似乎是有用的：

- **快速开始／入门页面**：\< 15,000 token
- **单个 API 参考页**：\< 25,000 token
- **完整 API 参考**：按资源／端点分块，不要按产品分块
- **概念指南**：\< 20,000 token；细节用链接指向，而不是内嵌

---

## AEO 技术栈：到底要建什么

AEO 不是单一的一件事——它是一层层的信号与标准。我一直把它想成一个栈，从地基到表面：

### 第一层：访问控制（`robots.txt`）

这是智能体的第一站。在抓取内容之前，许多智能体会检查 `robots.txt` 来确定自己被允许访问什么。

一个把已知 AI 爬虫挡住的、配置错误的 `robots.txt`，会静默地完全拒绝智能体访问你的文档。没有流量，没有报错，没有任何出错的迹象。我见过这坑到那些完全不知道自己的文档对智能体不可见的团队。

实际的做法：

- 审计你的 `robots.txt`，看有没有对 AI 智能体 user-agent 的意外封禁
- 考虑显式允许知名的 AI 智能体模式（Anthropic、OpenAI、Google、Perplexity 的爬虫）
- 如果你需要更细致的控制，看看 `agent-permissions.json`——一个正在浮现的规范，让你以声明式的方式指定允许哪些自动化交互、速率限制、首选 API 端点等等

### 第二层：通过 `llms.txt` 被发现

即便智能体能访问你的内容，它还得找到*对的*内容。这就是 `llms.txt` 的位置。

我把 `llms.txt` 看作给 AI 智能体用的站点地图。它是一份托管在 `yourdomain.com/llms.txt` 的扁平 Markdown 文件，为你的文档提供一个结构化的目录——带描述，这样智能体不必爬遍你整个站点就能判断出什么相关。

一份格式良好的 `llms.txt` 大概长这样：

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

什么算一份好的 `llms.txt`：

- 描述要告诉智能体它将*找到*什么，而不只是这一页叫什么
- 在有帮助的地方给出每页的 token 数（这样智能体能做出有依据的上下文决策）
- 按任务组织，而不是按产品层级组织
- 自身控制在 5,000 token 以内（它不该光是当个索引就把预算烧光）

### 第三层：通过 `skill.md` 发出能力信号

`llms.txt` 告诉智能体东西在哪里。`skill.md` 告诉它们你的产品实际能*做什么*。

我认为这个区分比它第一眼看上去更重要。与其让智能体不得不从散文式的文档里推断能力，`skill.md` 以声明式的方式把它们呈现出来——把意图映射到端点和资源。

一个认证服务的 `skill.md` 可能长这样：

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

这才让智能体做出有意义的决策——不只是抓文档，而是在把上下文预算花在完整阅读之前，先判断你的 API 究竟能不能满足用户的意图。

### 第四层：面向智能体解析的内容格式

即便有了完美的可发现性和能力信号，真正的内容仍然需要是智能体可读的。这里我觉得有几件事很重要：

**投递 Markdown，而不只是 HTML。** 许多文档平台允许你通过在 URL 后加 `.md` 或通过查询参数来访问原始 Markdown。让这件事可被发现。智能体处理 Markdown 的 token 开销远低于 HTML（没有标签噪音，没有导航外壳，没有页脚杂物）。

**为扫描而结构化，而不是为阅读。** 智能体不是线性地读——它们解析结构：

- 使用一致的标题层级（H1 → H2 → H3，不要跳级）
- 每个章节以结论开头，而不是以背景开头
- 把代码示例紧放在它所说明的论断之后
- 参数参考用表格——它们比散文式列表压缩得更好

**干掉导航噪音。** HTML 里出现的侧边栏、面包屑和页脚链接，在 Markdown／纯文本里只是噪音。把它们挡在可解析的内容路径之外。

**把有用的东西前置。** 任何页面的前 500 个 token 应当回答：这是什么、它能做什么、我要上手需要什么。智能体对开场白耐心有限。

### 第五层：暴露 token 数

这一层比听起来简单，但杠杆高得出奇：在你的文档页面上给出 token 数。理想情况下既在 `llms.txt` 索引里，也在页面本身上（作为元数据或页头）。

这给智能体提供了做出明智决策所需的信息：

- 「这一页是 8K token——我可以完整放进上下文」
- 「这一页是 150K token——我该只抓相关的那一节」
- 「这一页超出我的上下文窗口——我改用 llms.txt 里的摘要」

实现很直接：在服务端数字符，除以大约 4 得到一个粗略的 token 估计，然后把它暴露成一个 meta 标签或 HTTP 响应头。

### 第六层：「为 AI 复制」

这一层更像是 UX 上的桥，而不是基础设施层，但我觉得值得包括进来：**为 AI 复制**按钮。

当一个开发者在带 AI 助手的 IDE 里工作、想把文档作为上下文带进去时，他目前是从渲染后的 HTML 里复制粘贴——那里面有导航噪音、页脚，全套都有。一个把干净的 Markdown 复制到剪贴板的「为 AI 复制」按钮是件小事，但它实实在在地改善了智能体收到的上下文质量。

Anthropic、Cloudflare 等已经上线了这个东西的各种变体。代价很低，信号很强。

---

## AGENTS.md：正在浮现的默认

有一件事值得单独点出来：`AGENTS.md`。

正如 `README.md` 成了人类开发者探索一个仓库的默认入口，`AGENTS.md` 正在成为 AI 智能体的入口。当一个编码智能体打开一个项目时，它会在根目录寻找 `AGENTS.md`，把它的指示拉进之后的每一个任务。

我[在别处写过这件事](https://addyosmani.com/blog/agents-md/)，但简短版本是，一份好的 `AGENTS.md` 包括：

- 项目结构和关键文件位置
- 指向相关 API 或服务文档的直链
- 可用的开发沙箱和测试环境
- 智能体应当知道的速率限制与约束
- 代码库偏好的模式和约定
- 如果可用，MCP 服务器的链接

Cisco DevNet 已经把它采纳为他们开源项目 GitHub 模板里的默认文件——新建的项目自带一份预填的 `AGENTS.md`，里面有项目特定的内容、指向 OpenAPI 文档的链接、DevNet 沙箱和测试环境。

---

## 监控 AI 引荐流量

你现在就能做的一件事：开始在你的分析工具里追踪 AI 引荐流量。

下面这些是值得关注的引荐来源：

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

你还会想监控我前面提到的那些 HTTP 指纹——`axios/1.8.4`、`curl/8.4.0`、`got (sindresorhus/got)`、`colly`——以便抓住那些不带 referrer 直接到访的智能体流量。

建一个像样的 AI 流量分群，你就能拿到领先指标，判断这些工作到底有没有起作用。

---

## 对开发者体验更广泛的意义

我想往后退一步，因为我觉得 AEO 指向的东西比一份技术清单更大。

在 Web 历史的大部分时间里，开发者门户是围绕人类的认知模式来设计的：渐进披露、视觉层级、交互式示例、引导式教程。所有这些都假设每一步都有一个人在场。

在一个智能体密集的世界里，这些假设有很多会失效：

- **视觉层级变得无关**——智能体读的是文本，不是布局
- **渐进披露变成障碍**——智能体想要一次拿到所有东西
- **交互式示例失去价值**——除非有静态的／API 的等价物
- **用户旅程塌缩**——一个多章的教程变成一次上下文加载

这不意味着以人为中心的设计不再重要。人类仍然读文档。但他们越来越多地是在*一个 AI 助手的上下文里*读——这意味着智能体常常是直接消费者，哪怕人类才是最终受益者。

往后的最佳文档大概需要同时服务两个受众：对人类来说可扫描、结构良好，对智能体来说机器可读、token 高效。

---

## AEO 审计清单

如果今天让我评估一个文档站点的智能体就绪度，我会检查这些：

**可发现性**

- [ ] 根目录存在 `llms.txt`，带有全部文档的结构化索引
- [ ] `robots.txt` 没有无意中挡住已知的 AI 智能体 user-agent
- [ ] `agent-permissions.json` 为自动化客户端定义了访问规则
- [ ] 代码仓库里存在 `AGENTS.md`，链接到相关文档

**内容结构**

- [ ] 文档页面可以以干净的 Markdown 获取（不只是渲染后的 HTML）
- [ ] 每一页在前 200 词里给出清晰的结论陈述
- [ ] 标题一致，层级正确
- [ ] 代码示例紧跟其文字描述之后
- [ ] 参数参考用表格，而不是嵌套的散文

**token 经济学**

- [ ] 按文档页面追踪 token 数
- [ ] 没有任何单页超过 30,000 token 却没有分块策略
- [ ] 关键页面的 token 数在 `llms.txt` 中暴露
- [ ] token 数作为页面元数据可用（meta 标签或 HTTP 头）

**能力信号**

- [ ] `skill.md` 文件描述每个服务／API *做什么*，而不只是怎么调用它
- [ ] 每个技能包括：能力、必需输入、约束、关键文档链接
- [ ] 有可用于直接智能体集成的 MCP 服务器（如果适用）

**分析**

- [ ] 在 Web 分析里切分出 AI 引荐来源
- [ ] 服务器日志监控已知的 AI 智能体 HTTP 指纹
- [ ] 建立了 AI 与人类流量比例的基线

**UX 桥接**

- [ ] 文档页面上有「为 AI 复制」按钮
- [ ] Markdown 源码可通过 URL 惯例访问（例如加 `.md`）

**工具**

为了帮忙自动化其中一些检查，我发布了 [agentic-seo](https://github.com/addyosmani/agentic-seo)——一个轻量的审计工具，扫描你的站点找出 AEO 机会。它检查 `llms.txt`、`robots.txt` 对智能体的封禁、token 数、Markdown 可用性等等。把它想成 Lighthouse，但测的是智能体就绪度。

---

## 从哪里开始

如果你看着这份清单、想知道从哪儿下手，这是我建议的顺序：

1.  **审计你的 `robots.txt`**——十分钟的工作，防止智能体被静默锁在门外
2.  **加上 `llms.txt`**——几小时，立刻拿到可发现性收益
3.  **测量并暴露 token 数**——一个周末的项目，杠杆很高
4.  **为你最重要的 3 个 API 写 `skill.md`**——从智能体最可能去拿的那些开始
5.  **加「为 AI 复制」按钮**——代价低，信号强
6.  **搭起 AI 流量监控**——给你数据去论证其他一切

---

## 收尾

SEO 教会我们，好内容是不够的——你得让它以契合这个时代实际流量模式的方式可被发现。我认为 AEO 是同一课，只是换了个消费者。

AI 编码智能体已经是文档流量里显著且在增长的一份。它们的行为方式与人类读者根本不同。而大多数开发者门户还没为它们而建。

在这里早动的团队大概会拿到真实的优势：他们的 API 会成为智能体推荐、成功集成、并且反复回来的那些。没动的团队会看到文档质量与实际智能体任务成功率之间的差距越来越大——一个真正难以排查的静默失效模式。

好消息是，为智能体而建往往也让文档对人类更好。这两门手艺重叠的地方比分歧更多。

从 `llms.txt` 开始。发一份 `skill.md`。审计你的 `robots.txt`。测量你的 token。这些大多是周末的工作量，而回报已经是真的了。
