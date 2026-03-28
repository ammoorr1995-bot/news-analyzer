import os
import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document

# 1. إعدادات الصفحة
st.set_page_config(page_title="Asharq News Analytics", layout="wide", page_icon="🌐")

# تصميم CSS
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .hero-banner { background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); color: white; padding: 40px 20px; border-radius: 15px; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 30px; }
    .hero-banner h1 { color: #ffffff !important; font-size: 3em; margin-bottom: 10px; font-weight: 700; }
    .stMetric { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-right: 5px solid #1976d2; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. دالة استخراج البيانات (محدثة بأقوى طريقة للبحث)
def process_server_files():
    all_data = {'presentation': [], 'category': [], 'reporters': [], 'guests': [], 'officials': []}
    
    # استخدام المسار الأساسي لبيئة العمل (الأكثر أماناً في Streamlit)
    current_dir = os.getcwd()
    
    # جلب قائمة بكل الملفات الموجودة في السيرفر (لأغراض الفحص)
    all_files_in_dir = os.listdir(current_dir)
    
    # البحث بمرونة: تجاهل حالة الأحرف والتأكد من عدم وجود مسافات مخفية
    docx_files = [f for f in all_files_in_dir if f.strip().lower().endswith('.docx') and not f.startswith('~')]
    
    for file_name in docx_files:
        file_path = os.path.join(current_dir, file_name)
        try:
            doc = Document(file_path)
            report_name = file_name.replace('.docx', '')
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    cols = df.columns.tolist()
                    df['التقرير'] = report_name
                    
                    if 'شكل التقديم' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        all_data['presentation'].append(df[['التقرير', 'شكل التقديم', 'العدد']])
                    elif 'التصنيف' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        all_data['category'].append(df[['التقرير', 'التصنيف', 'العدد']])
                    elif 'المراسل/الصحفي' in cols and 'عدد المداخلات' in cols:
                        df['عدد المداخلات'] = pd.to_numeric(df['عدد المداخلات'], errors='coerce').fillna(0)
                        all_data['reporters'].append(df[['التقرير', 'المراسل/الصحفي', 'عدد المداخلات']])
                    elif 'الضيف' in cols and 'الصفة' in cols:
                        all_data['guests'].append(df)
                    elif 'المسؤول' in cols and 'الصفة' in cols:
                        all_data['officials'].append(df)
        except Exception:
            continue
            
    return all_data, docx_files, all_files_in_dir, current_dir

# 3. القائمة الجانبية
st.sidebar.markdown("## 🌐 قناة الشرق | تحليلات")
st.sidebar.markdown("---")
menu = st.sidebar.radio("القائمة الرئيسية:", ["🏠 الصفحة الرئيسية", "📊 لوحة الأداء العام", "📈 مقارنة التقارير الزمنية", "🗄️ قاعدة البيانات الخام"])

# معالجة البيانات
with st.spinner("جاري مسح السيرفر وقراءة البيانات..."):
    data, server_files, all_files, active_dir = process_server_files()

df_p = pd.concat(data['presentation']) if data['presentation'] else pd.DataFrame()
df_c = pd.concat(data['category']) if data['category'] else pd.DataFrame()
df_r = pd.concat(data['reporters']) if data['reporters'] else pd.DataFrame()
df_g = pd.concat(data['guests']) if data['guests'] else pd.DataFrame()
df_o = pd.concat(data['officials']) if data['officials'] else pd.DataFrame()

# ==========================================
# الصفحة الأولى: الرئيسية + رادار الفحص
# ==========================================
if menu == "🏠 الصفحة الرئيسية":
    st.markdown('<div class="hero-banner"><h1>منصة تحليلات البث الإخباري</h1><p>لوحة تحكم حية تعرض بيانات الرصد الإخباري لقناة الشرق</p></div>', unsafe_allow_html=True)
    
    if not server_files:
        st.error("لم يتم العثور على تقارير الوورد حتى الآن. يرجى الانتظار دقيقة وتحديث الصفحة، أو مراجعة رادار السيرفر بالأسفل.")
        
        # رادار السيرفر (يظهر فقط عند وجود مشكلة)
        st.warning("🔍 **رادار فحص السيرفر (مخصص للمطورين):**")
        st.write(f"**المسار الحالي الذي يبحث فيه الموقع:** `{active_dir}`")
        st.write("**قائمة بكل الملفات التي يراها الموقع حالياً:**")
        st.code(all_files)
        st.info("إذا لم تكن ملفات (اليوم الأول، اليوم الثاني...) موجودة في القائمة أعلاه، فهذا يعني أن سيرفر Streamlit لم يقم بسحبها من GitHub بعد. انتظر دقيقتين وقم بعمل Reboot App مجدداً.")
        
    else:
        st.success(f"✅ تم تحميل البيانات بنجاح! يوجد حالياً ({len(server_files)}) تقارير متصلة باللوحة (مثل: {server_files[0]}). تنقل بين الصفحات من القائمة الجانبية.")

# ==========================================
# باقي الصفحات
# ==========================================
elif menu == "📊 لوحة الأداء العام":
    st.title("📊 لوحة الأداء الإجمالي")
    if not server_files: st.warning("لا توجد بيانات للعرض.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("المواد الإخبارية", f"{int(df_p['العدد'].sum()) if not df_p.empty else 0:,}")
        col2.metric("حجم المراسلين", f"{len(df_r['المراسل/الصحفي'].unique()) if not df_r.empty else 0}")
        col3.metric("الضيوف والخبراء", f"{len(df_g) if not df_g.empty else 0}")
        col4.metric("تصريحات المسؤولين", f"{len(df_o) if not df_o.empty else 0}")
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🎯 قوالب التغطية")
            if not df_p.empty:
                comb_p = df_p.groupby('شكل التقديم')['العدد'].sum().reset_index().sort_values(by='العدد', ascending=True)
                fig_p = px.bar(comb_p, x='العدد', y='شكل التقديم', orientation='h', text='العدد', color='شكل التقديم', color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_p.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_p, use_container_width=True)
        with c2:
            st.markdown("#### 🌍 التوزيع الموضوعي")
            if not df_c.empty:
                comb_c = df_c.groupby('التصنيف')['العدد'].sum().reset_index()
                fig_c = px.pie(comb_c, values='العدد', names='التصنيف', hole=0.5, color_discrete_map={'سياسة': '#ef553b', 'اقتصاد': '#00cc96'})
                st.plotly_chart(fig_c, use_container_width=True)

elif menu == "📈 مقارنة التقارير الزمنية":
    st.title("📈 مقارنة الاتجاهات الزمنية والأداء")
    if not server_files: st.warning("لا توجد بيانات للعرض.")
    else:
        tab1, tab2 = st.tabs(["👥 مقارنة تواجد الضيوف", "🏗️ مقارنة الإنتاج الخبري"])
        with tab1:
            if not df_g.empty:
                guest_trend = df_g.groupby('التقرير').size().reset_index(name='عدد الضيوف')
                fig_trend = px.area(guest_trend, x='التقرير', y='عدد الضيوف', markers=True, color_discrete_sequence=['#1976d2'])
                st.plotly_chart(fig_trend, use_container_width=True)
        with tab2:
            if not df_p.empty:
                fig_stacked = px.bar(df_p, x='التقرير', y='العدد', color='شكل التقديم', text='العدد', barmode='stack')
                fig_stacked.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_stacked, use_container_width=True)

elif menu == "🗄️ قاعدة البيانات الخام":
    st.title("🗄️ مستكشف البيانات")
    if not server_files: st.warning("لا توجد بيانات للعرض.")
    else:
        reports_list = ["الكل"] + list(df_g['التقرير'].unique() if not df_g.empty else [])
        report_filter = st.selectbox("تصفية حسب التقرير:", reports_list)
        if not df_g.empty:
            st.markdown("#### 🎙️ سجل الضيوف والخبراء")
            display_df = df_g if report_filter == "الكل" else df_g[df_g['التقرير'] == report_filter]
            st.dataframe(display_df, use_container_width=True)
