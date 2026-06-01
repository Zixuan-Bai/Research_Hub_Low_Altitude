```markdown
# 条目摘要

## 元数据
- paper-supported: 标题：Remote ID-Based UAV Supervision System
- paper-supported: 作者：Zhaohui Yang、Zhiqiang Wu（通讯作者）、Shichao Xu，单位均为南京理工大学机械工程学院
- paper-supported: 会议/出版信息：2025 5th International Conference on Intelligent Communications and Computing (ICICC)
- paper-supported: DOI：10.1109/icicc66840.2025.11199528（由元数据提供，PDF页眉可见 DOI:10.11 前缀）
- paper-supported: 发表年份：2025
- paper-supported: IEEE 会议论文，出版物号：979-8-3315-4922-0/25

## 收录原因
- paper-supported: 元数据标记主题为 "remote_id_broadcast_capacity"，与低空研究中 UAV 监管、Remote ID 标准实施直接相关。
- paper-supported: 检索关键词匹配 UAV、Remote ID，涉及低空空域安全治理与监管平台技术。

## 核心内容
- paper-supported: 论文提出一种基于 Remote ID 的无人机地面监管系统，由嵌入式识别设备与基于 Qt6 开发的监管平台终端组成。
- paper-supported: 识别设备通过 Wi-Fi Beacon 被动截获无人机广播的 Remote ID 信号，提取无人机 ID、位置、速度、高度及飞行员位置等关键信息。
- paper-supported: 解析后的数据经网络上传至监管平台，实现多架无人机的实时可视化、状态跟踪、轨迹显示与告警功能。
- paper-supported: 实验评估表明，系统在动态条件下可在 2 km 半径内有效识别并监控多达 20 架无人机。

## 方法 / 系统 / 政策细节
- paper-supported: 政策背景：中国国家标准 GB 42590-2023《民用无人驾驶航空器系统安全要求》强制要求无人机飞行时实施 Remote ID 广播。
- paper-supported: 广播协议选择：Remote ID 支持蓝牙广播与 Wi-Fi Beacon 广播；本系统采用 Wi-Fi Beacon（2.4 GHz 与 5.8 GHz 频段），论文指出其通信距离更远、数据传输更可靠、稳定性更高。
- paper-supported: Remote ID 消息格式：共定义 7 种消息类型（0x0 Basic ID、0x1 Position report、0x3 Operation description、0x4 System、0xF Package message 等，0x2 与 0x5 为保留），每条消息长度 25 字节；首字节为消息头，其中 bit 7–4 表示消息类型，bit 3–0 表示协议版本。
- paper-supported: Wi-Fi Beacon 帧格式：使用 Vendor Specific IE，Element ID 为 221 (0xDD)；正文指出 OUI 固定值为 0xFA0BBC（表 2 中对应数值列为 16387004/0xFAOBBC），Vend Type 为 13 (0x0D)；包含 1 字节 Message Counter（0–255 循环计数）及 Remote ID Message 载荷。
- paper-supported: 硬件架构：识别与接收模块采用 ESP32 无线通信芯片（配置为 802.11 Promiscuous Mode），核心控制单元采用 STM32F7 嵌入式处理器；系统集成 GNSS 定位模块、4G LTE 网络传输模块；电源采用太阳能与可充电电池组合。
- paper-supported: 数据处理流程：ESP32 捕获 Wi-Fi Beacon 帧 → 依据 OUI 字段过滤 Remote ID 广播 → 提取并解析无人机标识、位置、速度、时间戳等字段 → 封装为标准 JSON 格式 → 经 STM32F7 聚合后通过 TCP/UDP/MQTT 上传至监管平台。
- paper-supported: 软件验证机制：采用数据完整性验证与协议验证双重机制，仅通过严格校验的数据被上传；上传后立即释放 Wi-Fi 连接资源并重启接收，形成"接收–验证–上传–复位"循环。
- paper-supported: 监管平台：基于 Qt6 框架开发，集成百度地图 API 实现地理可视化；平台端配置 MQTT 服务器接收前端数据，使用 SQLite 数据库存储已报备无人机信息以支持白名单管理。
- paper-supported: 平台核心功能包括：1）实时数据接收与可视化（解析 JSON 格式 Remote ID 数据并在地图显示轨迹）；2）自定义禁飞区与电子围栏（动态渲染并在侵入时自动记录标记）；3）非法无人机检测与告警（将接收数据与系统数据库比对，未登记无人机被判定为"黑飞"并触发实时告警）。

## 关键证据
- paper-supported: 实验平台：使用 DJI Mavic 3T 与 DJI Mini 4K 无人机进行现场测试。
- paper-supported: 识别设备接收性能：在 1.4 km 范围内，两架不同无人机 Remote ID 信号监测概率均达到 ≥99%。
- paper-supported: 最大监测范围：经 20 次测试飞行验证，判定标准为无人机超过某距离后 3 分钟内未传输任何数据包即视为超出有效范围；实测无人机飞行距离超过 2 km 且实验全程平均值大于 2 km，因此确定设备最大有效监测范围为 2 km。
- paper-supported: 并发识别能力：使用 20 架小型无人机同时在设备朝向的 90 度角扇区内同向飞行，系统成功检测约 20 个不同的 Remote ID 信号，表明单设备可同时识别约 20 架无人机。
- paper-supported: 监管平台数据接收性能：Remote ID 识别设备以平均每秒 1 次的频率向平台发送数据包，平台成功接收并在数字地图上准确渲染实时飞行轨迹及速度、高度、飞行员位置等参数。
- paper-supported: 实地部署测试：系统在 Jiang Ning Island（江宁岛）部署并监控周边区域，成功同时监控多架无人机并实时显示各自飞行路径与数据。

## 图表与可视证据
- paper-supported: 表 1（TAB 1）：Broadcast Remote Identification Message Types，列出 7 种消息类型（含保留项）及其含义。
- paper-supported: 表 2（TAB 2）：Wi-Fi Beacon Frame Format，列出 Element ID、Len、OUI/CID、Vend Type、Message Counter 及 Remote ID Message 字段的长度与取值描述。
- paper-supported: 图 1：Remote ID 监管系统硬件架构图，展示 ESP32、STM32F7、4G LTE、GNSS、电源管理等模块的连接与数据流向。
- paper-supported: 图 2：Remote ID 系统软件架构图，展示 ESP32 从系统初始化、数据捕获、OUI 过滤、解析到上传的软件流程。
- paper-supported: 图 3：Remote ID 监控平台总体流程图，展示系统初始化、数据接收处理、电子围栏管理、非法飞行检测的业务逻辑。
- paper-supported: 图 4：无人机监管系统逻辑架构图，展示 MQTT 数据接收、数据库录入、禁飞区管理三大功能模块的关系。
- paper-supported: 图 5：无人机数据库主框架图，展示数据库表结构及相关数据字段。
- paper-supported: 图 6：无人机识别设备测试场景示意图。
- paper-supported: 图 7：识别设备信号监测概率实验数据图，展示不同距离下两架无人机 Remote ID 信号接收性能曲线。
- paper-supported: 图 8：识别设备性能测试图，展示 20 次测试的最大监测范围统计结果。
- paper-supported: 图 9：无人机监管平台测试界面截图，展示地图上的飞行轨迹、飞行员位置及运动参数显示。

## 局限性
- paper-supported: 论文作者在总结章（VI）中明确指出，当前系统虽功能完善，但在以下方面仍存在不足：
- paper-supported: 目前主要实现被动监控与数据上报，对于非合规无人机缺乏即时自动响应机制。
- proposal: 作者建议未来应集成地理围栏（geofencing）、智能告警与自动响应机制，以实现主动监管与协同管控。
- proposal: 作者建议融合雷达、ADS-B 等多源传感数据，提升对未配备 Remote ID 无人机的检测能力。
- proposal: 作者建议引入边缘计算，在本地完成无人机行为识别与风险评估，减少对云服务的依赖并提升响应速度。
- proposal: 作者建议增强动态信道管理与抗干扰能力，以确保在高密度射频的城市低空环境中稳定运行。
- proposal: 作者提出系统应从被动监控向主动预测与预警转变。

## 与低空研究的关联
- paper-supported: 直接响应中国"低空经济"政策背景：论文引言提及 2024 年中国两会首次将"低空经济"写入政府工作报告，无人机在城市环境中大规模部署带来安全与监管挑战。
- paper-supported: 紧扣低空空域治理需求：系统针对城市低空"黑飞"问题，提供基于国家强制标准（GB 42590-2023）Remote ID 的地面监管方案。
- paper-supported: 为城市低空空域精细化管理与监管基础设施建设提供可参考的技术架构（硬件+平台）与性能基线。

## 可复用参数 / 模型 / 基线
- paper-supported: Remote ID Wi-Fi Beacon 过滤参数：Element ID = 221 (0xDD)，正文指定 OUI 固定值为 0xFA0BBC，Vend Type = 0x0D。
- paper-supported: Remote ID 消息结构基线：消息类型（0x0、0x1、0x3、0x4、0xF 等），单条消息 25 字节，首字节高 4 位为消息类型、低 4 位为协议版本。
- paper-supported: 硬件组合基线：ESP32（混杂模式监听 802.11）+ STM32F7（主控与网络聚合）+ 4G LTE + GNSS + 太阳能供电。
- paper-supported: 通信协议基线：设备到平台使用 MQTT（亦可 TCP/UDP），平台端基于 Qt6 集成百度地图 API 与 SQLite 数据库。
- paper-supported: 监测性能基线：最大有效监测距离 2 km；1.4 km 内监测概率 ≥99%；单设备并发识别容量约 20 架；平台数据刷新频率约 1 Hz。

## 后续动作
- proposal: 核验实验细节：建议交叉核对 20 架无人机并发测试的具体飞行构型（90 度扇区同向飞行）与统计方法，确认"约 20 个不同信号"的判定标准及误差范围。
- proposal: 补充 metadata：当前元数据中 abstract 字段为空，建议从 PDF 提取摘要文本补录。
- proposal: 查找政策/标准原文：获取 GB 42590-2023 标准文本，核验 Wi-Fi Beacon Remote ID 的 OUI、消息类型与帧格式是否与论文描述完全一致。
- proposal: 核验产业背景：调研 DJI Mavic 3T 与 Mini 4K 的 Remote ID 实现细节（广播频率、功率、Wi-Fi Beacon 兼容性），以评估论文实验的可复现性。
- proposal: 继续阅读：检索作者团队或其他团队在 ICICC 2025 同期发表的 ADS-B/雷达多源融合监管论文，以对比单一 Remote ID 方案的覆盖盲区。

## 可靠性说明
- paper-supported: 本笔记基于用户提供的 PDF 文本解析（PDF fingerprint: f2ccb2c5200013ff4a9e28c8ceacc73b3f3d4fe4723195b918a83bcc9fe4521f）生成。
- inferred: 笔记内容涵盖论文显式陈述的技术细节、实验数据与图表描述；涉及未来工作方向的归类属于对原文"Summary"章节建议性内容的直接转述。
- unsupported: PDF 中未提供完整的源代码、Qt 工程文件、数据库 Schema 详细定义及 MQTT 主题命名规范。
- unsupported: PDF 中未提供 ESP32 固件的具体射频灵敏度参数、天线增益规格及太阳能电源的续航量化指标。
- paper-supported: 所有数值结果（如 2 km、20 架、≥99%）均直接引用自论文"System Testing and Validation"章节；DOI 与会议信息来自用户提供的元数据并交叉核对 PDF 页眉。
```

<!-- item_reading_metadata
{
  "item_id": "7b62bed395bf",
  "reading_model": "kimi-k2.6",
  "reading_provider": "kimi",
  "read_at": "2026-05-31T04:16:32+00:00",
  "pdf_fingerprint": "f2ccb2c5200013ff4a9e28c8ceacc73b3f3d4fe4723195b918a83bcc9fe4521f",
  "pdf_source": "literature\\inbox\\papers\\Remote_ID-Based_UAV_Supervision_System.pdf",
  "reading_status": "full-text parsed",
  "human_reviewed": false
}
-->
