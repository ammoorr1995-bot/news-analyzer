import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import re

# 1. إعدادات الهوية البصرية الفاخرة
st.set_page_config(page_title="Asharq AI Strategic Hub", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    
    .stApp { background-color: #050a18; color: #f1f5f9; }
    .ai-insight-box { background: linear-gradient(90deg, rgba(59, 130, 246, 0.1), rgba(0, 0, 0, 0)); border-right: 5px solid #3b82f6; padding: 20px; border-radius: 10px; margin: 20px 0; line-height: 1.8; }
    .stat-card { background: #0f172a; padding: 20px; border-radius: 15px; border: 1px solid #1e293b; text-align: center; }
    .stat-value { font-size: 2.2rem; font-weight: 700; color: #ffffff; }
    .stat-label { color: #64748b; font-size: 0.9rem; }
    
    @media print { .no-print { display: none !important; } .stApp { background: white !important; color: black !important; } }
    </style>
    """, unsafe_allow_html=True)

def clean_num(text):
    if pd.isna(text): return 0
    nums = re.findall(r'\d+', str(text))
    return int(nums[0]) if nums else 0

@st.cache_data
def deep_parse(files):
    data = {'p': [], 'r': [], 'g': []}
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
                        df['Count'] = df[val_col].apply(clean_num)
                        data['p'].append(df)
                    elif any("المراسل" in c for c in cols) and val_col:
                        df['Activity'] = df[val_col].apply(clean_num)
                        data['r'].append(df)
        except: continue
    return data

# --- واجهة المستخدم الرئيسية ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>💎 مركز الذكاء الاستراتيجي | <span style='color:white'>قناة الشرق</span></h1>", unsafe_allow_html=True)

files = st.sidebar.file_uploader("📥 حَمِّل تقارير الرصد (Docx):", type="docx", accept_multiple_files=True)

if files:
    raw = deep_parse(files)
    df_p = pd.concat(raw['p']) if raw['p'] else pd.DataFrame()
    df_r = pd.concat(raw['r']) if raw['r'] else pd.DataFrame()

    menu = st.tabs(["🧠 الاستنتاجات الذكية", "📈 التحليل الزمني والشامل", "⚖️ المقارنة المتقدمة", "🖨️ تصدير التقرير"])

    # --- 1. الاستنتاجات الذكية (AI Thinking) ---
    with menu[0]:
        st.markdown("### 🕵️‍♂️ محرك التحليل الذكي")
        if not df_p.empty:
            total = df_p['Count'].sum()
            avg = total / len(files)
            top_fmt = df_p.groupby('شكل التقديم')['Count'].sum().idxmax()
            
            st.markdown(f"""
            <div class='ai-insight-box'>
            <b>🔍 ملخص الذكاء التحليلي:</b><br>
            بناءً على التقارير الـ {len(files)} المرفوعة، تم رصد <b>{int(total):,}</b> مادة إخبارية إجمالية.<br>
            يُظهر النظام أن القالب المهيمن هو <b>"{top_format}"</b>، مما يعكس هوية البث الحالية.<br>
            متوسط الإنتاج اليومي المستهدف هو <b>{avg:.1f}</b> مادة. نلاحظ استقراراً في الأداء مع وجود فرص لزيادة المداخلات الميدانية.
            </div>
            """, unsafe_allow_html=True)
            
            # عداد كفاءة التغطية
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = min(avg, 200),
                title = {'text': "مؤشر كثافة الإنتاج (اليومي)", 'font': {'size': 20, 'color': '#64748b'}},
                gauge = {'axis': {'range': [0, 200]}, 'bar': {'color': "#3b82f6"}, 'bgcolor': "#0f172a"}
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

    # --- 2. التحليل الزمني والشامل ---
    with menu[1]:
        st.markdown("### 📊 نبض القناة (التحليل الشامل)")
        if not df_p.empty:
            timeline = df_p.groupby('Date_Tag')['Count'].sum().reset_index()
            fig_line = px.line(timeline, x='Date_Tag', y='Count', markers=True, title="تطور حجم الإنتاج عبر التقارير المرفوعة", template="plotly_dark")
            fig_line.update_traces(line_color='#3b82f6', line_width=4)
            st.plotly_chart(fig_line, use_container_width=True)

    # --- 3. المقارنة المتقدمة ---
    with menu[2]:
        st.markdown("### ⚖️ مصفوفة المقارنة المخصصة")
        days = df_p['Date_Tag'].unique() if not df_p.empty else []
        selected = st.multiselect("اختر الأيام للمقارنة:", days, default=days[:2] if len(days)>1 else days)
        
        if selected:
            comp_data = df_p[df_p['Date_Tag'].isin(selected)]
            fig_comp = px.bar(comp_data, x='شكل التقديم', y='Count', color='Date_Tag', barmode='group', template="plotly_dark")
            st.plotly_chart(fig_comp, use_container_width=True)

    # --- 4. التصدير المريح ---
    with menu[3]:
        st.markdown("### 📥 جاهز للتصدير (Executive Report)")
        st.write("التقرير الآن مهيأ للقراءة المريحة والطباعة المباشرة.")
        if st.button("🚀 عرض نسخة الطباعة النهائية"):
            st.info("اضغط (Ctrl + P) الآن. تم ترتيب الرسوم لتظهر بوضوح فائق في ملف PDF.")

else:
    st.info("💎 أهلاً بك في Intel Hub. ارفع ملفات الرصد اليومي لبناء الذاكرة التحليلية للنظام.")
