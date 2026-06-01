# 研究情报复核面板

> 机器生成的轻量 review 面板。常规使用时优先看这里或 Streamlit，不需要直接维护内部文件。

## 建议操作

- 人工状态 `review_status`：`new` / `kept` / `downloaded` / `rejected`，由你在 GUI 中修改。
- 流程状态 `process_status`：`unread` / `noted` / `used_in_synthesis`，通常由脚本自动维护；阅读深度看 metadata 中的 `reading_status` / `reading_mode`。
- 元数据状态 `metadata_status`：`auto` / `needs_review` / `verified`，GUI 保存 metadata 后会标记为 `verified`。

## 元数据待复核

暂无。

## 后续建议待处理

- `4de29d1388` **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：继续阅读：跟踪作者团队（Li, Zhang, Liu 等）在无人机航线网络规划、低空空域安全间隔方面的后续研究
- `4bbd25e2f2` **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：核验参数：核实论文中无人机性能参数（Mavic Air 2、Inspire 2、M300 RTK 的轴距、高度、最大速度）与 DJI 官方 specs 的一致性
- `bf7306691e` **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：补充 metadata：查找该研究是否依托特定仿真平台（如 MATLAB、Python、AirSim、NASA ATC 仿真框架）及是否有开源代码或数据补充页
- `56adbec3b9` **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：查找政策/标准/产业背景：对照中国《无人驾驶航空器飞行管理暂行条例》、民航局低空航路划设相关咨询通告，评估论文中“沿路型/环形”交叉口概念在法规与工程实践中的可落地性
- `c82c3e6f21` **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility**：查找对比文献：检索同期或近期关于城市无人机“sky corridor / sky tube / sky lane”及“vertiport 进近航线”设计的文献，进行方案交叉对比
- `663478c470` **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling**：核验模糊参数：人工核对第 15 页 PSO 参数 β, φ, ψ 的原始排版（原文“empirically set equal to 13”疑似 OCR/排版错误，需确认是否为 1/3 或其他数值）
- `d416d7aa50` **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling**：补充低空对照文献：查找 U-space、UTM、无人机冲突消解（如 Geo-fencing、ADSB-X、DAIDALUS）方面的综述，与地面 AIM 进行结构化对比
- `1bc5d144a8` **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling**：提取真实测试基线：详细提取 Table 1 中各参考文献的实车/机器人测试条件（车辆数、通信方式、计算平台、碰撞原因），用于低空物理验证试验的风险评估
- `af7198972b` **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling**：查找政策/标准背景：检索 SAE、ISO、EU 及中国关于 CAV 交叉口协同管理与 V2X 通信标准的最新文件，判断其中 Reservation/Platoon 协议的标准化程度
- `35f09e330f` **Formalization of Interstate Traffic Rules in Temporal Logic**：继续阅读：查找该团队后续关于城市道路规则形式化及在线监控的论文（文中提及未来工作方向）
- `75fb9afc28` **Formalization of Interstate Traffic Rules in Temporal Logic**：核验参数：若计划将安全距离模型或 MTL 监控器用于低空场景，需核验飞行器纵向减速能力与 a_abrupt、t_d 等参数是否适配
- `1c03d8780f` **Formalization of Interstate Traffic Rules in Temporal Logic**：补充 metadata：确认论文具体页码范围（PDF 显示为 752–759），并补充准确的会议地点与日期信息
- `022d162c44` **Formalization of Interstate Traffic Rules in Temporal Logic**：查找政策/标准/产业背景：检索德国 StVO 与 VCoRT 的正式英文版本，对比文中基于 German Law Archive 的非官方翻译，确保法律引用准确；同时检索 ICAO/IATA 及中国民航局（CAAC）关于低空飞行规则的类似结构化需求
- `fa23644b6f` **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：继续阅读本文引用的相关工作，特别是 [12]（RSL*+SAL 的同一案例研究）与 [14]（RSL+RAISE 定理证明），以对比定理证明、符号模型检验与 UPPAAL 即时符号验证在低空场景中的适用边界
- `276dbb9b65` **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：核验并补充 metadata：查找该论文在 Springer 中的确切 DOI、LNCS 卷号与页码
- `8632004768` **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：查找 RELIS 2000 系统及其后续 SaRDIn 项目（见引用 [9]）的实际部署标准、安全完整性等级（SIL）与 CENELEC EN 50128 的符合性细节，以评估铁路安全标准对低空系统认证标准的借鉴价值
- `73a66339f3` **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：检索低空/无人机分布式交通管理领域是否已有使用 UPPAAL、nuXmv、SPIN 或 mCRL2 的形式化验证文献，建立跨领域方法映射
- `2b803a6adf` **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL**：若需复用模型，应下载 GitHub 仓库（DistributedRailwayControl）中的实验模型与性质文件，人工核对通道声明与配置数据格式，确认其可配置性是否支持非线性网络（如网格、多交叉点）的扩展
- `d40385e369` **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：继续阅读 Liu et al. (2018) 的分布式冲突消解工作（参考文献 [18]），以对比集中式与分布式策略在低空场景的可迁移性
- `01091580d2` **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：核验论文 Table 2–5 中的数值结果是否与文中给出的算法复杂度及参数设定一致
- `43a6bf4a23` **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：补充该论文在低空空域管理（UAM/UTM）领域的直接应用文献，确认图模型与循环移除算法是否已被后续研究迁移至无人机交叉口调度
- `2653d26510` **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：查找无人机/低空交通相关的形式化验证标准或政策文件（如 ASTM F3548、EASA U-space 等），对比本文死锁验证方法与低空监管要求的符合性
- `d466a0f214` **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles**：补充该论文在真实测试场景（硬件在环或实车实验）的后续验证记录，若存在
- `4b2656c9ba` **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management**：继续阅读该论文引用的STIP协议文献（[8][9]）及多智能体交叉路口管理文献（[5]），以理解更细粒度的网格化调度方法
- `7efd96e949` **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management**：核验论文中的超时参数（4 s / 8 s）是否仅针对DSRC车路通信场景，并评估其是否适用于低空5G/卫星/ADS-B链路的典型延迟分布
- `396275d76f` **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management**：查找低空/无人机空域管理领域是否已有基于UPPAAL或时序自动机的冲突消解形式化验证工作，进行横向对比
- `52e7f060e7` **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management**：补充该论文的完整出版metadata（如确认IEEE International Conference on Smart Computing的举办地点、 exact 页码）
- `f4bef370b2` **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets**：核验并修正情报库 metadata：将作者、年份更正为 Joakim Byg 等、2009 年，补充 venue（ATVA 2009）与出版商（Springer）
- `36a63e5859` **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets**：若低空课题涉及时间敏感并发系统的形式化验证，可进一步检索 TAPAAL 后续版本文献，确认其是否已解除对 EG/AF 查询的 transition 度数限制，以及是否已支持具体 timed trace 输出
- `d54bd0e55d` **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets**：检索该论文的引用网络，确认是否存在将 TAPN / TAPAAL 应用于无人机集群调度、低空交通流建模等形式化分析的研究
- `4dfd8e165b` **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets**：如需复现实验，访问 www.tapaal.net 获取工具发行版及文中包含的示例模型
- `8e914ade48` **Modeling traffic signal control using Petri nets**：继续阅读作者后续研究，特别是文中提及的机场跑道（airport runways）[36] 与 toll booth [35] 的 PN 建模工作，以评估其在低空场景的完整迁移路径
- `83242b4420` **Modeling traffic signal control using Petri nets**：查找并核验 NETMAN [22] 等 PN 图形化代码生成工具的可用性与许可证情况，判断其是否适用于低空仿真平台集成
- `2c8aeb2867` **Modeling traffic signal control using Petri nets**：补充检索 2004 年以后 PN 在 UTM/UAM、无人机冲突检测、vertiport 调度中的直接应用文献，建立从地面交通信号到低空空域的形式化方法演进链
- `4de5e789b0` **Modeling traffic signal control using Petri nets**：核验文中 28 个 P-不变量及可达树分析的具体数值/矩阵方程是否可通过公开数据复现，或是否有开源实现
- `d2eceb8044` **Remote ID-Based UAV Supervision System**：核验实验细节：建议交叉核对 20 架无人机并发测试的具体飞行构型（90 度扇区同向飞行）与统计方法，确认"约 20 个不同信号"的判定标准及误差范围
- `60af96d2c1` **Remote ID-Based UAV Supervision System**：补充 metadata：当前元数据中 abstract 字段为空，建议从 PDF 提取摘要文本补录
- `061e49af82` **Remote ID-Based UAV Supervision System**：查找政策/标准原文：获取 GB 42590-2023 标准文本，核验 Wi-Fi Beacon Remote ID 的 OUI、消息类型与帧格式是否与论文描述完全一致
- `46463c8407` **Remote ID-Based UAV Supervision System**：核验产业背景：调研 DJI Mavic 3T 与 Mini 4K 的 Remote ID 实现细节（广播频率、功率、Wi-Fi Beacon 兼容性），以评估论文实验的可复现性
- `a214af7a5a` **Remote ID-Based UAV Supervision System**：继续阅读：检索作者团队或其他团队在 ICICC 2025 同期发表的 ADS-B/雷达多源融合监管论文，以对比单一 Remote ID 方案的覆盖盲区
- `bceb26857b` **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：继续阅读论文引用的GPS NAVSTAR性能标准（2020）及EUROCONTROL NMAC定义文件，核验论文中3σ数值与40 m上界的来源
- `eff69d3c7f` **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：补充查阅FAA Remote ID最终规定（Docket No. FAA-2019-1100, 2021）与EASA对应条款，确认强制时间节点的当前状态
- `35926dd5c2` **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：查找文献[11]（MIT Lincoln Laboratory, 2022）中关于sNMAC及7.5 m最大翼展数据库的原始定义
- `3d20a23bce` **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：若需将该uNMAC模型用于城市低空场景，应核验三维扩展版本是否已发表，并评估垂直方向误差模型
- `11af6f87b0` **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：若需工程实施，应进一步核验5G NR Sidelink在实际低空场景中的1 km覆盖能力与1–8 kHz广播速率的可实现性
- `1466249646` **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：人工核验 Table 3 中 L 与 C 参数的准确数值、单位及其在原文中的排版对应关系
- `0aec24a032` **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：检索 FAA Remote ID 最终规则（Final Rule，2021 年后）与本文实验结论的关联，确认 LoRaWAN 是否在后续 Remote ID 标准或产业实践中被采纳
- `c7f3e5601d` **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：查找 2019 年后同一研究团队或第三方针对 LoRaWAN UAV Remote ID 的跟进文献，关注 RSSI 波动补偿、动态跟踪优化与多模块标定方法
- `738a804b64` **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：补充 Moteino、Seeeduino、Libelium 等模块的硬件规格、价格与 RSSI 报告机制，评估模块差异性对实际部署的影响
- `a11d92964d` **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：核实 DJI Phantom 2 / Phantom 4 Pro 的载重、电气接口与飞行时间数据，以评估额外搭载 LoRaWAN 模块与电池的可行性
- `c80e20f429` **Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions**：核验 IEEE 1937.8-2024、IEEE 1937.3-2024 等标准的最终发布状态与正式文本，确认引用的准确性
- `04315ff900` **Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions**：补充作者单位、通讯作者联系方式及 ORCID 等元数据，完善情报档案
- `78afa5818d` **Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions**：查找并核对文中提到的试点部署（EHang 深圳、Zipline FAA BVLOS、SoftBank 能登地震、Joby-NASA 达拉斯模拟、韩国 UAM Grand Challenge、JOUAV 广西巡检、英国 Sees.ai BVLOS）的原始公开报道与最新进展
- `0f1878bf36` **Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions**：追溯 Table II、Table IV 等表格中引用文献 [31]–[38] 的详细内容，评估本文综述边界与遗漏领域
- `4f0c75225e` **Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions**：对“关键证据”中引用的原始文献（如 [103]、[104]、[106]、[109]–[112] 等）进行独立核验，确认数值结果的实验条件与可迁移性
- `c195a1ef62` **Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions**：查找 3GPP Release-18 NR-UAV 增强条款的正式技术规范文档，核实 UAV 移动性管理、网络切片与干扰抑制的具体定义
- `da8c3c319c` **Linear Multi-hop Wireless Network Design with Directional Antenna**：继续阅读：精读 III-C 节 Z-chain 频谱效率极限推导细节，以及作者引用的 Gupta & Kumar 容量理论、Hussein 节点部署策略等文献，以建立完整的网络拓扑优化知识链
- `15be2c24b1` **Linear Multi-hop Wireless Network Design with Directional Antenna**：核验参数：通过 IEEE Xplore 核对论文最终出版版本与当前 PDF 的一致性（特别是 DOI 末位差异、Fig.5 数值是否修正）
- `ff49888775` **Linear Multi-hop Wireless Network Design with Directional Antenna**：查找政策/标准/产业背景：检索 3GPP NTN（非地面网络）及 IEEE 1900 系列中关于 UAV 中继部署与定向波束管理的讨论，评估 Z-chain 在低空/6G 标准化中的潜在映射
- `403a7c9fc5` **Linear Multi-hop Wireless Network Design with Directional Antenna**：补充 metadata：确认并补录论文具体发表日期、会议举办地点等信息到情报库
- `fad2d96ccb` **Sky highway: An air traffic structure for low-altitude heterogeneous VTOL aircraft**：继续阅读论文附录及引用的相关文献（如Quan et al., 2021c; Fu et al., 2025），以深入理解分布式控制器的稳定性证明及3-D roundabout的几何约束推导
- `11584848ab` **Sky highway: An air traffic structure for low-altitude heterogeneous VTOL aircraft**：核验论文中仿真参数（如航路宽度40m、高度20m）与现行低空/无人机法规（如中国《民用无人驾驶航空发展路线图》、FAA UTM标准）中关于空域分类和间隔标准的兼容性
- `b360e184fd` **Sky highway: An air traffic structure for low-altitude heterogeneous VTOL aircraft**：查找并补充该研究团队此前发表的"sky highway"初步研究（Quan et al., 2021c）及后续3-D roundabout分布式控制论文（Fu et al., 2025），以建立完整的技术演进脉络
- `2d64e7041d` **Sky highway: An air traffic structure for low-altitude heterogeneous VTOL aircraft**：进一步调研NASA/FAA的UTM ConOps及Eurocontrol相关标准，对比本文提出的FIFO边界规则、分层高度与现有UAM走廊（corridor）规范的异同
- `b635bbac27` **Sky highway: An air traffic structure for low-altitude heterogeneous VTOL aircraft**：若需复现仿真，应核实论文中开源视频链接（https://youtu.be/URRFmUB8JJA）及是否存在配套代码/数据集

## 按数据库视图

### 论文数据库

- **Use of LoRa for UAV Remote ID with Multi-User Interference and Different Spreading Factors** [openalex](https://openalex.org/W3170762244)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：5；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Remote ID-Based UAV Supervision System** [crossref](https://ieeexplore.ieee.org/document/11199528)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Reducing safe UAV separation distances with U2U communication and new Remote ID formats** [crossref](https://doi.org/10.1109/gcwkshps56602.2022.10008607)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)** [openalex](https://onlinelibrary.wiley.com/doi/10.1155/2019/9060121)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility** [openalex](https://openalex.org/W4403601806)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：2；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling** [local_pdf](https://doi.org/10.1002/ett.3966)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：2；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Formalization of Interstate Traffic Rules in Temporal Logic** [local_pdf](https://doi.org/10.1109/iv47402.2020.9304549)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL** [local_pdf](https://link.springer.com/chapter/10.1007/978-3-030-61467-6_27)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles** [local_pdf](https://dl.acm.org/doi/10.1145/3358221)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management** [local_pdf](https://doi.org/10.1109/smartcomp.2017.7946999)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets** [crossref](https://link.springer.com/chapter/10.1007/978-3-642-04761-9_7)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Modeling traffic signal control using Petri nets** [local_pdf](https://doi.org/10.1109/tits.2004.833763)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions** [local_pdf](https://ieeexplore.ieee.org/abstract/document/11131292)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Linear Multi-hop Wireless Network Design with Directional Antenna** [local_pdf](https://doi.org/10.1109/icc52391.2025.11161536)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Sky highway: An air traffic structure for low-altitude heterogeneous VTOL aircraft** [openalex](https://www.sciencedirect.com/science/article/pii/S0968090X26000197)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`dtmb_uav_control`；topics：`dtmb_uav_control`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`

### 社会数据库

- **ASTM F3411 Standard Specification for Remote ID and Tracking** [ASTM International](https://store.astm.org/f3411-19.html)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`catalog_or_paywalled`；metadata_status：`auto`
- **3GPP UAS Connectivity, Identification and Tracking Work Item** [3GPP](https://www.3gpp.org/DynaReport/WiVsSpec--820011.htm)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`catalog_or_paywalled`；metadata_status：`auto`
- **3GPP NR Support for UAVs** [3GPP](https://www.3gpp.org/technologies/nr-uav)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`needs_document_search`；metadata_status：`auto`
- **NASA UAS Traffic Management Project** [NASA](https://www.nasa.gov/utm)；数据库：社会数据库；类型：报告 (`report`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **FAA Unmanned Aircraft System Traffic Management** [FAA](https://www.faa.gov/uas/advanced_operations/traffic_management)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **FAA Remote Identification of Drones** [FAA](https://www.faa.gov/uas/getting_started/remote_id/)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`html_fulltext`；metadata_status：`auto`
- **EASA U-space** [EASA](https://www.easa.europa.eu/en/domains/air-traffic-management/u-space)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **CAAC Minimum Performance Requirements for Operation Identification of Civil Micro, Light and Small UAVs** [CAAC](https://www.caac.gov.cn/English/News/202403/t20240305_223119.html)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`news_or_portal`；metadata_status：`auto`
- **CAAC General Aviation and Low-Altitude Economy Steering Group** [CAAC](https://www.caac.gov.cn/English/News/202507/t20250709_227896.html)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`dtmb_uav_control`；topics：`dtmb_uav_control`；相关性：3；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`news_or_portal`；metadata_status：`auto`

## 社会数据库文档可用性

### direct_pdf

暂无。

### html_fulltext

- **FAA Remote Identification of Drones** [FAA](https://www.faa.gov/uas/getting_started/remote_id/)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`html_fulltext`；metadata_status：`auto`

### landing_page

- **NASA UAS Traffic Management Project** [NASA](https://www.nasa.gov/utm)；数据库：社会数据库；类型：报告 (`report`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **FAA Unmanned Aircraft System Traffic Management** [FAA](https://www.faa.gov/uas/advanced_operations/traffic_management)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **EASA U-space** [EASA](https://www.easa.europa.eu/en/domains/air-traffic-management/u-space)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`

### catalog_or_paywalled

- **ASTM F3411 Standard Specification for Remote ID and Tracking** [ASTM International](https://store.astm.org/f3411-19.html)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`catalog_or_paywalled`；metadata_status：`auto`
- **3GPP UAS Connectivity, Identification and Tracking Work Item** [3GPP](https://www.3gpp.org/DynaReport/WiVsSpec--820011.htm)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`catalog_or_paywalled`；metadata_status：`auto`

### news_or_portal

- **CAAC Minimum Performance Requirements for Operation Identification of Civil Micro, Light and Small UAVs** [CAAC](https://www.caac.gov.cn/English/News/202403/t20240305_223119.html)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`news_or_portal`；metadata_status：`auto`
- **CAAC General Aviation and Low-Altitude Economy Steering Group** [CAAC](https://www.caac.gov.cn/English/News/202507/t20250709_227896.html)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`dtmb_uav_control`；topics：`dtmb_uav_control`；相关性：3；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`news_or_portal`；metadata_status：`auto`

### needs_document_search

- **3GPP NR Support for UAVs** [3GPP](https://www.3gpp.org/technologies/nr-uav)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`needs_document_search`；metadata_status：`auto`

## 按人工状态

### new

- **ASTM F3411 Standard Specification for Remote ID and Tracking** [ASTM International](https://store.astm.org/f3411-19.html)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`catalog_or_paywalled`；metadata_status：`auto`
- **3GPP UAS Connectivity, Identification and Tracking Work Item** [3GPP](https://www.3gpp.org/DynaReport/WiVsSpec--820011.htm)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`catalog_or_paywalled`；metadata_status：`auto`
- **3GPP NR Support for UAVs** [3GPP](https://www.3gpp.org/technologies/nr-uav)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`needs_document_search`；metadata_status：`auto`
- **CAAC General Aviation and Low-Altitude Economy Steering Group** [CAAC](https://www.caac.gov.cn/English/News/202507/t20250709_227896.html)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`dtmb_uav_control`；topics：`dtmb_uav_control`；相关性：3；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`news_or_portal`；metadata_status：`auto`

### kept

- **NASA UAS Traffic Management Project** [NASA](https://www.nasa.gov/utm)；数据库：社会数据库；类型：报告 (`report`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **FAA Unmanned Aircraft System Traffic Management** [FAA](https://www.faa.gov/uas/advanced_operations/traffic_management)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **FAA Remote Identification of Drones** [FAA](https://www.faa.gov/uas/getting_started/remote_id/)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`html_fulltext`；metadata_status：`auto`
- **EASA U-space** [EASA](https://www.easa.europa.eu/en/domains/air-traffic-management/u-space)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **CAAC Minimum Performance Requirements for Operation Identification of Civil Micro, Light and Small UAVs** [CAAC](https://www.caac.gov.cn/English/News/202403/t20240305_223119.html)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`news_or_portal`；metadata_status：`auto`

### downloaded

- **Use of LoRa for UAV Remote ID with Multi-User Interference and Different Spreading Factors** [openalex](https://openalex.org/W3170762244)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：5；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Remote ID-Based UAV Supervision System** [crossref](https://ieeexplore.ieee.org/document/11199528)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Reducing safe UAV separation distances with U2U communication and new Remote ID formats** [crossref](https://doi.org/10.1109/gcwkshps56602.2022.10008607)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)** [openalex](https://onlinelibrary.wiley.com/doi/10.1155/2019/9060121)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility** [openalex](https://openalex.org/W4403601806)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：2；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling** [local_pdf](https://doi.org/10.1002/ett.3966)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：2；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Formalization of Interstate Traffic Rules in Temporal Logic** [local_pdf](https://doi.org/10.1109/iv47402.2020.9304549)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL** [local_pdf](https://link.springer.com/chapter/10.1007/978-3-030-61467-6_27)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles** [local_pdf](https://dl.acm.org/doi/10.1145/3358221)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management** [local_pdf](https://doi.org/10.1109/smartcomp.2017.7946999)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets** [crossref](https://link.springer.com/chapter/10.1007/978-3-642-04761-9_7)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Modeling traffic signal control using Petri nets** [local_pdf](https://doi.org/10.1109/tits.2004.833763)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions** [local_pdf](https://ieeexplore.ieee.org/abstract/document/11131292)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Linear Multi-hop Wireless Network Design with Directional Antenna** [local_pdf](https://doi.org/10.1109/icc52391.2025.11161536)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Sky highway: An air traffic structure for low-altitude heterogeneous VTOL aircraft** [openalex](https://www.sciencedirect.com/science/article/pii/S0968090X26000197)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`dtmb_uav_control`；topics：`dtmb_uav_control`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`

### rejected

暂无。

## 按流程状态

### unread

- **NASA UAS Traffic Management Project** [NASA](https://www.nasa.gov/utm)；数据库：社会数据库；类型：报告 (`report`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **FAA Unmanned Aircraft System Traffic Management** [FAA](https://www.faa.gov/uas/advanced_operations/traffic_management)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **FAA Remote Identification of Drones** [FAA](https://www.faa.gov/uas/getting_started/remote_id/)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`html_fulltext`；metadata_status：`auto`
- **EASA U-space** [EASA](https://www.easa.europa.eu/en/domains/air-traffic-management/u-space)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **CAAC Minimum Performance Requirements for Operation Identification of Civil Micro, Light and Small UAVs** [CAAC](https://www.caac.gov.cn/English/News/202403/t20240305_223119.html)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`kept`；process_status：`unread`；文档可用性：`news_or_portal`；metadata_status：`auto`
- **ASTM F3411 Standard Specification for Remote ID and Tracking** [ASTM International](https://store.astm.org/f3411-19.html)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`catalog_or_paywalled`；metadata_status：`auto`
- **3GPP UAS Connectivity, Identification and Tracking Work Item** [3GPP](https://www.3gpp.org/DynaReport/WiVsSpec--820011.htm)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`catalog_or_paywalled`；metadata_status：`auto`
- **3GPP NR Support for UAVs** [3GPP](https://www.3gpp.org/technologies/nr-uav)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`needs_document_search`；metadata_status：`auto`
- **CAAC General Aviation and Low-Altitude Economy Steering Group** [CAAC](https://www.caac.gov.cn/English/News/202507/t20250709_227896.html)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`dtmb_uav_control`；topics：`dtmb_uav_control`；相关性：3；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`news_or_portal`；metadata_status：`auto`

### noted

- **Use of LoRa for UAV Remote ID with Multi-User Interference and Different Spreading Factors** [openalex](https://openalex.org/W3170762244)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：5；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Remote ID-Based UAV Supervision System** [crossref](https://ieeexplore.ieee.org/document/11199528)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Reducing safe UAV separation distances with U2U communication and new Remote ID formats** [crossref](https://doi.org/10.1109/gcwkshps56602.2022.10008607)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)** [openalex](https://onlinelibrary.wiley.com/doi/10.1155/2019/9060121)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Air Route Design of Multi-Rotor UAVs for Urban Air Mobility** [openalex](https://openalex.org/W4403601806)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：2；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Autonomous Intersection Management: Optimal Trajectories and Efficient Scheduling** [local_pdf](https://doi.org/10.1002/ett.3966)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：2；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Formalization of Interstate Traffic Rules in Temporal Logic** [local_pdf](https://doi.org/10.1109/iv47402.2020.9304549)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Formal Modelling and Verification of a Distributed Railway Interlocking System Using UPPAAL** [local_pdf](https://link.springer.com/chapter/10.1007/978-3-030-61467-6_27)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Graph-Based Modeling, Scheduling, and Verification for Intersection Management of Intelligent Vehicles** [local_pdf](https://dl.acm.org/doi/10.1145/3358221)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Delay-Aware Design, Analysis and Verification of Intelligent Intersection Management** [local_pdf](https://doi.org/10.1109/smartcomp.2017.7946999)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **TAPAAL: Editor, Simulator and Verifier of Timed-Arc Petri Nets** [crossref](https://link.springer.com/chapter/10.1007/978-3-642-04761-9_7)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Modeling traffic signal control using Petri nets** [local_pdf](https://doi.org/10.1109/tits.2004.833763)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`structured_air_space`；topics：`structured_air_space`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions** [local_pdf](https://ieeexplore.ieee.org/abstract/document/11131292)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Linear Multi-hop Wireless Network Design with Directional Antenna** [local_pdf](https://doi.org/10.1109/icc52391.2025.11161536)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`dynamic_directional_networking`；topics：`dynamic_directional_networking`；相关性：1；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Sky highway: An air traffic structure for low-altitude heterogeneous VTOL aircraft** [openalex](https://www.sciencedirect.com/science/article/pii/S0968090X26000197)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`dtmb_uav_control`；topics：`dtmb_uav_control`；相关性：1；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`

### used_in_synthesis

暂无。
