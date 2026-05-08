#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红色传播导航仪表盘 — 云端版
基于《数链红星·星火篇》革命老区青少年红色文化触达率调研（2025）
合并"现状诊断"与"规划导航"两大模块，通过侧边栏切换
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# ────────────────── 页面配置 ──────────────────
st.set_page_config(
    page_title="红色传播导航仪表盘",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────── 红色主题色板（明亮版）──────────────────
C_PRIMARY = "#B71C1C"       # 深红
C_DARK = "#8B0000"          # 暗红（用于标题/强调）
C_ACCENT = "#DC143C"        # 赤红
C_BG = "#F5F0F0"            # 浅灰白背景
C_CARD = "#FFFFFF"          # 白色卡片
C_TEXT = "#333333"          # 深灰文字
C_WHITE = "#FFFFFF"
C_GOLD = "#FFD54F"          # 金色点缀

# ────────────────── 全局 CSS ──────────────────
st.markdown(f"""
<style>
    /* 全局 */
    .stApp {{ background-color: {C_BG}; color: {C_TEXT}; }}
    section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #8B0000 0%, #B71C1C 100%); }}
    section[data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}
    h1, h2, h3, h4 {{ color: {C_DARK} !important; }}
    .stMetric {{ background-color: {C_CARD}; border-radius: 12px; padding: 18px 22px;
                 border-left: 4px solid {C_ACCENT}; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
    .stMetric > div > label {{ color: #666666 !important; font-size: 0.95rem; }}
    .stMetric > div > div {{ color: {C_DARK} !important; font-size: 2rem; font-weight: 700; }}
    /* 表格 */
    .stDataFrame {{ background-color: {C_CARD}; }}
    /* 隐藏默认页脚 */
    footer {{ visibility: hidden; }}

    /* 规划版专用样式 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');

    .main-title {{
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        color: #8B0000;
        font-size: 2.4rem;
        font-weight: 900;
        font-family: 'Noto Sans SC', sans-serif;
        letter-spacing: 4px;
    }}
    .sub-title {{
        text-align: center;
        color: #666666;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        font-family: 'Noto Sans SC', sans-serif;
    }}

    /* KPI大数字卡片 */
    .kpi-card {{
        background: #FFFFFF;
        border: 1px solid #FFCDD2;
        border-left: 4px solid #DC143C;
        border-radius: 16px;
        padding: 1.5rem 1rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(220,20,60,0.12);
    }}
    .kpi-label {{
        color: #666666;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.6rem;
        letter-spacing: 1px;
    }}
    .kpi-current {{
        font-size: 2.2rem;
        font-weight: 900;
        color: #DC143C;
        font-family: 'Noto Sans SC', sans-serif;
    }}
    .kpi-arrow {{
        font-size: 1.4rem;
        color: #B71C1C;
        margin: 0 0.3rem;
    }}
    .kpi-target {{
        font-size: 2.2rem;
        font-weight: 900;
        color: #2E7D32;
        font-family: 'Noto Sans SC', sans-serif;
    }}
    .kpi-gap {{
        color: #B71C1C;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-weight: 600;
    }}

    /* 区块标题 */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #FFCDD2;
    }}
    .section-icon {{
        font-size: 1.5rem;
    }}
    .section-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: #B71C1C;
        font-family: 'Noto Sans SC', sans-serif;
        letter-spacing: 2px;
    }}

    /* 信息卡片 */
    .info-card {{
        background: #FFFFFF;
        border: 1px solid #FFCDD2;
        border-left: 4px solid #DC143C;
        padding: 1rem 1.2rem;
        border-radius: 0 12px 12px 0;
        margin: 0.5rem 0;
        color: #333333;
        font-size: 0.9rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }}

    /* 甘特图相关 */
    .gantt-done {{
        background: linear-gradient(90deg, #4CAF50, #66BB6A);
        color: white;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
    }}
    .gantt-progress {{
        background: linear-gradient(90deg, #FF8C00, #FFA500);
        color: white;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
    }}
    .gantt-plan {{
        background: linear-gradient(90deg, #DC143C, #E53935);
        color: white;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
    }}

    /* 数据来源标签 */
    .data-source {{
        color: #888888;
        font-size: 0.75rem;
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid #FFCDD2;
    }}
</style>
""", unsafe_allow_html=True)

# ────────────────── 加载数据 ──────────────────
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.xlsx")
    df = pd.read_excel(path)
    return df

df = load_data()
total_n = len(df)

# ────────────────── 通用列名映射 ──────────────────
COL_AGE = df.columns[3]
COL_REGION = df.columns[4]
COL_CHANNEL = df.columns[8]
COL_HISTORY1 = df.columns[10]   # 血战高台
COL_HISTORY2 = df.columns[11]   # 梨园口突围
COL_HISTORY3 = df.columns[12]   # 妇女独立团阻击战
COL_WATCH = df.columns[13]      # 是否看过血色高台
COL_FEELING = df.columns[15]    # 观看感受
COL_PREACH = df.columns[17]     # 说教感太强
COL_OLD = df.columns[18]        # 形式老旧
COL_INTERACT = df.columns[19]   # 缺少互动
COL_VIDEO = df.columns[20]      # 是否参与视频创作
COL_DEVICE = df.columns[21]     # 创作设备
COL_WILLING = df.columns[25]    # 扫码答题意愿
COL_AVATAR = df.columns[26]     # 虚拟主播形象
COL_EQUIP = df.columns[28]      # 需要的创作设备支持

# 计算派生字段
df["史实认知均分"] = (df[COL_HISTORY1] + df[COL_HISTORY2] + df[COL_HISTORY3]) / 3

# ────────────────── Plotly 通用布局（现状诊断版）──────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(color="#333333", family="Microsoft YaHei, SimHei, sans-serif"),
    margin=dict(l=40, r=30, t=50, b=40),
)

def _fig(fig):
    """统一风格并返回"""
    fig.update_layout(**PLOT_LAYOUT)
    return fig

# ────────────────── Plotly 通用布局（规划版）──────────────────
COLOR_BASELINE = "#DC143C"    # 现状-赤红
COLOR_TARGET = "#4CAF50"      # 目标-绿色
COLOR_GAP = "#B71C1C"         # 差距-深红
COLOR_BG2 = "#FFFFFF"         # 白色背景
COLOR_GRID = "#E8E8E8"        # 浅灰网格线
COLOR_TEXT2 = "#333333"        # 深色文字

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Noto Sans SC, sans-serif", color="#333333", size=12),
    legend=dict(bgcolor="rgba(255,255,255,0.9)", font=dict(color="#333333")),
    margin=dict(l=50, r=30, t=50, b=50),
)

def _merge_layout(extra=None):
    """合并基础布局与额外参数，避免 yaxis/xaxis 重复传入报错"""
    base = dict(PLOTLY_LAYOUT)
    if extra:
        base.update(extra)
    base.setdefault("xaxis", dict(gridcolor=COLOR_GRID, linecolor=COLOR_GRID))
    base.setdefault("yaxis", dict(gridcolor=COLOR_GRID, linecolor=COLOR_GRID))
    return base

# ────────────────── 规划版：从真实数据计算基线值 ──────────────────
youth_pct = (df[COL_AGE] == "16-22岁").sum() / total_n * 100
watch_pct = (df[COL_WATCH] == "是").sum() / total_n * 100

score_gaotai = df[COL_HISTORY1].mean()
score_liyuan = df[COL_HISTORY2].mean()
score_funv = df[COL_HISTORY3].mean()
avg_knowledge = round((score_gaotai + score_liyuan + score_funv) / 3, 1)

preach_score = df[COL_PREACH].mean()
old_form_score = df[COL_OLD].mean()
no_interact_score = df[COL_INTERACT].mean()

satisfaction = 10 - preach_score
create_pct = (df[COL_VIDEO] == "是").sum() / total_n * 100
scan_willing = df[COL_WILLING].mean()
anchor_pref = df[COL_AVATAR].value_counts()
channels = df[COL_CHANNEL].dropna().str.split(",").explode().value_counts()
equip_need = df[COL_EQUIP].dropna().str.split(",").explode().value_counts()

# 目标值设定
target_watch = 65.0
target_knowledge = 7.0
target_satisfaction = 6.5
target_create = 45.0
target_preach = 3.5
target_old_form = 3.5
target_no_interact = 3.0
target_scan = 8.5

# ══════════════════════════════════════════════
#            侧 边 栏 导 航
# ══════════════════════════════════════════════
page = st.sidebar.radio(
    "📌 页面切换",
    ["现状诊断", "规划导航"],
    index=0,
    help="选择要查看的仪表盘页面"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 数据概览")
st.sidebar.markdown(f"- **总样本量**: {total_n}")
st.sidebar.markdown(f"- **16-22岁占比**: {youth_pct:.1f}%")
st.sidebar.markdown(f"- **看过《血色高台》**: {watch_pct:.1f}%")
st.sidebar.markdown(f"- **史实认知均分**: {avg_knowledge}/10")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 数据来源")
st.sidebar.markdown(
    "《数链红星·星火篇》<br>"
    "革命老区青少年红色文化<br>触达率调研（2025）",
    unsafe_allow_html=True
)


# ══════════════════════════════════════════════
#         页面一：现 状 诊 断
# ══════════════════════════════════════════════
if page == "现状诊断":

    # 标题
    st.markdown(f"""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <h1 style="color:#8B0000; font-size:2.6rem; margin-bottom:2px;">🔴 红色传播导航仪表盘 · 现状诊断</h1>
        <p style="color:#666666; font-size:1rem;">《数链红星·星火篇》革命老区青少年红色文化触达率调研 · 2025</p>
    </div>
    <hr style="border:1px solid #FFCDD2;"/>
    """, unsafe_allow_html=True)

    # ───────── 1. 总览看板 ─────────
    st.markdown("## 📊 总览看板")

    youth_df = df[df[COL_AGE] == "16-22岁"]
    youth_reach = len(youth_df[youth_df[COL_WATCH] == "是"]) / len(youth_df) * 100 if len(youth_df) else 0
    avg_history = df["史实认知均分"].mean()
    video_rate = len(df[df[COL_VIDEO] == "是"]) / total_n * 100
    avg_willing = df[COL_WILLING].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("总样本量", f"{total_n}")
    with col2:
        st.metric("青少年触达率", f"{youth_reach:.1f}%", help="16-22岁看过《血色高台》的比例")
    with col3:
        st.metric("平均史实认知分", f"{avg_history:.2f}", help="血战高台/梨园口突围/妇女独立团阻击战均分，满分10")
    with col4:
        st.metric("视频创作参与率", f"{video_rate:.1f}%")
    with col5:
        st.metric("互动意愿均值", f"{avg_willing:.2f}", help="扫码答题兑换勋章意愿，满分10")

    st.markdown("<br>", unsafe_allow_html=True)

    # ───────── 2. 青少年触达分析 ─────────
    st.markdown("---")
    st.markdown("## 🎯 青少年触达分析")

    col_a, col_b = st.columns(2)

    # 年龄分布饼图
    with col_a:
        age_counts = df[COL_AGE].value_counts()
        fig_age = px.pie(
            values=age_counts.values,
            names=age_counts.index,
            title="年龄分布",
            color_discrete_sequence=[C_ACCENT, C_DARK, "#E57373", "#FF8A80"],
            hole=0.45,
        )
        fig_age.update_traces(textfont_color="#333333", textinfo="percent+label")
        st.plotly_chart(_fig(fig_age), use_container_width=True)

    # 是否看过《血色高台》按年龄段
    with col_b:
        cross = pd.crosstab(df[COL_AGE], df[COL_WATCH])
        for c in ["是", "否"]:
            if c not in cross.columns:
                cross[c] = 0
        age_order = ["16岁以下", "16-22岁", "23-35岁", "35岁以上"]
        cross = cross.reindex(age_order)
        fig_watch = go.Figure()
        fig_watch.add_trace(go.Bar(
            x=age_order, y=cross["是"], name="看过",
            marker_color=C_ACCENT,
        ))
        fig_watch.add_trace(go.Bar(
            x=age_order, y=cross["否"], name="未看过",
            marker_color="#8D6E63",
        ))
        fig_watch.update_layout(
            title="是否看过《血色高台》（按年龄段）",
            barmode="group",
            xaxis_title="年龄段", yaxis_title="人数",
        )
        st.plotly_chart(_fig(fig_watch), use_container_width=True)

    # 信息获取渠道排名
    st.markdown("#### 信息获取渠道排名")
    channel_series = df[COL_CHANNEL].dropna()
    all_channels = []
    for c in channel_series:
        all_channels.extend([p.strip() for p in str(c).split(",")])
    ch_counts = Counter(all_channels)
    ch_df = pd.DataFrame(ch_counts.most_common(), columns=["渠道", "人次"]).sort_values("人次")

    fig_ch = px.bar(
        ch_df, x="人次", y="渠道", orientation="h",
        title="信息获取渠道排名（多选）",
        color="人次", color_continuous_scale=["#FFCDD2", C_ACCENT],
    )
    fig_ch.update_layout(coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=13)))
    st.plotly_chart(_fig(fig_ch), use_container_width=True)

    # 观看感受分布
    st.markdown("#### 观看感受分布")
    feeling_series = df[COL_FEELING].dropna()
    all_feelings = []
    for f in feeling_series:
        all_feelings.extend([p.strip() for p in str(f).split(",")])
    fe_counts = Counter(all_feelings)
    fe_df = pd.DataFrame(fe_counts.most_common(), columns=["感受", "人次"])

    fig_feel = px.pie(
        fe_df, values="人次", names="感受",
        title="观看感受分布（多选）",
        color_discrete_sequence=[C_ACCENT, C_GOLD, "#E57373", "#FF8A80", "#8D6E63"],
        hole=0.4,
    )
    fig_feel.update_traces(textfont_color="#333333", textinfo="percent+label")
    st.plotly_chart(_fig(fig_feel), use_container_width=True)

    # ───────── 3. 传播痛点诊断 ─────────
    st.markdown("---")
    st.markdown("## 🔍 传播痛点诊断")

    pain_cols = {
        "说教感太强": COL_PREACH,
        "形式老旧": COL_OLD,
        "缺少互动": COL_INTERACT,
    }

    col_p1, col_p2, col_p3 = st.columns(3)

    for idx, (label, col_name) in enumerate(pain_cols.items()):
        target_col = [col_p1, col_p2, col_p3][idx]
        with target_col:
            series = df[col_name].dropna()
            fig_hist = px.histogram(
                series, x=series.values,
                title=f'"{label}"评分分布',
                nbins=10, range_x=[0, 10],
                color_discrete_sequence=[C_ACCENT],
            )
            fig_hist.update_layout(
                xaxis_title="评分", yaxis_title="人数",
                bargap=0.15,
            )
            st.plotly_chart(_fig(fig_hist), use_container_width=True)

    # 三个维度均值对比雷达图
    st.markdown("#### 痛点维度均值对比")
    pain_means = {label: df[col_name].mean() for label, col_name in pain_cols.items()}

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=list(pain_means.values()),
        theta=list(pain_means.keys()),
        fill="toself",
        fillcolor="rgba(220, 20, 60, 0.2)",
        line=dict(color=C_ACCENT, width=2),
        marker=dict(color=C_ACCENT, size=8),
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color="#666666")),
            bgcolor="#FFFFFF",
            angularaxis=dict(tickfont=dict(color="#333333", size=14)),
        ),
        title="传播痛点均值雷达图（满分10）",
    )
    st.plotly_chart(_fig(fig_radar), use_container_width=True)

    # ───────── 4. 内容改进方向 ─────────
    st.markdown("---")
    st.markdown("## 💡 内容改进方向")

    col_i1, col_i2 = st.columns(2)

    # 虚拟主播形象偏好
    with col_i1:
        avatar_counts = df[COL_AVATAR].value_counts()
        fig_avatar = px.bar(
            x=avatar_counts.index, y=avatar_counts.values,
            title='"红小西"虚拟主播形象偏好',
            color=avatar_counts.values,
            color_continuous_scale=["#FFCDD2", C_ACCENT],
        )
        fig_avatar.update_layout(
            xaxis_title="形象类型", yaxis_title="人数",
            coloraxis_showscale=False,
        )
        st.plotly_chart(_fig(fig_avatar), use_container_width=True)

    # 创作设备需求
    with col_i2:
        equip_series = df[COL_EQUIP].dropna()
        all_equips = []
        for e in equip_series:
            all_equips.extend([p.strip() for p in str(e).split(",")])
        eq_counts = Counter(all_equips)
        eq_df = pd.DataFrame(eq_counts.most_common(), columns=["设备", "人次"]).sort_values("人次")

        fig_equip = px.bar(
            eq_df, x="人次", y="设备", orientation="h",
            title="创作设备需求（多选）",
            color="人次", color_continuous_scale=["#FFCDD2", C_GOLD],
        )
        fig_equip.update_layout(coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=13)))
        st.plotly_chart(_fig(fig_equip), use_container_width=True)

    # 扫码答题参与意愿分布
    st.markdown("#### 扫码答题参与意愿分布")
    willing_series = df[COL_WILLING]
    fig_willing = px.histogram(
        willing_series, x=willing_series.values,
        title="扫码答题兑换勋章参与意愿",
        nbins=10, range_x=[0, 10],
        color_discrete_sequence=[C_GOLD],
    )
    fig_willing.update_layout(
        xaxis_title="意愿评分", yaxis_title="人数",
        bargap=0.15,
    )
    st.plotly_chart(_fig(fig_willing), use_container_width=True)

    # ───────── 5. 区域对比 ─────────
    st.markdown("---")
    st.markdown("## 🌍 区域对比")

    col_r1, col_r2 = st.columns(2)

    # 区域史实认知对比
    with col_r1:
        region_history = df.groupby(COL_REGION)["史实认知均分"].mean().reindex(["城市", "县城", "乡村"])
        fig_rh = px.bar(
            x=region_history.index, y=region_history.values,
            title="城市/县城/乡村 史实认知均分对比",
            color=region_history.values,
            color_continuous_scale=["#FFCDD2", C_ACCENT],
        )
        fig_rh.update_layout(
            xaxis_title="区域", yaxis_title="认知均分（满分10）",
            coloraxis_showscale=False,
            yaxis=dict(range=[0, 10]),
        )
        st.plotly_chart(_fig(fig_rh), use_container_width=True)

    # 区域信息渠道差异（分组柱状图）
    with col_r2:
        channel_names = ["抖音/快手等短视频平台", "学校课程/学校组织", "微信公众号/朋友圈",
                         "纪念馆实地参观", "B站/小红书/贴吧等社区"]
        region_list = ["城市", "县城", "乡村"]
        data_rows = []
        for region in region_list:
            sub = df[df[COL_REGION] == region]
            ch_series = sub[COL_CHANNEL].dropna()
            ch_list = []
            for c in ch_series:
                ch_list.extend([p.strip() for p in str(c).split(",")])
            ch_cnt = Counter(ch_list)
            n = len(sub)
            for ch in channel_names:
                data_rows.append({"区域": region, "渠道": ch, "占比(%)": ch_cnt.get(ch, 0) / n * 100})
        ch_region_df = pd.DataFrame(data_rows)

        fig_cr = px.bar(
            ch_region_df, x="渠道", y="占比(%)", color="区域",
            barmode="group",
            title="城市/县城/乡村 信息渠道差异",
            color_discrete_map={"城市": C_ACCENT, "县城": C_GOLD, "乡村": "#8D6E63"},
        )
        fig_cr.update_layout(xaxis_tickangle=-25)
        st.plotly_chart(_fig(fig_cr), use_container_width=True)

    # 页脚
    st.markdown(f"""
    <hr style="border:1px solid #FFCDD2;"/>
    <div style="text-align:center; color:#888888; font-size:0.85rem; padding:10px 0;">
        数据来源：《数链红星·星火篇》革命老区青少年红色文化触达率调研（2025） · 样本量 {total_n}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#         页面二：规 划 导 航
# ══════════════════════════════════════════════
elif page == "规划导航":

    # 页面标题
    st.markdown('<div class="main-title">🎯 红色传播导航仪表盘（规划版）</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">从数据诊断到行动规划 — 基于革命老区青少年红色文化触达率调研（2025）| 总样本量 N={} | 16-22岁占{:.1f}%</div>'.format(
            total_n, youth_pct
        ),
        unsafe_allow_html=True
    )

    # ───────── 模块1: 总览看板 - 核心KPI对比 ─────────
    st.markdown(
        '<div class="section-header"><span class="section-icon">📋</span>'
        '<span class="section-title">总览看板 · 核心KPI对比</span></div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    kpi_data = [
        {
            "label": "青少年触达率",
            "current": f"{watch_pct:.1f}%",
            "target": f"{target_watch:.0f}%",
            "gap": f"+{target_watch - watch_pct:.1f}pp",
            "icon": "📺"
        },
        {
            "label": "史实认知分",
            "current": f"{avg_knowledge}",
            "target": f"{target_knowledge}",
            "gap": f"+{target_knowledge - avg_knowledge:.1f}",
            "icon": "📖"
        },
        {
            "label": "内容满意度",
            "current": f"{satisfaction:.1f}",
            "target": f"{target_satisfaction}",
            "gap": f"+{target_satisfaction - satisfaction:.1f}",
            "icon": "👍"
        },
        {
            "label": "创作参与率",
            "current": f"{create_pct:.1f}%",
            "target": f"{target_create:.0f}%",
            "gap": f"+{target_create - create_pct:.1f}pp",
            "icon": "🎬"
        },
    ]

    for i, (col, kpi) in enumerate(zip([col1, col2, col3, col4], kpi_data)):
        with col:
            st.markdown(
                f'''
                <div class="kpi-card">
                    <div class="kpi-label">{kpi["icon"]} {kpi["label"]}</div>
                    <div>
                        <span class="kpi-current">{kpi["current"]}</span>
                        <span class="kpi-arrow">→</span>
                        <span class="kpi-target">{kpi["target"]}</span>
                    </div>
                    <div class="kpi-gap">差距 {kpi["gap"]}</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

    # 进度条
    st.markdown("#### 达成进度")
    progress_data = [
        ("青少年触达率", watch_pct, target_watch, "%"),
        ("史实认知分", avg_knowledge, target_knowledge, "分"),
        ("内容满意度", satisfaction, target_satisfaction, "分"),
        ("创作参与率", create_pct, target_create, "%"),
    ]

    for name, current, target, unit in progress_data:
        progress = min(current / target, 1.0)
        st.markdown(
            f"**{name}**: {current:.1f}{unit} / {target}{unit} "
            f"（达成 {progress*100:.0f}%）"
        )
        st.progress(progress)

    st.markdown("---")

    # ───────── 模块2: 触达率提升路径 ─────────
    st.markdown(
        '<div class="section-header"><span class="section-icon">🚀</span>'
        '<span class="section-title">触达率提升路径</span></div>',
        unsafe_allow_html=True
    )

    # 渠道数据（从问卷提取）
    channel_names_plan = [
        "抖音/快手", "学校课程", "微信公众号", "纪念馆实地",
        "B站/小红书等", "其他", "从未接触"
    ]
    channel_baseline_pcts = [
        channels.get("抖音/快手等短视频平台", 0) / total_n * 100,
        channels.get("学校课程/学校组织", 0) / total_n * 100,
        channels.get("微信公众号/朋友圈", 0) / total_n * 100,
        channels.get("纪念馆实地参观", 0) / total_n * 100,
        channels.get("B站/小红书/贴吧等社区", 0) / total_n * 100,
        channels.get("其他", 0) / total_n * 100,
        channels.get("从未接触", 0) / total_n * 100,
    ]

    # 目标：核心渠道提升幅度
    channel_targets = [
        channel_baseline_pcts[0] + 8,
        channel_baseline_pcts[1] + 3,
        channel_baseline_pcts[2] + 5,
        channel_baseline_pcts[3] + 2,
        channel_baseline_pcts[4] + 7,
        channel_baseline_pcts[5] + 1,
        max(channel_baseline_pcts[6] - 5, 0),
    ]

    fig_channel = go.Figure()

    fig_channel.add_trace(go.Bar(
        name="基线现状",
        x=channel_names_plan,
        y=channel_baseline_pcts,
        marker_color=COLOR_BASELINE,
        marker_line=dict(color="#8B0000", width=1),
        text=[f"{v:.1f}%" for v in channel_baseline_pcts],
        textposition="outside",
        textfont=dict(color=COLOR_BASELINE, size=11),
        hovertemplate="%{x}<br>基线: %{y:.1f}%<extra></extra>",
    ))

    fig_channel.add_trace(go.Bar(
        name="目标值",
        x=channel_names_plan,
        y=channel_targets,
        marker_color=COLOR_TARGET,
        marker_line=dict(color="#2E7D32", width=1),
        text=[f"{v:.1f}%" for v in channel_targets],
        textposition="outside",
        textfont=dict(color=COLOR_TARGET, size=11),
        hovertemplate="%{x}<br>目标: %{y:.1f}%<extra></extra>",
    ))

    for i, (base, target) in enumerate(zip(channel_baseline_pcts, channel_targets)):
        diff = target - base
        if abs(diff) > 0.1:
            fig_channel.add_annotation(
                x=channel_names_plan[i],
                y=max(base, target) + 3,
                text=f"{'+' if diff > 0 else ''}{diff:.1f}pp",
                showarrow=False,
                font=dict(color=COLOR_GAP, size=12, family="Noto Sans SC"),
            )

    fig_channel.update_layout(
        **_merge_layout(dict(
            barmode="group",
            bargap=0.25,
            bargroupgap=0.1,
            title=dict(text="各渠道青少年触达现状 vs 目标", font=dict(color=COLOR_TEXT2, size=16)),
            yaxis=dict(title="触达率 (%)", gridcolor=COLOR_GRID, linecolor=COLOR_GRID),
            height=450,
        ))
    )

    st.plotly_chart(fig_channel, use_container_width=True)

    # 优先投入建议
    st.markdown("#### 📌 渠道优先投入建议")
    pri_col1, pri_col2, pri_col3 = st.columns(3)

    with pri_col1:
        st.markdown(
            f'''
            <div class="info-card" style="border-left-color: #DC143C;">
                <b>🔴 第一优先 · 抖音/快手</b><br>
                当前触达率: {channel_baseline_pcts[0]:.1f}% → 目标: {channel_targets[0]:.1f}%<br>
                理由: 青少年最高频渠道，短视频天然适配红色内容<br>
                行动: 投放话题挑战赛+KOL联动
            </div>
            ''',
            unsafe_allow_html=True
        )

    with pri_col2:
        st.markdown(
            f'''
            <div class="info-card" style="border-left-color: #DAA520;">
                <b>🔴 第二优先 · B站/小红书</b><br>
                当前触达率: {channel_baseline_pcts[4]:.1f}% → 目标: {channel_targets[4]:.1f}%<br>
                理由: 创作者社区属性强，适合深度内容<br>
                行动: UP主共创计划+互动H5首发
            </div>
            ''',
            unsafe_allow_html=True
        )

    with pri_col3:
        st.markdown(
            f'''
            <div class="info-card" style="border-left-color: #4CAF50;">
                <b>🟡 持续优化 · 微信公众号</b><br>
                当前触达率: {channel_baseline_pcts[2]:.1f}% → 目标: {channel_targets[2]:.1f}%<br>
                理由: 家校沟通主渠道，适合触达家长群体<br>
                行动: 公众号菜单嵌入扫码答题入口
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ───────── 模块3: 痛点改善路线图 ─────────
    st.markdown(
        '<div class="section-header"><span class="section-icon">🔧</span>'
        '<span class="section-title">痛点改善路线图</span></div>',
        unsafe_allow_html=True
    )

    pain_names = ["说教感太强", "形式老旧", "缺少互动"]
    pain_baselines = [round(preach_score, 1), round(old_form_score, 1), round(no_interact_score, 1)]
    pain_targets_list = [target_preach, target_old_form, target_no_interact]

    fig_pain = go.Figure()

    fig_pain.add_trace(go.Bar(
        name="基线现状（分数越高问题越严重）",
        x=pain_names,
        y=pain_baselines,
        marker_color=COLOR_BASELINE,
        marker_line=dict(color="#8B0000", width=1),
        text=[f"{v}" for v in pain_baselines],
        textposition="outside",
        textfont=dict(color=COLOR_BASELINE, size=13),
        width=0.35,
    ))

    fig_pain.add_trace(go.Bar(
        name="改善目标",
        x=pain_names,
        y=pain_targets_list,
        marker_color=COLOR_TARGET,
        marker_line=dict(color="#2E7D32", width=1),
        text=[f"{v}" for v in pain_targets_list],
        textposition="outside",
        textfont=dict(color=COLOR_TARGET, size=13),
        width=0.35,
    ))

    for i in range(len(pain_names)):
        diff = pain_baselines[i] - pain_targets_list[i]
        fig_pain.add_annotation(
            x=pain_names[i],
            y=max(pain_baselines[i], pain_targets_list[i]) + 0.6,
            text=f"改善 -{diff:.1f}",
            showarrow=False,
            font=dict(color=COLOR_GAP, size=13, family="Noto Sans SC"),
        )

    fig_pain.update_layout(
        **_merge_layout(dict(
            barmode="group",
            bargap=0.3,
            bargroupgap=0.15,
            title=dict(text="三大痛点 · 基线 vs 改善目标（分数越低越好）", font=dict(color=COLOR_TEXT2, size=16)),
            yaxis=dict(title="严重程度评分 (1-10)", range=[0, 8], gridcolor=COLOR_GRID, linecolor=COLOR_GRID),
            height=420,
        ))
    )

    st.plotly_chart(fig_pain, use_container_width=True)

    # 解决方案卡片
    st.markdown("#### 💡 痛点→解决方案映射")
    sol_col1, sol_col2, sol_col3 = st.columns(3)

    solutions = [
        {
            "pain": "说教感太强",
            "icon": "📢",
            "base": pain_baselines[0],
            "target": pain_targets_list[0],
            "sol": "互动H5 + 沉浸式叙事",
            "detail": "将线性说教转化为沉浸式互动体验，用户自主选择叙事路径，从被动接受变主动探索"
        },
        {
            "pain": "形式老旧",
            "icon": "📼",
            "base": pain_baselines[1],
            "target": pain_targets_list[1],
            "sol": "虚拟主播「红小西」+ 短视频化",
            "detail": "虚拟主播带来新鲜感，短视频形态适配青少年消费习惯，热血青年战士形象获48.5%偏好"
        },
        {
            "pain": "缺少互动",
            "icon": "🤝",
            "base": pain_baselines[2],
            "target": pain_targets_list[2],
            "sol": "扫码答题兑换勋章 + UGC激励",
            "detail": "扫码答题意愿7.8/10，勋章兑换机制激活参与；创作培训+设备支持提升UGC产出"
        },
    ]

    for col, sol in zip([sol_col1, sol_col2, sol_col3], solutions):
        with col:
            st.markdown(
                f'''
                <div class="info-card" style="border-left-color: #DC143C;">
                    <b>{sol["icon"]} {sol["pain"]}</b><br>
                    <span style="color:#DC143C;">{sol["base"]}</span>
                    <span style="color:#B71C1C;"> → </span>
                    <span style="color:#2E7D32;">{sol["target"]}</span><br><br>
                    <b>✅ {sol["sol"]}</b><br>
                    <span style="color:#666666; font-size:0.82rem;">{sol["detail"]}</span>
                </div>
                ''',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ───────── 模块4: 行动计划甘特图 ─────────
    st.markdown(
        '<div class="section-header"><span class="section-icon">📅</span>'
        '<span class="section-title">行动计划甘特图</span></div>',
        unsafe_allow_html=True
    )

    gantt_tasks = [
        {"task": "舆情数据采集与分析", "start": "2025-06-01", "end": "2025-06-30", "status": "done", "progress": 100},
        {"task": "互动H5开发与测试", "start": "2025-07-01", "end": "2025-07-31", "status": "progress", "progress": 30},
        {"task": "虚拟主播内容制作", "start": "2025-07-01", "end": "2025-07-31", "status": "progress", "progress": 20},
        {"task": "校园试点推广", "start": "2025-08-01", "end": "2025-08-31", "status": "plan", "progress": 0},
        {"task": "效果评估与迭代", "start": "2025-09-01", "end": "2025-09-30", "status": "plan", "progress": 0},
    ]

    status_colors = {
        "done": "#4CAF50",
        "progress": "#FF8C00",
        "plan": "#8B0000",
    }

    status_labels = {
        "done": "✅ 已完成",
        "progress": "🔄 进行中",
        "plan": "📋 计划中",
    }

    fig_gantt = go.Figure()

    for i, task in enumerate(reversed(gantt_tasks)):
        color = status_colors[task["status"]]
        label = status_labels[task["status"]]

        fig_gantt.add_trace(go.Bar(
            name=f"{task['task']} ({label})",
            orientation="h",
            y=[task["task"]],
            x=[
                (pd.Timestamp(task["end"]) - pd.Timestamp(task["start"])).days
            ],
            base=[
                (pd.Timestamp(task["start"]) - pd.Timestamp("2025-06-01")).days
            ],
            marker_color=color,
            marker_line=dict(color="rgba(183,28,28,0.3)", width=1),
            text=f"{label} ({task['progress']}%)",
            textposition="inside",
            textfont=dict(color="white", size=12),
            hovertemplate=(
                f"{task['task']}<br>"
                f"{task['start']} ~ {task['end']}<br>"
                f"状态: {label}<br>"
                f"进度: {task['progress']}%<extra></extra>"
            ),
            showlegend=False,
        ))

    fig_gantt.update_layout(
        **_merge_layout(dict(
            title=dict(text="关键行动时间线（2025年6月-9月）", font=dict(color=COLOR_TEXT2, size=16)),
            xaxis=dict(
                title="",
                tickvals=[0, 30, 61, 92, 122],
                ticktext=["6月1日", "7月1日", "8月1日", "9月1日", "10月1日"],
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
            ),
            yaxis=dict(
                autorange="reversed",
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                tickfont=dict(size=13),
            ),
            height=320,
            bargap=0.25,
        ))
    )

    st.plotly_chart(fig_gantt, use_container_width=True)

    # 甘特图状态说明
    gantt_col1, gantt_col2, gantt_col3 = st.columns(3)
    with gantt_col1:
        st.markdown('<span class="gantt-done">✅ 已完成</span> 舆情数据采集与分析（6月）', unsafe_allow_html=True)
    with gantt_col2:
        st.markdown('<span class="gantt-progress">🔄 进行中</span> 互动H5 + 虚拟主播（7月）', unsafe_allow_html=True)
    with gantt_col3:
        st.markdown('<span class="gantt-plan">📋 计划中</span> 校园试点 + 效果评估（8-9月）', unsafe_allow_html=True)

    st.markdown("---")

    # ───────── 模块5: 资源投入建议 ─────────
    st.markdown(
        '<div class="section-header"><span class="section-icon">💰</span>'
        '<span class="section-title">资源投入建议</span></div>',
        unsafe_allow_html=True
    )

    res_col1, res_col2, res_col3 = st.columns(3)

    # 设备需求
    with res_col1:
        st.markdown("#### 📱 创作设备需求")
        st.markdown(
            '<div class="info-card" style="border-left-color: #DC143C;">'
            '<b>基于问卷数据，青少年最需要的创作设备：</b></div>',
            unsafe_allow_html=True
        )

        equip_names = equip_need.index.tolist()
        equip_vals = equip_need.values.tolist()

        fig_equip_plan = go.Figure(go.Bar(
            orientation="h",
            y=equip_names,
            x=equip_vals,
            marker_color=["#DC143C", "#FF6B6B", "#FF8C00", "#FFD700", "#4CAF50"][:len(equip_names)],
            text=equip_vals,
            textposition="outside",
            textfont=dict(color=COLOR_TEXT2, size=12),
        ))
        fig_equip_plan.update_layout(
            **_merge_layout(dict(
                title=dict(text="设备需求人数", font=dict(color=COLOR_TEXT2, size=14)),
                xaxis=dict(title="人数", gridcolor=COLOR_GRID, linecolor=COLOR_GRID),
                yaxis=dict(gridcolor=COLOR_GRID, linecolor=COLOR_GRID),
                height=280,
                margin=dict(l=120, r=30, t=40, b=40),
            ))
        )
        st.plotly_chart(fig_equip_plan, use_container_width=True)

    # 平台投放
    with res_col2:
        st.markdown("#### 📊 平台投放预算建议")

        platforms = ["抖音/快手", "B站/小红书", "微信", "线下纪念馆"]
        budget_pct = [40, 25, 20, 15]
        budget_labels = ["40%", "25%", "20%", "15%"]
        budget_colors = ["#DC143C", "#FF8C00", "#DAA520", "#4CAF50"]

        fig_budget = go.Figure(go.Pie(
            labels=platforms,
            values=budget_pct,
            marker_colors=budget_colors,
            text=budget_labels,
            textposition="inside",
            textfont=dict(color="white", size=13),
            hole=0.45,
            hovertemplate="%{label}<br>预算占比: %{value}%<extra></extra>",
        ))
        fig_budget.update_layout(
            **_merge_layout(dict(
                title=dict(text="投放预算分配建议", font=dict(color=COLOR_TEXT2, size=14)),
                height=280,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(color=COLOR_TEXT2, size=11),
                ),
            ))
        )
        st.plotly_chart(fig_budget, use_container_width=True)

    # 人力配置
    with res_col3:
        st.markdown("#### 👥 人力配置建议")

        roles = [
            ("内容策划", "2人", "互动H5脚本+虚拟主播台词"),
            ("短视频运营", "2人", "抖音/B站日常运营+数据监控"),
            ("技术支持", "1人", "H5开发+扫码答题系统维护"),
            ("校园推广", "2人", "试点学校对接+活动落地"),
            ("数据分析师", "1人", "效果追踪+迭代优化"),
        ]

        for role, count, desc in roles:
            st.markdown(
                f'''
                <div class="info-card" style="border-left-color: #FFCDD2; padding: 0.5rem 0.8rem; margin: 0.3rem 0;">
                    <b>{role}</b> × {count}<br>
                    <span style="color:#888888; font-size:0.78rem;">{desc}</span>
                </div>
                ''',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ───────── 补充：虚拟主播偏好 & 扫码答题意愿 ─────────
    st.markdown(
        '<div class="section-header"><span class="section-icon">🎭</span>'
        '<span class="section-title">关键洞察 · 虚拟主播偏好与互动意愿</span></div>',
        unsafe_allow_html=True
    )

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        # 虚拟主播偏好
        anchor_names = anchor_pref.index.tolist()
        anchor_vals = anchor_pref.values.tolist()
        anchor_pcts = [v / total_n * 100 for v in anchor_vals]

        fig_anchor = go.Figure(go.Pie(
            labels=anchor_names,
            values=anchor_vals,
            marker_colors=["#DC143C", "#FF8C00", "#DAA520", "#4CAF50"],
            text=[f"{p:.1f}%" for p in anchor_pcts],
            textposition="inside",
            textfont=dict(color="white", size=13),
            hole=0.4,
            hovertemplate="%{label}<br>人数: %{value}<br>占比: %{percent}<extra></extra>",
        ))
        fig_anchor.update_layout(
            **_merge_layout(dict(
                title=dict(
                    text='虚拟主播「红小西」形象偏好<br><sub>热血青年战士以48.5%高票领先</sub>',
                    font=dict(color=COLOR_TEXT2, size=14)
                ),
                height=350,
                margin=dict(l=20, r=20, t=70, b=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5,
                    font=dict(color=COLOR_TEXT2, size=11),
                ),
            ))
        )
        st.plotly_chart(fig_anchor, use_container_width=True)

    with insight_col2:
        # 扫码答题意愿分布
        scan_dist = df[COL_WILLING].value_counts().sort_index()

        fig_scan = go.Figure(go.Bar(
            x=scan_dist.index.astype(str),
            y=scan_dist.values,
            marker_color=[
                "#DC143C" if int(k) <= 5 else "#FF8C00" if int(k) <= 7 else "#4CAF50"
                for k in scan_dist.index
            ],
            text=scan_dist.values,
            textposition="outside",
            textfont=dict(color=COLOR_TEXT2, size=11),
        ))
        fig_scan.update_layout(
            **_merge_layout(dict(
                title=dict(
                    text=f'扫码答题兑换勋章意愿分布<br><sub>均值 {scan_willing:.1f}/10 → 目标 {target_scan}/10</sub>',
                    font=dict(color=COLOR_TEXT2, size=14)
                ),
                xaxis=dict(title="意愿评分 (1-10)", gridcolor=COLOR_GRID, linecolor=COLOR_GRID),
                yaxis=dict(title="人数", gridcolor=COLOR_GRID, linecolor=COLOR_GRID),
                height=350,
            ))
        )
        st.plotly_chart(fig_scan, use_container_width=True)

    st.markdown("---")

    # ───────── 底部：闭环总结 ─────────
    st.markdown(
        '<div class="section-header"><span class="section-icon">🔄</span>'
        '<span class="section-title">从诊断到行动 · 闭环总结</span></div>',
        unsafe_allow_html=True
    )

    close_col1, close_col2, close_col3, close_col4 = st.columns(4)

    with close_col1:
        st.markdown(
            '''
            <div class="kpi-card" style="border-color: #FFCDD2;">
                <div class="kpi-label">1️⃣ 诊断</div>
                <div style="color:#DC143C; font-size:0.9rem;">
                    问卷N=272<br>
                    触达率52.6%<br>
                    认知分6.0/10<br>
                    三大痛点明确
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with close_col2:
        st.markdown(
            '''
            <div class="kpi-card" style="border-color: #FFE0B2;">
                <div class="kpi-label">2️⃣ 定标</div>
                <div style="color:#E65100; font-size:0.9rem;">
                    触达率→65%<br>
                    认知分→7.0<br>
                    痛点全面改善<br>
                    创作参与→45%
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with close_col3:
        st.markdown(
            '''
            <div class="kpi-card" style="border-color: #C8E6C9;">
                <div class="kpi-label">3️⃣ 行动</div>
                <div style="color:#2E7D32; font-size:0.9rem;">
                    互动H5开发<br>
                    虚拟主播上线<br>
                    渠道精准投放<br>
                    校园试点推广
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with close_col4:
        st.markdown(
            '''
            <div class="kpi-card" style="border-color: #FFF9C4;">
                <div class="kpi-label">4️⃣ 迭代</div>
                <div style="color:#F57F17; font-size:0.9rem;">
                    9月效果评估<br>
                    数据驱动优化<br>
                    机制固化推广<br>
                    持续监测闭环
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    # 数据来源声明
    st.markdown(
        '''
        <div class="data-source">
            📂 数据来源：《数链红星·星火篇》 革命老区青少年红色文化触达率调研（2025）| 
            总样本量 N={} | 
            目标值基于基线数据的务实提升设定
        </div>
        '''.format(total_n),
        unsafe_allow_html=True
    )
