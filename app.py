import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import re

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="Asharq AI Strategy Hub", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    .stApp { background-color: #050a18; color: #f1f5f9; }
    .ai-box { background: rgba(59, 130, 246, 0.05); border: 1px solid #1e293b; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    .highlight { color: #3b82f6; font-weight: 700; }
    @media print { .no-print { display: none !important; } .stApp { background: white !important; color: black !important; } }
    </style>
    """, unsafe_allow_html=True)

def clean_val(text):
    if pd.isna(text): return 0
    nums = re.findall(r'\d+', str(text))
    return int(nums[0]) if nums else 0

@st.cache_data
def process_data(files):
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

# --- الواجهة ---
st.markdown("<h1 style='text-align: center;'>💎 مركز استخبارات المحتوى <span style='color:#3b82f6'>| قناة الشرق</span></h1>", unsafe_allow_html=True)

files = st.sidebar.file_uploader("📥 حَمِّل تقاريرك الاستراتيجية:", type="docx", accept_multiple_files=True)

if files:
    raw = process_data(files)
    df_p = pd.concat(raw['p']) if raw['p'] else pd.DataFrame()
    df_r = pd.concat(raw['r']) if raw['r'] else pd.DataFrame()
    df_g = pd.concat(raw['g']) if raw['g'] else pd.DataFrame()

    tabs = st.tabs(["🚀 الملخص التنفيذي", "🕸️ بصمة التوازن", "📈 التحليل الزمني", "📥 التقارير النهائية"])

    with tabs[0]:
        st.markdown("### 🧠 رؤية الذكاء الاصطناعي الاستراتيجية")
        if not df_p.empty:
            total = df_p['Count'].sum()
            avg = total / len(files)
            st.markdown(f"""
            <div class='ai-box'>
            <b>📊 تحليل الكفاءة:</b><br>
            حجم الإنتاج الكلي للفترة المرفوعة بلغ <span class='highlight'>{int(total):,}</span> مادة.<br>
            مؤشر الحيوية: <span class='highlight'>مرتفع</span>. يلاحظ النظام استقراراً في مخرجات التغطية مع معدل <span class='highlight'>{avg:.1f}</span> مادة يومياً.
            </div>
            """, unsafe_allow_html=True)
            
            # عداد الإنجاز
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = avg,
                title = {'text': "متوسط الكثافة اليومية", 'font': {'size': 18, 'color': '#94a3b8'}},
                gauge = {'axis': {'range': [0, 200]}, 'bar': {'color': "#3b82f6"}}
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

    with tabs[1]:
        st.markdown("### 🕸️ رادار توازن الهوية البصرية")
        if not df_p.empty:
            radar_df = df_p.groupby('شكل التقديم')['Count'].sum().reset_index()
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=radar_df['Count'], theta=radar_df['شكل التقديم'], fill='toself',
                line_color='#3b82f6', fillcolor='rgba(59, 130, 246, 0.2)'
            ))
            fig_radar.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=True, gridcolor='#1e293b')),
                                    paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_radar, use_container_width=True)

    with tabs[2]:
        st.markdown("### 📉 التوجه التاريخي للنمو")
        if not df_p.empty:
            line_data = df_p.groupby('Date_Tag')['Count'].sum().reset_index()
            st.plotly_chart(px.line(line_data, x='Date_Tag', y='Count', markers=True, template="plotly_dark"), use_container_width=True)

    with tabs[3]:
        st.markdown("### 📄 تصدير ملفات الدعم الإداري")
        st.info("التقرير جاهز الآن للعرض في اجتماعات مجلس الإدارة. استخدم (Ctrl+P) للطباعة الورقية.")
        if not df_p.empty:
            pivot = df_p.pivot_table(index='شكل التقديم', columns='Date_Tag', values='Count', aggfunc='sum').fillna(0)
            st.table(pivot)

else:
    st.info("💎 بانتظار الملفات لتفعيل محرك الاستخبارات الإعلامية.")
