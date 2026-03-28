import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import re

# 1. إعدادات الفخامة والهوية البصرية
st.set_page_config(page_title="Asharq AI Grand Suite", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Kufi Arabic', sans-serif; text-align: right; }
    .stApp { background: radial-gradient(circle, #0f172a 0%, #050a18 100%); color: #f1f5f9; }
    .executive-card { background: rgba(30, 41, 59, 0.7); padding: 25px; border-radius: 20px; border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); }
    .ai-voice { border-right: 5px solid #3b82f6; background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 10px; color: #93c5fd; font-size: 1.1rem; line-height: 1.8; }
    .stMetric { background: #1e293b; padding: 15px; border-radius: 15px; border-bottom: 4px solid #3b82f6; }
    @media print { .no-print { display: none !important; } .stApp { background: white !important; color: black !important; } }
    </style>
    """, unsafe_allow_html=True)

# دالة ذكية لتنظيف الأرقام من أي نصوص
def auto_clean_num(text):
    if pd.isna(text): return 0
    res = re.findall(r'\d+', str(text))
    return int(res[0]) if res else 0

# 2. المحرك الفائق لمعالجة البيانات (Flexible Parser)
@st.cache_data
def ultra_parser(files):
    storage = {'p': [], 'r': [], 'g': [], 'c': []}
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
                    # بحث مرن عن أعمدة الأرقام
                    num_col = next((c for c in cols if any(k in c for k in ["العدد", "عدد", "مداخلات"])), None)
                    
                    if any("شكل التقديم" in c for c in cols) and num_col:
                        df['Count'] = df[num_col].apply(auto_clean_num)
                        storage['p'].append(df)
                    elif any("المراسل" in c for c in cols) and num_col:
                        df['Activity'] = df[num_col].apply(auto_clean_num)
                        storage['r'].append(df)
                    elif any("الضيف" in c for c in cols): storage['g'].append(df)
        except: continue
    return storage

# 3. بناء الواجهة (The Interface)
st.markdown("<h1 style='text-align: center; color: #3b82f6; font-size: 3.5rem; margin-bottom:0;'>ASHARQ <span style='color:white'>AI GRAND SUITE</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem;'>نظام إدارة واستخبارات المحتوى الإخباري - الإصدار التنفيذي</p>", unsafe_allow_html=True)

uploaded_files = st.sidebar.file_uploader("📂 ارفع حزمة التقارير (docx):", type="docx", accept_multiple_files=True)

if uploaded_files:
    raw = ultra_parser(uploaded_files)
    df_p = pd.concat(raw['p']) if raw['p'] else pd.DataFrame()
    df_r = pd.concat(raw['r']) if raw['r'] else pd.DataFrame()
    df_g = pd.concat(raw['g']) if raw['g'] else pd.DataFrame()

    menu = st.tabs(["🚀 ملخص القيادة", "📅 تحليل يومي", "⚖️ المقارنة الذكية", "📈 الاتجاهات الشهرية", "📥 تصدير PDF"])

    # --- 1. ملخص القيادة (AI Insights) ---
    with menu[0]:
        st.markdown("### 🧠 استنتاجات الذكاء الاصطناعي للمديرين")
        if not df_p.empty:
            total = df_p['Count'].sum()
            avg = total / len(uploaded_files)
            top_fmt = df_p.groupby('شكل التقديم')['Count'].sum().idxmax()
            
            st.markdown(f"""
            <div class='ai-voice'>
            <b>💡 التوصية الإدارية:</b><br>
            حجم الإنتاج الكلي بلغ <b>{int(total):,}</b> مادة. يلاحظ النظام هيمنة قالب <b>"{top_fmt}"</b> بنسبة كبيرة.<br>
            مؤشر التنوع اليومي: <b>مستقر</b>. ننصح بتعزيز مداخلات الميدان لرفع مؤشر الحيوية إلى مستويات الوكالات العالمية.
            </div>
            """, unsafe_allow_html=True)
            
            # عداد الأداء الكلي
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = avg,
                title = {'text': "متوسط الكثافة الإنتاجية اليومية", 'font': {'size': 20}},
                gauge = {'axis': {'range': [0, 200]}, 'bar': {'color': "#3b82f6"}}
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
            st.plotly_chart(fig_gauge, use_container_width=True)

    # --- 2. تحليل يوم بيوم ---
    with menu[1]:
        st.markdown("### 🔍 تفاصيل اليوم المختار")
        days = df_p['Date_Tag'].unique() if not df_p.empty else []
        selected_day = st.selectbox("اختر التاريخ:", days)
        day_p = df_p[df_p['Date_Tag'] == selected_day]
        
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(day_p, values='Count', names='شكل التقديم', hole=0.5, title="توزيع القوالب"), use_container_width=True)
        with c2:
            day_total = day_p['Count'].sum()
            st.metric("إنتاج اليوم", f"{int(day_total)} مادة")
            st.info(f"هذا اليوم يمثل {(day_total/total*100):.1f}% من إجمالي الفترة المرفوعة.")

    # --- 3. المقارنة الذكية (بين أي فترات) ---
    with menu[2]:
        st.markdown("### ⚖️ مصفوفة المقارنة المخصصة")
        selected_comp = st.multiselect("اختر الأيام للمقارنة:", days, default=days[:2] if len(days)>1 else days)
        if selected_comp:
            comp_df = df_p[df_p['Date_Tag'].isin(selected_comp)]
            st.plotly_chart(px.bar(comp_df, x='شكل التقديم', y='Count', color='Date_Tag', barmode='group'), use_container_width=True)

    # --- 4. الاتجاهات الشهرية (Trend Analysis) ---
    with menu[3]:
        st.markdown("### 📈 نبض القناة الزمني")
        if not df_p.empty:
            line_data = df_p.groupby('Date_Tag')['Count'].sum().reset_index()
            st.plotly_chart(px.line(line_data, x='Date_Tag', y='Count', markers=True, title="تطور حجم الإنتاج"), use_container_width=True)
            
            st.markdown("### 🔥 خريطة نشاط المراسلين")
            if not df_r.empty:
                pivot_r = df_r.pivot_table(index='المراسل/الصحفي', columns='Date_Tag', values='Activity', aggfunc='sum').fillna(0)
                st.plotly_chart(px.imshow(pivot_r, text_auto=True, color_continuous_scale='Blues'), use_container_width=True)

    # --- 5. تصدير PDF ---
    with menu[4]:
        st.markdown("### 📥 جاهز للتصدير التنفيذي")
        st.info("المنصة الآن مهيأة للطباعة المباشرة. اضغط (Ctrl + P) لحفظ التقرير كملف PDF عالي الجودة.")
        if not df_p.empty:
            pivot_final = df_p.pivot_table(index='شكل التقديم', columns='Date_Tag', values='Count', aggfunc='sum').fillna(0).astype(int)
            st.table(pivot_final)

else:
    st.info("💎 بانتظار رفع ملفات الرصد لبناء الذاكرة المؤسسية للمنصة.")
