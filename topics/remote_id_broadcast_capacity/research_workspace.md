# Topic Research Workspace: remote_id_broadcast_capacity

- updated_at: 2026-06-01T09:48:44+00:00
- item_count: 10
- noted_count: 4
- context_signal_count: 6

> needs-review: 本页是人机共同维护的研究讨论草稿，不是最终研究结论、novelty claim 或路线卡。

## 证据基底

- **Remote ID-Based UAV Supervision System** [crossref](https://ieeexplore.ieee.org/document/11199528)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Reducing safe UAV separation distances with U2U communication and new Remote ID formats** [crossref](https://doi.org/10.1109/gcwkshps56602.2022.10008607)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：5；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Use of LoRa for UAV Remote ID with Multi-User Interference and Different Spreading Factors** [openalex](https://openalex.org/W3170762244)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：5；权威性：4；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`
- **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)** [openalex](https://onlinelibrary.wiley.com/doi/10.1155/2019/9060121)；数据库：论文数据库；类型：论文 (`paper`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：2；权威性：3；review_status：`downloaded`；process_status：`noted`；metadata_status：`verified`

## 社会数据库线索

- **ASTM F3411 Standard Specification for Remote ID and Tracking** [ASTM International](https://store.astm.org/f3411-19.html)；数据库：社会数据库；类型：标准 (`standard`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`catalog_or_paywalled`；metadata_status：`auto`
- **FAA Remote Identification of Drones** [FAA](https://www.faa.gov/uas/getting_started/remote_id/)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`html_fulltext`；metadata_status：`auto`
- **EASA U-space** [EASA](https://www.easa.europa.eu/en/domains/air-traffic-management/u-space)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **FAA Unmanned Aircraft System Traffic Management** [FAA](https://www.faa.gov/uas/advanced_operations/traffic_management)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **NASA UAS Traffic Management Project** [NASA](https://www.nasa.gov/utm)；数据库：社会数据库；类型：报告 (`report`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`landing_page`；metadata_status：`auto`
- **CAAC Minimum Performance Requirements for Operation Identification of Civil Micro, Light and Small UAVs** [CAAC](https://www.caac.gov.cn/English/News/202403/t20240305_223119.html)；数据库：社会数据库；类型：政策 (`policy`)；主主题：`remote_id_broadcast_capacity`；topics：`remote_id_broadcast_capacity`；相关性：4；权威性：5；review_status：`new`；process_status：`unread`；文档可用性：`news_or_portal`；metadata_status：`auto`

## 当前认识

- paper-supported: needs-review
- inferred: needs-review
- unsupported: needs-review

## 不确定信息

- needs-review: **Remote ID-Based UAV Supervision System**：核验实验细节：建议交叉核对 20 架无人机并发测试的具体飞行构型（90 度扇区同向飞行）与统计方法，确认"约 20 个不同信号"的判定标准及误差范围
- needs-review: **Remote ID-Based UAV Supervision System**：补充 metadata：当前元数据中 abstract 字段为空，建议从 PDF 提取摘要文本补录
- needs-review: **Remote ID-Based UAV Supervision System**：查找政策/标准原文：获取 GB 42590-2023 标准文本，核验 Wi-Fi Beacon Remote ID 的 OUI、消息类型与帧格式是否与论文描述完全一致
- needs-review: **Remote ID-Based UAV Supervision System**：核验产业背景：调研 DJI Mavic 3T 与 Mini 4K 的 Remote ID 实现细节（广播频率、功率、Wi-Fi Beacon 兼容性），以评估论文实验的可复现性
- needs-review: **Remote ID-Based UAV Supervision System**：继续阅读：检索作者团队或其他团队在 ICICC 2025 同期发表的 ADS-B/雷达多源融合监管论文，以对比单一 Remote ID 方案的覆盖盲区
- needs-review: **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：继续阅读论文引用的GPS NAVSTAR性能标准（2020）及EUROCONTROL NMAC定义文件，核验论文中3σ数值与40 m上界的来源
- needs-review: **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：补充查阅FAA Remote ID最终规定（Docket No. FAA-2019-1100, 2021）与EASA对应条款，确认强制时间节点的当前状态
- needs-review: **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：查找文献[11]（MIT Lincoln Laboratory, 2022）中关于sNMAC及7.5 m最大翼展数据库的原始定义
- needs-review: **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：若需将该uNMAC模型用于城市低空场景，应核验三维扩展版本是否已发表，并评估垂直方向误差模型
- needs-review: **Reducing safe UAV separation distances with U2U communication and new Remote ID formats**：若需工程实施，应进一步核验5G NR Sidelink在实际低空场景中的1 km覆盖能力与1–8 kHz广播速率的可实现性
- needs-review: **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：人工核验 Table 3 中 L 与 C 参数的准确数值、单位及其在原文中的排版对应关系
- needs-review: **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：检索 FAA Remote ID 最终规则（Final Rule，2021 年后）与本文实验结论的关联，确认 LoRaWAN 是否在后续 Remote ID 标准或产业实践中被采纳
- needs-review: **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：查找 2019 年后同一研究团队或第三方针对 LoRaWAN UAV Remote ID 的跟进文献，关注 RSSI 波动补偿、动态跟踪优化与多模块标定方法
- needs-review: **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：补充 Moteino、Seeeduino、Libelium 等模块的硬件规格、价格与 RSSI 报告机制，评估模块差异性对实际部署的影响
- needs-review: **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)**：核实 DJI Phantom 2 / Phantom 4 Pro 的载重、电气接口与飞行时间数据，以评估额外搭载 LoRaWAN 模块与电池的可行性

## 可能论文 idea（问题形式）

- proposal: needs-review

## 推荐下一步阅读 / 检索

- needs-review: 优先补齐直接 PDF/报告/标准原文，再讨论 gap。

## 讨论记录

- needs-review: 在 Streamlit Topic Workspace 中追加你和 LLM 的讨论结论；保留证据标签。
