# Program Design 101

Program design 是在写代码之前，说明一个程序如何从输入可靠地产生有价值输出的过程。

好的 design 不是把所有实现细节提前写死，而是提前明确目标、边界、数据、流程、工具能力、失败路径和验收标准。

## 1. Design 要回答什么

一份 program design 至少要回答：

- 这个程序解决什么问题？
- 谁会使用它？
- 输入是什么？
- 输出是什么？
- 成功标准是什么？
- 主要 workflow 是什么？
- 每一步产生什么 artifact？
- 每一步怎么验证？
- 失败时怎么办？
- 用什么工具、库、模型或外部系统？
- 哪些地方需要人工介入？
- 如何测试、debug、恢复和维护？

一句话：

```text
Design = goal + workflow + contracts + tools + validation + failure handling
```

## 2. Design 和 Architecture 的区别

Architecture 关注系统的高层结构：

- 有哪些组件？
- 组件之间怎么通信？
- 数据怎么流动？
- 系统如何部署？
- 边界和依赖在哪里？

Design 关注系统如何真正工作：

- workflow 怎么走？
- 每一步输入输出是什么？
- 数据 schema 是什么？
- 错误怎么处理？
- 怎么判断结果合格？
- 需要哪些测试？
- 用户是否得到想要的结果？

Architecture 是 design 的一部分。Architecture 更像骨架，design 是骨架、行为、质量和失败路径的完整说明。

## 3. 设计顺序

推荐顺序：

```text
1. 定义目标输出
2. 定义用户和使用场景
3. 定义成功标准
4. 设计最小可靠 workflow
5. 为每一步定义 input / output contract
6. 为每一步选择 required capability
7. 选择 primary tool 和 fallback tool
8. 定义 quality gate
9. 定义 failure path
10. 设计 tests 和 observability
```

不要一开始就问：

```text
我要几个模块？
我要几个 agent？
用哪个框架？
```

先问：

```text
从输入到可靠输出，最短可信路径是什么？
```

## 4. 每个 Workflow Step 应该写什么

每一步都应该有明确 contract：

```text
Stage name:
Purpose:
Input artifacts:
Output artifacts:
Required capability:
Primary tool:
Fallback tool:
Quality gate:
Failure modes:
Failure action:
Human review needed:
Estimated cost/time:
```

例子：

```text
Stage: PDF figure extraction
Purpose: 从论文 PDF 中提取原始 figures
Input: input/paper.pdf
Output: assets/figures/index.json, assets/figures/*.png
Required capability: 提取图片、保留页码、生成稳定 figure ID
Primary tool: PyMuPDF
Fallback tool: pypdf + Pillow
Quality gate: source_figure_count > 0, or explicit warning
Failure action: block visual-heavy output or require human approval
```

## 5. 工具选择怎么设计

工具不是最后才想的实现细节。工具会影响 workflow、artifact、质量门和失败路径。

设计时不一定要锁死具体工具，但必须明确：

- 这一步需要什么能力。
- 哪些工具可能满足。
- 主工具是什么。
- fallback 是什么。
- 工具不可用时怎么办。
- 工具输出如何验证。
- 工具失败是否允许继续。

正确写法：

```text
Required capability: generate editable PPTX and preview PNGs
Primary tool: Presentations artifact-tool
Fallback: none
Failure action: block, because visual QA depends on preview rendering
```

比下面这种写法更好：

```text
Use some PPTX library later.
```

## 6. Quality Gate 是核心

每一步都要有 quality gate。否则 pipeline 只是在检查“有没有跑完”，不是检查“有没有做对”。

常见 quality gate：

- schema valid
- required fields present
- source coverage sufficient
- generated file exists
- output can be opened
- benchmark result parsed
- no known unsafe condition
- no obvious content leakage
- human review approved
- downstream consumer can use the artifact

一个坏 design 的信号：

```text
status = complete
```

但没有说明为什么 complete。

## 7. Failure Path 必须提前设计

每一步都可能失败。设计里要说明失败后怎么处理。

常见动作：

- retry: 临时错误，重试。
- fallback: 换备用工具。
- degrade: 降级输出，但记录限制。
- block: 停止 workflow，等待人工输入。
- revise: 回到上游重新生成。
- reject: 标记不可用，不进入下游。

不要让失败静默发生。静默失败会让下游认真地执行错误输入。

## 8. Artifact 和 State

重要输出应该写成文件或可审计 artifact，不应该只存在聊天记录或内存里。

好的 artifact 应该：

- 有明确路径。
- 有明确 schema。
- 能被人读懂。
- 能被程序读取。
- 能支持 resume。
- 能支持 debug。
- 能被下游验证。

Artifact 是 audit trail，不是权威。下游应该有权拒绝上游 artifact。

## 9. Testing 要从设计开始

不要等代码写完才想测试。

设计时就要写：

- requirement 如何变成 acceptance test。
- design 如何变成 integration test。
- module 如何变成 unit test。
- workflow 如何做 end-to-end test。
- 失败路径如何测试。
- 人工 review gate 如何记录。

V-model 思路：

```text
Requirements -> acceptance tests
Design       -> integration tests
Code         -> unit tests
```

## 10. Multi-Agent System 怎么设计

不要从“需要几个 agent”开始。

先设计 workflow 和 artifact contract，再决定是否需要多个 agent。

拆 agent 的条件：

- 任务边界清楚。
- 输入输出可结构化。
- 输出可独立验证。
- agent 需要不同工具或权限。
- 下游可以拒绝上游输出。
- 并行能带来真实收益。
- 拆分不会破坏全局判断。

每个 agent 都应该写清楚：

- responsibility
- input artifact
- output artifact
- allowed tools/skills
- forbidden actions
- quality gate
- failure path
- human gate
- whether it can veto upstream output

Agent 不是人名牌。Agent 是带职责、权限、contract 和质量门的执行单元。

## 11. Human Gates

当一步风险高、成本高、不可逆、依赖外部资源、或需要主观判断时，应该设置 human gate。

常见 human gate：

- claim review
- command review
- tool permission review
- result review
- final report review
- risky code execution approval

Human approval 应该写成 artifact，不应该只留在聊天里。

## 12. Observability 和 Debuggability

好的 design 要让人知道系统为什么做出某个结果。

应该记录：

- run log
- status change
- input/output artifact path
- command stdout/stderr
- tool version
- environment metadata
- warnings
- deviations
- reviewer decision
- recovery instruction

如果结果坏了，但你不知道是哪一步坏的，design 就还不够。

## 13. 常见错误

常见 program design 错误：

- 先设计复杂架构，而不是最小可靠路径。
- 只写模块职责，不写 artifact contract。
- 只检查 schema，不检查语义质量。
- 工具选择留到实现时才想。
- 没有 fallback 和 failure path。
- 上游错误被下游放大。
- 数据库保存很多 artifact，但没有质量过滤。
- reviewer 太宽松。
- 人工 approval 没有落文件。
- 把“跑完”当成“成功”。
- 把“多 agent”当成“更可靠”。

## 14. 最小 Design Doc 模板

```text
# Program Design

## Goal

## Users / Use Cases

## Success Criteria

## Inputs

## Outputs

## Workflow

## Artifacts

## Components / Agents

## Tools / Skills

## Contracts / Schemas

## Quality Gates

## Failure Modes

## Human Gates

## Tests

## Observability

## Open Questions
```

## 15. 一句话原则

好的 program design 应该让你在写代码前知道：

```text
我要产出什么；
怎么一步步产出；
每一步凭什么算合格；
工具失败怎么办；
下游如何拒绝上游错误；
最后如何证明用户真的得到了想要的结果。
```
