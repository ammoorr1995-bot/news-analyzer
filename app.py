import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import re

# 1. إعدادات الهوية البصرية الفاخرة
st.set_page_config(page_title="Asharq AI Intelligence Hub", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    .stApp { background-color: #050a18; color: #f1f5f9; }
    .ai-card { background: linear-gradient(145deg, #0f172a, #1e293b); padding: 25px; border-radius: 15px; border: 1px solid #334155; margin-bottom: 20px; }
    .ai-insight-box { border-right: 5px solid #3b82f6; background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 8px; color: #93c5fd; font-size: 1.1rem; }
    .kpi-value { font-size: 2.5rem; font-weight: 800; color: #3b82f6; }
    @media print { .no-print { display: none !important; } .stApp { background: white !important; color: black !important; } }
    </style>
    """, unsafe_allow_html=True)

# دالة تنظيف البيانات
def clean_val(text):
    if pd.isna(text): return 0
    nums = re.findall(r'\d+', str(text))
    return int(nums[0]) if nums else 0

# 2. محرك المعالجة العميق
@st.cache_data
def process_data_stream(files):
    pool = {'p': [], 'r': [], 'g': []}
    for f in files:
        try:
            doc = Document(f)
            tag = f.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['Date_Tag'] = tag
                    cols = df.columns.tolist()
                    val_col = next((c for c in cols if "العدد" in c or "عدد" in c), None)
                    if any("شكل التقديم" in c for c in cols) and val_col:
                        df['Count'] = df[val_col].apply(clean_val)
                        pool['p'].append(df)
                    elif any("المراسل" in c for c in cols) and val_col:
                        df['Activity'] = df[val_col].apply(clean_val)
                        pool['r'].append(df)
                    elif any("الضيف" in c for c in cols): pool['g'].append(df)
        except: continue
    return pool

# --- الواجهة الرئيسية ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>💎 مركز الذكاء الاستراتيجي <span style='color:white'>| قناة الشرق</span></h1>", unsafe_allow_html=True)

uploaded = st.sidebar.file_uploader("📥 حَمِّل تقارير الرصد (Docx):", type="docx", accept_multiple_files=True)

if uploaded:
    raw = process_data_stream(uploaded)
    df_p = pd.concat(raw['p']) if raw['p'] else pd.DataFrame()
    df_r = pd.concat(raw['r']) if raw['r'] else pd.DataFrame()
    df_g = pd.concat(raw['g']) if raw['g'] else pd.DataFrame()

    tabs = st.tabs(["🧠 التحليل الذكي التلقائي", "📊 لوحة التحكم الشاملة", "⚖️ المقارنة المرنة", "📥 تصدير التقرير"])

    # --- التبويب 1: التحليل الذكي ---
    with tabs[0]:
        st.markdown("### 🕵️‍♂️ محرك الاستنتاجات الاستراتيجي")
        if not df_p.empty:
            total_prod = df_p['Count'].sum()
            avg_prod = total_prod / len(uploaded)
            # إصلاح الخطأ: تعريف المتغير قبل استخدامه
            top_format_row = df_p.groupby('شكل التقديم')['Count'].sum().idxmax()
            
            st.markdown(f"""
            <div class='ai-insight-box'>
            <b>🔍 رؤية الذكاء الاصطناعي:</b><br>
            بناءً على تحليل {len(uploaded)} تقارير، بلغ حجم الإنتاج الكلي <b>{int(total_prod):,}</b> مادة.<br>
            يُظهر النظام أن القالب المهيمن هو <b>"{top_format_row}"</b>. 
            المعدل اليومي الحالي هو <b>{avg_prod:.1f}</b> مادة، وهو ما يعكس استقراراً في تدفق المحتوى.
            </div>
            """, unsafe_allow_html=True)

            # عداد الكفاءة
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = avg_prod,
                title = {'text': "معدل كثافة الإنتاج اليومي", 'font': {'size': 20}},
                gauge = {'axis': {'range': [0, max(200, avg_prod)]}, 'bar': {'color': "#3b82f6"}}
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
            st.plotly_chart(fig_gauge, use_container_width=True)

    # --- التبويب 2: لوحة التحكم الشاملة ---
    with tabs[1]:
        st.markdown("### 📈 نبض الإنتاج الزمني (التقرير الشهري)")
        if not df_p.empty:
            timeline = df_p.groupby('Date_Tag')['Count'].sum().reset_index()
            st.plotly_chart(px.line(timeline, x='Date_Tag', y='Count', markers=True, template="plotly_dark"), use_container_width=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🎙️ نشاط المراسلين")
                if not df_r.empty:
                    top_r = df_r.groupby('المراسل/الصحفي')['Activity'].sum().nlargest(10).reset_index()
                    st.plotly_chart(px.bar(top_r, x='Activity', y='المراسل/الصحفي', orientation='h', color='Activity'), use_container_width=True)
            with c2:
                st.markdown("### 👤 أكثر الضيوف حضوراً")
                if not df_g.empty:
                    top_g = df_g.groupby('الضيف').size().nlargest(10).reset_index(name='الظهور')
                    st.plotly_chart(px.bar(top_g, x='الظهور', y='الضيف', orientation='h', color_discrete_sequence=['#10b981']), use_container_width=True)

    # --- التبويب 3: المقارنة المرنة ---
    with tabs[2]:
        st.markdown("### ⚖️ مصفوفة المقارنة المخصصة")
        dates = df_p['Date_Tag'].unique() if not df_p.empty else []
        selected = st.multiselect("اختر الأيام للمقارنة:", dates, default=dates[:2] if len(dates)>1 else dates)
        if selected:
            comp_df = df_p[df_p['Date_Tag'].isin(selected)]
            st.plotly_chart(px.bar(comp_df, x='شكل التقديم', y='Count', color='Date_Tag', barmode='group', template="plotly_dark"), use_container_width=True)

    # --- التبويب 4: التصدير ---
    with tabs[3]:
        st.markdown("### 📥 تصدير التقرير التنفيذي")
        st.info("المنصة مهيأة الآن للطباعة. اضغط (Ctrl + P) لحفظ التقرير كملف PDF عالي الجودة.")
        if not df_p.empty:
            st.table(df_p.pivot_table(index='شكل التقديم', columns='Date_Tag', values='Count', aggfunc='sum').fillna(0))

else:
    st.info("💎 أهلاً بك. يرجى رفع تقارير الرصد اليومي لبدء التحليل.")
