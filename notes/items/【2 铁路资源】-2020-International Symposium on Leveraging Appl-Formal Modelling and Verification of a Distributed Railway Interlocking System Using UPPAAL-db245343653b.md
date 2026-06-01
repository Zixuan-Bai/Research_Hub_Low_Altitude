```markdown
# 条目摘要

## 元数据

- `paper-supported:` 标题：*Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL*
- `paper-supported:` 作者：Per Lange Laursen, Van Anh Thi Trinh, Anne Elisabeth Haxthausen
- `paper-supported:` 机构：DTU Compute, Technical University of Denmark, Kongens Lyngby, Denmark
- `paper-supported:` 年份：2020
- `paper-supported:` 发表刊物/会议：*Leveraging Applications of Formal Methods, Verification and Validation: Applications*（Springer）
- `unsupported:` PDF 中未提供具体 DOI 字符串
- `paper-supported:` 实验模型与验证性质开源地址：`https://github.com/perlangelaursen/DistributedRailwayControl`（见页脚与 Sect. 7）
- `inferred:` 本文属于 Springer LNCS 系列会议论文集（基于同一系列常规出版形式推断，具体卷号 PDF 中未给出）

## 收录原因

- `inferred:` 用户本地文件路径包含“铁路资源”，表明采集意图是将铁路分布式控制与形式化验证作为低空/分布式交通管理的跨领域参考。
- `inferred:` 论文涉及的分布式资源预留、冲突避免、形式化模型检验方法，与低空交通管理系统（UTM/U-space）中分布式冲突消解、航路/空域资源分配问题具有方法论类比价值。

## 核心内容

- `paper-supported:` 研究对象为一个真实世界的分布式铁路联锁系统算法（基于 INSY GmbH 的 RELIS 2000 系统概念），使用 UPPAAL 进行建模与模型检验。
- `paper-supported:` 提出可重配置（re-configurable）的通用模型，通过配置数据实例化到具体铁路网络与列车集合。
- `paper-supported:` 定义了三种模型变体：
  1. **First model（基础模型）**：包含最小必要操作——预留区段（reserve a segment）、切换并锁定道岔（switch and lock a point）、列车移动（move a train）。列车控制计算机（TCC）可在满足守卫条件时以任意顺序尝试这些操作。
  2. **Restricted model（受限模型）**：在基础模型上限制操作执行顺序（例如：尽可能先完成所有区段预留，再尽可能完成锁定，再前进），以减少交错（interleavings）。
  3. **Extended model（扩展模型）**：在基础模型上增加取消操作（cancel），允许列车在发生死锁（livelock）时按相反顺序释放已获得的预留与锁。
- `paper-supported:` 验证性质包括：安全性（无碰撞、无脱轨）、一致性（TCC 与 CB 状态一致性）、活性（存在路径使所有列车最终到达终点）。
- `paper-supported:` 实验覆盖了可扩展性网络（两端列车、中间 n 个车站，n 最高至 20）以及丹麦真实本地铁路网 Nærumbanen（2 列车常规场景与 3 列车高峰场景）。

## 方法 / 系统 / 政策细节

- `paper-supported:` **建模工具**：UPPAAL（版本 4.1.19）。模型为无时间自动机（untimed automata），即使用时钟但不依赖时间约束展开状态空间。
- `paper-supported:` **系统架构组件**：
  - **Train / TCC（列车控制计算机）**：每列车一个，存储自身路线、当前位置、已获得的区段预留与道岔锁、下一步待预留/待锁定索引。
  - **CB（Control Box，控制箱）**：位于区段连接处，管理关联区段的预留状态；若位于道岔处则称为 Switch Box，还管理道岔连接状态与锁定状态。
  - **Point（道岔）**：具有 stem、plus、minus 三段连接，可处于切换中或已连接状态，需被锁定后才能被列车通过。
- `paper-supported:` **通信机制**：使用 UPPAAL 的同步通道（unicast / broadcast channels）建模组件间交互，而非共享变量。主要通道包括 `reqSeg`（区段预留请求）、`reqLock`（锁定请求）、`OK`/`notOK`（确认/拒绝）、`pass`/`passed`（通过传感器）、`switchPoint`/`OKp`（道岔切换与完成确认）。
- `paper-supported:` **控制策略**：
  - **防碰撞**：列车进入区段前必须获得该区段两端 CB 的“完整预留”（full reservation），且同一区段同时只能被一列车预留。
  - **防脱轨**：列车通过道岔前必须获得该道岔在正确位置的锁；锁定时如道岔未在正确连接状态，Switch Box 先切换再锁定。
- `paper-supported:` **优化性建模约束（相较于 [12]）**：
  - 列车仅按实际前进顺序依次预留区段和申请道岔锁（Just-In-Time 式），不提前预留远期区段。
  - 增加局部约束：列车只在离当前位置最近的 CB 申请预留；申请新预留前必须已获得当前位置到目标区段间的全部预留；申请锁定前必须已获得相邻区段在对应 CB 的预留。
- `paper-supported:` **性质规范语言**：UPPAAL 支持的 TCTL 子集。外层仅允许路径量词 `A`（所有路径）、`E`（存在路径）或 `leadsto`（`-->`），且禁止嵌套。
- `paper-supported:` **硬件实验环境**：Arch Linux OS, AMD Ryzen 2700X @ 4.0 GHz, 64 GB RAM（用于主要 UPPAAL 实验）；与 SAL 对比实验另在 Intel Core i7-8650U @ 1.90 GHz, 31 GB RAM 上由 Signe Geisler 复现执行以保证可比性。

## 关键证据

- `paper-supported:` **无碰撞（No collision）性质形式化**（TCTL）：
  ```
  A[] forall(i:t_id) forall(j:t_id) Initializer.Initialized && i != j imply
  (Train(i).curSeg != Train(j).curSeg) &&
  (Train(i).DoubleSegment imply Train(i).headSeg != Train(j).curSeg) &&
  (Train(i).DoubleSegment && Train(j).DoubleSegment imply Train(i).headSeg != Train(j).headSeg)
  ```
  含义：初始化后，任意时刻不同列车不能占据同一区段（考虑单区段与跨两区段的 DoubleSegment 状态）。
- `paper-supported:` **活性性质形式化**：
  ```
  E<> forall(i:t_id) Train(i).Arrived
  ```
  含义：存在至少一条执行路径，使得所有列车最终都到达终点。
- `paper-supported:` **可扩展性验证结果（表 1，limit = 2）**：
  - Station One：First model 0.013 s / 6515 KB；Restricted model 0.021 s / 8508 KB；Cancel model 0.046 s / 8727 KB。
  - Station Ten：First model 4344 s / 955109 KB；Restricted model 1064 s / 560651 KB；Cancel model 23912 s / 5207884 KB。
  - Station Fourteen：First model 47898 s / 5680072 KB；Restricted model 8540 s / 2043916 KB；Cancel model 在 24 小时（86400 s）内未跑完被停止。
  - Station Twenty：仅 Restricted model 完成，耗时 72986 s / 6961996 KB；其余两模型未完成。
  - Nærumbanen (2T)：First model 112 s / 122196 KB；Restricted model 20 s / 113553 KB；Cancel model 251 s / 238945 KB。
  - Nærumbanen (3T)：First model 4700 s / 1834129 KB；Restricted model 395 s / 313881 KB；Cancel model 9697 s / 3638703 KB。
- `paper-supported:` **UPPAAL 与 SAL 对比（表 2，Station One 网络，无碰撞性质）**：
  - SAL + RSL* Model 4（经适配以采用更严格的预留顺序）：约 6.03–6.18 秒，内存 105–110 MB。
  - UPPAAL First model（limit = 1）：0.017 秒，内存 9.5 MB。
  - Station Ten 网络：UPPAAL 1858 秒 / 675 MB；RSL*-SAL 无法扩展（did not scale up）。

## 图表与可视证据

- `paper-supported:` 图 1：UPPAAL 中一个带守卫、更新与同步标签的时间自动机示例。
- `paper-supported:` 图 2：铁路网络示意图，展示 segments、points、sensors、TCC（列车上）与 CB（轨道旁）的物理分布关系。
- `paper-supported:` 图 3：控制组件与道岔之间的交互箭头图（对应 8 类单播通道）。
- `paper-supported:` 图 4：First model 的 Train 模板自动机（含 Initial、SingleSegment、DoubleSegment、Arrived 等位置）。
- `paper-supported:` 图 6：Restricted model 的 Train 模板自动机，将 SingleSegment 细分为 SingleSegment → Reserving → PassOrLock → Locking 等子位置以强制确定性顺序。
- `paper-supported:` 图 7：可扩展性测试网络拓扑——两端各一列车、中间 n 个车站的线性/分支网络。
- `paper-supported:` 图 8：Nærumbanen 网络拓扑及两列车常规场景路线。
- `paper-supported:` 表 1：三种模型在多个网络实例上验证“无碰撞”的耗时（秒）与内存峰值（KB）。
- `paper-supported:` 表 2：UPPAAL 与 SAL 在 Station One 网络上的验证性能对比。

## 局限性

- `paper-supported:` **建模语言表达限制**：UPPAAL 提供的数据类型少于 RSL/RSL*，例如没有变长列表（list），不得不使用固定长度数组并以 `-1` 作为未使用槽位的填充值，导致模型“不够优雅”（less elegant）。
- `paper-supported:` **状态空间爆炸**：随车站数增加，潜在错车点增多，状态空间指数增长；Cancel model 因新增操作与状态，资源消耗最高。
- `paper-supported:` **无时间约束的抽象**：本文模型为 untimed，未对通信延迟、道岔切换时间、列车运行时间进行实时建模，因此验证结果仅保证逻辑安全，不保证时间维度的安全性。
- `paper-supported:` **通信可靠性假设**：当前模型假设同步通道通信无消息丢失、无消息篡改；论文在结论中明确指出未来需扩展消息丢失场景（无线通信环境）。
- `unsupported:` PDF 中未提供该算法在实际 RELIS 2000 部署中的具体运营数据或现场故障率统计。

## 与低空研究的关联

- `inferred:` **分布式资源预留机制可类比**：铁路中区段（segment）的“完整预留”与低空交通中空域单元/航路段的分布式预留/占用授权具有相似的互斥与一致性要求。
- `inferred:` **冲突避免策略可类比**：铁路通过“预留+锁”避免碰撞与脱轨；低空可通过“空域预留+地理围栏锁定/航线锁定”避免飞行器间冲突及侵入禁飞区。
- `inferred:` **死锁/活锁消解**：铁路场景中因双向请求导致的部分预留死锁，与多无人机在交叉航路或会合点可能出现的循环等待/资源抢占死锁问题同类；论文提出的 Cancel 操作对应低空场景中的航线重规划或资源释放机制。
- `inferred:` **形式化验证方法迁移**：UPPAAL 对分布式联锁系统的建模模式（可重配置模板+网络实例化+可达性/活性检验）可直接迁移到低空 UTM 原型系统的验证框架设计。
- `inferred:` **控制节点分布**：铁路的 TCC/CB 分布式架构与低空 UTM 中无人机机载计算机、地面控制站、分布式 UTM 服务节点（如 USS）之间的功能分层有映射关系。

## 可复用参数 / 模型 / 基线

- `paper-supported:` **资源限制参数**：`resLimit`（同时最大区段预留数）、`lockLimit`（同时最大道岔锁数）。在低空类比中可映射为单个飞行器同时占用的最大空域单元数或最大冲突消解锁点数。
- `paper-supported:` **网络配置参数**：`NTRAIN`（列车/飞行器数）、`NCB`（控制节点数）、`NSEG`（区段/航路段数）、`NROUTELENGTH`（路线长度）。可作为低空场景生成可扩展测试实例的模板。
- `paper-supported:` **验证性质模板**：
  - 互斥安全性：`A[]` 全局不变式，确保不同智能体不同时占据同一空间单元。
  - 活性/到达性：`E<>` 存在路径，确保所有智能体最终到达目标状态。
  - 一致性：分布式节点间状态（机载 vs. 地面）的双向一致性。
- `paper-supported:` **基线数据**：表 1 与表 2 提供了在特定网络规模（Station One ~ Station Twenty、Nærumbanen）上使用 UPPAAL 与 SAL 的验证时间与内存基线，可用于评估其他形式化工具在低空同类问题上的相对效率。

## 后续动作

- `proposal:` 继续阅读本文引用的相关工作，特别是 [12]（RSL*+SAL 的同一案例研究）与 [14]（RSL+RAISE 定理证明），以对比定理证明、符号模型检验与 UPPAAL 即时符号验证在低空场景中的适用边界。
- `proposal:` 核验并补充 metadata：查找该论文在 Springer 中的确切 DOI、LNCS 卷号与页码。
- `proposal:` 查找 RELIS 2000 系统及其后续 SaRDIn 项目（见引用 [9]）的实际部署标准、安全完整性等级（SIL）与 CENELEC EN 50128 的符合性细节，以评估铁路安全标准对低空系统认证标准的借鉴价值。
- `proposal:` 检索低空/无人机分布式交通管理领域是否已有使用 UPPAAL、nuXmv、SPIN 或 mCRL2 的形式化验证文献，建立跨领域方法映射。
- `proposal:` 若需复用模型，应下载 GitHub 仓库（`DistributedRailwayControl`）中的实验模型与性质文件，人工核对通道声明与配置数据格式，确认其可配置性是否支持非线性网络（如网格、多交叉点）的扩展。

## 可靠性说明

- `paper-supported:` 本笔记基于已解析的 PDF 全文内容生成（full-text parsed）。
- `paper-supported:` 所有数值结果（时间、内存、模型规模）均直接摘录自 PDF 中的表 1、表 2 与正文描述，未做数值修正。
- `unsupported:` 本笔记未经过对原始 PDF 的人工逐页审阅（full-text parsed ≠ human review），因此不排除因 PDF 排版或 OCR 解析导致的个别字符识别偏差（例如 `resBit` 与 `resCBIndex` 的代码片段在 PDF 中断行处可能存在拼接误差）。
- `unsupported:` 论文的具体 DOI、Springer LNCS 卷号及页码范围在提供的 PDF 文本中未出现，因此未纳入笔记。
```

<!-- item_reading_metadata
{
  "item_id": "db245343653b",
  "reading_model": "kimi-k2.6",
  "reading_provider": "kimi",
  "read_at": "2026-05-31T04:59:11+00:00",
  "pdf_fingerprint": "4b14a2846dfbd3b23e0669908934e90719e571402002b19856deca9d838dfbf1",
  "pdf_source": "literature\\inbox\\papers\\year-unknown-local_pdf-General rights-db245343653b.pdf",
  "reading_status": "model_parsed_pdf",
  "human_reviewed": false
}
-->
