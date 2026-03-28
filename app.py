# ----------------------------------------
    # التبويب الأول: نظرة عامة (Overview)
    # ----------------------------------------
    with tab1:
        st.markdown("### 📈 مؤشرات الأداء المجمعة")
        col1, col2, col3, col4 = st.columns(4)
        
        total_mats = int(pd.concat(data['presentation'])['العدد'].sum()) if data['presentation'] else 0
        total_reporters = len(pd.concat(data['reporters'])['المراسل/الصحفي'].unique()) if data['reporters'] else 0
        total_guests = sum([len(df) for df in data['guests']]) if data['guests'] else 0
        total_officials = sum([len(df) for df in data['officials']]) if data['officials'] else 0

        col1.metric("إجمالي المواد الإخبارية", f"{total_mats:,}")
        col2.metric("حجم شبكة المراسلين", f"{total_reporters}")
        col3.metric("إجمالي الضيوف والخبراء", f"{total_guests}")
        col4.metric("تصريحات المسؤولين", f"{total_officials}")
        
        st.markdown("---")
        if data['presentation']:
            st.markdown("#### 🎯 تفاصيل قوالب العرض (مفصلة)")
            
            # تجهيز وترتيب البيانات من الأكبر للأصغر
            comb_p = pd.concat(data['presentation']).groupby('شكل التقديم').sum().reset_index()
            comb_p = comb_p.sort_values(by='العدد', ascending=False)
            
            # 1. عرض أبرز القوالب في بطاقات منفصلة (فصل التصنيفات)
            top_formats = st.columns(min(4, len(comb_p)))
            for i in range(min(4, len(comb_p))):
                top_formats[i].info(f"**{comb_p.iloc[i]['شكل التقديم']}** \n\n {int(comb_p.iloc[i]['العدد'])} مادة")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 2. مخطط أعمدة أفقي يفصل كل قالب بوضوح
            fig_p = px.bar(comb_p, x='العدد', y='شكل التقديم', orientation='h',
                           text='العدد', color='شكل التقديم',
                           color_discrete_sequence=px.colors.qualitative.Prism)
            
            # تحسين شكل المخطط ليكون جذاباً
            fig_p.update_traces(textposition='outside')
            fig_p.update_layout(showlegend=False, 
                                yaxis={'categoryorder':'total ascending'},
                                plot_bgcolor='rgba(0,0,0,0)',
                                xaxis_title="", yaxis_title="")
            
            st.plotly_chart(fig_p, use_container_width=True)
