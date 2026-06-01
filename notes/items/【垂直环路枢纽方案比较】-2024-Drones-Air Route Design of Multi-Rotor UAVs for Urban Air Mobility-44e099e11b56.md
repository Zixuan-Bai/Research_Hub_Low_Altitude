# 条目摘要

## 元数据

- `paper-supported:` 标题：Air Route Design of Multi-Rotor UAVs for Urban Air Mobility
- `paper-supported:` 作者：Shan Li、Honghai Zhang、Zhuolun Li、Hao Liu
- `paper-supported:` 期刊/venue：Drones（MDPI）
- `paper-supported:` 年份：2024
- `paper-supported:` DOI：10.3390/drones8100601
- `paper-supported:` 页数：24 页（PDF 页码标注 1–24）
- `paper-supported:` 机构：南京航空航天大学民航学院、东南大学交通学院、南京航空航天大学数学学院
- `paper-supported:` 基金：国家社会科学基金（Grant number: 22&ZD169）、江苏省研究生科研与实践创新计划（KYCX23_0392）、国家留学基金委

## 收录原因

- `inferred:` 该论文聚焦城市低空空域中多旋翼无人机的航路（air route）与交叉口（intersection）微观构型设计，属于低空经济基础设施与空域管理的关键研究方向。
- `inferred:` 论文直接对比了“沿路型”与“环形”两种交叉口方案的安全与效率表现，可为低空航路网络规划、无人机交通管理系统（UTM）规则制定提供定量参考。

## 核心内容

- `paper-supported:` 研究对象：城市低空空域（高度 60–90 m）中多旋翼无人机的航路段（leg）与交叉口（intersection）三维构型设计。
- `paper-supported:` 核心方案：基于结构化分层空域（structured and layered urban airspace），设计圆柱形管道航路段；提出两种交叉口模式——沿路型（along-road）与环形（roundabout），并分别定义其运行概念、特征参数和飞行程序（飞入、转弯、升降、飞出）。
- `paper-supported:` 评估维度：从安全（冲突风险）与效率（交叉口通过率、平均通过时间）两方面建立指标，通过仿真实验对比两种交叉口在不同规模无人机运行场景下的表现。
- `paper-supported:` 主要结论性发现：
  - 交叉口无人机数量与冲突概率呈正相关；
  - 交叉航路数量与交叉口通过率呈负相关；
  - 无人机到达率与交叉口平均通过时间呈正相关；
  - 沿路型适用于交叉航路少、无人机稀疏的场景；环形适用于交叉航路多、无人机密集的场景。

## 方法 / 系统 / 政策细节

### 空域与航路基本框架
- `proposal:` 采用分层单向运行模式：东向航路（0°–180°）与西向航路（180°–360°）分属不同高度层，相邻层反向运行，通过垂直电梯（elevator）实现换层。
- `proposal:` 航路段采用“圆柱形管道”构型，单车道单向运行；基于无人机最小外接球（spherical protected zone）设计，球直径 \(D=\sqrt{d^2+h^2}\)，其中 \(d\) 为轴距，\(h\) 为机高；并在球外设置缓冲长度 \(b\)。

### 沿路型交叉口（Along-Road）
- `proposal:` 概念：类似地面普通岔口，无人机在航路交叉区域执行转向；交叉区内设置两部单向电梯，分别用于上升与下降，避免对头冲突。
- `proposal:` 特征参数：定义交叉区域圆形范围（半径 \(r_{area}\)）、航路宽度 \(w\)、航路交叉角 \(\tau\)、最小转弯半径 \(r_{min}=\frac{v^2}{g\tan\phi_{max}}\) 与最大转弯半径 \(r_{max}=\frac{w}{1-\cos\tau}\)；交叉口状态以二元变量（Available/Occupied）表示。
- `proposal:` 飞行程序：
  - 飞入：若交叉口空闲直接进入；若占用则在等待点悬停；多机时按先到先服务或各方向轮询进入。
  - 转弯：同层转弯沿航线直接转向；需换层则进入电梯。
  - 升降：通过电梯完成，电梯高度 \(h_e = H - D - 2b\)，最大容量 \(C = 1 + \frac{H-2D-4b}{S_v}\)，\(S_v\) 为垂直安全间隔。
  - 飞出：完成转弯或升降后进入目标航路。

### 环形交叉口（Roundabout）
- `proposal:` 概念：借鉴“旋转木马”模式，在航路交汇处设置中心岛，无人机沿单向环形航路飞行；环内设置等角度等距分布的虚拟“旋转座椅”（rotate seats），无人机依附座椅绕中心运动。
- `proposal:` 特征参数：
  - 环道半径 \(R\) 需满足水平安全间隔 \(S_l\)；当 \(m\) 条航路均匀分布时，最小半径 \(R_{min}=\frac{S_l}{2\sin(\pi/2m)}\)。
  - 旋转座椅中心角 \(\theta_s = \cos^{-1}(1-\frac{S_l^2}{2R^2})\)，最大容纳座椅数 \(n = \frac{2\pi}{\theta_s}\)。
  - 座椅以恒定角速度 \(\omega_r\) 运动，无人机速度 \(v = \omega_r R\)。
  - 电梯数量等于航路数量的两倍（升降各半）。
- `proposal:` 飞行程序：
  - 飞入：无人机在入口等待点寻找空闲旋转座椅，若当前经过座椅被占用则继续等待，若空闲则沿切入线进入。
  - 转弯：无人机随座椅沿环道运动；若目标航路与进入航路同向则同层飞出，否则执行升降。
  - 升降：随座椅到达目标航路对应的电梯入口，进入电梯完成升降，再在目标层等待点判断后飞出。
  - 飞出：无人机调整航向离开座椅进入目标航路，座椅状态恢复为 Available。

### 评估指标
- `proposal:` 冲突风险（Conflict Risk）：当两架无人机保护区球心距 \(d^{k_f k_b} \le D\) 时判定潜在冲突；假设纵向、横向、垂向跟踪误差相互独立且服从三维高斯分布，冲突概率为三方向冲突概率的乘积。
- `proposal:` 服务水平（Service Level）：
  - 交叉口通过率 \(C_{uav}\)：单位时间内通过交叉口范围的架次与计划出发总架次之比。
  - 平均通过时间 \(W_{uav}\)：无人机进入与离开交叉口范围时刻差的平均值。

## 关键证据

### 仿真设置（Experiment 1–3）
- `paper-supported:` 仿真场景：城市 60–90 m 高度范围，双层标准交叉口，2/3/4 条航路等角度相交（相邻航路夹角分别为 90°、60°、45°）。
- `paper-supported:` 无人机到达率：每条航路 1–6 veh/min。
- `paper-supported:` 无人机选型及比例：Mavic Air 2、Inspire 2、M300 RTK，比例为 3:5:2；最大横滚角 45°。
- `paper-supported:` 关键仿真参数：航路宽度 4 m；20% 无人机在交叉口换层；交叉口范围半径 50 m；沿路型通过速度 6 m/s；环形角速度 15°/s；电梯高度 30 m；上升速度 4 m/s，下降速度 3 m/s；环道半径 25 m。

### 安全分析结果
- `paper-supported:` 沿路型冲突风险密集区主要分布在航路交叉区，并沿航路向外延伸；电梯和一般航路段风险较低（Figure 15）。
- `paper-supported:` 环形冲突风险密集区主要分布在环道、环道与航路连接处、以及电梯与环道连接处（Figure 16）。
- `paper-supported:` 回归分析显示：无人机数量与冲突风险正相关，航路数量越多相关性越强（Table 3）。
- `paper-supported:` 两路交叉口：沿路型平均风险 0.02%，环形 0.05%；三路：沿路型 0.06%，环形 0.07%；四路：沿路型 0.36%，环形 0.11%。四路时沿路型平均风险显著高于环形。

### 效率分析结果
- `paper-supported:` 到达率 1 veh/min 的两路交叉口：沿路型平均通过时间（17.39 s）比环形（19.48 s）快约 2 s；三路、四路在到达率 1–3 veh/min 时沿路型效率亦优于环形（Table 4）。
- `paper-supported:` 四路交叉口到达率 6 veh/min 时：沿路型平均通过时间（44.13 s）比环形（26.79 s）慢约 17 s；与 1 veh/min 相比，沿路型通过时间增加 87%，环形仅增加 18%。
- `paper-supported:` 沿路型属于单通道模式，随着到达率增加易产生拥堵并向外蔓延；环形通过旋转座椅隔离各航路冲突点，不同航路无人机可同时进入形成渠化交通。

### 随机性与容量分析结果
- `paper-supported:` 沿路型通过时间主要集中在 15–20 s，环形主要集中在 20–25 s（Figure 17）。
- `paper-supported:` 随机到达条件下，航路数量与通过时间正相关、与通过率负相关（Table 5）。
- `paper-supported:` 在 450 s 时间窗口内，向每条航路发送 30 架无人机：两路/三路/四路沿路型与环形的最大容纳无人机数量接近，且与航路数量正相关；但三路、四路沿路型无法满足全部交通需求，而环形基本可以（Figure 18）。

## 图表与可视证据

- `paper-supported:` Figure 1：无人机低空空域运行示意图（分层不同高度、不同颜色箭头表示不同飞行方向）。
- `paper-supported:` Figure 2：无人机球形保护区示意图（球体、俯视图、前视图）。
- `paper-supported:` Figure 3：航路段微观构型（俯视图、横截面图）。
- `paper-supported:` Figure 4：航迹交叉类型对比（自由型、沿路型、环型）。
- `paper-supported:` Figure 5：沿路型交叉口运行模式（含电梯、上升/下降航线）。
- `paper-supported:` Figure 6：交叉航路俯视图（交叉角、辅助角、交叉区域范围）。
- `paper-supported:` Figure 7：电梯示意图。
- `paper-supported:` Figure 8：沿路型交叉口飞行路线（同层转弯、不同层转弯、飞出）。
- `paper-supported:` Figure 9：环形运行模式（旋转座椅、电梯、出入方向）。
- `paper-supported:` Figure 10：环形特征参数（航路交叉角、环道半径）。
- `paper-supported:` Figure 11：环形旋转座椅示意图。
- `paper-supported:` Figure 12：无人机飞入环形过程（t0–t2 时刻状态）。
- `paper-supported:` Figure 13：无人机在双层环形交叉口改变飞行层过程（UAV A 下降、UAV B 上升）。
- `paper-supported:` Figure 14：无人机飞出环形过程。
- `paper-supported:` Figure 15：沿路型交叉口冲突风险分布（两路、三路、四路）。
- `paper-supported:` Figure 16：环形交叉口冲突风险分布（两路、三路、四路）。
- `paper-supported:` Figure 17：交叉口通过时间分布箱线图（红框标注大部分无人机通过时间范围）。
- `paper-supported:` Figure 18：不同类型交叉口交通容量曲线（0–450 s 内交叉口内无人机数量变化）。

## 局限性

- `paper-supported:` 论文明确指出：研究主要针对多旋翼无人机及标准化参数配置，未来需进一步研究航线结构与无人机之间的适应性与协调性。
- `paper-supported:` 论文指出：无人机速度对飞行性能及交叉口运行情况影响显著，当前未区分高速航线与普通航线设计。
- `paper-supported:` 论文指出：需进一步探讨无人机类型对航线构型的影响，并将航线设计扩展至固定翼无人机。
- `paper-supported:` 实验采用仿真验证，尚未在真实城市低空空域或实体无人机集群中进行实测。
- `unsupported:` PDF 中未提供开源代码、仿真平台名称或数据集链接。

## 与低空研究的关联

- `inferred:` 直接关联城市空中交通（UAM）基础设施设计，为低空航路网络的“微观构型”提供可量化的交叉口方案比选依据。
- `inferred:` 其分层单向空域、航路宽度/保护区/缓冲区等参数设定，可支撑低空飞行规则、空域划设标准及无人机交通管理（UTM）系统的策略制定。
- `inferred:` 冲突概率模型与服务水平指标可作为低空交通流仿真与空域容量评估的参考基准。

## 可复用参数 / 模型 / 基线

- `paper-supported:` 无人机保护区球体直径公式：\(D=\sqrt{d^2+h^2}\)。
- `paper-supported:` 最小转弯半径公式：\(r_{min}=\frac{v^2}{g\tan\phi_{max}}\)。
- `paper-supported:` 沿路型交叉区域最大转弯半径公式：\(r_{max}=\frac{w}{1-\cos\tau}\)。
- `paper-supported:` 电梯最大容量公式：\(C = 1 + \frac{H-2D-4b}{S_v}\)。
- `paper-supported:` 环形最小半径（均匀分布）：\(R_{min}=\frac{S_l}{2\sin(\pi/2m)}\)。
- `paper-supported:` 旋转座椅中心角公式：\(\theta_s = \cos^{-1}(1-\frac{S_l^2}{2R^2})\)。
- `paper-supported:` 冲突概率计算模型：基于三维高斯分布的纵向/横向/垂向误差乘积模型。
- `paper-supported:` 服务水平指标：交叉口通过率、平均通过时间。
- `paper-supported:` 仿真实验基线参数：高度层 60–90 m、航路宽度 4 m、沿路型速度 6 m/s、环形角速度 15°/s、电梯高度 30 m、上升/下降速度 4/3 m/s、环道半径 25 m、交叉口范围半径 50 m。
- `paper-supported:` 无人机安全间隔矩阵（Table 2）：涵盖 Mavic Air 2、Inspire 2、M300 RTK 之间的垂直与水平安全间隔（例如 Mavic Air 2 与 Inspire 2 之间垂直 2 m、水平 15 m）。

## 后续动作

- `proposal:` 继续阅读：跟踪作者团队（Li, Zhang, Liu 等）在无人机航线网络规划、低空空域安全间隔方面的后续研究。
- `proposal:` 核验参数：核实论文中无人机性能参数（Mavic Air 2、Inspire 2、M300 RTK 的轴距、高度、最大速度）与 DJI 官方 specs 的一致性。
- `proposal:` 补充 metadata：查找该研究是否依托特定仿真平台（如 MATLAB、Python、AirSim、NASA ATC 仿真框架）及是否有开源代码或数据补充页。
- `proposal:` 查找政策/标准/产业背景：对照中国《无人驾驶航空器飞行管理暂行条例》、民航局低空航路划设相关咨询通告，评估论文中“沿路型/环形”交叉口概念在法规与工程实践中的可落地性。
- `proposal:` 查找对比文献：检索同期或近期关于城市无人机“sky corridor / sky tube / sky lane”及“vertiport 进近航线”设计的文献，进行方案交叉对比。

## 可靠性说明

- `paper-supported:` 本笔记基于对 PDF 全文的自动解析与提取，信息直接来源于论文文本、公式、表格与图表说明。
- `inferred:` 笔记中的“收录原因”“与低空研究的关联”部分基于论文主题与低空经济/低空管理领域的映射关系推断得出，非论文原文直接陈述。
- `unsupported:` PDF 中未提供仿真源代码、底层仿真平台名称、原始轨迹数据集或实验复现指引。
- `unsupported:` PDF 中未提供该研究与真实城市空域运行数据或实际飞行试验的对比验证。

<!-- item_reading_metadata
{
  "item_id": "44e099e11b56",
  "reading_model": "kimi-k2.6",
  "reading_provider": "kimi",
  "read_at": "2026-05-31T05:21:53+00:00",
  "pdf_fingerprint": "18a0532d9bf253cfb471c98cee7c1fa5957932324eac336f745e689084bd1074",
  "pdf_source": "literature\\inbox\\papers\\2024-Drones-Air Route Design of Multi-Rotor UAVs for Urban Air Mobility-44e099e11b56.pdf",
  "reading_status": "model_parsed_pdf",
  "human_reviewed": false
}
-->
