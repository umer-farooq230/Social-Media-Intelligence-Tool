import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Social Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    </style>
    """, unsafe_allow_html=True)

# Mock data generator - simulating API/scraper data
@st.cache_data
def generate_mock_data():
    """Generate mock social media data with custom attributes"""
    np.random.seed(42)
    
    platforms = ['Instagram', 'TikTok', 'LinkedIn']
    hooks = ['Question', 'Controversy', 'Story', 'Tutorial', 'Trend', 'Before/After', 'Data Insight']
    creatives = ['Carousel', 'Video', 'Reel', 'Text Post', 'Infographic', 'Story']
    visuals = ['Bold Text', 'Face to Camera', 'Minimal', 'Dynamic B-Roll', 'Trending Audio', 
               'Comparison', 'Clean Graphics', 'POV Style']
    times = ['07:00', '08:00', '09:00', '11:00', '14:00', '16:00', '18:00', '20:00']
    
    data = []
    for i in range(50):
        platform = np.random.choice(platforms)
        base_followers = {'Instagram': 28000, 'TikTok': 35000, 'LinkedIn': 12000}[platform]
        reach_multiplier = np.random.uniform(0.5, 8.0)
        reach = int(base_followers * reach_multiplier)
        
        likes = int(reach * np.random.uniform(0.02, 0.15))
        shares = int(reach * np.random.uniform(0.005, 0.025))
        saves = int(reach * np.random.uniform(0.003, 0.04))
        comments = int(reach * np.random.uniform(0.002, 0.015))
        
        quality_score = np.random.uniform(6.0, 9.5)
        
        data.append({
            'post_id': f'POST_{i+1}',
            'platform': platform,
            'date': datetime.now() - timedelta(days=np.random.randint(0, 30)),
            'hook_type': np.random.choice(hooks),
            'creative_type': np.random.choice(creatives),
            'visual_style': np.random.choice(visuals),
            'post_time': np.random.choice(times),
            'reach': reach,
            'likes': likes,
            'shares': shares,
            'saves': saves,
            'comments': comments,
            'followers': base_followers,
            'quality_score': quality_score
        })
    
    return pd.DataFrame(data)

# Calculate enriched metrics
def enrich_data(df):
    """Add calculated metrics for deeper analysis"""
    df = df.copy()
    df['total_engagement'] = df['likes'] + df['shares'] + df['saves'] + df['comments']
    df['engagement_rate'] = (df['total_engagement'] / df['reach'] * 100).round(2)
    df['quality_engagement'] = ((df['shares'] + df['saves']) / df['likes'].replace(0, 1) * 100).round(2)
    df['reach_efficiency'] = (df['reach'] / df['followers']).round(2)
    df['viral_ratio'] = ((df['reach'] - df['followers']) / df['followers'] * 100).round(1)
    df['save_rate'] = (df['saves'] / df['reach'] * 100).round(3)
    df['share_rate'] = (df['shares'] / df['reach'] * 100).round(3)
    df['hour'] = df['post_time'].str[:2].astype(int)
    return df

# Load and enrich data
df = generate_mock_data()
df = enrich_data(df)

# Sidebar filters
st.sidebar.title("🎯 Filters")
st.sidebar.markdown("---")

platform_filter = st.sidebar.multiselect(
    "Platform",
    options=df['platform'].unique(),
    default=df['platform'].unique()
)

date_range = st.sidebar.slider(
    "Days to Include",
    min_value=1,
    max_value=30,
    value=7
)

hook_filter = st.sidebar.multiselect(
    "Hook Type",
    options=df['hook_type'].unique(),
    default=df['hook_type'].unique()
)

# Apply filters
cutoff_date = datetime.now() - timedelta(days=date_range)
filtered_df = df[
    (df['platform'].isin(platform_filter)) &
    (df['hook_type'].isin(hook_filter)) &
    (df['date'] >= cutoff_date)
]

# Main dashboard
st.title("📊 Social Media Intelligence Dashboard")
st.markdown("### Real-time Content Performance with Custom Attribution Analysis")
st.markdown("---")

# Key Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_reach = filtered_df['reach'].sum()
    st.metric("Total Reach", f"{total_reach:,}")

with col2:
    avg_engagement = filtered_df['engagement_rate'].mean()
    st.metric("Avg Engagement Rate", f"{avg_engagement:.2f}%")

with col3:
    avg_quality = filtered_df['quality_score'].mean()
    st.metric("Avg Quality Score", f"{avg_quality:.1f}/10")

with col4:
    total_saves = filtered_df['saves'].sum()
    st.metric("Total Saves", f"{total_saves:,}")

with col5:
    avg_viral = filtered_df['viral_ratio'].mean()
    st.metric("Avg Viral Ratio", f"{avg_viral:.1f}%")

st.markdown("---")

# Row 1: Hook Performance & Time Analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎣 Hook Type Performance")
    hook_perf = filtered_df.groupby('hook_type').agg({
        'reach': 'mean',
        'quality_score': 'mean',
        'saves': 'mean',
        'shares': 'mean'
    }).round(0).reset_index()
    
    fig_hook = px.bar(
        hook_perf,
        x='hook_type',
        y='reach',
        color='quality_score',
        color_continuous_scale='Viridis',
        labels={'reach': 'Avg Reach', 'hook_type': 'Hook Type', 'quality_score': 'Quality Score'},
        title="Average Reach by Hook Type (colored by quality)"
    )
    fig_hook.update_layout(height=400)
    st.plotly_chart(fig_hook, use_container_width=True)

with col2:
    st.subheader("⏰ Time of Day Performance")
    time_perf = filtered_df.groupby('hour').agg({
        'reach': 'mean',
        'engagement_rate': 'mean'
    }).reset_index()
    
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(
        x=time_perf['hour'],
        y=time_perf['reach'],
        name='Avg Reach',
        line=dict(color='#8b5cf6', width=3)
    ))
    fig_time.add_trace(go.Scatter(
        x=time_perf['hour'],
        y=time_perf['engagement_rate'] * 1000,  # Scale for visibility
        name='Engagement Rate (scaled)',
        line=dict(color='#ec4899', width=3),
        yaxis='y2'
    ))
    fig_time.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Average Reach",
        yaxis2=dict(title="Engagement Rate", overlaying='y', side='right'),
        height=400
    )
    st.plotly_chart(fig_time, use_container_width=True)

st.markdown("---")

# Row 2: Quality vs Virality & Creative Distribution
col1, col2 = st.columns(2)

with col1:
    st.subheader("💎 Quality Score vs Viral Ratio")
    st.markdown("*Identifying content that balances authenticity with reach*")
    
    fig_scatter = px.scatter(
        filtered_df,
        x='quality_score',
        y='viral_ratio',
        size='reach',
        color='platform',
        hover_data=['hook_type', 'creative_type', 'saves'],
        labels={'quality_score': 'Quality Score', 'viral_ratio': 'Viral Ratio (%)'},
        color_discrete_map={'Instagram': '#E4405F', 'TikTok': '#000000', 'LinkedIn': '#0A66C2'}
    )
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("🎨 Creative Type Distribution")
    creative_dist = filtered_df['creative_type'].value_counts().reset_index()
    creative_dist.columns = ['creative_type', 'count']
    
    fig_pie = px.pie(
        creative_dist,
        values='count',
        names='creative_type',
        color_discrete_sequence=px.colors.sequential.Purples_r
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Row 3: Engagement Quality Analysis
st.subheader("📈 Engagement Quality Analysis")
st.markdown("*Comparing high-intent engagement (saves/shares) vs vanity metrics (likes)*")

col1, col2 = st.columns(2)

with col1:
    quality_by_visual = filtered_df.groupby('visual_style').agg({
        'save_rate': 'mean',
        'share_rate': 'mean',
        'engagement_rate': 'mean'
    }).reset_index()
    
    fig_quality = go.Figure()
    fig_quality.add_trace(go.Bar(
        x=quality_by_visual['visual_style'],
        y=quality_by_visual['save_rate'],
        name='Save Rate (%)',
        marker_color='#10b981'
    ))
    fig_quality.add_trace(go.Bar(
        x=quality_by_visual['visual_style'],
        y=quality_by_visual['share_rate'],
        name='Share Rate (%)',
        marker_color='#3b82f6'
    ))
    fig_quality.update_layout(
        barmode='group',
        xaxis_title="Visual Style",
        yaxis_title="Rate (%)",
        height=400
    )
    st.plotly_chart(fig_quality, use_container_width=True)

with col2:
    reach_eff = filtered_df.groupby('creative_type')['reach_efficiency'].mean().reset_index()
    reach_eff = reach_eff.sort_values('reach_efficiency', ascending=True)
    
    fig_eff = px.bar(
        reach_eff,
        y='creative_type',
        x='reach_efficiency',
        orientation='h',
        labels={'reach_efficiency': 'Reach Efficiency', 'creative_type': 'Creative Type'},
        title="Reach Efficiency by Creative Type",
        color='reach_efficiency',
        color_continuous_scale='Blues'
    )
    fig_eff.update_layout(height=400)
    st.plotly_chart(fig_eff, use_container_width=True)

st.markdown("---")

# Detailed Data Table
st.subheader("📋 Detailed Post Data")
st.markdown("*Granular, post-level data for operational decisions*")

display_cols = ['post_id', 'platform', 'date', 'hook_type', 'creative_type', 'visual_style', 
                'reach', 'engagement_rate', 'quality_score', 'save_rate', 'viral_ratio']

st.dataframe(
    filtered_df[display_cols].sort_values('date', ascending=False).head(20),
    use_container_width=True,
    height=400
)

# Download button
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download Full Dataset (CSV)",
    data=csv,
    file_name=f"social_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #cbd5e1; padding: 20px;'>
    <p>🚀 Custom Intelligence Framework | Built for Operational Clarity</p>
    <p style='font-size: 0.9em;'>Data pipeline extracts → Custom attribution enrichment → Real-time visualization</p>
</div>
""", unsafe_allow_html=True)