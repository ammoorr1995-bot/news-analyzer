import streamlit as st
import pandas as pd
import plotly.express as px

# إعدادات الصفحة الاحترافية (العرض الكامل)
st.set_page_config(page_title="Asharq Analytics Hub", layout="wide", page_icon="📺")

# تصميم CSS متقدم لواجهة أكثر جاذبية
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #1877f2; }
    h1, h2, h3 { color: #202124; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 600; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #ffffff; border-radius: 8px 8px 0 0; padding: 10px 20px; box-shadow: 0 -2px 5px rgba(0,0,0,0.02); }
    .stTabs [aria-selected="true"] { background-color: #1877f2; color: white; }
    </style>
    """, unsafe_allow_html=True)

from docx import Document

@st.cache_data # تسريع أداء الموقع عند تحميل نفس الملفات
def process_files(uploaded_files):
    all_data = {'presentation': [], 'category': [], 'reporters': [], 'guests': [], 'officials': []}
    
    for file in uploaded_files:
        try:
            doc = Document(file)
            for table in doc.tables:
                rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if len(rows) > 1:
                    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])
                    cols = df.columns.tolist()
                    
                    # 1. شكل التقديم
                    if 'شكل التقديم' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        all_data['presentation'].append(df[['شكل التقديم', 'العدد']])
                    
                    # 2. التصنيف (سياسة/اقتصاد)
                    elif 'التصنيف' in cols and 'العدد' in cols:
                        df['العدد'] = pd.to_numeric(df['العدد'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
                        all_data['category'].append(df[['التصنيف', 'العدد']])
                        
                    # 3. المراسلين
                    elif 'المراسل/الصحفي' in cols and 'عدد المداخلات' in cols:
                        df['عدد المداخلات'] = pd.to_numeric(df['عدد المداخلات'], errors='coerce').fillna(0)
                        all_data['reporters'].append(df[['المراسل/الصحفي', 'عدد المداخلات']])
                    
                    # 4. الضيوف والخبراء
                    elif 'الضيف' in cols and 'الصفة' in cols:
                        all_data['guests'].append(df)
                        
                    # 5. تصريحات المسؤولين
                    elif 'المسؤول' in cols and 'الصفة' in cols:
                        all_data['officials'].append(df)
        except Exception:
            continue
            
    return all_data

# --- رأس الصفحة ---
st.title("📺 مركز تحليلات البث الإخباري - قناة الشرق")
st.markdown("لوحة تحكم تفاعلية متقدمة لتحليل الأداء والمحتوى والضيوف")

uploaded_files = st.file_uploader("ارفق تقارير الرصد الشاملة (يمكنك تحديد عدة تقارير معاً)", type="docx", accept_multiple_files=True)

if uploaded_files:
    with st.spinner("جاري المعالجة والتحليل العميق للبيانات..."):
        data = process_files(uploaded_files)
    
    st.success(f"تم تحليل {len(uploaded_files)} تقارير وتجميع البيانات بنجاح.")
    st.markdown("---")
    
    # بناء التبويبات للواجهة
    tab1, tab2, tab3, tab4 = st.tabs(["📊 نظرة عامة", "🌍 التصنيف السياسي والاقتصادي", "🎙️ شبكة التغطية (مراسلين وضيوف)", "📋 الجداول والبيانات الخام"])
    
    # ----------------------------------------
    # التبويب الأول: نظرة عامة (Overview)
    # ----------------------------------------
    with tab1:
        st.markdown("### 📈 مؤشرات الأداء المجمعة")
        col1, col2, col3, col4 = st.columns(4)
        
        # حساب الإجماليات
        total_mats = 0
        if data['presentation']:
            total_mats = int(pd.concat(data['presentation'])['العدد'].sum())
            
        total_reporters = 0
        if data['reporters']:
            total_reporters = len(pd.concat(data['reporters'])['المراسل/الصحفي'].unique())
            
        total_guests = sum([len(df) for df in data['guests']]) if data['guests'] else 0
        total_officials = sum([len(df) for df in data['officials']]) if data['officials'] else 0

        col1.metric("إجمالي المواد الإخبارية", f"{total_mats:,}")
        col2.metric("حجم شبكة المراسلين", f"{total_reporters}")
        col3.metric("إجمالي الضيوف والخبراء", f"{total_guests}")
        col4.metric("تصريحات المسؤولين", f"{total_officials}")
        
        st.markdown("---")
        if data['presentation']:
            st.markdown("#### 🎯 قوالب العرض الإخباري")
            comb_p = pd.concat(data['presentation']).groupby('شكل التقديم').sum().reset_index()
            fig_p = px.pie(comb_p, values='العدد', names='شكل التقديم', hole=0.5, 
                           color_discrete_sequence=px.colors.qualitative.Prism)
            fig_p.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_p, use_container_width=True)

    # ----------------------------------------
    # التبويب الثاني: التصنيف الموضوعي (سياسة / اقتصاد)
    # ----------------------------------------
    with tab2:
        st.markdown("### 🌍 تحليل المحتوى: سياسة مقابل اقتصاد")
        if data['category']:
            comb_c = pd.concat(data['category']).groupby('التصنيف').sum().reset_index()
            
            c1, c2 = st.columns([2, 1])
            with c1:
                # رسم بياني شريطي متطور
                fig_c = px.bar(comb_c, x='التصنيف', y='العدد', color='التصنيف', 
                               text='العدد', color_discrete_map={'سياسة': '#ef553b', 'اقتصاد': '#00cc96'})
                fig_c.update_traces(textposition='outside')
                fig_c.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', yaxis_title="عدد المواد", xaxis_title="")
                st.plotly_chart(fig_c, use_container_width=True)
            with c2:
                st.info("💡 يعكس هذا التصنيف تركيز التغطية. يمكنك ملاحظة طغيان الملف السياسي أثناء التغطيات الخاصة أو الحروب، بينما يبرز الاقتصاد في أوقات الأزمات المالية أو تأثير الممرات المائية.")
                st.dataframe(comb_c.style.background_gradient(cmap='Blues'), use_container_width=True)
        else:
            st.warning("لم يتم العثور على جداول 'التصنيف' في التقارير المرفوعة.")

    # ----------------------------------------
    # التبويب الثالث: شبكة التغطية والضيوف
    # ----------------------------------------
    with tab3:
        st.markdown("### 🎙️ خريطة المراسلين وأبرز الضيوف")
        r1, r2 = st.columns(2)
        
        with r1:
            if data['reporters']:
                st.markdown("#### أعلى 10 مراسلين نشاطاً")
                comb_r = pd.concat(data['reporters']).groupby('المراسل/الصحفي').sum().reset_index()
                top_r = comb_r.sort_values(by='عدد المداخلات', ascending=False).head(10)
                fig_r = px.bar(top_r, x='عدد المداخلات', y='المراسل/الصحفي', orientation='h', color='عدد المداخلات', color_continuous_scale='Blues')
                fig_r.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_r, use_container_width=True)
                
        with r2:
            if data['guests']:
                st.markdown("#### تصنيف الضيوف الميدانيين والخبراء")
                comb_g = pd.concat(data['guests'])
                # إحصاء تكرار صفات الضيوف (محلل سياسي، خبير عسكري، إلخ)
                guest_types = comb_g['الصفة'].value_counts().reset_index()
                guest_types.columns = ['صفة الضيف', 'التكرار']
                fig_g = px.treemap(guest_types.head(15), path=['صفة الضيف'], values='التكرار', color='التكرار', color_continuous_scale='Teal')
                st.plotly_chart(fig_g, use_container_width=True)
            else:
                st.info("لا توجد بيانات للضيوف في هذا التقرير.")

    # ----------------------------------------
    # التبويب الرابع: الجداول التفصيلية (Data Tables)
    # ----------------------------------------
    with tab4:
        st.markdown("### 📋 استعراض البيانات التفصيلية")
        st.write("استخدم هذه الجداول للبحث، الترتيب، أو النسخ مباشرة.")
        
        if data['officials']:
            st.markdown("**أبرز تصريحات المسؤولين:**")
            st.dataframe(pd.concat(data['officials']), use_container_width=True)
            
        if data['guests']:
            st.markdown("**سجل الضيوف والخبراء:**")
            st.dataframe(pd.concat(data['guests']), use_container_width=True)
            
        if data['reporters']:
            st.markdown("**سجل المداخلات للمراسلين:**")
            comb_r_full = pd.concat(data['reporters']).groupby('المراسل/الصحفي').sum().reset_index().sort_values(by='عدد المداخلات', ascending=False)
            st.dataframe(comb_r_full, use_container_width=True)
