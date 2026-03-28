import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document
import re

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="Asharq Reporting System", layout="wide", page_icon="📊")

# تصميم CSS خاص للطباعة وللواجهة الداكنة
st.markdown("""
    <style>
    @media print {
        .no-print { display: none !important; }
        .stApp { background-color: white !important; color: black !important; }
        .report-header { text-align: center; color: #1e3a8a !important; }
    }
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    .report-box { background: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #334155; margin-bottom: 20px; }
    .ai-tag { background: #3b82f6; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(text):
    if pd.isna(text): return 0
    nums = re.findall(r'\d+', str(text))
    return int(nums[0]) if nums else 0

@st.cache_data
def parse_data(uploaded_files):
    pool = {'p': [], 'r': [], 'g': []}
    for file in uploaded_files:
        try:
            doc = Document(file)
            tag = file.name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    df['Date'] = tag
                    cols = df.columns.tolist()
                    col_num = next((c for c in cols if "العدد" in c or "عدد" in c), None)
                    if any("شكل التقديم" in c for c in cols) and col_num:
                        df['العدد'] = df[col_num].apply(clean_num)
                        pool['p'].append(df)
                    elif any("المراسل" in c for c in cols) and col_num:
                        df['عدد المداخلات'] = df[col_num].apply(clean_num)
                        pool['r'].append(df)
        except: continue
    return pool

# --- الواجهة الرئيسية ---
st.markdown("<div class='no-print'><h1 style='text-align: center;'>💎 مركز تصدير التقارير الذكية</h1></div>", unsafe_allow_html=True)

files = st.sidebar.file_uploader("📥 ارفع ملفات التقارير (docx):", type="docx", accept_multiple_files=True)

if files:
    data = parse_data(files)
    df_p = pd.concat(data['p']) if data['p'] else pd.DataFrame()
    df_r = pd.concat(data['r']) if data['r'] else pd.DataFrame()

    # --- منطقة اختيار الأيام للتصدير ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ إعدادات تصدير الـ PDF")
    all_days = df_p['Date'].unique() if not df_p.empty else []
    selected_days = st.sidebar.multiselect("اختر الأيام المراد تضمينها في التقرير والمقارنة:", all_days, default=all_days[:2] if len(all_days)>1 else all_days)

    if selected_days:
        # تصفية البيانات بناءً على اختيار المستخدم
        filtered_p = df_p[df_p['Date'].isin(selected_days)]
        filtered_r = df_r[df_r['Date'].isin(selected_days)]

        # --- بداية التقرير القابل للطباعة ---
        st.markdown(f"<div class='report-header'><h1>تقرير تحليل الأداء المقارن</h1><p>الأيام المختارة: {', '.join(selected_days)}</p></div>", unsafe_allow_html=True)

        # 1. المقارنة الإجمالية (Bar Chart)
        st.markdown("### 📊 مقارنة قوالب البث للأيام المختارة")
        fig1 = px.bar(filtered_p, x='شكل التقديم', y='العدد', color='Date', barmode='group', text='العدد', template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

        # 2. تحليل التوجه الزمني (Line Chart)
        st.markdown("### 📈 منحنى الإنتاج للأيام المختارة")
        trend = filtered_p.groupby('Date')['العدد'].sum().reset_index()
        fig2 = px.line(trend, x='Date', y='العدد', markers=True, template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

        # 3. جدول المقارنة التفصيلي (للطباعة)
        st.markdown("### 📋 جدول البيانات المقارن")
        comparison_table = filtered_p.pivot_table(index='شكل التقديم', columns='Date', values='العدد', aggfunc='sum').fillna(0)
        st.table(comparison_table)

        # 4. زر التصدير (التنبيه)
        st.markdown("---")
        st.markdown("<div class='no-print ai-tag'>💡 جاهز للتصدير!</div>", unsafe_allow_html=True)
        if st.button("🚀 توليد نسخة PDF للطباعة"):
            st.info("الآن اضغط على لوحة المفاتيح: **Ctrl + P** (أو Cmd + P في الماك) ثم اختر **Save as PDF**. الموقع مهيأ لإخفاء الأزرار الجانبية وطباعة الرسوم فقط.")
        
    else:
        st.warning("يرجى اختيار يوم واحد على الأقل من القائمة الجانبية لتوليد التقرير.")

else:
    st.info("👈 يرجى رفع ملفات الوورد من القائمة الجانبية لتفعيل نظام التقارير.")
