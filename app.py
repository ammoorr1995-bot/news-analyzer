import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import re

# 1. إعدادات الفخامة (Executive UI)
st.set_page_config(page_title="Asharq AI Elite Suite", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    .stApp { background: #050a18; color: #f1f5f9; }
    .executive-card { background: #0f172a; padding: 20px; border-radius: 15px; border: 1px solid #1e293b; margin-bottom: 15px; }
    .stMetric { background: #1e293b; border-bottom: 4px solid #3b82f6; border-radius: 10px; }
    .profile-header { background: linear-gradient(90deg, #1e3a8a, #0f172a); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-right: 5px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# دالة تنظيف الأرقام
def clean_num(text):
    if pd.isna(text): return 0
    res = re.findall(r'\d+', str(text))
    return int(res[0]) if res else 0

# 2. محرك قراءة البيانات (Advanced Multi-Table Parser)
@st.cache_data
def advanced_parser(files):
    pool = {'p': [], 'r': [], 'g': [], 'o': []}
    for f in files:
        try:
            doc = Document(f)
            tag = f.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['Source'] = tag
                    cols = df.columns.tolist()
                    num_col = next((c for c in cols if any(k in c for k in ["العدد", "عدد", "مداخلات"])), None)
                    
                    if any("شكل التقديم" in c for c in cols) and num_col:
                        df['Count'] = df[num_col].apply(clean_num)
                        pool['p'].append(df)
                    elif any("المراسل" in c for c in cols) and num_col:
                        df['Count'] = df[num_col].apply(clean_num)
                        pool['r'].append(df)
                    elif any("الضيف" in c for c in cols): pool['g'].append(df)
                    elif any("المسؤول" in c for c in cols): pool['o'].append(df)
        except: continue
    return pool

# --- الواجهة الرئيسية ---
st.markdown("<h1 style='text-align: center; color: #3b82f6; margin-bottom:0;'>ASHARQ <span style='color:white'>ELITE SUITE</span></h1>", unsafe_allow_html=True)

uploaded = st.sidebar.file_uploader("📥 حَمِّل التقارير الاستراتيجية:", type="docx", accept_multiple_files=True)

if uploaded:
    data = advanced_parser(uploaded)
    df_p = pd.concat(data['p']) if data['p'] else pd.DataFrame()
    df_r = pd.concat(data['r']) if data['r'] else pd.DataFrame()
    df_g = pd.concat(data['g']) if data['g'] else pd.DataFrame()

    # التبويبات العلوية (تمت إضافة تبويب النجوم والموارد)
    tabs = st.tabs(["🚀 ملخص القيادة", "📅 التحليل اليومي", "⚖️ المقارنة الذكية", "🌟 النجوم والموارد", "📥 التصدير"])

    # --- تبويب 1: ملخص القيادة (AI Insight) ---
    with tabs[0]:
        st.markdown("### 🧠 مركز استنتاجات الذكاء الاصطناعي")
        if not df_p.empty:
            total = df_p['Count'].sum()
            avg = total / len(uploaded)
            st.metric("إجمالي الإنتاج الإخباري", f"{int(total):,}", f"بمعدل {avg:.1f} يومياً")
            fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=avg, gauge={'bar':{'color':"#3b82f6"}}))
            fig_gauge.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_gauge, use_container_width=True)

    # --- تبويب 2: تحليل يومي ---
    with tabs[1]:
        st.markdown("### 🔍 تفاصيل الأداء اليومي")
        day = st.selectbox("اختر اليوم:", df_p['Source'].unique() if not df_p.empty else [])
        st.plotly_chart(px.pie(df_p[df_p['Source']==day], values='Count', names='شكل التقديم', hole=0.5), use_container_width=True)

    # --- تبويب 3: المقارنة ---
    with tabs[2]:
        st.markdown("### ⚖️ مقارنة الأيام والفترات")
        sel_days = st.multiselect("اختر الأيام للمقارنة:", df_p['Source'].unique() if not df_p.empty else [])
        if sel_days:
            st.plotly_chart(px.bar(df_p[df_p['Source'].isin(sel_days)], x='شكل التقديم', y='Count', color='Source', barmode='group'), use_container_width=True)

    # --- تبويب 4: النجوم والموارد (الجديد والمطلوب) ---
    with tabs[3]:
        st.markdown("<div class='profile-header'><h3>🌟 محرك تحليل الموارد (مراسلين - ضيوف - مذيعين)</h3></div>", unsafe_allow_html=True)
        category = st.selectbox("اختر الفئة المستهدفة للتحليل:", ["🎙️ المراسلين والمناديب", "👥 الضيوف والخبراء", "👔 المذيعين وأداء الاستوديو"])
        
        if category == "🎙️ المراسلين والمناديب" and not df_r.empty:
            rep_name = st.selectbox("اختر اسم المراسل:", df_r['المراسل/الصحفي'].unique())
            rep_data = df_r[df_r['المراسل/الصحفي'] == rep_name]
            st.markdown(f"**إجمالي المداخلات لـ {rep_name}:** `{int(rep_data['Count'].sum())}`")
            st.plotly_chart(px.line(rep_data, x='Source', y='Count', title=f"منحنى نشاط {rep_name}"), use_container_width=True)
            
        elif category == "👥 الضيوف والخبراء" and not df_g.empty:
            guest_name = st.selectbox("اختر اسم الضيف:", df_g['الضيف'].unique())
            guest_data = df_g[df_g['الضيف'] == guest_name]
            st.markdown(f"**عدد مرات استضافة {guest_name}:** `{len(guest_data)}`")
            st.table(guest_data[['الصفة', 'Source']])

        elif category == "👔 المذيعين وأداء الاستوديو" and not df_p.empty:
            presenters = df_p[df_p['شكل التقديم'] == 'مذيع']
            # ميزة المقارنة الذاتية للمذيع
            st.markdown("#### ⚖️ مقارنة أداء المذيع (اليوم مقابل المتوسط العام)")
            avg_p = presenters.groupby('Source')['Count'].sum().mean()
            st.plotly_chart(px.bar(presenters, x='Source', y='Count', title="عدد مرات ظهور المذيع يومياً"), use_container_width=True)
            st.info(f"متوسط ظهور المذيع المعتاد هو: {avg_p:.1f} مرة باليوم.")

    # --- تبويب 5: التصدير ---
    with tabs[4]:
        st.markdown("### 📥 تصدير التقرير التنفيذي")
        if st.button("🚀 تجهيز نسخة PDF للطباعة"):
            st.success("اضغط (Ctrl + P) الآن. تم ترتيب الرسوم لتظهر في ورقة واحدة منظمة.")

else:
    st.info("💎 بانتظار رفع ملفات الرصد لتفعيل محرك الاستخبارات الإعلامية.")
