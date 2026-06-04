# SkillGen Phase 0 Blocked / Not-Testable 缺失项说明

日期：2026-06-04

本文档解释当前 SkillGen Phase 0 research validation report 中所有 `blocked` 和
`not_testable` claim 到底缺什么。后续如果继续追问某个术语、某个 claim、某个
artifact，本文件应继续追加澄清，而不是只把解释留在聊天里。

## 0. 先区分两个状态

`blocked` 和 `not_testable` 都可能表现为“现在还不能成功验证”，但它们不是同一个意思。

```text
blocked = 我们知道论文要验证什么，但还缺能执行的实验 contract / 数据桥接 / 原始轨迹。
not_testable = 当前官方材料不足以定义“原论文实验到底怎么跑”，强行做会变成重构实验。
```

换句话说：

- `blocked`：验证目标比较清楚，缺的是可补的前置条件。
- `not_testable`：当前材料不足以说明什么才算“按原论文方式复现”。

状态不是永久的。如果后来找到官方脚本、官方数据、官方 config，`not_testable` 可以变成
`blocked` 或进入执行。如果一个 `blocked` 项最后发现没有官方依据，也可能降为
`not_testable`。

## 1. 基础术语

### 1.1 Dataset 在 SkillGen 里是什么意思

SkillGen 不是凭空让 LLM 写一个通用 skill。它需要一批任务实例，让 base agent 先跑，
然后从成功和失败轨迹里总结 skill。

可以理解为：

```text
LLM 预训练能力 = 会读、会推理、会总结建议
dataset / trajectories = 告诉它这个任务里具体哪里成功、哪里失败
SkillGen = 从这些成功/失败案例里归纳一个可部署 skill，并验证它有没有净收益
```

SkillGen 的主程序吃的是自己的 JSON 数据格式，而不是每个 benchmark 的原始格式。官方
`main.py` 期望的数据大致是：

```json
{
  "dataset_id": "...",
  "task_name": "...",
  "task_type": "binary | scored | open_ended",
  "instances": [
    {
      "instance_id": "...",
      "input": "...",
      "ground_truth": "...",
      "metadata": {}
    }
  ]
}
```

所以“有原始 benchmark 数据”不等于“有 SkillGen 可执行数据”。还需要把原始 benchmark
转换成 SkillGen 的 `TaskInstance`。

### 1.2 什么叫“怎么切”

论文实验不是把一个大数据集全部直接拿来跑。它通常要把数据分成几份：

```text
原始数据池
-> construction / training set：用来生成 skill
   -> induction subset：分析成功/失败轨迹，总结 skill
   -> verification subset：验证 candidate skill，有净收益才通过 gate
-> held-out test set：最终评估 BASE vs SKILL
```

“怎么切”就是问：

```text
从原始数据池里，哪几个样本进 construction？
哪几个样本进 held-out test？
用什么随机种子？
是否按任务类型分层？
是否去重？
是否保证 train/test 没有同一个 task？
样本顺序是否会影响抽样？
```

举例：LiveCodeBench 现在有一个 `release_v6_all.json`，它是一大包题目。论文说用了
release v6、seed 42、construction/test 数量。但我们还需要明确：

```text
第 1、8、19、... 这些题进 construction？
第 3、4、27、... 这些题进 held-out test？
还是按日期、难度、contest id、task id 排序后再抽？
```

如果这个规则不同，最后 accuracy 可能不同，所以不能随便切。

### 1.3 什么叫 adapter

`adapter` 是“格式和执行桥接层”。它负责把某个 benchmark 原本的任务形态接到
SkillGen 可以运行和评分的接口上。

例如 ALFWorld 是一个交互式环境。任务不是单个问答，而是一连串动作：

```text
look around
open cabinet
take apple
clean apple
put apple in fridge
```

ALFWorld 环境每一步返回 observation，最后环境判断任务是否成功。SkillGen 需要的是
`TaskInstance`，并且它的 agent runner 要知道怎么执行任务、怎么评分、怎么保存轨迹。

所以 ALFWorld adapter 要定义：

- 每个 ALFWorld task 的 `instance_id` 是什么。
- `input` 里放什么：任务说明、初始 observation、允许动作、环境状态等。
- agent 输出的动作怎么送回 ALFWorld 环境。
- 环境返回的 observation 怎么继续给 agent。
- 什么时候停止。
- 怎么判断 success / failure。
- 怎么保存 trajectory。
- 怎么保证 IOD/OOD 和论文一致。

这不是普通改字段名，而是一整套执行协议。

### 1.4 什么叫论文的完整轨迹

这里的“轨迹”是 trajectory，不是数学曲线。一次 agent 完整执行任务的记录就是一条
trajectory。

例如一个 ALFWorld 任务的 trajectory 可能包括：

```text
task: put a clean apple in the fridge

step 1:
  agent message: I need to find the apple.
  action: look around
  observation: You are in the kitchen...

step 2:
  action: open cabinet
  observation: The cabinet contains an apple.

step 3:
  action: take apple
  observation: You take the apple.

final:
  success = true / false
```

SkillGen 需要 trajectory，因为它要比较：

```text
成功 trajectory 做了什么
失败 trajectory 少做了什么
skill 介入后修复了哪些失败
skill 又破坏了哪些原本成功的 case
```

“论文的完整轨迹”指的是足以从原始执行记录重算论文图表的逐步运行日志。例如 Figure 7
需要：

```text
每个 benchmark-model run
每一轮 refinement round
每个 candidate skill
在 verification/test instances 上的结果
哪些是 repair
哪些是 regression
每轮 accuracy
best-of-K 到第 K 轮时选了哪个 skill
```

当前 run 有一些 smoke-scale traces，但不是论文完整实验规模的 traces。

## 2. 当前 blocked claims 缺什么

### 2.1 `claim_table1_average_gains_all_models`

状态：`blocked`

这个 claim 要验证 Table 1 的主结果：

```text
8 个模型 * 10 个 benchmark/split 行 = 80 个 Table 1 条目
每个模型的平均 BASE accuracy、SKILL accuracy、Delta
```

当前主要缺三类东西。

#### 2.1.1 缺 ALFWorld IOD/OOD 的 SkillGen adapter

ALFWorld 是交互式环境，SkillGen 吃的是 `TaskInstance` JSON。adapter 要把 ALFWorld
任务变成 SkillGen 能跑的任务，并且能把 agent 的动作送进 ALFWorld 环境、拿回
observation、判断 success/failure、保存 trajectory。

当前状态是：

```text
canonical ALFWorld code 已经 fetched
但这不等于 SkillGen 有可执行的 ALFWorld 数据和 runner contract
```

缺失的具体内容：

- ALFWorld raw task 到 SkillGen `TaskInstance` 的转换规则。
- ALFWorld agent action loop 怎么接入 SkillGen。
- ALFWorld 的 success/failure 怎么映射成 SkillGen accuracy。
- 每次执行的 trajectory 怎么保存成后续可比较的 artifacts。
- 这个 adapter 是否是官方提供、论文暗示，还是我们自己补的 deviation。

#### 2.1.2 缺 ALFWorld IOD/OOD split contract

论文里 ALFWorld 有：

```text
IOD = valid_seen
OOD = valid_unseen
```

但我们还需要明确：

- 哪些 `valid_seen` task 进入 construction。
- 哪些 `valid_seen` task 进入 held-out test。
- 哪些 `valid_unseen` task 进入 construction。
- 哪些 `valid_unseen` task 进入 held-out test。
- 是否使用 seed 42。
- 是否按 task type 分层抽样。
- 是否要排除重复或近似重复任务。
- 样本顺序来自哪里。

如果这些规则不清楚，跑出来的 ALFWorld accuracy 不能说对应 Table 1。

#### 2.1.3 缺 LiveCodeBench train/test split contract

当前有：

```text
code/official/data/livecodebench/release_v6_all.json
```

但它是一个 all-instances 文件。Table 1 需要明确 construction/test 划分。

缺失的具体内容：

- release v6 里哪些题用于 skill construction。
- 哪些题用于 held-out test。
- 是否严格对应论文的 `test_release_v6`。
- seed 42 如何作用在抽样上。
- code-generation task 如何包装成 SkillGen 的 `input`、`ground_truth`、`metadata`。
- pass/fail 或 accuracy 如何计算。

没有这些，Table 1 的完整平均值不能算。

### 2.2 `claim_table1_entry_counts`

状态：`blocked`

这个 claim 要验证：

```text
80 个条目中：
50 个 delta > 0
25 个 delta = 0
5 个 delta < 0
```

它缺的底层东西和 `claim_table1_average_gains_all_models` 基本一样，但验证目标不同。

平均提升只需要算每个模型的均值；这个 claim 必须拿到全部 80 个条目的 delta 后逐个分类。

每个条目的分类规则是：

```text
delta > 0  -> improved
delta = 0  -> unchanged
delta < 0  -> regressed
```

只要 ALFWorld IOD、ALFWorld OOD、LiveCodeBench 任何一组没有可靠跑完，就没有完整
80 个 delta。少一批条目，`50/25/5` 就不是论文计数。

### 2.3 `claim_table1_alfworld_scienceworld_patterns`

状态：`blocked`

这个 claim 要验证：

```text
ALFWorld 16 个条目中 14 个提升
ScienceWorld 8 个条目全部提升
```

ScienceWorld 的 SkillGen 数据相对清楚；真正缺的是 ALFWorld。

这里缺的不只是 ALFWorld 文件，而是完整 ALFWorld execution bridge：

```text
ALFWorld raw task
-> SkillGen TaskInstance
-> agent action loop
-> ALFWorld environment observation
-> final success/failure
-> trajectory log
-> BASE vs SKILL paired comparison
```

还要区分 IOD 和 OOD。IOD/OOD 如果混错，或者 task ids 不对应论文，`14 of 16` 这个
结论就没有意义。

### 2.4 `claim_cross_model_transfer`

状态：`blocked`

这个 claim 对应 Figure 4：

```text
4 个 benchmark * 6 个 source model * 5 个不同 evaluator model
= 120 个 off-diagonal transfer comparisons
```

当前 ScienceWorld、Mind2Web、SocialMaze FTS 有计划；缺的是 ALFWorld OOD。

transfer 不是普通 evaluation。它需要：

```text
source model 生成 skill
evaluator model 使用这个 skill
同一个 evaluator model 的 no-skill baseline
同一批 held-out instances
比较 evaluator with transferred skill vs evaluator no-skill
```

如果 ALFWorld OOD 没有 adapter 和 split contract，就缺 30 个 ALFWorld OOD transfer
comparisons。这样 120 个 off-diagonal comparisons 不完整，70% non-negative / 42%
exceed +5 pp 也不能算。

### 2.5 `claim_refinement_best_of_k`

状态：`blocked`

这个 claim 对应 Figure 7。它不是只看最终 skill，而是看每一轮 refinement：

```text
round 1 candidate skill 表现如何
round 2 candidate skill 表现如何
...
round 8 candidate skill 表现如何
best-of-K 到每个 K 时选到的最好 skill 表现如何
```

现在缺的是论文规模的完整 trajectory / trace。

这里的“完整轨迹”包括：

```text
每个 benchmark-model run
每一轮 candidate skill
每一轮 verification baseline outcome
每一轮 with-skill outcome
哪些 case 是 repair
哪些 case 是 regression
每轮 net gain
每轮 accuracy
best-so-far 曲线
最终 Figure 7 的聚合数据
```

当前 smoke runs 有一些 verification traces，但不够覆盖论文 Figure 7 的代表性 runs 和
aggregate 曲线。所以它是 `blocked`，不是 `reproduced`。

## 3. 当前 not-testable claims 缺什么

### 3.1 `claim_baseline_generator_comparison`

状态：`not_testable`

这个 claim 对应 Figure 2：SkillGen 对比 Trace2Skill、SkillX、EvoSkill、CoEvoSkills。

缺的是可信的 baseline reproduction package：

```text
Trace2Skill 的可执行 runner
SkillX 的可执行 runner
EvoSkill 的可执行 runner
CoEvoSkills 的可执行 runner
论文使用的版本 / commit
如何改造成 single-skill setting
如何接入同一个 evaluation harness
如何使用同一批 split、模型、judge、metric
输出如何转换成 Table/Figure 里的 delta accuracy
```

如果我们自己从 GitHub 找类似 repo，再自己写 wrapper，那通常是“重新做一个近似比较”，
不是原论文复现。除非找到论文作者使用的官方代码或明确版本，否则当前材料不足以定义
可信验证任务，所以是 `not_testable`。

### 3.2 `claim_ablation_full_wins`

状态：`not_testable`

这个 claim 对应 Figure 3：Full SkillGen 赢过 A1/A2/A3/A4/A5。

缺的是 ablation 的精确定义和可执行配置：

```text
A1: ICL k=3 到底怎么实现
A2: no refinement 是关掉哪些步骤
A3: no verification gate 是完全不 gate，还是只不 reject
A4: no Failure Lessons 是删除 prompt 哪一段
A5: plain-text skill 是禁用 script/reference bundle 到什么程度
```

还缺：

```text
ablation runner
每个 ablation 的 named config
dataset-model pair 列表
命令
输出解析规则
Figure 3 每个柱子对应的 raw result
```

这些如果人工重构，很容易和论文真实设置不一样。比如 “no verification gate” 改法稍微
不同，实验含义就变了。所以当前不是 `blocked`，而是 `not_testable`：我们还没有足够
官方依据说“这就是论文 Figure 3 的 ablation 实验”。

## 4. 简短总表

| Claim | Status | 主要缺失 |
| --- | --- | --- |
| `claim_table1_average_gains_all_models` | `blocked` | ALFWorld IOD/OOD adapter、ALFWorld split contract、LiveCodeBench split contract、完整 80-entry 执行 |
| `claim_table1_entry_counts` | `blocked` | 完整 80 个 delta，尤其 ALFWorld IOD/OOD 和 LiveCodeBench |
| `claim_table1_alfworld_scienceworld_patterns` | `blocked` | ALFWorld IOD/OOD 的 SkillGen execution bridge 和论文匹配 split |
| `claim_cross_model_transfer` | `blocked` | ALFWorld OOD transfer 所需 adapter/split，导致 120 off-diagonal comparisons 不完整 |
| `claim_refinement_best_of_k` | `blocked` | 论文规模的每轮 refinement trajectory / trace / aggregate 数据 |
| `claim_baseline_generator_comparison` | `not_testable` | Trace2Skill、SkillX、EvoSkill、CoEvoSkills 的官方可执行 runner、版本、harness 适配 |
| `claim_ablation_full_wins` | `not_testable` | Figure 3 A1-A5 的官方 config、runner、开关定义、输出映射 |

## 5. 后续追问记录

本节用于记录后续问题中澄清出来的新理解。追加时建议使用如下格式：

```text
### YYYY-MM-DD - 问题标题

问题：
...

澄清：
...

对当前验证状态的影响：
...
```

### 2026-06-04 - ALFWorld 是否可以用开源 benchmark 数据继续验证

问题：

```text
ALFWorld 是不是一个开源 benchmark？
如果是，是否可以从网上找相关数据，然后根据相关数据 proceed？
```

澄清：

ALFWorld 是开源 benchmark。官方 GitHub 仓库是 `alfworld/alfworld`，README 说明
ALFWorld contains interactive TextWorld environments，并提供安装、`alfworld-download`
数据下载命令。官方官网也说明 ALFWorld contains interactive TextWorld environments that
parallel embodied worlds in the ALFRED dataset。

本地当前 run 里也已经 fetched 了 canonical ALFWorld code：

```text
phase_0/runs/skillgen_phase0_thorough_20260602/code/official/benchmarks/external/alfworld
```

本地 canonical ALFWorld 配置明确包含：

```text
$ALFWORLD_DATA/json_2.1.1/train
$ALFWORLD_DATA/json_2.1.1/valid_seen
$ALFWORLD_DATA/json_2.1.1/valid_unseen
```

并且 `scripts/alfworld-download` 指向 GitHub releases 里的 `json_2.1.1` 数据包。因此，
从“benchmark 是否公开、数据是否有 canonical 来源”的角度看，ALFWorld 是可以继续推进的。

但是，需要严格区分三件事：

```text
1. ALFWorld canonical benchmark/data 是公开的。
2. SkillGen 官方 checkout 当前没有原生 ALFWorld SkillGen adapter / dataset contract。
3. 如果我们自己用 canonical ALFWorld 数据补 adapter 和 split，这应标注为 recorded deviation 或 official-compatible reconstruction。
```

也就是说，可以从网上找 ALFWorld 官方数据并 proceed，但不能直接把它说成“SkillGen 官方仓库已经提供了完整 ALFWorld reproduction path”。更准确的说法是：

```text
使用 ALFWorld 官方开源 benchmark 和 canonical data，
构造一个 SkillGen-compatible ALFWorld adapter，
记录该 adapter 的来源、规则、偏离点和 human approval，
然后执行一个 best-available verification。
```

这样做可以消除“完全无法验证”的状态，但最终报告必须标注验证性质：

- 如果 adapter 和 split 能被证明和论文高度一致，可以接近 paper reproduction。
- 如果 split 或 adapter 是我们推导/重构的，只能标注为 approximate / reconstructed / deviation-backed verification。
- 如果只跑小样本或 smoke set，只能支持 partial / smoke-scale evidence。

对当前验证状态的影响：

这条澄清主要影响以下 blocked claims：

```text
claim_table1_average_gains_all_models
claim_table1_entry_counts
claim_table1_alfworld_scienceworld_patterns
claim_cross_model_transfer
```

新的推进方向不是继续停在“ALFWorld missing”，而是把缺失项拆成可执行任务：

```text
1. 下载或确认 ALFWorld official json_2.1.1 data。
2. 确认 valid_seen 对应论文 IOD，valid_unseen 对应论文 OOD。
3. 写 ALFWorld -> SkillGen TaskInstance adapter contract。
4. 明确 construction/test split 规则。
5. 写 human-reviewable deviation note。
6. 经过 human approval 后执行 reduced 或 full verification。
7. 在最终 report 中把结果标为 exact reproduction、approximate reconstruction、partial evidence 或 not_reproduced。
```

这不会自动让 claim 变成 `reproduced`，但它提供了一条把 `blocked` 变成“已执行、带标注的验证结果”的路径。

### 2026-06-04 - ALFWorld 解决后是否解决问题 1-4，以及 LiveCodeBench 是否开源

问题：

```text
问题 3 和 4 是否就是需要再跑一遍？
问题 1 和 2 是否是另一个 benchmark？
LiveCodeBench 是否开源？
ALFWorld 的 solution 是否可以套用到 LiveCodeBench？
```

澄清：

这个理解基本正确，但需要拆开：

```text
问题 3 = claim_table1_alfworld_scienceworld_patterns
问题 4 = claim_cross_model_transfer
问题 1 = claim_table1_average_gains_all_models
问题 2 = claim_table1_entry_counts
```

问题 3 和 4 的主要结构 blocker 是 ALFWorld。ALFWorld adapter / split contract 解决后，
它们的主要工作会变成执行和聚合：

```text
问题 3：
  跑 ALFWorld IOD/OOD + ScienceWorld 的相关 Table 1 rows，
  然后判断 ALFWorld 是否 16 个条目中 14 个提升，
  ScienceWorld 是否 8 个条目全部提升。

问题 4：
  跑 cross-model transfer matrix。
  这不是普通 evaluation，而是 source model 生成 skill，
  evaluator model 使用这个 skill，
  再和 evaluator 自己的 no-skill baseline 比。
```

所以“再跑一遍”这个说法方向是对的，但更准确应写成：

```text
在补齐 ALFWorld canonical-data adapter 和 split contract 后，
执行对应的 full / reduced verification run，
并把结果聚合成 claim-level verdict。
```

问题 1 和 2 是整体 Table 1 claims。它们不只依赖 ALFWorld，还依赖 LiveCodeBench。
当前缺口是：

```text
ALFWorld IOD
ALFWorld OOD
LiveCodeBench
```

所以 ALFWorld 解决后，问题 1 和 2 还剩 LiveCodeBench。只有 ALFWorld 和 LiveCodeBench
都处理完，才可能凑齐完整 80-entry matrix，然后计算：

```text
每个模型平均提升
80 个条目中 50 improved / 25 unchanged / 5 regressed
```

LiveCodeBench 是开源/公开 benchmark。官方 GitHub 是 `LiveCodeBench/LiveCodeBench`，
README 标注为 official repository，并提供 MIT license。官方数据在 Hugging Face
`livecodebench/code_generation_lite`，dataset card 标注 license 为 `cc`，并提供 release
versions。官方 README 说明 `release_v6` 包含 May 2023 到 Apr 2025 的 1055 个问题。

本地当前 run 里已经有：

```text
code/official/benchmarks/livecodebench_adapter.py
code/official/data/livecodebench/release_v6_all.json
```

并且 `release_v6_all.json` 已经是 SkillGen dataset wrapper：

```text
dataset_id: livecodebench_release_v6
task_name: livecodebench_release_v6_competitive_programming
task_type: binary
instances: 1055
```

这说明 LiveCodeBench 比 ALFWorld 更轻一些：

```text
ALFWorld：主要缺 adapter + split contract + execution bridge。
LiveCodeBench：adapter/evaluator 已经存在，主要缺 approved train/test split contract。
```

ALFWorld 的 solution principle 可以套用到 LiveCodeBench，但具体工作更偏 split：

```text
1. 使用 official/canonical LiveCodeBench source。
2. 固定 release_v6 / code_generation_lite。
3. 明确哪些 instance 进入 SkillGen construction。
4. 明确哪些 instance 进入 held-out test。
5. 记录 seed、排序、抽样、去重、时间窗口等规则。
6. 把该 split 写成 human-reviewable contract。
7. 执行并在 report 中标注 exact / reconstructed / deviation-backed。
```

对当前验证状态的影响：

```text
问题 3：ALFWorld 解决后基本进入 execution/aggregation。
问题 4：ALFWorld OOD 解决后基本进入 transfer execution/aggregation。
问题 1/2：ALFWorld 解决后仍需 LiveCodeBench split contract，之后才能完整验证 Table 1。
```

### 2026-06-04 - 所有 benchmark-model 能 run 后是否解决问题 5

问题：

```text
如果 ALFWorld 和 LiveCodeBench 都补齐后，所有 benchmark-model entries 都可以 run，
是不是问题 5 也解决了？
```

澄清：

不自动解决。这里需要区分两个层级：

```text
benchmark-model entry 可以 run
!=
Figure 7 / refinement best-of-K claim 已经 verify
```

如果 ALFWorld 和 LiveCodeBench 都补齐，Table 1 的 benchmark-model 执行路径会基本完整。
这主要解决的是：

```text
问题 1：Table 1 平均提升
问题 2：80 entries 的 50/25/5 计数
问题 3：ALFWorld / ScienceWorld pattern
问题 4：cross-model transfer 的 ALFWorld OOD blocker
```

但问题 5 是 `claim_refinement_best_of_k`，对应 Figure 7。它验证的不是最终 BASE vs SKILL
accuracy，而是 SkillGen refinement loop 的每一轮过程：

```text
round 1 candidate skill
round 2 candidate skill
...
round 8 candidate skill
每轮 candidate 的 paired accuracy
每轮 repairs / regressions / net gain
best-of-K 到每个 K 时选择的 best-so-far skill
最后把多个 representative runs 聚合成 Figure 7 曲线
```

所以，即使所有 benchmark-model entries 都能 run，问题 5 仍然需要额外确认：

```text
1. 每次 run 是否保存 per-round candidate skill。
2. 每轮 verification baseline outcome 和 with-skill outcome 是否保存。
3. 每轮 repairs/regressions/net gain 是否可从 raw logs 重算。
4. 哪些 benchmark-model runs 对应论文 Figure 7 的 representative runs。
5. Figure 7 的 aggregate 是怎么从这些 runs 计算出来的。
6. 当前执行规模是否足够支持 paper claim，而不是只支持 smoke-scale trace mechanics。
```

如果新 run 的 pipeline 自动保存完整 `verification/round_*` logs，那么问题 5 可以借这些
full/reconstructed runs 继续验证。但它仍需要一个单独的 Figure 7 trace aggregation contract，
不能因为 Table 1 能跑就自动判定解决。

对当前验证状态的影响：

```text
所有 benchmark-model entries 可 run = 问题 5 的原始材料可能可生成。
但问题 5 要解决，还需要 per-round trace extraction + best-of-K aggregation + Figure 7 mapping。
```

因此，问题 5 的状态可以从“缺完整 traces”推进到：

```text
ready_to_generate_traces
或
ready_for_trace_aggregation
```

但不能直接变成 `reproduced`。

### 2026-06-04 - 所有 benchmark 跑通后是否能抽数据解决问题 5

问题：

```text
如果所有 benchmark 都能跑通，我们是不是就能抽数据，从而解决问题 5？
```

澄清：

基本方向是对的：

```text
所有 benchmark 能跑通
-> 每个 run 产生 refinement / verification traces
-> 从 traces 里抽取每轮 candidate skill 的表现
-> 聚合成 Figure 7 所需的 best-of-K 曲线
-> 给 claim_refinement_best_of_k 一个可验证 verdict
```

但中间仍然有两个条件。

第一，run 必须真的保存 Figure 7 需要的 per-round 数据。只保存最终 skill 结果不够。问题 5
需要的是每一轮 refinement 的记录：

```text
round 1 candidate skill
round 2 candidate skill
...
round 8 candidate skill
每轮 baseline outcome
每轮 with-skill outcome
每轮 repairs
每轮 regressions
每轮 net gain
每轮 accuracy
best-so-far 到每个 K 的结果
```

如果官方 pipeline 在 full run 中保存这些 `verification/round_*` artifacts，那么我们可以
从 raw artifacts 中重算 Figure 7 所需指标。如果它只保存最终 selected skill，则还需要修改
日志保存或运行方式；这会成为新的 recorded deviation。

第二，需要知道 Figure 7 的聚合范围。也就是说，需要明确论文 Figure 7 用的是哪些
benchmark-model runs：

```text
只用 ALFWorld + ChemLLMBench？
还是多个 representative runs？
每条曲线对应哪些 model / dataset？
平均值和 95% CI 怎么算？
```

所以更准确的结论是：

```text
如果所有 benchmark 都跑通，并且 per-round traces 保存完整，
那么问题 5 就可以从 blocked 变成可验证；
最终状态取决于抽取和聚合后的结果。
```

这时问题 5 的解决方案不是“再跑一次最终 benchmark”本身，而是：

```text
跑完整实验
+ 保留每轮 refinement traces
+ 写 trace extraction / aggregation contract
+ 从 raw logs 重算 Figure 7 指标
+ 在 report 中给出 reproduced / partially_reproduced / not_reproduced / failed_to_run
```

执行备注：

```text
下一次执行 full / reconstructed benchmark runs 时，必须保留所有 per-round traces。
不能只保存最终 selected skill 或最终 eval_results。
```

最低限度应保留：

```text
verification/round_*/verification_baseline.jsonl
verification/round_*/verification_with_skill.jsonl
verification/round_*/verification_summary.json
verification/round_*/verification_case_analyses.json
每轮 candidate skill artifact
每轮 gate / net_gain / repair / regression / accuracy summary
```

如果官方代码默认不会保存这些内容，需要在执行前记录 deviation，并调整日志/配置，使这些
artifacts 保存在 run directory 内。

### 2026-06-04 - 问题 6 baseline comparison 是否可以找开源代码使用并备注

问题：

```text
问题 6 是 baseline generator comparison。
能否找开源代码使用，然后备注？
```

澄清：

可以。这个方向是合理的，而且现在比最初判断更乐观。公开网络检索显示，论文 Figure 2
涉及的 baseline 至少都有公开/官方代码线索：

```text
Trace2Skill -> Qwen-Applications/Trace2Skill
SkillX -> zjunlp/SkillX
EvoSkill -> sentient-agi/EvoSkill
CoEvoSkills -> Zhang-Henry/CoEvoSkills
```

但是，这仍然不能直接等价于“原论文 Figure 2 精确复现”。原因是 SkillGen 论文 Appendix
C.6 明确说，它把这些方法适配到了同一个 controlled single-skill setting：

```text
每个方法最后都输出一个 Markdown-formatted skill
不允许使用 executable helper functions
不允许使用 generated tools
不允许使用 retrieval documents
不允许调用 skill_load_reference
全部通过同一个 paired rollout harness 评估
```

很多 baseline 的 native form 不是“单个 Markdown skill”。例如 SkillX 原本构建 skill
knowledge base，EvoSkill / CoEvoSkills 可能构建多文件 skill packages 或 agent programs。
所以我们要做的是：

```text
public-code baseline reconstruction
而不是无备注的 exact Figure 2 reproduction
```

推荐执行路径：

```text
1. 对四个 baseline repo 做 source identity review：
   - repo URL
   - commit hash
   - license
   - 是否是 paper official code
   - 是否和 SkillGen 论文引用的 paper / method 对得上

2. 对每个 baseline 写 adapter contract：
   - 输入：SkillGen 已保存的 baseline trajectories / train instances
   - 输出：一个 Markdown skill
   - 禁止：scripts、references、retrieval、multi-skill routing、test-time library search
   - 允许：论文 Appendix C.6 中描述的 extraction / clustering / merging / evolution steps

3. 用同一套 held-out evaluation harness：
   - 同一 dataset split
   - 同一 base model
   - 同一 seed
   - 同一 judge/evaluator
   - same BASE vs with-skill paired comparison

4. 在 report 中标注：
   - source = public official baseline code
   - adaptation = single-skill Markdown interface
   - deviation = not necessarily SkillGen authors' exact private runner
```

这样问题 6 可以从 `not_testable` 推进为：

```text
blocked_pending_baseline_source_identity_review
或
ready_for_reconstructed_baseline_comparison
```

最终 claim status 取决于结果：

```text
reproduced：只有在能证明 repo、commit、adaptation 与论文 Figure 2 一致时才适合。
partially_reproduced：公开代码重构比较支持 SkillGen 最大平均提升，但不是作者原始 runner。
not_reproduced：公开代码重构比较不支持 Figure 2。
failed_to_run：baseline repo 或 adapter 执行失败。
```

核心备注：

```text
可以找开源代码使用，但必须做 source identity review 和 adaptation disclosure。
不要把 public-code reconstructed comparison 写成 exact original-paper baseline reproduction。
```

### 2026-06-04 - 问题 7 ablation claim 可以怎么做

问题：

```text
问题 7 是 ablation full wins。
这个感觉很难办。可以怎么做？
```

澄清：

确实更难，因为 Figure 3 的 A1-A5 没有官方 named configs 和 runner。但不是完全没办法。
可行方向是做：

```text
deviation-backed reconstructed ablation matrix
```

也就是我们自己把论文描述的 A1-A5 转成可执行 config / patch / wrapper，并且逐项标注
“这是根据论文文字重构的 ablation，不是作者提供的原始 Figure 3 config”。

论文 Figure 3 的 ablations 是：

```text
A1: ICL k=3 instead of induced skill
A2: no refinement
A3: no verification gate
A4: no Failure Lessons
A5: plain-text skill, no script + reference bundle
Full: complete SkillGen
```

可执行设计如下。

#### A1: ICL k=3 instead of induced skill

含义：

```text
不运行 SkillGen induction -> skill generation。
从 training trajectories 中选 3 个 demonstrations，
把它们作为 few-shot / in-context examples 注入 agent prompt，
然后在 held-out test 上评估。
```

可能实现：

```text
1. 从 baseline success trajectories 里固定 seed 选 3 个成功案例。
2. 把这 3 个案例写成一个 Markdown "demonstration skill"。
3. 用 SkillGen eval_skill.py 的 skill slot 注入。
4. 和 no-skill baseline 做 paired comparison。
```

必须备注：

```text
如果论文没有公布 exact 3 demonstrations 和 selection rule，
这是 reconstructed ICL-k3 ablation。
```

#### A2: no refinement

含义：

```text
只生成 round 1 candidate skill，不根据 verification feedback 进入后续 refine rounds。
```

本地官方代码中比较容易实现，因为 config 里有：

```text
pipeline.max_refine_rounds
```

可能实现：

```text
pipeline.max_refine_rounds = 1
```

这样只跑 initial generation + verification，不跑 round 2..8 refinement。

必须备注：

```text
这验证的是 no-refinement reconstructed config。
如果论文 A2 还有其他隐藏设置，这里不能声称 exact Figure 3 reproduction。
```

#### A3: no verification gate

含义：

```text
不使用 construction-time net-gain gate 来 reject / deprecate candidate skill。
即使 skill 没有通过 gate，也允许它进入 held-out evaluation。
```

可能实现：

```text
1. 保留 generation/refinement。
2. 仍然记录 verification result。
3. 但不要把 failed-gate skill 标为 deprecated/no-op。
4. held-out eval 强制使用 selected candidate skill。
```

这个需要小心，因为当前 official code 在 no round passed 时会把 skill 标记为
`DEPRECATED`，下游 eval 会当 no-op。要做 A3 可能需要新增 config，例如：

```text
verification.disable_gate_for_ablation = true
```

或者在 ablation runner 中覆盖 skill status。

必须备注：

```text
这是有行为影响的 code/config deviation。
必须保存 failed-gate skill 的原始 verification evidence，
并在 report 中标注该 run 故意禁用了 safety gate。
```

#### A4: no Failure Lessons

含义：

```text
生成 skill 时不使用 / 不输出 Failure Lessons 部分。
```

可能实现有两种：

```text
方案 1：prompt-level ablation
  修改 generation/refinement prompt，使其不要求 "Failure lessons" section。

方案 2：post-process ablation
  正常生成 skill 后，删除 "## Failure lessons" section，再评估。
```

方案 1 更接近组件级 ablation，但需要改 prompt。方案 2 更容易执行，但更粗糙，因为 skill
生成过程仍然看过 failure evidence，只是最后删除了输出 section。

推荐：

```text
优先做方案 1，并记录 prompt patch。
如果时间不够，方案 2 可以作为 weaker reconstructed ablation。
```

必须备注：

```text
如果不能证明论文 A4 使用同样删除方式，则只能叫 reconstructed no-failure-lessons ablation。
```

#### A5: plain-text skill, no script + reference bundle

含义：

```text
Full 允许 scripts + references。
A5 只允许纯文本 skill。
```

本地 official code 已有相关开关：

```text
generation.generate_scripts: false
generation.generate_references: false
```

或者通过 CLI 不传 `--generate-scripts`。

需要注意：

```text
如果某个 benchmark 的 Full 本来就是 plain-text，那么 A5 和 Full 不会有区别。
Figure 3 里 A5 主要适用于 ChemLLMBench 这类 script/reference bundle 有帮助的任务。
```

必须备注：

```text
A5 应只在 Full 确实启用了 scripts/references 的 dataset-model pair 上有意义。
```

#### Full

Full 应该使用最接近论文的 SkillGen config：

```text
max_refine_rounds = 8
verification gate enabled
Failure Lessons enabled
contrastive induction enabled
scripts/references enabled only for paper对应需要 resource bundle 的 benchmarks
```

#### 推荐的 ablation 执行策略

不要一开始就全矩阵执行。先做两层：

```text
Layer 1: smoke reconstructed ablation
  选一个便宜 dataset-model pair，验证 A1-A5 runner 都能跑，artifact 完整。

Layer 2: paper-target reconstructed ablation
  按 Figure 3 的 dataset-model pairs 跑完整 reconstructed matrix。
```

每个 ablation run 必须写：

```text
ablation_contract.json
ablation_config.yaml
deviation_note.md
raw outputs
per-round traces
held-out eval results
claim comparison
```

最终报告应该避免说：

```text
Figure 3 exactly reproduced
```

除非找到了作者原始 ablation configs。更稳妥的结论格式是：

```text
We reconstructed the Figure 3 ablation controls from the paper description.
The reconstructed ablation uses recorded config/code deviations.
Observed result: Full / not Full wins under this reconstructed setting.
```

对当前验证状态的影响：

问题 7 可以从：

```text
not_testable
```

推进为：

```text
blocked_pending_reconstructed_ablation_contract
```

一旦 contract 写完并 human-approved，就可以执行。最终状态根据结果改为：

```text
partially_reproduced
not_reproduced
failed_to_run
```

只有找到作者原始 A1-A5 configs / runner 时，才适合走 `reproduced`。

## 6. 多 agent 并行解决方案

本节用于支持后续多 agent 并行工作。新 agent 进入项目后，应先读：

```text
1. AGENTS.md
2. logs/phase_0_skillgen_handoff_20260603.md
3. logs/phase_0_skillgen_blocked_not_testable_missing_details_20260604.md
4. phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/00_run_summary/research_validation_report.md
5. phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/02_claims/all_claim_verification_matrix.md
6. phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/benchmark_execution_plan.json
7. ai4research_b/phase0/skillgen_automation.py
```

当前老板要求是：

```text
不允许 claim 停留在“不能 verify”。
每个 blocked / not_testable claim 都要想办法变成：
  - exact reproduction，或
  - canonical-source reconstruction，或
  - deviation-backed reconstructed verification，或
  - executed negative evidence，或
  - failed_to_run with preserved logs。
```

注意：这不是要求无条件把论文 claim 判成 reproduced。它要求每个 claim 都有一个可执行验证路径，
并且最终状态必须由 artifacts、raw logs、comparison 和 deviation notes 支撑。

### 6.1 并行分组总览

建议分成 6 个并行工作组：

| 组 | 名称 | 主要目标 | 解决哪些问题 |
| --- | --- | --- | --- |
| A | ALFWorld Contract / Adapter 组 | 用 canonical ALFWorld 数据补齐 SkillGen-compatible adapter 和 IOD/OOD split contract | 问题 1、2、3、4 的最大 blocker |
| B | LiveCodeBench Split 组 | 用 official LiveCodeBench release v6 数据补齐 train/test split contract | 问题 1、2 的剩余 blocker |
| C | Full Matrix / Transfer / Trace Orchestration 组 | 把 A/B 产物接入 execution plan，确保 full runs、transfer runs、per-round traces 可执行和可聚合 | 问题 1、2、3、4、5 |
| D | Baseline Source Identity 组 | 找并审查 Trace2Skill、SkillX、EvoSkill、CoEvoSkills 公开代码，设计 single-skill adapter contract | 问题 6 |
| E | Reconstructed Ablation 组 | 把 Figure 3 A1-A5 重构成可执行 ablation configs / wrappers / deviation notes | 问题 7 |
| F | Evidence / Report Integration 组 | 统一状态标签、deviation disclosures、claim matrix 更新规则和最终 report 模板 | 所有问题 |

建议每个组只写自己的工作目录，避免互相覆盖：

```text
logs/phase_0_parallel_20260604/
  A_alfworld/
  B_livecodebench/
  C_execution_trace/
  D_baseline_comparison/
  E_ablation/
  F_report_integration/
```

如果要生成正式 run artifacts，放在当前 run 的对应 artifact 目录下，但不要覆盖已有文件。
优先新建带明确名字的文件，例如：

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/alfworld_adapter_contract.md
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/livecodebench_split_contract.md
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/reconstructed_ablation_contract.md
```

### 6.2 工作组 A：ALFWorld Contract / Adapter 组

目标：

```text
把 ALFWorld 从 blocked_canonical_code_fetched_missing_skillgen_contract
推进到 ready_for_reconstructed_execution 或 ready_for_canonical_source_execution。
```

背景：

ALFWorld 是开源 benchmark。本地已经有 canonical ALFWorld code：

```text
phase_0/runs/skillgen_phase0_thorough_20260602/code/official/benchmarks/external/alfworld
```

本地 ALFWorld config 已出现：

```text
$ALFWORLD_DATA/json_2.1.1/train
$ALFWORLD_DATA/json_2.1.1/valid_seen
$ALFWORLD_DATA/json_2.1.1/valid_unseen
```

需要解决：

```text
1. 官方 ALFWorld data 如何下载到 run directory 内。
2. valid_seen 是否可作为论文 IOD。
3. valid_unseen 是否可作为论文 OOD。
4. ALFWorld raw task 如何转成 SkillGen TaskInstance。
5. SkillGen agent 如何和 ALFWorld text environment 交互。
6. success/failure 如何由 ALFWorld 环境返回并映射成 accuracy。
7. construction/test split 如何抽样，是否匹配论文 Table 3。
8. 哪些部分是 canonical，哪些是 reconstructed deviation。
```

交付物：

```text
logs/phase_0_parallel_20260604/A_alfworld/alfworld_source_review.md
logs/phase_0_parallel_20260604/A_alfworld/alfworld_adapter_contract.md
logs/phase_0_parallel_20260604/A_alfworld/alfworld_split_contract.md
logs/phase_0_parallel_20260604/A_alfworld/alfworld_deviation_note.md
```

如果实现代码，必须另外交付：

```text
logs/phase_0_parallel_20260604/A_alfworld/implementation_notes.md
tests or smoke command logs
```

禁止事项：

```text
不要把非官方二次整理数据冒充 canonical ALFWorld 数据。
不要把自写 adapter 描述成 SkillGen 官方原生支持。
不要下载数据到项目目录外；所有数据、cache、依赖必须在项目/run directory 内。
```

完成标准：

```text
能够清楚回答：
  - IOD/OOD 数据来自哪里？
  - 哪些 instance 被用作 construction/test？
  - adapter 如何执行环境交互和评分？
  - 结果应标注 exact、canonical-source reconstruction 还是 deviation-backed reconstruction？
```

### 6.3 工作组 B：LiveCodeBench Split 组

目标：

```text
把 LiveCodeBench 从 blocked_pending_train_test_split_contract
推进到 ready_for_execution。
```

背景：

LiveCodeBench 是公开 benchmark。当前 run 已有：

```text
phase_0/runs/skillgen_phase0_thorough_20260602/code/official/benchmarks/livecodebench_adapter.py
phase_0/runs/skillgen_phase0_thorough_20260602/code/official/data/livecodebench/release_v6_all.json
```

`release_v6_all.json` 已经是 SkillGen dataset wrapper：

```text
dataset_id: livecodebench_release_v6
task_name: livecodebench_release_v6_competitive_programming
task_type: binary
instances: 1055
```

所以 LiveCodeBench 的主要缺口不是 adapter，而是 split contract。

需要解决：

```text
1. 论文 Table 3 的 LiveCodeBench split 到底如何理解：
   - construction size
   - held-out test size
   - release_v6 / test_release_v6
   - seed 42

2. 从 release_v6_all.json 中如何确定 train/test：
   - 按原始顺序？
   - 按 contest/date？
   - 按 question id 排序？
   - random sample with seed 42？
   - 是否需要去重？

3. 生成哪些派生文件：
   - train_release_v6_n50_or_n150_seed42.json
   - test_release_v6_n150_seed42.json
   注意文件名必须反映真实样本量。

4. 如果不能证明 exact paper split，如何标注：
   - paper-matching inferred split
   - reconstructed split
   - deviation-backed split
```

交付物：

```text
logs/phase_0_parallel_20260604/B_livecodebench/livecodebench_source_review.md
logs/phase_0_parallel_20260604/B_livecodebench/livecodebench_split_contract.md
logs/phase_0_parallel_20260604/B_livecodebench/livecodebench_deviation_note.md
```

如果生成数据文件，必须：

```text
1. 不覆盖 release_v6_all.json。
2. 写 manifest，列出每个 output file 的 source、seed、排序、instance_ids。
3. 让 train/test instance_ids 可审计。
```

完成标准：

```text
LiveCodeBench target 可以从 benchmark_execution_plan 的 blocked 变成 ready_for_execution，
且 split 规则和 deviation 风险写清楚。
```

### 6.4 工作组 C：Full Matrix / Transfer / Trace Orchestration 组

目标：

```text
把 A/B 产出的 contracts 接入完整执行计划，
确保问题 1-5 都有执行路径和聚合路径。
```

依赖：

```text
依赖 A：ALFWorld IOD/OOD contract。
依赖 B：LiveCodeBench split contract。
```

可以先并行做不依赖 A/B 的部分：

```text
1. 审查 benchmark_execution_plan.json 的 ready targets。
2. 设计 full matrix execution manifest。
3. 设计 transfer execution manifest。
4. 设计 Figure 7 trace extraction schema。
5. 确认下一次 run 必须保留 per-round traces。
```

必须保留的 per-round trace 最低要求：

```text
verification/round_*/verification_baseline.jsonl
verification/round_*/verification_with_skill.jsonl
verification/round_*/verification_summary.json
verification/round_*/verification_case_analyses.json
每轮 candidate skill artifact
每轮 gate / net_gain / repair / regression / accuracy summary
```

需要解决：

```text
1. Table 1 full matrix 如何调度。
2. 80 entries 的 delta 如何聚合成：
   - average gains
   - 50/25/5 entry counts
   - ALFWorld 14/16
   - ScienceWorld 8/8

3. Transfer matrix 如何调度：
   - 4 benchmarks
   - 6 source models
   - 5 non-identical evaluator models
   - 120 off-diagonal comparisons

4. Figure 7 如何从 per-round traces 聚合：
   - per-round skill accuracy
   - best-of-K skill accuracy
   - aggregate mean / CI
```

交付物：

```text
logs/phase_0_parallel_20260604/C_execution_trace/full_matrix_execution_contract.md
logs/phase_0_parallel_20260604/C_execution_trace/transfer_execution_contract.md
logs/phase_0_parallel_20260604/C_execution_trace/figure7_trace_extraction_contract.md
logs/phase_0_parallel_20260604/C_execution_trace/per_round_trace_retention_checklist.md
```

完成标准：

```text
当 A/B 交付 ready contracts 后，C 组可以直接生成/更新 execution plan，
并且不会再因为“没有聚合规则”导致问题 1-5 卡住。
```

### 6.5 工作组 D：Baseline Source Identity 组

目标：

```text
把 claim_baseline_generator_comparison 从 not_testable
推进到 blocked_pending_baseline_source_identity_review
或 ready_for_reconstructed_baseline_comparison。
```

背景：

论文 Appendix C.6 对四个 baseline 的适配方式有文字说明：

```text
Trace2Skill
SkillX
EvoSkill
CoEvoSkills
```

公开代码线索：

```text
Trace2Skill -> Qwen-Applications/Trace2Skill
SkillX -> zjunlp/SkillX
EvoSkill -> sentient-agi/EvoSkill
CoEvoSkills -> Zhang-Henry/CoEvoSkills
```

需要解决：

```text
1. 每个 repo 是否是 official code。
2. commit / release tag 是什么。
3. license 是否允许使用。
4. native method 输出什么：
   - skill library？
   - multi-file skill package？
   - prompt patch？
   - agent program？

5. 如何适配成 SkillGen 论文要求的 single Markdown skill：
   - 禁用 scripts
   - 禁用 references
   - 禁用 retrieval documents
   - 禁用 multi-skill routing
   - 禁用 test-time skill selection

6. 如何接入同一个 paired rollout harness。
```

交付物：

```text
logs/phase_0_parallel_20260604/D_baseline_comparison/baseline_source_identity_review.md
logs/phase_0_parallel_20260604/D_baseline_comparison/baseline_single_skill_adapter_contract.md
logs/phase_0_parallel_20260604/D_baseline_comparison/baseline_deviation_note.md
```

完成标准：

```text
可以明确说：
  - 哪些 baseline 可以 public-code reconstructed verification。
  - 哪些 baseline 仍缺可执行 identity。
  - 每个 baseline 的 deviation 风险是什么。
```

### 6.6 工作组 E：Reconstructed Ablation 组

目标：

```text
把 claim_ablation_full_wins 从 not_testable
推进到 blocked_pending_reconstructed_ablation_contract
或 ready_for_reconstructed_ablation_execution。
```

背景：

论文 Figure 3 的 ablations：

```text
A1: ICL k=3 instead of induced skill
A2: no refinement
A3: no verification gate
A4: no Failure Lessons
A5: plain-text skill, no script + reference bundle
Full: complete SkillGen
```

本地官方代码已有一些可控配置：

```text
pipeline.max_refine_rounds
generation.generate_scripts
generation.generate_references
verification.min_net_gain_abs
verification.min_net_gain_rel
generation / refinement prompts
```

需要解决：

```text
1. 为 A1-A5 各自写 exact intended behavior。
2. 为 A1-A5 各自写 implementation method。
3. 区分 config-only ablation 和 code/prompt-patch ablation。
4. 写 safety/deviation notes。
5. 设计 smoke ablation 和 paper-target ablation 两层执行。
```

建议实现层级：

```text
A1 ICL k=3:
  从 fixed seed 的 training success trajectories 选 3 个 demonstrations，
  构造 Markdown demonstration skill。

A2 no refinement:
  pipeline.max_refine_rounds = 1。

A3 no verification gate:
  强制保留 failed-gate skill 并用于 held-out eval。
  必须标注 safety gate disabled。

A4 no Failure Lessons:
  优先 prompt-level ablation。
  次优 post-process 删除 "## Failure lessons" section。

A5 plain-text skill:
  generation.generate_scripts = false
  generation.generate_references = false
```

交付物：

```text
logs/phase_0_parallel_20260604/E_ablation/reconstructed_ablation_contract.md
logs/phase_0_parallel_20260604/E_ablation/ablation_config_matrix.md
logs/phase_0_parallel_20260604/E_ablation/ablation_deviation_note.md
logs/phase_0_parallel_20260604/E_ablation/ablation_smoke_plan.md
```

完成标准：

```text
每个 A1-A5 都有：
  - clear behavior
  - config/patch path
  - expected artifact outputs
  - deviation label
  - rollback/safety note
```

### 6.7 工作组 F：Evidence / Report Integration 组

目标：

```text
防止多个 agent 各做各的，最后无法合并成 Phase 0 validation package。
```

需要解决：

```text
1. 统一 status transition rules。
2. 统一 deviation disclosure format。
3. 统一 artifact naming。
4. 统一 claim matrix 更新规则。
5. 统一 final report 语言。
```

建议 status transition：

```text
not_testable
-> blocked_pending_source_identity_review
-> ready_for_reconstructed_execution
-> partially_reproduced / not_reproduced / failed_to_run

blocked
-> ready_for_execution
-> reproduced / partially_reproduced / not_reproduced / failed_to_run
```

必须避免：

```text
不要因为“找到一个可执行办法”就直接标 reproduced。
不要把 reconstructed verification 写成 exact reproduction。
不要删除旧的 negative evidence。
不要覆盖 raw logs。
```

交付物：

```text
logs/phase_0_parallel_20260604/F_report_integration/status_transition_policy.md
logs/phase_0_parallel_20260604/F_report_integration/deviation_disclosure_template.md
logs/phase_0_parallel_20260604/F_report_integration/claim_matrix_update_plan.md
logs/phase_0_parallel_20260604/F_report_integration/final_report_patch_plan.md
```

完成标准：

```text
任何组交付结果后，F 组能判断该结果应该如何进入：
  - all_claim_verification_matrix
  - research_validation_report
  - hardcoding_disclosures / deviation notes
  - benchmark execution artifacts
```

### 6.8 推荐并行顺序

第一批立即并行：

```text
A: ALFWorld contract / adapter
B: LiveCodeBench split
D: baseline source identity
E: reconstructed ablation contract
F: status/deviation/report integration policy
```

第二批依赖 A/B/D/E 的产物：

```text
C: full matrix / transfer / trace execution plan finalization
F: report integration and claim status update
```

也可以让 C 先做不依赖 A/B 的部分：

```text
trace retention checklist
Figure 7 extraction schema
ready-target execution manifest
aggregation formulas
```

### 6.9 新 agent 的通用工作要求

每个 agent 不论负责哪组，都必须遵守：

```text
1. 所有依赖、数据、cache、生成文件必须留在项目目录或 run directory 内。
2. 不覆盖已有 raw logs、reports、matrix、source files，除非明确获得指令。
3. 所有外部来源必须记录 URL、commit/tag、license、下载/访问时间。
4. 所有 reconstructed / inferred / approximate 决策必须写 deviation note。
5. 不把 AI 推理当作验证证据。验证证据必须来自代码、数据、logs、artifacts、raw outputs。
6. 不运行昂贵 API / network / Docker / 大下载前，先写 command plan 和 human review note。
7. 每个交付物必须能让下游 agent 不看聊天也能继续。
```

每个 agent 的最终回复至少要包含：

```text
负责组别
读过的关键文件
产出的 artifact 路径
当前状态
剩余 blocker
建议下一个 agent 做什么
```
