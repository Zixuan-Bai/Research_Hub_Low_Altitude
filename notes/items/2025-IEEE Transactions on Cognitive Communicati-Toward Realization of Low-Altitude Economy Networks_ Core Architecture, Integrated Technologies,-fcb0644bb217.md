# 条目摘要

本文是一篇关于低空经济（Low-Altitude Economy, LAE）网络的综述论文，系统阐述了支撑 LAE 网络的核心架构、多技术集成方案及未来研究方向。论文重点讨论了无人机（UAV）与电动垂直起降飞行器（eVTOL）在高密度低空场景下的通信、感知、计算、定位、导航、监视、飞行控制与空域管理的协同机制，并分析了生成式人工智能（GAI）在提升系统智能适应、不确定性建模与实时优化方面的使能作用。此外，论文梳理了物流、救援、交通与巡检四类典型应用，并展望了智能自适应优化、安全隐私、可持续能源、量子协调、生成式治理与三维空域覆盖等未来方向。

---

## 元数据

- **paper-supported:** DOI: `10.1109/tccn.2025.3601015`
- **paper-supported:** 标题: *Toward Realization of Low-Altitude Economy Networks: Core Architecture, Integrated Technologies, and Future Directions*
- **paper-supported:** 作者: Yixian Wang, Geng Sun (Senior Member, IEEE), Zemin Sun (Member, IEEE), Jiacheng Wang (Member, IEEE), Jiahui Li (Member, IEEE), Changyuan Zhao (Graduate Student Member, IEEE), Jing Wu, Shuang Liang, Minghao Yin (Member, IEEE), Pengfei Wang (Member, IEEE), Dusit Niyato (Fellow, IEEE), Sumei Sun (Fellow, IEEE), Dong In Kim (Life Fellow, IEEE)
- **paper-supported:** 期刊/venue: *IEEE Transactions on Cognitive Communications and Networking*, Vol. 11, No. 5, October 2025
- **paper-supported:** 关键时间节点：Received 25 April 2025; revised 2 August 2025; accepted 10 August 2025; published 20 August 2025; current version 8 October 2025
- **paper-supported:** 基金支持：中国国家自然科学基金（62272194, 62471200）、吉林省科技发展计划项目（20250101027JJ）、中国博士后科学基金（GZC20240592, 2024M761123）、吉林省教育厅科研项目（JJKH20250117KJ）、韩国国家研究基金会（NRF）资助（2021R1A2C2007638）
- **unsupported:** PDF 中未提供完整通讯作者邮箱及所有作者详细单位层级信息（仅部分片段）

---

## 收录原因

- **paper-supported:** 该文是目前系统性覆盖 LAE 网络“架构-技术-应用-未来方向”的综述，明确区分了 LAE 网络与传统 UAV 网络在密度、空域管理、安全与异构协同方面的差异。
- **paper-supported:** 论文将 GAI 作为跨通信、感知、计算、控制的多技术集成粘合剂进行专题讨论，与当前低空智能化趋势高度相关。
- **paper-supported:** 涉及多项 IEEE/ITU 标准（如 IEEE 1939.1-2021、IEEE 1937.8-2024、ITU-T Y.4421 等），可作为政策与标准化研究的入口文献。

---

## 核心内容

- **paper-supported:** 提出 LAE 网络的三层核心架构：机载终端与物理基础设施层、智能协同与数字空域层、多主体协同与服务保障层。
- **paper-supported:** 强调 LAE 网络需满足四大关键需求：智能自主决策、高精度协同技术体系、弹性资源调度、有效动态空域管理。
- **paper-supported:** 识别四大实际挑战：碎片化监管与标准化缺失、频谱共享与干扰、城市密集环境信号退化（NLOS/多径）、环境不确定性（雨雪雾湍流）。
- **paper-supported:** 将支撑技术归纳为三大集成方向：(1) 通信-感知-智能计算融合；(2) 定位-导航-监视协同；(3) 飞行控制-空域管理融合。
- **paper-supported:** 突出 GAI 在三类集成中的角色：通过生成式扩散模型（GDM）、大语言模型（LLM）、生成对抗网络（GAN）等实现智能适应、不确定性建模与实时优化。
- **paper-supported:** 讨论四大应用场景：低空物流（仓库-零售店、零售店-住宅）、低空救援、低空交通（城市空中交通 UAM）、低空巡检（电力线、桥梁、管道等）。
- **paper-supported:** 提出六个未来方向：动态空域智能自适应优化、安全与隐私保护、可持续能源与动力管理、量子驱动智能协调、生成式治理、LAE-LEO 协同三维空域覆盖。

---

## 方法 / 系统 / 政策细节

### 标准与监管框架
- **paper-supported:** IEEE 1939.1-2021：定义低空无人机操作空域结构化框架，提出 1km×1km 网格化航线规划，整合 eMBB 与 URLLC，要求动态频率调整与实时适应性。
- **paper-supported:** IEEE 1937.8-2024：规定无人机蜂窝通信终端的功能与接口，支持 BVLOS 飞行控制与高清视频实时传输，要求蜂窝基站切换延迟不超过 5ms。
- **paper-supported:** ITU-T Y.4421：定义无人机与控制器交互的功能架构，涵盖协调通信、任务编排与服务管理。
- **paper-supported:** IEEE P1954：支持无人机自组织与频谱灵活通信的架构与协议，允许自动建网与动态频谱适配。
- **paper-supported:** IEEE 1937.3-2024：规定基于短消息机制的民用无人机飞行监控数据传输，采样间隔不超过 2 秒，利用 GNSS 短消息机制传输身份、状态、经纬度、高度、航向、速度与时间戳。
- **paper-supported:** ITU-R M.2171：提供无人机频谱需求、共存策略与干扰评估指导。
- **paper-supported:** 3GPP Release-18 规定 NR-UAV 增强，包括无人机移动性管理、网络切片与干扰抑制。

### 通信技术
- **paper-supported:** 5G-Advanced（5G-A）引入 RTBC（实时宽带通信）、uCBC（上行中心宽带通信）、HCS（和谐通信与感知），并继续使用 eMBB、URLLC、mMTC。
- **paper-supported:** 采用毫米波（mmWave，30–300 GHz）与大规模 MIMO；结合 AI/ML 进行混合波束成形与信道估计。
- **paper-supported:** 非正交多址（NOMA）用于提升网络容量；具体文献报告了 240% 容量增益（简化单径假设）、54.6% 频谱效率增益（假设完美 CSI）、37% 频谱效率与 26% 能效提升。
- **paper-supported:** GAI 辅助波束成形：GDM-enabled TD3 实现平均保密速率 7.24 bps/Hz（8 架 UAV）；MoE-Transformer 架构在最坏情况下保密速率提升超 44%；边缘多任务推理吞吐量提升最高 40.25%。
- **paper-supported:** GAI 语义通信：GAN 驱动系统通信量减少 93.45%；Swin Transformer+Diffusion 在 AWGN 下 PSNR 提升 17.75%，Rayleigh 下提升 20.86%；Stable Diffusion 视频传输 PSNR 提升高达 69%。
- **paper-supported:** LEO 卫星通信：选择算法实现平均总时延 42.76 ms、资源利用率 66.67%；IABC 优化后系统吞吐量 112.86 Mbps；基于 DRL 的切换优化降低接入时延最高 6.86 倍。

### 感知技术
- **paper-supported:** 协作主动感知：多模态传感器（雷达、LiDAR、视觉、红外）融合；FRCPNet 提升显著目标检测精度；ViTAL-TAPE 实现 0.01 米精度着陆检测。
- **paper-supported:** 通感一体化（ISAC）：通过波束共享同步雷达感知与数据通信；GAI 用于 ISAC 的到达方向估计（近场 MSE 1.03 度）、RIS 辅助信道估计、安全感知信号生成（未授权设备感知精度降低约 70%）。
- **paper-supported:** 非协作被动感知：利用现有 Wi-Fi/4G/5G 信号反射进行环境检测，无需额外硬件，但易受多径、静态杂波与噪声影响。

### 智能计算
- **paper-supported:** GAI 驱动 MEC：扩散模型用于 UAV 轨迹规划与障碍物规避（合成邻近 UAV 速度状态、生成带标注 UAV 图像使 YOLOv7 AP@0.5:0.95 提升 42%）；D2SAC 在 190 步达到基线性能；GDM 用于 UAV 辅助车辆孪生迁移，RSU 工作负载降低 52%，UAV 能耗降低 15%。
- **paper-supported:** 提示工程（Prompt Engineering）与 LLM：ICL（上下文学习）用于应急数据收集调度；Chain-of-Thought 增强中间推理；Self-refinement 支持迭代优化。
- **paper-supported:** 云-边-端协同：GAI 与 XR（AR/VR/MR）结合，通过 RAG（检索增强生成）提升 AR 导航与应急响应的上下文理解；GDM 赋能数字孪生（DT）进行数据增强与行为建模。

### 定位、导航与监视
- **paper-supported:** 高精度定位：GNSS（GPS/GLONASS/Galileo/BeiDou）为基础；A-GNSS 通过地面移动通信网络传输星历与校正数据，加速首次定位时间（TTFF）并提升精度。
- **paper-supported:** 动态融合导航：单传感器（视觉/LiDAR SLAM、INS）适用于 GNSS 拒止环境；多传感器融合（SLG-SLAM 在 KITTI 数据集绝对轨迹误差降低 43.50%；INS/LiDAR SLAM 紧耦合/松耦合方案）。
- **paper-supported:** 实时监视：ADS-B 基于 GNSS 周期性广播位置、速度、航向、高度；采样间隔不超过 2 秒。
- **paper-supported:** ADS-B 安全增强：无证书短签名认证（CABBA）；TDoA/MLAT 验证位置真实性；ATBAS 定位精度较 MLAT 提升 56.93%，较预期 TDoA 提升 48.86%；迁移学习与自编码器检测恶意发射器与 GNSS 欺骗。

### 飞行控制与空域管理
- **paper-supported:** 先进飞行控制：AI 增强 PID（混合 IAFC/ILAFC，抗干扰与敏捷性能提升 17%）；AI 增强 MPC（NN+NMPC、MPC+DRL 分层框架）；HITL-RL（人在回路强化学习）用于多 UAV 协同（TD3-H 成功率 0.94；HITL-DDPG 导航成功率从 0.78 提升至 0.83）。
- **paper-supported:** 空域管理模式：全混合管理（Fully Mixed）、分层管理（Layered，如 400 英尺以下分层）、分区管理（Zoning，由 ZSP 管理各区域）、走廊管理（Corridor，如隧道空域概念）。
- **paper-supported:** GAI 在空管与飞行控制融合中的应用：GAIL 用于虚拟导航训练；BezierVAE 重建误差降低 91.3%，轨迹粗糙度降低 83.4%；Lyapunov-GDM-RL 保障长期稳定性；HG-MADDPG 平均任务完成延迟降低 20.35%；DBRL 在 VR 视频场景下 QoSSR 维持约 1.0。

---

## 关键证据

- **paper-supported:** GDM-TD3 波束成形：平均保密速率 7.24 bps/Hz，8 UAV 每步能耗 1879.85 J（文献 [106]）。
- **paper-supported:** MoE-Transformer 鲁棒波束成形：最坏情况保密速率提升超 44%（文献 [15]）。
- **paper-supported:** 语义通信减容：GAN 系统通信量减少 93.45%（文献 [109]）；Stable Diffusion 视频传输 PSNR 提升高达 69%，MSE 降低 52%，FVD 降低 38%（文献 [112]）。
- **paper-supported:** NOMA-mmWave 容量：文献 [103] 报告 240% 容量增益（基于简化单径假设，无多小区干扰）；文献 [104] 报告 54.6% 频谱效率增益（假设完美 CSI，仅上行）。
- **paper-supported:** LEO 卫星通信性能：平均总时延 42.76 ms，资源利用率 66.67%（文献 [113]）；系统吞吐量 112.86 Mbps（文献 [114]）；DHO 接入时延降低最高 6.86 倍（文献 [119]）。
- **paper-supported:** 感知精度：ViTAL-TAPE 着陆检测精度 0.01 m（文献 [124]）；ISAC 近场 DOA 估计 MSE 1.03°（文献 [127]）。
- **paper-supported:** GAI-MEC 性能：YOLOv7 检测 AP@0.5:0.95 提升 42%（文献 [135]）；D2SAC 效用 494，碰撞率 1.1%，训练时间 1.3 小时（文献 [136]）；RSU 负载降低 52%，UAV 能耗降低 15%（文献 [137]）。
- **paper-supported:** 导航精度：SLG-SLAM 在 KITTI 数据集绝对轨迹误差降低 43.50%，MVE 降低 14.91%（文献 [179]）。
- **paper-supported:** ADS-B 增强：ATBAS 定位精度较 MLAT 提升 56.93%，较预期 TDoA 提升 48.86%（文献 [194]）。
- **paper-supported:** 飞行控制：PID-ILAFC 抗干扰与敏捷性能提升 17%（文献 [215]）；HITL-DDPG 导航成功率从 0.78 提升至 0.83（文献 [221]）。
- **paper-supported:** 轨迹生成：BezierVAE 重建误差降低 91.3%，轨迹粗糙度降低 83.4%（文献 [234]）；HG-MADDPG 平均任务完成延迟降低 20.35%（文献 [236]）。
- **unsupported:** PDF 中未提供上述所有数值结果在本文作者自身实验中的复现或验证情况；多数数值来自引用的参考文献，而非本文独立实验。

---

## 图表与可视证据

- **paper-supported:** **Fig. 1**：本文结构概览图，展示四大章节逻辑关系：LAE 网络概述、使能技术、多技术集成应用、未来方向。
- **paper-supported:** **Fig. 2**：LAE 网络架构交互图，展示三层架构（机载终端与物理基础设施层、智能协同与数字空域层、多主体协同与服务保障层）及各模块间的数据流、控制流与双向交互。
- **paper-supported:** **Fig. 3**：GAI 驱动计算架构图。Part A 展示基于 MEC 的架构（文本生成、AI 聊天机器人、决策支持）；Part B 展示云-边-端协同框架（图像生成、视频生成、图生成）。
- **paper-supported:** **Fig. 4**：文献 [148] 提出的 ISCC 多用户无线网络架构，基站利用 ISAC 波形整合通信与感知，并与 IoT 设备协同计算。
- **paper-supported:** **Fig. 5**：综合 UAV 导航与定位框架。Part A 为 GNSS 模块（BDS/Galileo/GPS/GLONASS）；Part B 为 SLAM 流程（前端特征提取、后端地图估计与位姿优化）；Part C 为 INS 模块（加速度计与陀螺仪数据）。
- **paper-supported:** **Fig. 6**：文献 [185] 的 INS/LiDAR SLAM 松耦合集成系统整体结构，包含 IMU 模块、LiDAR SLAM 模块、GNSS/INS 模块及 EKF 滤波融合。
- **paper-supported:** **Fig. 7**：空中交通监视架构对比。Part A 为 ADS-B 系统；Part B 为 MLAT 架构；Part C 为预期 TDoA 架构。
- **paper-supported:** **Fig. 8**：文献 [215] 的 PID–ILAFC 示意图，展示 PID 控制器生成控制信号、ILA 模块补偿、反馈回路纠错。
- **paper-supported:** **Fig. 9**：低空飞行器空域管理示意图。Part A 全混合管理；Part B 分层管理；Part C 分区管理；Part D 走廊管理。
- **paper-supported:** **Fig. 10**：文献 [227] 基于区域的网络结构。Part A 单区域内结构与流；Part B 多区域整体结构。
- **paper-supported:** **Fig. 11**：多技术集成优化 UAV 物流操作，涵盖仓库到零售店、零售店到住宅两个关键场景。
- **paper-supported:** **Fig. 12**：多技术集成提升 UAV 救援效率。
- **paper-supported:** **Fig. 13**：多技术集成增强 UAV 交通运营。
- **paper-supported:** **Fig. 14**：多技术集成实现有效 UAV 巡检操作。

---

## 局限性

- **paper-supported:** 本文作为综述，主要整合已有研究，未报告新的统一实验平台或大规模实测结果；多数性能数据来自引用的独立文献，实验条件与假设不一致。
- **paper-supported:** 论文指出大规模生成模型在资源受限边缘节点部署时，存在训练数据与计算资源需求高的问题（文献 [145]）。
- **paper-supported:** GAI 生成输出的可解释性差，可能阻碍安全关键应用中的可靠性与可追溯性（文献 [146]）。
- **paper-supported:** 边缘环境高度动态，导致训练场景与部署场景差异大，泛化能力不足（文献 [145]）。
- **paper-supported:** 依赖分布式多源数据增加了隐私与安全保护的复杂性（文献 [147]）。
- **paper-supported:** 在通信-感知-计算集成部分，论文指出设备快速增长与有限通信资源之间的矛盾、空口动态开放导致的 3D 空间覆盖与安全问题仍是现实挑战。
- **paper-supported:** ADS-B 在低密度空域设计，直接应用于高密度低空环境时面临广播拥塞、信道碰撞、复杂地形多径、对资源受限异构平台适应性不足等问题。

---

## 与低空研究的关联

- **paper-supported:** 直接面向低空经济网络（LAE Networks），覆盖低空物流、救援、交通、巡检四大核心场景，可作为低空产业技术路线图的顶层参考。
- **paper-supported:** 系统梳理了 IEEE、ITU、3GPP 等国际标准组织的低空相关标准，对政策制定与合规研究具有直接参考价值。
- **paper-supported:** 将 GAI 与低空网络深度融合，提出“生成式治理”“GAI-空域管理”“GAI-飞行控制”等交叉方向，对当前低空智能化研究具有前瞻指引。
- **paper-supported:** 明确区分 LAE 网络与传统 UAV 网络在规模（数百至数千架）、空域密度、异构协同、监管复杂度上的差异，有助于研究定位的精确化。

---

## 可复用参数 / 模型 / 基线

- **paper-supported:** 标准编号：IEEE 1939.1-2021、IEEE 1937.8-2024、IEEE 1937.3-2024、IEEE P1954、IEEE P1920.1、ITU-T Y.4421、ITU-R M.2171、3GPP Release-18 NR-UAV。
- **paper-supported:** 架构模型：三层 LAE 网络架构（机载终端与物理基础设施层、智能协同与数字空域层、多主体协同与服务保障层）。
- **paper-supported:** 通信技术基线：5G-A、mmWave、Massive MIMO、NOMA、LEO 卫星通信、RIS、STARS-OFDMA。
- **paper-supported:** GAI 模型/方法：GDM（生成扩散模型）、GAN、VAE、LLM（大语言模型）、MoE-Transformer、Swin Transformer、Stable Diffusion、D2SAC、TD3、DDPG、PPO、MADDPG、HG-MADDPG、DBRL、RAG。
- **paper-supported:** 感知/导航算法：FRCPNet、ViTAL-TAPE、SLG-SLAM、EKF-based INS/LiDAR SLAM、GNSS/INS/LiDAR 紧耦合。
- **paper-supported:** 控制方法：PID-ILAFC、AI-based MPC、HITL-RL（TD3-H、HITL-DDPG）、NMPC、BezierVAE、GAIL。
- **paper-supported:** 空域管理模型：Fully Mixed、Layered、Zoning（ZSP）、Corridor（含隧道空域概念）。
- **paper-supported:** 数据集/工具：KITTI、MVE、M2DGR、CU、GNSS RUMS 城市模拟工具。
- **paper-supported:** 性能基准数值：详见“关键证据”章节所列各文献报告的具体数值（需注意其原始假设条件）。

---

## 后续动作

- **proposal:** 核验 IEEE 1937.8-2024、IEEE 1937.3-2024 等标准的最终发布状态与正式文本，确认引用的准确性。
- **proposal:** 补充作者单位、通讯作者联系方式及 ORCID 等元数据，完善情报档案。
- **proposal:** 查找并核对文中提到的试点部署（EHang 深圳、Zipline FAA BVLOS、SoftBank 能登地震、Joby-NASA 达拉斯模拟、韩国 UAM Grand Challenge、JOUAV 广西巡检、英国 Sees.ai BVLOS）的原始公开报道与最新进展。
- **proposal:** 追溯 Table II、Table IV 等表格中引用文献 [31]–[38] 的详细内容，评估本文综述边界与遗漏领域。
- **proposal:** 对“关键证据”中引用的原始文献（如 [103]、[104]、[106]、[109]–[112] 等）进行独立核验，确认数值结果的实验条件与可迁移性。
- **proposal:** 查找 3GPP Release-18 NR-UAV 增强条款的正式技术规范文档，核实 UAV 移动性管理、网络切片与干扰抑制的具体定义。

---

## 可靠性说明

- **paper-supported:** 本笔记中的标题、作者、DOI、期刊卷期号、接收/修订/接受日期、基金编号、标准编号均直接提取自 PDF 文本或页眉页脚。
- **paper-supported:** 所有技术细节、数值结果、图表编号与描述均基于 PDF 全文解析内容，未引入外部数据库或搜索引擎的推断信息。
- **inferred:** 关于期刊具体出版月份（October 2025）与当前版本日期（8 October 2025）来自 PDF 页眉信息，结合 IEEE 典型出版流程推断为正式刊出时间。
- **unsupported:** PDF 中未提供本文作者自行开展的统一实验验证；文中性能数据均引用自第三方文献，其实验设置、数据集与假设条件可能存在差异，需独立审阅原始文献后方可用于研究基线。
- **full-text parsed:** 本笔记基于模型对 PDF 全文的自动解析生成，尚未经过人工逐页精读与逐句核对，可能存在表格断行、引用关联错位或数值转录误差。

<!-- item_reading_metadata
{
  "item_id": "fcb0644bb217",
  "reading_model": "kimi-k2.6",
  "reading_provider": "kimi",
  "read_at": "2026-05-31T04:19:56+00:00",
  "pdf_fingerprint": "fa043c2df6f4804ecaf90f7de85a8ee5b34f5622c255d97191bf6536a77bf04c",
  "pdf_source": "literature\\inbox\\papers\\Toward_Realization_of_Low-Altitude_Economy_Networks_Core_Architecture_Integrated_Technologies_and_Future_Directions.pdf",
  "reading_status": "full-text parsed",
  "human_reviewed": false
}
-->
