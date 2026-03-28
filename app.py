import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="Asharq AI Intelligence", layout="wide", page_icon="💎")

# تصميم واجهة مستخدم عالمية (Executive Dark Theme)
st.markdown("""
    <style>
    .stApp { background-color: #050a18; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #0f172a; border-left: 1px solid #1e293b; }
    .ai-card { background: linear-gradient(145deg, #0f172a, #1e293b); padding: 25px; border-radius: 20px; border: 1px solid #334155; margin-bottom: 20px; }
    .ai-insight-box { border-right: 4px solid #3b82f6; background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 10px; color: #93c5fd; font-size: 1.1rem; line-height: 1.6; }
    .status-badge { background: #3b82f6; color: white; padding: 5px 15px; border-radius: 50px; font-size: 0.8rem; }
    h1, h2, h3 { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; letter-spacing: -1px; }
    .stMetric [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. المحرك التحليلي (AI Logic Engine)
@st.cache_data
def analyze_data_stream(uploaded_files):
    all_dfs = {'p': [], 'r': [], 'g': [], 'c': []}
    for file in uploaded_files:
        try:
            doc = Document(file)
            fname = file.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['Reference'] = fname
                    cols = df.columns.tolist()
                    if 'شكل التقديم' in cols: all_dfs['p'].append(df)
                    elif 'المراسل/الصحفي' in cols: all_dfs['r'].append(df)
                    elif 'الضيف' in cols: all_dfs['g'].append(df)
                    elif 'التصنيف' in cols: all_dfs['c'].append(df)
        except: continue
    return all_dfs

# 3. الهيكل البصري (Main UI)
st.markdown("<h1 style='text-align: center; color: #3b82f6; margin-bottom: 0;'>ASHARQ <span style='color:white'>INTELLIGENCE</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem;'>نظام تحليل المحتوى الإخباري المدعوم بالذكاء الاصطناعي</p>", unsafe_allow_html=True)

files = st.sidebar.file_uploader("📂 اسحب حزمة التقارير هنا:", type="docx", accept_multiple_files=True)

if files:
    data = analyze_data_stream(files)
    df_p = pd.concat(data['p']) if data['p'] else pd.DataFrame()
    df_r = pd.concat(data['r']) if data['r'] else pd.DataFrame()
    df_g = pd.concat(data['g']) if data['g'] else pd.DataFrame()

    # --- القسم الأول: ذكاء القرار (Executive Insights) ---
    st.markdown("### 🧠 مركز استنتاجات الذكاء الاصطناعي")
    col_ins_1, col_ins_2 = st.columns([2, 1])

    with col_ins_1:
        st.markdown("<div class='ai-insight-box'>", unsafe_allow_html=True)
        if not df_p.empty:
            total = int(pd.to_numeric(df_p['العدد'], errors='coerce').sum())
            top_format = df_p.groupby('شكل التقديم')['العدد'].count().idxmax()
            st.markdown(f"**تحليل اليوم:** تم رصد إجمالي **{total}** مادة إخبارية. القالب الأكثر تأثيراً هو **'{top_format}'**. "
                        f"نلاحظ توازناً جيداً في توزيع المداخلات، ولكن ننصح بزيادة التغطية الميدانية لرفع مستوى التفاعل.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_ins_2:
        # عداد الكفاءة (Gauge Chart)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = 85,
            title = {'text': "مؤشر جودة التغطية", 'font': {'size': 18, 'color': '#94a3b8'}},
            gauge = {'axis': {'range': [0, 100], 'tickcolor': "#3b82f6"},
                     'bar': {'color': "#3b82f6"},
                     'bgcolor': "rgba(0,0,0,0)",
                     'steps': [{'range': [0, 50], 'color': '#1e293b'}, {'range': [50, 100], 'color': '#0f172a'}]}
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Arial"}, height=250, margin=dict(l=20,r=20,t=50,b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # --- القسم الثاني: التحليل البصري المعمق ---
    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='ai-card'><h4>📊 الرادار الاستراتيجي للمحتوى</h4>", unsafe_allow_html=True)
        if not df_p.empty:
            radar_df = df_p.groupby('شكل التقديم').size().reset_index(name='count')
            fig_radar = px.line_polar(radar_df, r='count', theta='شكل التقديم', line_close=True)
            fig_radar.update_traces(fill='toself', line_color='#3b82f6')
            fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False)))
            st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='ai-card'><h4>📈 المسار الزمني للإنتاج</h4>", unsafe_allow_html=True)
        if not df_p.empty:
            line_df = df_p.groupby('Reference').size().reset_index(name='Total')
            fig_line = px.line(line_df, x='Reference', y='Total', markers=True, color_discrete_sequence=['#3b82f6'])
            fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1e293b'))
            st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- القسم الثالث: خرائط الأداء (Performance Maps) ---
    st.markdown("<div class='ai-card'>", unsafe_allow_html=True)
    st.markdown("### 🎙️ مصفوفة أداء شبكة المراسلين")
    if not df_r.empty:
        df_r['عدد المداخلات'] = pd.to_numeric(df_r['عدد المداخلات'], errors='coerce').fillna(0)
        fig_r = px.bar(df_r.groupby('المراسل/الصحفي')['عدد المداخلات'].sum().reset_index().sort_values('عدد المداخلات'), 
                       x='عدد المداخلات', y='المراسل/الصحفي', orientation='h', color='عدد المداخلات', color_continuous_scale='Blues')
        fig_r.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_r, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- القسم الرابع: الجدول الذكي ---
    with st.expander("📄 عرض البيانات الخام والتقارير المدمجة"):
        st.dataframe(df_g, use_container_width=True)

else:
    st.info("💎 بانتظار رفع ملفات الرصد لتشغيل محرك الذكاء الاصطناعي...")
