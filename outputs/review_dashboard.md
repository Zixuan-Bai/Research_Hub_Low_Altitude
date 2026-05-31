# 研究情报复核面板

> 机器生成的轻量 review 面板。常规使用时优先看这里或 Streamlit，不需要直接维护内部文件。

## 建议操作

- 人工状态 `review_status`：`new` / `kept` / `downloaded` / `rejected`，由你在 GUI 中修改。
- 流程状态 `process_status`：`unread` / `read` / `summarized` / `used_in_synthesis`，通常由脚本自动维护。
- 元数据状态 `metadata_status`：`auto` / `needs_review` / `verified`，GUI 保存 metadata 后会标记为 `verified`。

## 按人工状态

### new

暂无。

### kept

暂无。

### downloaded

- **Use of LoRa for UAV Remote ID with Multi-User Interference and Different Spreading Factors** [openalex](https://openalex.org/W3170762244)；主题：`remote_id_broadcast_capacity`；相关性：5；权威性：4；review_status：`downloaded`；process_status：`summarized`；metadata_status：`auto`
- **Remote ID-Based UAV Supervision System** [crossref](https://doi.org/10.1109/icicc66840.2025.11199528)；主题：`remote_id_broadcast_capacity`；相关性：2；权威性：4；review_status：`downloaded`；process_status：`unread`；metadata_status：`auto`
- **Reducing safe UAV separation distances with U2U communication and new Remote ID formats** [crossref](https://doi.org/10.1109/gcwkshps56602.2022.10008607)；主题：`remote_id_broadcast_capacity`；相关性：2；权威性：4；review_status：`downloaded`；process_status：`summarized`；metadata_status：`auto`
- **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)** [openalex](https://openalex.org/W2981262669)；主题：`remote_id_broadcast_capacity`；相关性：2；权威性：1；review_status：`downloaded`；process_status：`unread`；metadata_status：`auto`

### rejected

暂无。

## 按流程状态

### unread

- **Remote ID-Based UAV Supervision System** [crossref](https://doi.org/10.1109/icicc66840.2025.11199528)；主题：`remote_id_broadcast_capacity`；相关性：2；权威性：4；review_status：`downloaded`；process_status：`unread`；metadata_status：`auto`
- **Experiments with a LoRaWAN-Based Remote ID System for Locating Unmanned Aerial Vehicles (UAVs)** [openalex](https://openalex.org/W2981262669)；主题：`remote_id_broadcast_capacity`；相关性：2；权威性：1；review_status：`downloaded`；process_status：`unread`；metadata_status：`auto`

### read

暂无。

### summarized

- **Use of LoRa for UAV Remote ID with Multi-User Interference and Different Spreading Factors** [openalex](https://openalex.org/W3170762244)；主题：`remote_id_broadcast_capacity`；相关性：5；权威性：4；review_status：`downloaded`；process_status：`summarized`；metadata_status：`auto`
- **Reducing safe UAV separation distances with U2U communication and new Remote ID formats** [crossref](https://doi.org/10.1109/gcwkshps56602.2022.10008607)；主题：`remote_id_broadcast_capacity`；相关性：2；权威性：4；review_status：`downloaded`；process_status：`summarized`；metadata_status：`auto`

### used_in_synthesis

暂无。
