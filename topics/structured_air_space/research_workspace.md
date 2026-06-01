# Topic Research Workspace: structured_air_space

- updated_at: 2026-06-01T09:48:44+00:00
- item_count: 8
- noted_count: 8
- context_signal_count: 0

> needs-review: 本页是人机共同维护的研究讨论草稿，不是最终研究结论、novelty claim 或路线卡。

## 证据基底

- **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility** [openalex](https://openalex.org/W4403601806)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：2；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling** [local_pdf](https://doi.org/10.1002/ett.3966)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：2；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Formalization of Interstate Traffic Rules in Temporal Logic** [local_pdf](https://doi.org/10.1109/iv47402.2020.9304549)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL** [local_pdf](https://link.springer.com/chapter/10.1007/978-3-030-61467-6_27)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles** [local_pdf](https://dl.acm.org/doi/10.1145/3358221)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management** [local_pdf](https://doi.org/10.1109/smartcomp.2017.7946999)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets** [crossref](https://link.springer.com/chapter/10.1007/978-3-642-04761-9_7)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Modeling traffic signal control using Petri nets** [local_pdf](https://doi.org/10.1109/tits.2004.833763)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`

## 社会数据库线索

- needs-review: 暂无标准、政策、报告、白皮书或产业线索。

## 当前认识

- paper-supported: needs-review
- inferred: needs-review
- unsupported: needs-review

## 不确定信息

- needs-review: **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：继续阅读：跟踪作者团队（Li, Zhang, Liu 等）在无人机航线网络规划、低空空域安全间隔方面的后续研究
- needs-review: **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：核验参数：核实论文中无人机性能参数（Mavic Air 2、Inspire 2、M300 RTK 的轴距、高度、最大速度）与 DJI 官方 specs 的一致性
- needs-review: **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：补充 metadata：查找该研究是否依托特定仿真平台（如 MATLAB、Python、AirSim、NASA ATC 仿真框架）及是否有开源代码或数据补充页
- needs-review: **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：查找政策/标准/产业背景：对照中国《无人驾驶航空器飞行管理暂行条例》、民航局低空航路划设相关咨询通告，评估论文中“沿路型/环形”交叉口概念在法规与工程实践中的可落地性
- needs-review: **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：查找对比文献：检索同期或近期关于城市无人机“sky corridor / sky tube / sky lane”及“vertiport 进近航线”设计的文献，进行方案交叉对比
- needs-review: **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling**：核验模糊参数：人工核对第 15 页 PSO 参数 β, φ, ψ 的原始排版（原文“empirically set equal to 13”疑似 OCR/排版错误，需确认是否为 1/3 或其他数值）
- needs-review: **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling**：补充低空对照文献：查找 U-space、UTM、无人机冲突消解（如 Geo-fencing、ADSB-X、DAIDALUS）方面的综述，与地面 AIM 进行结构化对比
- needs-review: **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling**：提取真实测试基线：详细提取 Table 1 中各参考文献的实车/机器人测试条件（车辆数、通信方式、计算平台、碰撞原因），用于低空物理验证试验的风险评估
- needs-review: **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling**：查找政策/标准背景：检索 SAE、ISO、EU 及中国关于 CAV 交叉口协同管理与 V2X 通信标准的最新文件，判断其中 Reservation/Platoon 协议的标准化程度
- needs-review: **Formalization of Interstate Traffic Rules in Temporal Logic**：继续阅读：查找该团队后续关于城市道路规则形式化及在线监控的论文（文中提及未来工作方向）
- needs-review: **Formalization of Interstate Traffic Rules in Temporal Logic**：核验参数：若计划将安全距离模型或 MTL 监控器用于低空场景，需核验飞行器纵向减速能力与 a_abrupt、t_d 等参数是否适配
- needs-review: **Formalization of Interstate Traffic Rules in Temporal Logic**：补充 metadata：确认论文具体页码范围（PDF 显示为 752–759），并补充准确的会议地点与日期信息
- needs-review: **Formalization of Interstate Traffic Rules in Temporal Logic**：查找政策/标准/产业背景：检索德国 StVO 与 VCoRT 的正式英文版本，对比文中基于 German Law Archive 的非官方翻译，确保法律引用准确；同时检索 ICAO/IATA 及中国民航局（CAAC）关于低空飞行规则的类似结构化需求
- needs-review: **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：继续阅读本文引用的相关工作，特别是 [12]（RSL*+SAL 的同一案例研究）与 [14]（RSL+RAISE 定理证明），以对比定理证明、符号模型检验与 UPPAAL 即时符号验证在低空场景中的适用边界
- needs-review: **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：核验并补充 metadata：查找该论文在 Springer 中的确切 DOI、LNCS 卷号与页码
- needs-review: **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：查找 RELIS 2000 系统及其后续 SaRDIn 项目（见引用 [9]）的实际部署标准、安全完整性等级（SIL）与 CENELEC EN 50128 的符合性细节，以评估铁路安全标准对低空系统认证标准的借鉴价值
- needs-review: **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：检索低空/无人机分布式交通管理领域是否已有使用 UPPAAL、nuXmv、SPIN 或 mCRL2 的形式化验证文献，建立跨领域方法映射
- needs-review: **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：若需复用模型，应下载 GitHub 仓库（DistributedRailwayControl）中的实验模型与性质文件，人工核对通道声明与配置数据格式，确认其可配置性是否支持非线性网络（如网格、多交叉点）的扩展
- needs-review: **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：继续阅读 Liu et al. (2018) 的分布式冲突消解工作（参考文献 [18]），以对比集中式与分布式策略在低空场景的可迁移性
- needs-review: **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：核验论文 Table 2–5 中的数值结果是否与文中给出的算法复杂度及参数设定一致
- needs-review: **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：补充该论文在低空空域管理（UAM/UTM）领域的直接应用文献，确认图模型与循环移除算法是否已被后续研究迁移至无人机交叉口调度
- needs-review: **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：查找无人机/低空交通相关的形式化验证标准或政策文件（如 ASTM F3548、EASA U-space 等），对比本文死锁验证方法与低空监管要求的符合性
- needs-review: **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：补充该论文在真实测试场景（硬件在环或实车实验）的后续验证记录，若存在
- needs-review: **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management**：继续阅读该论文引用的STIP协议文献（[8][9]）及多智能体交叉路口管理文献（[5]），以理解更细粒度的网格化调度方法
- needs-review: **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management**：核验论文中的超时参数（4 s / 8 s）是否仅针对DSRC车路通信场景，并评估其是否适用于低空5G/卫星/ADS-B链路的典型延迟分布
- needs-review: **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management**：查找低空/无人机空域管理领域是否已有基于UPPAAL或时序自动机的冲突消解形式化验证工作，进行横向对比
- needs-review: **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management**：补充该论文的完整出版metadata（如确认IEEE International Conference on Smart Computing的举办地点、 exact 页码）
- needs-review: **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets**：核验并修正情报库 metadata：将作者、年份更正为 Joakim Byg 等、2009 年，补充 venue（ATVA 2009）与出版商（Springer）
- needs-review: **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets**：若低空课题涉及时间敏感并发系统的形式化验证，可进一步检索 TAPAAL 后续版本文献，确认其是否已解除对 EG/AF 查询的 transition 度数限制，以及是否已支持具体 timed trace 输出
- needs-review: **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets**：检索该论文的引用网络，确认是否存在将 TAPN / TAPAAL 应用于无人机集群调度、低空交通流建模等形式化分析的研究

## 可能论文 idea（问题形式）

- proposal: needs-review

## 推荐下一步阅读 / 检索

- needs-review: 优先补齐直接 PDF/报告/标准原文，再讨论 gap。

## 讨论记录

- needs-review: 在 Streamlit Topic Workspace 中追加你和 LLM 的讨论结论；保留证据标签。
