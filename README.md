# Addy Osmani 博客双语存档

[Addy Osmani](https://addyosmani.com/)（Google Chrome 工程负责人）2026 年关于 **智能体工程（agentic engineering）** 的 24 篇博客文章存档，每篇含英文原文与中文译文。

- **在线版本**：https://wangjunjian.com/addyosmani-blog/ （可读版站点，含分类索引、全文搜索、中英切换）
- **来源**：https://addyosmani.com/blog/
- **采集时间**：2026-11-08
- **文章时间跨度**：2026-04-07 ~ 2026-09-14
- **体量**：24 篇 / 英文 73,745 词 / 中文 108,867 字 / 配图 89 张

> 版权归 Addy Osmani 所有。此仓库为个人学习用途的离线存档与中文翻译，不作商业使用。原文以链接指向的线上版本为准。

**先读什么**：下面的「文章分类」给出 24 篇的分组与一句话主旨，「推荐阅读路径」按角色和主题给出入口。采集规则与翻译规则是实现细节，放在文末备查。

---

## 文章分类

按主题分六组。**组内按"先立框架、再谈落地"的顺序排列**，建议顺着读。

### 一、基础设施：harness、循环、技术栈（5 篇）

看懂智能体工程到底在造什么。

| 文章 | 日期 | 主旨 |
|---|---|---|
| [智能体技术栈的赌注](articles/the-agent-stack-bet.zh.md) | 04-18 | 掀开"生产环境智能体"的引擎盖，看到的是脆弱管道和共享账号。技术栈天花板正在制造治理与可靠性缺口，智能体需要的是**身份**和**普适上下文** |
| [智能体 Harness 工程](articles/agent-harness-engineering.zh.md) | 04-19 | 智能体 = 模型 + 你围在它周围的一切。harness 工程把那层脚手架当一等产物，并且**每出一次错就收紧一条规则**（棘轮机制） |
| [长时间运行的智能体](articles/long-running-agents.zh.md) | 04-28 | 跨越数天数周持续推进的智能体会撞上三堵墙。横向对比 Ralph 循环、Anthropic 的大脑/手/会话拆分、Cursor 的规划器-工人-裁判、Google Agent Platform |
| [循环工程](articles/loop-engineering.zh.md) | 06-07 | 把自己从"给智能体写提示词的人"这个角色上换掉，转而**设计一个替你写提示词的系统**。五个零件：自动化、worktree、技能、插件连接器、子智能体 |
| [循环工程实战](articles/practical-loop-engineering.zh.md) | 08-14 | 概念篇的落地版：goal 与 loop 的区别、什么该委托什么该盯、作者每天跑的工作流，以及循环买不到的东西 |

**读法**：时间紧就先读 *循环工程* → *实战*，这两篇是同一条线的概念与实践。*技术栈的赌注* 视角最宏观，适合放最后当收尾。

### 二、自主性与人的位置（4 篇）

自主性该开多大，人退到哪里。

| 文章 | 日期 | 主旨 |
|---|---|---|
| [智能体自主性等级](articles/agentic-autonomy-levels.zh.md) | 07-02 | 六级自主性量表。核心判据不是模型多有信心，而是**风险与可逆性决定天花板**，再用指标让判断稍可靠一点。附四种反模式 |
| [拥有外层循环](articles/own-the-outer-loop.zh.md) | 07-15 | AI Engineer World's Fair 2026 闭幕演讲文字版。工程师要拥有外层循环——为系统承担责任；提出撑起软件工厂的**十二根支柱** |
| [软件工厂：明与暗](articles/software-factories.zh.md) | 07-20 | 明厂用人换取速度，暗厂用理解换取吞吐。**瓶颈从来不在生成**，而在你能否造出配得上熄灯的循环 |
| [人类的判断力从未离开软件工厂，它只是换了位置](articles/human-judgment-doesnt-leave-the-software.zh.md) | 08-21 | 最诚实的一篇自述：作者自己搞错过项目、被绿灯骗过。核心概念是**验证预算**，以及"自主性不是单一开关" |

**读法**：*自主性等级* 是决策工具，*拥有外层循环* 是立场宣示，后两篇是同一立场的实证与反思。想说服团队别盲目追高自主性，直接拿 08-21 那篇。

### 三、质量、评审与老代码库（3 篇）

代码写便宜了以后，质量靠什么兜底。

| 文章 | 日期 | 主旨 |
|---|---|---|
| [智能体化代码质量](articles/agentic-code-quality.zh.md) | 08-08 | 代码多到没人读得完，质量检查必须前移到 harness、环境和操作系统。**软件质量现在取决于你围在智能体周围的约束**——质量闸门 |
| [智能体时代的代码评审](articles/agentic-code-review.zh.md) | 06-15 | 难题从写代码转移到判断可信度。引 2026 年三组数据：Faros（22,000 名开发者）、CodeRabbit、GitClear——**4 倍代码换 10% 的交付价值**，差额全在评审 |
| [棕地智能体工程](articles/brownfield-agentic-engineering.zh.md) | 09-14 | 老代码库里仓库不再是完整描述。先给代码**分区**（绿/黄/红），按影响半径、可观测性、可恢复性分配自主性，并让研究产出活过这次会话 |

**读法**：三篇构成"新代码 → 评审 → 老代码"的完整链条。*代码评审* 数据最硬，适合拿去向管理层论证评审投入；*棕地* 是唯一讲存量系统迁移方法论的，工程价值最高。

### 四、债务与组织成本（4 篇）

智能体不会替你承担的那部分代价。

| 文章 | 日期 | 主旨 |
|---|---|---|
| [你的并行智能体上限](articles/cognitive-parallel-agents.zh.md) | 04-07 | 更多智能体在跑不等于有更多个你。并行不是线性扩展，**找到自己的并行上限本身就是一种技能** |
| [认知投降](articles/cognitive-surrender.zh.md) | 05-05 | 认知卸载是把事委派出去但仍拥有答案；认知投降是 AI 的产出悄悄变成你的产出，而你觉得没什么要检查了。软件工程师格外容易暴露 |
| [编排税](articles/orchestration-tax.zh.md) | 05-24 | 所有判断必须穿过恰好一个串行处理器——你。编排税就是忘记这点的代价，解法是**像架构并发系统那样架构自己的注意力** |
| [意图债](articles/intent-debt.zh.md) | 06-05 | 技术债在代码里，认知债在脑子里，意图债在那些你可能从未写下来的目标与理由里。**这是智能体唯一替你还不了的债** |

**读法**：这四篇是本合集里最"反潮流"的部分，专门对冲"多开几个智能体就完事"的叙事。建议作为一组连读，*编排税* 最短（约 2,500 字），可先读。

### 五、专业能力的养成（4 篇）

智能体拿走重复劳动后，手艺从哪来。

| 文章 | 日期 | 主旨 |
|---|---|---|
| [不要把学习外包出去](articles/dont-outsource-learning.zh.md) | 05-16 | bug 修好了但心智模型没动——我们在用未来能力换当下速度。解法在**怎么提问**，以及用两个指标而非一个来衡量自己 |
| [智能体时代的职业](articles/career-advice-age-of-agents.zh.md) | 07-06 | AI 会变得擅长任何有标准答案的事；而你的职业，恰恰是那些没有标准答案的部分 |
| [赢得品味与判断力](articles/earning-judgment.zh.md) | 07-14 | 品味过去是重复练习的副产品，智能体把重复拿走了。所以初级工程师现在**必须有意识地获取品味**，不能再等它自然长出来 |
| [智能体技能退化](articles/agentic-skill-decay.zh.md) | 08-31 | 作者自己的练习清单与"短路"现象。结论有反转：**专业能力的回报正在上升**，只是获取路径变了 |

**读法**：写给个人的一组，与工作流无关。如果你是带新人的，*赢得品味* + *技能退化* 这两篇可以直接当培养方案的讨论材料。

### 六、工具与规范落地（4 篇）

能马上抄去用的部分。

| 文章 | 日期 | 主旨 |
|---|---|---|
| [智能体引擎优化（AEO）](articles/agentic-engine-optimization.zh.md) | 04-11 | 智能体读文档的方式与人不同：只取前 N 个 token、跳过 JS、不点折叠。给出 `llms.txt` / `skill.md` / `AGENTS.md` 三层技术栈与审计清单 |
| [智能体技能](articles/agent-skills.zh.md) | 05-03 | 技能**不是**参考文档，而是带检查点、以明确退出标准收尾的工作流。附五条承重原则与"即使不安装也该偷走"的东西 |
| [新的软件生命周期](articles/new-sdlc-vibe-coding.zh.md) | 06-16 | Google 白皮书配套文。智能体 = 模型 + harness，**验证是 vibe coding 与工程之间的分界线**，附各阶段变化与成本经济学 |
| [审查你的智能体文件](articles/audit-your-agent-files.zh.md) | 08-27 | 你给智能体的配置有半衰期。作者每几周跑一次 `/doctor`、独立审查记忆，并**测试移除每条指令**，让它重新证明自己配得上留下 |

**读法**：*AEO* 面向做文档和开发者关系的人，*技能* + *审查智能体文件* 是配置实操的上下篇（先建后审），*新的软件生命周期* 适合讲给不写代码但要看懂流程的人。

---

## 推荐阅读路径

**如果只有一个小时**（三篇，约 1.3 万字）：

1. [循环工程](articles/loop-engineering.zh.md) — 建立"循环"这个核心心智模型
2. [智能体时代的代码评审](articles/agentic-code-review.zh.md) — 看清真实数据与瓶颈在哪
3. [意图债](articles/intent-debt.zh.md) — 理解智能体替不了你的那部分

**分角色的入口**

| 你是 | 从这里开始 | 然后 |
|---|---|---|
| 刚开始用编码智能体 | [循环工程](articles/loop-engineering.zh.md) | [循环工程实战](articles/practical-loop-engineering.zh.md) → [智能体技能](articles/agent-skills.zh.md) |
| 已经在并行跑多个智能体 | [编排税](articles/orchestration-tax.zh.md) | [你的并行智能体上限](articles/cognitive-parallel-agents.zh.md) → [长时间运行的智能体](articles/long-running-agents.zh.md) |
| 要落地到团队/生产 | [智能体自主性等级](articles/agentic-autonomy-levels.zh.md) | [软件工厂：明与暗](articles/software-factories.zh.md) → [拥有外层循环](articles/own-the-outer-loop.zh.md) |
| 维护存量老系统 | [棕地智能体工程](articles/brownfield-agentic-engineering.zh.md) | [智能体化代码质量](articles/agentic-code-quality.zh.md) → [智能体时代的代码评审](articles/agentic-code-review.zh.md) |
| 带团队 / 管工程 | [人类的判断力从未离开软件工厂](articles/human-judgment-doesnt-leave-the-software.zh.md) | [智能体时代的代码评审](articles/agentic-code-review.zh.md) → [智能体技能退化](articles/agentic-skill-decay.zh.md) |
| 做文档 / 开发者关系 | [智能体引擎优化（AEO）](articles/agentic-engine-optimization.zh.md) | [新的软件生命周期](articles/new-sdlc-vibe-coding.zh.md) |
| 担心自己的手艺 | [不要把学习外包出去](articles/dont-outsource-learning.zh.md) | [赢得品味与判断力](articles/earning-judgment.zh.md) → [智能体技能退化](articles/agentic-skill-decay.zh.md) |

**按主题纵向追一条线**

- **循环这条线**：[循环工程](articles/loop-engineering.zh.md)（概念）→ [循环工程实战](articles/practical-loop-engineering.zh.md)（落地）→ [软件工厂：明与暗](articles/software-factories.zh.md)（规模化）→ [长时间运行的智能体](articles/long-running-agents.zh.md)（工程实现）
- **自主性这条线**：[智能体自主性等级](articles/agentic-autonomy-levels.zh.md)（分级）→ [拥有外层循环](articles/own-the-outer-loop.zh.md)（责任）→ [人类的判断力从未离开软件工厂](articles/human-judgment-doesnt-leave-the-software.zh.md)（验证预算）
- **成本这条线**：[编排税](articles/orchestration-tax.zh.md)（注意力）→ [认知投降](articles/cognitive-surrender.zh.md)（理解力）→ [意图债](articles/intent-debt.zh.md)（组织记忆）→ [智能体技能退化](articles/agentic-skill-decay.zh.md)（个人能力）

---

## 目录结构

```
.
├── articles/
│   ├── <slug>.md          # 英文原文（Markdown）
│   └── <slug>.zh.md       # 中文译文
├── images/                # 全部配图，命名 <slug>-<原文件名>
├── assets/                # 站点样式、脚本、图标
├── build.py               # 静态站点构建脚本
├── requirements.txt       # 构建依赖（仅 Python-Markdown）
├── .github/workflows/     # 推送到 main 后自动构建并部署
└── README.md
```

- `slug` 取自原文 URL，如 `https://addyosmani.com/blog/intent-debt/` → `intent-debt`
- 中文版一律加 `.zh.md` 后缀，与英文版严格一一对应
- 图片名带 slug 前缀，因为不同文章存在大量同名文件（`01.webp`、`02.webp`），不加前缀会互相覆盖

### 构建与预览

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py --serve      # 构建到 _site/ 并起本地预览（127.0.0.1:8777）
```

`build.py` 只做三件事：把 Markdown 渲染成 HTML、把 README 的分类表与推荐路径解析成站点导航、复制静态资源。产物是零外部依赖的纯静态文件（不引 CDN、不加载远程字体），`_site/` 已在 `.gitignore` 中，由 GitHub Actions 在推送时构建。

每篇文件头部统一格式：

```markdown
# 标题

> 原文：[英文标题](原文链接)
>
> 发布日期：2026-06-05

---
```

---

## 采集规则

| 项目 | 规则 |
|---|---|
| 采集范围 | 首页 `Personal Blog` 分区全部文章，共 24 篇 |
| 排除项 | `Substack` 分区 7 篇、`LeadDev` 分区 7 篇（均为跳转外站的链接，不属本站内容） |
| 排除项 | `/blog/page2/` 等分页（属另外的页面，非本页内容） |
| 正文提取 | 定位 `<section id="post-body">`，只取该容器内容，丢弃导航、页脚、推荐位 |
| 格式转换 | pandoc `-f html -t gfm --wrap=none`，保留标题层级、粗体、列表、表格、代码块、链接 |
| 图片 | 正文中所有图片（含 Markdown 语法与 HTML `<img>` 两种写法）全部下载到 `images/`，引用改写为相对路径 `../images/` |
| 图片路径补全 | 原文使用站内相对路径（`/assets/images/...`），需补 `https://addyosmani.com` 前缀才能下载 |
| 视频嵌入 | 原文的 YouTube `<iframe>` 由 JS 加载，静态抓取后只剩报错占位。改为从原始 HTML 取视频 ID，替换为一条视频链接 |
| 代码高亮块 | 原文用 Rouge 的 `<div class="language-x highlighter-rouge">` 包裹，pandoc 会残留 div 并把语言标成 `highlight`。统一清理为 ` ```语言 ` 标准围栏 |
| 图注 | `<figure>` + `<figcaption>` 转成 Markdown 图片 + 斜体图注 |
| 分隔线 | pandoc 输出的长串 `-----`（`<hr>`）统一改回 `---` |
| 日期 | 原文 `Sep 14 2026` 统一转为 ISO 格式 `2026-09-14` |

---

## 翻译规则

### 基本原则

1. **逐段完整翻译**：不省略、不合并、不概括、不添加原文没有的解释。原文几段，译文就是几段。
2. **结构完整保留**：标题层级、粗体强调句、斜体、列表、表格、分隔线、引用块原样对应。
3. **代码块不翻译**：代码、命令行、配置片段保持原样，仅代码内的英文注释可译。
4. **链接**：URL 完全不变，只翻译链接文字。
5. **图片**：`../images/` 路径完全不变；`![alt]` 的 alt 文本译为中文。
6. **数字与指标**：`861%`、`1.7x`、`PR`、`SWE-bench`、`token` 等保留原样。
7. **专有名词保留英文**：人名（Addy Osmani、Simon Willison、Bill Harding）、公司/产品（Google、GitHub、Copilot、Claude、CodeRabbit、GitClear、Faros AI）不音译。
8. **标点**：正文用全角（，。：；？！「」），代码、URL、英文短语内部用半角。
9. **语气**：保持原文第一人称技术随笔的口吻——直接、务实、有判断。不加"综上所述""总而言之"这类原文没有的过渡句。

### 术语对照

| 英文 | 中文 | | 英文 | 中文 |
|---|---|---|---|---|
| agent | 智能体 | | orchestration | 编排 |
| sub-agent / subagent | 子智能体 | | orchestration tax | 编排税 |
| multi-agent | 多智能体 | | intent debt | 意图债 |
| agentic engineering | 智能体工程 | | cognitive surrender | 认知投降 |
| workflow | 工作流 | | cognitive debt | 认知债 |
| harness | harness（首次出现注"承载框架"） | | technical debt | 技术债 |
| context / context window | 上下文 / 上下文窗口 | | taste | 品味 |
| prompt / prompt engineering | 提示词 / 提示工程 | | judgment | 判断力 |
| token | token | | characterization test | 表征测试 |
| code review | 代码评审 | | codebase / repository | 代码库 / 仓库 |
| reviewer | 评审者 | | PR / pull request | PR |
| vibe coding | vibe coding | | merge | 合并 |
| brownfield / greenfield | 棕地 / 绿地 | | ship | 交付（上线） |
| blast radius | 影响半径 | | throughput | 吞吐量 |
| autonomy / autonomy level | 自主性 / 自主性等级 | | churn | 代码流失 |
| software factory | 软件工厂 | | defect | 缺陷 |
| inner loop / outer loop | 内层循环 / 外层循环 | | refactor | 重构 |
| spec / spec-driven | 规格 / 规格驱动 | | test coverage | 测试覆盖率 |
| skill（Agent Skills） | 技能（智能体技能） | | regression | 回归 |
| tool call | 工具调用 | | eval | 评测 |
| guardrail | 护栏 | | scaffold | 脚手架 |

### 质检口径

交付前对 24 对文件逐一脚本核验，不看主观感受：

- 中英文的二级、三级标题数量必须相等
- 图片引用数量相等，且每个 `../images/*` 都能在磁盘找到
- 代码围栏 ` ``` ` 必须成对闭合
- 不得残留 `<div>`、`<figure>`、`<img>`、`<figcaption>`、`<iframe>`
- 扫描"英文词 > 40 且中文字 < 60"的行作为未译嫌疑；已知两类误报需人工判断：链接密集的已译句、代码块内的英文示例

**当前状态**：24 对文件齐全，标题数全部对齐，图片引用 89 种 / 磁盘 89 个、零缺失零冗余，无残留 HTML，代码块全部闭合。

---

## 已知边界

- **只覆盖首页 24 篇**。作者全站累计文章远多于此，`/blog/page2/` 及更早的存档未采集。
- **未采外部平台**：首页另有 Substack 7 篇、LeadDev 7 篇，均为外站链接，正文不在本站。
- **图片 alt 较长**：原文 alt 常是幻灯片内容的完整文字描述（作者有意为之，兼顾无障碍）。译文照实翻译，因此部分行较长，属正常现象。
- **视频仅留链接**：原文的 YouTube 嵌入无法静态保存，已替换为视频链接，不含视频文件。
- **翻译为机器翻译**：已按统一术语表与逐段对齐规则产出并脚本核验结构，但技术长文难免有语气与细腻语义的偏差。引用前建议对照同目录的英文原文。
