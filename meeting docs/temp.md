# Program Design Notes

> Source: `docs/temp.txt`

核心结论是：你之前的问题不是“没有设计”，而是设计太停留在 agent 分工和 pipeline 形状上，没有足够围绕真实产物、工具链、失败模式和质量门来设计。

## 1. 一个程序的 design 应该包含什么？

一个程序的 design 不只是“有哪些模块”。至少应该包含：

- 目标：这个程序要解决什么问题，成功标准是什么。
- 用户和场景：谁会用，在什么情况下用，最重要的 workflow 是什么。
- 输入和输出：输入格式、输出格式、边界条件、错误输入怎么处理。
- 核心流程：从输入到输出，每一步发生什么。
- 数据结构和 artifact：中间状态如何保存，哪些结果需要可追踪、可恢复、可审计。
- 模块职责：每个组件负责什么，不负责什么。
- 接口契约：模块之间传什么数据，用什么 schema，谁可以拒绝谁的输出。
- 技术栈：用什么库、工具、模型、renderer、数据库、文件格式。
- 失败模式：每一步可能怎么失败，失败后是重试、降级、阻塞还是人工介入。
- 质量门：怎么判断每一步真的合格，而不是只是“跑完了”。
- 测试策略：unit test、integration test、end-to-end test、人工 review 分别覆盖什么。
- 可观测性：日志、运行记录、调试 artifact、决策 trace。
- 成本和性能：运行时间、API 调用、并发、缓存、timeout、fallback。
- 安全和权限：文件写入、网络、外部代码、API key、Docker、模型调用等风险。

对于 AI workflow，尤其还要加一条：每个 AI 产物都应该落到文件里，并且下游不能盲信上游输出。

## 2. 设计程序时最关键的是什么？

结合你的复盘，最关键的是：

> 从最终用户真正需要的高质量产物倒推，设计一条最小可靠路径，并在每个关键步骤设置真实质量门。

你之前的主要错误不是“用了多 agent”，而是这些点：

- 过早设计 agent org chart，而不是先复刻一个强 human/Codex workflow。
- 把 workflow 设计理解成“谁负责什么”，但没有充分设计“用什么工具做、失败怎么办、怎么验收”。
- 上游 section parser 污染了输入，下游却机械执行，没有 veto/replan 能力。
- global plan 虽然存在，但建立在错误 section 和缺失 figures 上。
- database 保存了很多 artifact，但 noisy artifact 反过来主导了叙事。
- reviewer 只检查 structural correctness，没有检查用户感知质量。
- renderer 被当成末端导出工具，而不是 visual quality loop 的核心。
- 复杂 pipeline 放大了错误和运行成本，却没有提升最终 PPTX 质量。

所以关键不是“设计得复杂”，也不是“agent 越多越专业”。关键是：

> 每一步都必须服务于最终结果，并且有能力发现、阻止、修正上一步的错误。

对 Paper2Slide 这种项目，设计重点应该是：

```text
可靠解析论文主线
-> 提取原始 figures
-> 过滤 appendix/prompt/rubric 噪声
-> 生成全局叙事
-> 构建 slidespec
-> 用成熟 renderer 生成 PPTX
-> render preview/contact sheet
-> 检查真实视觉和叙事质量
-> 修正弱页
```

而不是先问：

```text
需要几个 agent？
每个 agent 叫什么？
每个 stage 是否 complete？
```

## 3. Program design 和 program architecture 有什么区别？

简单说：

> Architecture 是程序的高层结构；design 是程序如何真正工作。

Architecture 更关心：

- 系统由哪些大组件组成。
- 组件之间怎么通信。
- 数据怎么流动。
- 边界在哪里。
- 哪些部分同步、异步、并行。
- 部署形态是什么。
- 主要技术选型是什么。

Design 更关心：

- 具体 workflow 怎么走。
- 每一步输入输出是什么。
- 数据 schema 是什么。
- 错误怎么处理。
- 质量怎么验证。
- 用户体验是否达标。
- 某个模块内部算法或逻辑怎么实现。
- 测试和 review 怎么覆盖。

可以这样区分：

```text
Architecture: 这个系统的骨架是什么？
Design: 这个系统怎样一步步产生正确、有用、可验证的结果？
```

Architecture 是 design 的一部分，但 design 更宽。一个系统可以有看起来很清楚的 architecture，比如很多 agents、database、orchestrator、renderer、reviewer，但 design 仍然可能是失败的，因为它没有处理输入污染、工具失败、质量门过弱、用户感知质量不足这些真实问题。
