# 红色传播导航仪表盘

基于272份革命老区青少年红色文化触达率调研数据，提供**现状诊断**与**规划导航**两大视角的数据可视化仪表盘。

## 项目描述

- **数据来源**：《数链红星·星火篇》革命老区青少年红色文化触达率调研（2025）
- **样本量**：272份有效问卷
- **功能模块**：
  - 🔴 **现状诊断**：总览看板、青少年触达分析、传播痛点诊断、内容改进方向、区域对比
  - 🎯 **规划导航**：核心KPI对比、触达率提升路径、痛点改善路线图、行动计划甘特图、资源投入建议

## 运行方式

### 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Community Cloud 部署

1. 在 GitHub 创建新仓库，上传以下文件：
   - `app.py`
   - `data.xlsx`
   - `requirements.txt`
   - `.streamlit/config.toml`
2. 登录 [share.streamlit.io](https://share.streamlit.io)
3. 点击 **"New app"**，选择刚创建的仓库
4. 主文件设置为 `app.py`
5. 点击 **Deploy**

## 技术栈

- **前端**：Streamlit + Plotly
- **数据处理**：Pandas
- **主题**：暗红主题（深红 `#B71C1C` / 暗红黑 `#1A0A0A`）
