import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data_loader import *

st.set_page_config(
    page_title="图书销售数据与读者画像分析看板",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

CATEGORY_COLORS = {
    '文学': '#FF6B6B',
    '社科': '#4ECDC4',
    '科技': '#45B7D1',
    '少儿': '#96CEB4',
    '教辅': '#FFEAA7'
}

CHANNEL_COLORS = {
    '线上电商': '#6C5CE7',
    '线下书店': '#FD79A8',
    '馆配': '#00B894'
}

books_df, sales_df, readers_df, ratings_df = load_data()
best_sellers, worst_sellers = get_book_rankings(sales_df, books_df)

st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        font-family: 'Microsoft YaHei', sans-serif;
        font-weight: 600;
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    }
    .best-seller {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        border-left: 4px solid #f39c12;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .worst-seller {
        background: linear-gradient(135deg, #fab1a0 0%, #e17055 100%);
        border-left: 4px solid #d63031;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2d3436 0%, #636e72 100%);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .plot-container {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("📚 图书数据分析看板")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "选择页面",
    ["📊 销售趋势分析", "👥 读者画像分析", "📖 单品分析"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 快捷信息")
st.sidebar.markdown(f"**图书总数:** {len(books_df)} 本")
st.sidebar.markdown(f"**销售记录:** {len(sales_df)} 条")
st.sidebar.markdown(f"**读者样本:** {len(readers_df)} 人")

if page == "📊 销售趋势分析":
    st.title("📊 销售趋势分析")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    available_years = get_available_years(sales_df)
    with col1:
        start_year = st.selectbox("开始年份", available_years, index=0, key='start_year')
    with col2:
        start_month = st.selectbox("开始月份", get_available_months(), index=0, key='start_month')
    with col3:
        end_year = st.selectbox("结束年份", available_years, index=len(available_years)-1, key='end_year')
    with col4:
        end_month = st.selectbox("结束月份", get_available_months(), index=11, key='end_month')
    
    categories = ['全部'] + list(CATEGORY_COLORS.keys())
    selected_category = st.selectbox("选择图书品类", categories, index=0, key='trend_category')
    
    filtered_sales = filter_sales_by_date(sales_df, books_df, start_year, start_month, end_year, end_month)
    
    total_sales = filtered_sales['销量'].sum()
    total_revenue = filtered_sales['营收'].sum()
    avg_order_value = total_revenue / total_sales if total_sales > 0 else 0
    unique_books = filtered_sales['ISBN'].nunique()
    
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">📦 总销量</h3>
            <h2 style="color: #2d3436; margin: 0.5rem 0;">{total_sales:,}</h2>
            <p style="color: #636e72; margin: 0;">册</p>
        </div>
        """, unsafe_allow_html=True)
    with mcol2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #00b894; margin: 0;">💰 总营收</h3>
            <h2 style="color: #2d3436; margin: 0.5rem 0;">¥{total_revenue:,.2f}</h2>
            <p style="color: #636e72; margin: 0;">元</p>
        </div>
        """, unsafe_allow_html=True)
    with mcol3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #fd79a8; margin: 0;">📈 平均单价</h3>
            <h2 style="color: #2d3436; margin: 0.5rem 0;">¥{avg_order_value:.2f}</h2>
            <p style="color: #636e72; margin: 0;">元/册</p>
        </div>
        """, unsafe_allow_html=True)
    with mcol4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #6c5ce7; margin: 0;">📚 动销品种</h3>
            <h2 style="color: #2d3436; margin: 0.5rem 0;">{unique_books}</h2>
            <p style="color: #636e72; margin: 0;">种</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    monthly_trend = get_monthly_sales_trend(filtered_sales, selected_category)
    
    tab1, tab2 = st.tabs(["📈 销量趋势", "💰 营收趋势"])
    
    with tab1:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        fig_sales = go.Figure()
        
        if selected_category == '全部':
            for cat in CATEGORY_COLORS.keys():
                cat_data = monthly_trend[monthly_trend['品类'] == cat]
                if len(cat_data) > 0:
                    fig_sales.add_trace(go.Scatter(
                        x=cat_data['年月'],
                        y=cat_data['销量'],
                        mode='lines+markers',
                        name=cat,
                        line=dict(color=CATEGORY_COLORS[cat], width=3),
                        marker=dict(size=8, line=dict(width=2, color='white'))
                    ))
        else:
            fig_sales.add_trace(go.Scatter(
                x=monthly_trend['年月'],
                y=monthly_trend['销量'],
                mode='lines+markers',
                name=selected_category,
                line=dict(color=CATEGORY_COLORS[selected_category], width=3),
                marker=dict(size=10, line=dict(width=2, color='white')),
                fill='tonexty',
                fillcolor=f"rgba{tuple(int(CATEGORY_COLORS[selected_category][1:][i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}"
            ))
        
        fig_sales.update_layout(
            title=f'{selected_category} 月度销量趋势',
            xaxis_title='月份',
            yaxis_title='销量（册）',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=500,
            template='plotly_white'
        )
        st.plotly_chart(fig_sales, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        fig_revenue = go.Figure()
        
        if selected_category == '全部':
            for cat in CATEGORY_COLORS.keys():
                cat_data = monthly_trend[monthly_trend['品类'] == cat]
                if len(cat_data) > 0:
                    fig_revenue.add_trace(go.Scatter(
                        x=cat_data['年月'],
                        y=cat_data['营收'],
                        mode='lines+markers',
                        name=cat,
                        line=dict(color=CATEGORY_COLORS[cat], width=3),
                        marker=dict(size=8, line=dict(width=2, color='white'))
                    ))
        else:
            fig_revenue.add_trace(go.Scatter(
                x=monthly_trend['年月'],
                y=monthly_trend['营收'],
                mode='lines+markers',
                name=selected_category,
                line=dict(color=CATEGORY_COLORS[selected_category], width=3),
                marker=dict(size=10, line=dict(width=2, color='white')),
                fill='tonexty',
                fillcolor=f"rgba{tuple(int(CATEGORY_COLORS[selected_category][1:][i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}"
            ))
        
        fig_revenue.update_layout(
            title=f'{selected_category} 月度营收趋势',
            xaxis_title='月份',
            yaxis_title='营收（元）',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=500,
            template='plotly_white'
        )
        st.plotly_chart(fig_revenue, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        category_summary = get_category_sales_summary(filtered_sales)
        
        fig_cat = px.bar(
            category_summary,
            x='品类',
            y='销量',
            color='品类',
            color_discrete_map=CATEGORY_COLORS,
            title='各品类销量对比',
            text='销量',
            height=400
        )
        fig_cat.update_traces(textposition='outside', texttemplate='%{text:,}')
        fig_cat.update_layout(showlegend=False, template='plotly_white')
        st.plotly_chart(fig_cat, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        channel_summary = get_channel_sales(filtered_sales)
        
        fig_channel = px.bar(
            channel_summary,
            x='渠道',
            y='销量',
            color='品类',
            color_discrete_map=CATEGORY_COLORS,
            title='各渠道销量分布（按品类）',
            height=400
        )
        fig_channel.update_layout(barmode='stack', template='plotly_white')
        st.plotly_chart(fig_channel, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📋 品类销售明细")
    st.dataframe(
        category_summary.style.format({
            '销量': '{:,}',
            '营收': '{:,.2f}',
            '平均单价': '{:.2f}'
        }).background_gradient(cmap='Blues', subset=['销量']),
        width='stretch'
    )

elif page == "👥 读者画像分析":
    st.title("👥 读者画像分析")
    st.markdown("---")
    
    all_categories = list(CATEGORY_COLORS.keys())
    selected_categories = st.multiselect(
        "选择要对比的品类（可多选）",
        all_categories,
        default=['文学', '科技'],
        key='profile_categories'
    )
    
    if len(selected_categories) == 0:
        st.warning("请至少选择一个品类进行分析")
    else:
        profiles = get_reader_profile_by_category(readers_df, selected_categories)
        radar_df = get_radar_data(profiles, selected_categories)
        
        if len(radar_df) == 0:
            st.warning("没有找到对应品类的读者数据")
        else:
            st.subheader("📊 多维度读者画像对比（雷达图）")
            
            radar_dims = [
                '18-25岁', '26-35岁', '36-45岁', '46-55岁', '55岁以上',
                '男性比例', '女性比例',
                '20-50元', '50-100元', '100元以上',
                '复购率'
            ]
            
            fig = go.Figure()
            
            for idx, row in radar_df.iterrows():
                cat = row['品类']
                values = [row[dim] for dim in radar_dims]
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=radar_dims,
                    fill='toself',
                    name=cat,
                    line=dict(color=CATEGORY_COLORS[cat], width=3),
                    fillcolor=f"rgba{tuple(int(CATEGORY_COLORS[cat][1:][i:i+2], 16) for i in (0, 2, 4)) + (0.3,)}",
                    opacity=0.8
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=10)
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=11)
                    )
                ),
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5),
                height=600,
                template='plotly_white',
                title='读者画像多维对比（百分比%）'
            )
            
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            for i in range(0, len(selected_categories), 2):
                col1, col2 = st.columns(2)
                
                with col1:
                    cat = selected_categories[i]
                    if cat in profiles:
                        profile = profiles[cat]
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="color: {CATEGORY_COLORS[cat]}; margin-top: 0;">{cat}读者画像</h3>
                            <p style="color: #636e72; margin: 0.25rem 0;">样本量: <strong>{profile['total_readers']}</strong> 人</p>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 1rem;">
                        """, unsafe_allow_html=True)
                        
                        for age in ['18-25', '26-35', '36-45', '46-55', '55+']:
                            pct = profile['age_dist'].get(age, 0) * 100
                            st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 6px;">
                                <div style="font-size: 0.85rem; color: #636e72;">{age}岁</div>
                                <div style="font-weight: 600; color: #2d3436;">{pct:.1f}%</div>
                                <div style="height: 6px; background: #e0e0e0; border-radius: 3px; margin-top: 4px;">
                                    <div style="height: 100%; width: {pct}%; background: {CATEGORY_COLORS[cat]}; border-radius: 3px;"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style="margin-top: 1rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                            <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); padding: 0.75rem; border-radius: 8px; color: white;">
                                <div style="font-size: 0.85rem; opacity: 0.9;">男性比例</div>
                                <div style="font-size: 1.5rem; font-weight: 700;">{profile['gender_dist']['男']*100:.1f}%</div>
                            </div>
                            <div style="background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); padding: 0.75rem; border-radius: 8px; color: white;">
                                <div style="font-size: 0.85rem; opacity: 0.9;">女性比例</div>
                                <div style="font-size: 1.5rem; font-weight: 700;">{profile['gender_dist']['女']*100:.1f}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style="margin-top: 1rem;">
                            <div style="font-weight: 600; margin-bottom: 0.5rem;">购买力分布</div>
                            <div style="display: flex; gap: 0.5rem;">
                        """, unsafe_allow_html=True)
                        
                        for pr in ['20-50', '50-100', '100+']:
                            pct = profile['price_dist'].get(pr, 0) * 100
                            st.markdown(f"""
                            <div style="flex: 1; text-align: center; background: #f8f9fa; padding: 0.5rem; border-radius: 6px;">
                                <div style="font-size: 0.8rem; color: #636e72;">{pr}元</div>
                                <div style="font-weight: 600; color: #2d3436;">{pct:.1f}%</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("""
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style="margin-top: 1rem; background: linear-gradient(135deg, #55efc4 0%, #00b894 100%); padding: 1rem; border-radius: 8px; color: white;">
                            <div style="font-size: 0.9rem; opacity: 0.9;">三个月内复购率</div>
                            <div style="font-size: 2rem; font-weight: 700;">{profile['repurchase_rate']*100:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                if i + 1 < len(selected_categories):
                    with col2:
                        cat = selected_categories[i + 1]
                        if cat in profiles:
                            profile = profiles[cat]
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3 style="color: {CATEGORY_COLORS[cat]}; margin-top: 0;">{cat}读者画像</h3>
                                <p style="color: #636e72; margin: 0.25rem 0;">样本量: <strong>{profile['total_readers']}</strong> 人</p>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 1rem;">
                            """, unsafe_allow_html=True)
                            
                            for age in ['18-25', '26-35', '36-45', '46-55', '55+']:
                                pct = profile['age_dist'].get(age, 0) * 100
                                st.markdown(f"""
                                <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 6px;">
                                    <div style="font-size: 0.85rem; color: #636e72;">{age}岁</div>
                                    <div style="font-weight: 600; color: #2d3436;">{pct:.1f}%</div>
                                    <div style="height: 6px; background: #e0e0e0; border-radius: 3px; margin-top: 4px;">
                                        <div style="height: 100%; width: {pct}%; background: {CATEGORY_COLORS[cat]}; border-radius: 3px;"></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style="margin-top: 1rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                                <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); padding: 0.75rem; border-radius: 8px; color: white;">
                                    <div style="font-size: 0.85rem; opacity: 0.9;">男性比例</div>
                                    <div style="font-size: 1.5rem; font-weight: 700;">{profile['gender_dist']['男']*100:.1f}%</div>
                                </div>
                                <div style="background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); padding: 0.75rem; border-radius: 8px; color: white;">
                                    <div style="font-size: 0.85rem; opacity: 0.9;">女性比例</div>
                                    <div style="font-size: 1.5rem; font-weight: 700;">{profile['gender_dist']['女']*100:.1f}%</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style="margin-top: 1rem;">
                                <div style="font-weight: 600; margin-bottom: 0.5rem;">购买力分布</div>
                                <div style="display: flex; gap: 0.5rem;">
                            """, unsafe_allow_html=True)
                            
                            for pr in ['20-50', '50-100', '100+']:
                                pct = profile['price_dist'].get(pr, 0) * 100
                                st.markdown(f"""
                                <div style="flex: 1; text-align: center; background: #f8f9fa; padding: 0.5rem; border-radius: 6px;">
                                    <div style="font-size: 0.8rem; color: #636e72;">{pr}元</div>
                                    <div style="font-weight: 600; color: #2d3436;">{pct:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("""
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style="margin-top: 1rem; background: linear-gradient(135deg, #55efc4 0%, #00b894 100%); padding: 1rem; border-radius: 8px; color: white;">
                                <div style="font-size: 0.9rem; opacity: 0.9;">三个月内复购率</div>
                                <div style="font-size: 2rem; font-weight: 700;">{profile['repurchase_rate']*100:.1f}%</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                age_data = []
                for cat in selected_categories:
                    if cat in profiles:
                        for age in ['18-25', '26-35', '36-45', '46-55', '55+']:
                            age_data.append({
                                '品类': cat,
                                '年龄区间': age,
                                '比例': profiles[cat]['age_dist'].get(age, 0) * 100
                            })
                
                if age_data:
                    age_df = pd.DataFrame(age_data)
                    fig_age = px.bar(
                        age_df,
                        x='年龄区间',
                        y='比例',
                        color='品类',
                        barmode='group',
                        color_discrete_map=CATEGORY_COLORS,
                        title='年龄分布对比',
                        height=400
                    )
                    fig_age.update_layout(template='plotly_white', yaxis_title='比例(%)')
                    st.plotly_chart(fig_age, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                price_data = []
                for cat in selected_categories:
                    if cat in profiles:
                        for pr in ['20-50', '50-100', '100+']:
                            price_data.append({
                                '品类': cat,
                                '购买力区间': pr + '元',
                                '比例': profiles[cat]['price_dist'].get(pr, 0) * 100
                            })
                
                if price_data:
                    price_df = pd.DataFrame(price_data)
                    fig_price = px.bar(
                        price_df,
                        x='购买力区间',
                        y='比例',
                        color='品类',
                        barmode='group',
                        color_discrete_map=CATEGORY_COLORS,
                        title='购买力分布对比',
                        height=400
                    )
                    fig_price.update_layout(template='plotly_white', yaxis_title='比例(%)')
                    st.plotly_chart(fig_price, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)

elif page == "📖 单品分析":
    st.title("📖 单品分析")
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        isbn_list = books_df['ISBN'].tolist()
        book_titles = books_df['书名'].tolist()
        book_options = [f"{title} ({isbn})" for title, isbn in zip(book_titles, isbn_list)]
        
        selected_book = st.selectbox(
            "选择图书或输入ISBN",
            book_options,
            index=0,
            key='book_select'
        )
        
        selected_isbn = selected_book.split('(')[-1].rstrip(')')
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 分析", width='stretch'):
            pass
    
    st.markdown("---")
    
    book_data = get_book_by_isbn(sales_df, books_df, ratings_df, selected_isbn)
    
    if book_data is None:
        st.error("未找到该图书信息")
    else:
        info = book_data['info']
        
        is_best = selected_isbn in best_sellers['ISBN'].values
        is_worst = selected_isbn in worst_sellers['ISBN'].values
        
        badge_html = '<div></div>'
        if is_best:
            badge_html = '<div><span style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem; font-weight: 600;">⭐ 畅销书</span></div>'
        elif is_worst:
            badge_html = '<div><span style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem; font-weight: 600;">📉 滞销书</span></div>'
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h2 style="margin: 0; color: #2d3436;">{info['书名']}</h2>
                    <p style="color: #636e72; margin: 0.5rem 0;">作者: {info['作者']} | ISBN: {info['ISBN']}</p>
                    <p style="color: #636e72; margin: 0;">品类: <span style="background: {CATEGORY_COLORS[info['品类']]}; color: white; padding: 0.2rem 0.6rem; border-radius: 4px;">{info['品类']}</span> | 定价: ¥{info['定价']:.2f} | 出版日期: {info['出版日期']}</p>
                </div>
                {badge_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h4 style="color: #667eea; margin: 0;">📦 累计销量</h4>
                <h2 style="color: #2d3436; margin: 0.5rem 0;">{book_data['total_sales']:,}</h2>
                <p style="color: #636e72; margin: 0;">册</p>
            </div>
            """, unsafe_allow_html=True)
        with mcol2:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h4 style="color: #00b894; margin: 0;">💰 累计营收</h4>
                <h2 style="color: #2d3436; margin: 0.5rem 0;">¥{book_data['total_revenue']:,.2f}</h2>
                <p style="color: #636e72; margin: 0;">元</p>
            </div>
            """, unsafe_allow_html=True)
        with mcol3:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h4 style="color: #fd79a8; margin: 0;">⭐ 平均评分</h4>
                <h2 style="color: #2d3436; margin: 0.5rem 0;">{book_data['avg_rating']:.2f}</h2>
                <p style="color: #636e72; margin: 0;">（{book_data['total_ratings']}人评价）</p>
            </div>
            """, unsafe_allow_html=True)
        with mcol4:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h4 style="color: #6c5ce7; margin: 0;">📊 平均单价</h4>
                <h2 style="color: #2d3436; margin: 0.5rem 0;">¥{book_data['total_revenue']/book_data['total_sales']:.2f}</h2>
                <p style="color: #636e72; margin: 0;">元/册</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["📈 销量趋势", "🏪 渠道分布", "⭐ 评分分布"])
        
        with tab1:
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            monthly_sales = book_data['monthly_sales']
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=monthly_sales['年月'],
                y=monthly_sales['销量'],
                mode='lines+markers',
                name='销量',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10, line=dict(width=2, color='white')),
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.2)'
            ))
            
            if len(monthly_sales) > 0:
                max_idx = monthly_sales['销量'].idxmax()
                min_idx = monthly_sales['销量'].idxmin()
                
                fig.add_annotation(
                    x=monthly_sales.loc[max_idx, '年月'],
                    y=monthly_sales.loc[max_idx, '销量'],
                    text=f"峰值: {monthly_sales.loc[max_idx, '销量']:,}册",
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-40,
                    bgcolor='rgba(46, 204, 113, 0.9)',
                    font=dict(color='white'),
                    borderpad=4
                )
                
                fig.add_annotation(
                    x=monthly_sales.loc[min_idx, '年月'],
                    y=monthly_sales.loc[min_idx, '销量'],
                    text=f"低谷: {monthly_sales.loc[min_idx, '销量']:,}册",
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=40,
                    bgcolor='rgba(231, 76, 60, 0.9)',
                    font=dict(color='white'),
                    borderpad=4
                )
            
            fig.update_layout(
                title=f"{info['书名']} 月度销量趋势",
                xaxis_title='月份',
                yaxis_title='销量（册）',
                hovermode='x unified',
                height=450,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                channel_dist = book_data['channel_dist']
                
                fig_channel = px.pie(
                    channel_dist,
                    values='销量',
                    names='渠道',
                    color='渠道',
                    color_discrete_map=CHANNEL_COLORS,
                    title='销量渠道分布',
                    hole=0.4,
                    height=400
                )
                fig_channel.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    marker=dict(line=dict(color='white', width=3))
                )
                fig_channel.update_layout(template='plotly_white')
                st.plotly_chart(fig_channel, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                fig_rev_channel = px.pie(
                    channel_dist,
                    values='营收',
                    names='渠道',
                    color='渠道',
                    color_discrete_map=CHANNEL_COLORS,
                    title='营收渠道分布',
                    hole=0.4,
                    height=400
                )
                fig_rev_channel.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    marker=dict(line=dict(color='white', width=3))
                )
                fig_rev_channel.update_layout(template='plotly_white')
                st.plotly_chart(fig_rev_channel, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.dataframe(
                channel_dist.style.format({
                    '销量': '{:,}',
                    '营收': '{:,.2f}'
                }).background_gradient(cmap='Blues', subset=['销量']),
                width='stretch'
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                rating_dist = book_data['rating_dist']
                rating_df = pd.DataFrame({
                    '评分等级': list(rating_dist.keys()),
                    '人数': list(rating_dist.values())
                })
                
                colors = ['#f1c40f', '#f39c12', '#95a5a6']
                fig_rating = px.bar(
                    rating_df,
                    x='评分等级',
                    y='人数',
                    color='评分等级',
                    color_discrete_sequence=colors,
                    title='读者评分分布',
                    text='人数',
                    height=400
                )
                fig_rating.update_traces(textposition='outside')
                fig_rating.update_layout(showlegend=False, template='plotly_white')
                st.plotly_chart(fig_rating, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                total_ratings = sum(rating_dist.values())
                if total_ratings > 0:
                    fig_star = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=book_data['avg_rating'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "平均评分", 'font': {'size': 20}},
                        gauge={
                            'axis': {'range': [0, 5], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "#f1c40f"},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "#667eea",
                            'steps': [
                                {'range': [0, 2], 'color': '#ecf0f1'},
                                {'range': [2, 3.5], 'color': '#bdc3c7'},
                                {'range': [3.5, 4.5], 'color': '#f39c12'},
                                {'range': [4.5, 5], 'color': '#f1c40f'}
                            ],
                            'threshold': {
                                'line': {'color': "#e74c3c", 'width': 4},
                                'thickness': 0.75,
                                'value': book_data['avg_rating']
                            }
                        }
                    ))
                    fig_star.update_layout(height=400, template='plotly_white')
                    st.plotly_chart(fig_star, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 畅销书榜（前10%）")
            for _, row in best_sellers.iterrows():
                highlight = "border: 2px solid #f39c12;" if row['ISBN'] == selected_isbn else ""
                st.markdown(f"""
                <div class="best-seller" style="{highlight}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #2d3436;">{row['书名']}</strong>
                            <div style="font-size: 0.85rem; color: #636e72;">{row['品类']} | {row['ISBN']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 700; color: #e67e22;">{row['销量']:,} 册</div>
                            <div style="font-size: 0.85rem; color: #636e72;">¥{row['营收']:,.0f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📉 滞销书榜（后10%）")
            for _, row in worst_sellers.iterrows():
                highlight = "border: 2px solid #e74c3c;" if row['ISBN'] == selected_isbn else ""
                st.markdown(f"""
                <div class="worst-seller" style="{highlight}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #2d3436;">{row['书名']}</strong>
                            <div style="font-size: 0.85rem; color: #636e72;">{row['品类']} | {row['ISBN']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 700; color: #c0392b;">{row['销量']:,} 册</div>
                            <div style="font-size: 0.85rem; color: #636e72;">¥{row['营收']:,.0f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 提示")
st.sidebar.info("""
- 销售趋势：按年份月份筛选，查看各品类销量和营收
- 读者画像：对比不同品类读者的年龄、性别、购买力和复购率
- 单品分析：输入ISBN查询单本书详情，自动识别畅销/滞销
""")
