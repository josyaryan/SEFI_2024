import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json
from branca.colormap import LinearColormap
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt

# Konfigurasi awal dashboard
st.set_page_config(
    layout="wide", 
    page_title="SUMUT CERDAS",
    initial_sidebar_state="collapsed"
)

# Sembunyikan menu hamburger, footer, dan header
hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            .stDeployButton {display:none !important;}
            footer {visibility: hidden !important;}
            header {visibility: hidden !important;}
            #MainMenu {visibility: hidden !important;}
            div.block-container {padding-top:0rem !important;}
            [data-testid="stHeader"] {visibility: hidden !important;}
            [data-testid="stSidebar"] {visibility: hidden !important;}
            section[data-testid="stSidebar"] {display: none !important;}
            div.viewerBadge_container__1QSob {display: none !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom CSS untuk styling
st.markdown("""
    <style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 24px;
        text-align: center;
        color: #666;
        margin-bottom: 20px;
    }
    .period-text {
        font-size: 20px;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Judul Dashboard
st.markdown('<p class="main-title">SUMUT CERDAS</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Sumatera Utara Cerminan Data Inklusi Keuangan dan Kesejahteraan</p>', unsafe_allow_html=True)
st.markdown('<p class="period-text">Periode 2019-2023</p>', unsafe_allow_html=True)

# Buat tabs
tab1, tab2 = st.tabs(["Analisis Cluster", "Korelasi & Prediksi"])

# Definisi warna dan label cluster
cluster_colors = {
    0: '#4D96FF',  # untuk Wilayah Maju/Kota Besar
    1: '#FFD93D',  # untuk Wilayah Berkembang dengan Tantangan Kemiskinan
    2: '#FF6B6B',  # untuk Wilayah Tertinggal
    3: '#6BCB77'   # untuk Wilayah Menengah/Transisi
}

cluster_labels = {
    0: 'Wilayah Maju/Kota Besar',
    1: 'Wilayah Berkembang dengan Tantangan Kemiskinan',
    2: 'Wilayah Tertinggal',
    3: 'Wilayah Menengah/Transisi'
}

with tab1:
    try:
        data = pd.read_excel('hasil_cluster_sumut.xlsx')
        with open('prov_bykabkota.geojson') as f:
            geojson_data = json.load(f)

        # Buat layout dengan 2 kolom
        col1, col2 = st.columns([4,1])

        with col1:
            # Filter tahun
            years = sorted(data['tahun'].unique())
            selected_year = st.selectbox("Pilih Tahun", years)
            
            # Buat peta dengan ukuran yang lebih besar
            m = folium.Map(location=[2.5, 98.7], zoom_start=7)
            
            # Set ukuran container untuk peta
            st.markdown(
                """
                <style>
                iframe {
                    width: 100%;
                    min-height: 800px;
                    height: 800px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Filter data tahun terpilih
            year_data = data[data['tahun'] == selected_year]
            
            # Tambahkan color scale
            colormap = LinearColormap(
                colors=['#4D96FF', '#FFD93D', '#FF6B6B', '#6BCB77'],
                vmin=0,
                vmax=3
            )
            m.add_child(colormap)
            
            # Tambahkan popup dengan informasi detail
            for feature in geojson_data['features']:
                kabupaten = feature['properties']['nmkab']
                if kabupaten in year_data['kab_kota'].values:
                    row = year_data[year_data['kab_kota'] == kabupaten].iloc[0]
                    cluster = row['Cluster']
                    
                    # Buat konten popup
                    popup_content = f"""
                    <div style="font-family: Arial; padding: 10px;">
                        <h4 style="margin-bottom: 10px;">{kabupaten}</h4>
                        <p style="margin: 5px 0;"><b>Cluster:</b> {cluster} ({cluster_labels[cluster]})</p>
                    """
                    
                    # Tambahkan variabel lain dari excel jika ada
                    for col in year_data.columns:
                        if col not in ['kab_kota', 'Cluster', 'tahun']:
                            popup_content += f'<p style="margin: 5px 0;"><b>{col}:</b> {row[col]}</p>'
                    
                    popup_content += "</div>"
                    
                    # Definisikan style untuk feature ini
                    style_function = lambda x, cluster=cluster: {
                        'fillColor': cluster_colors[cluster],
                        'fillOpacity': 0.7,
                        'color': 'white',
                        'weight': 1
                    }
                    
                    # Buat popup dan tambahkan ke feature
                    popup = folium.Popup(popup_content, max_width=300)
                    
                    # Tambahkan GeoJSON untuk feature ini
                    folium.GeoJson(
                        feature,
                        style_function=style_function,
                        highlight_function=lambda x: {
                            'fillOpacity': 0.9,
                            'weight': 2,
                            'color': 'black'
                        },
                        popup=popup,
                        tooltip=folium.GeoJsonTooltip(
                            fields=['nmkab'],
                            aliases=['Kabupaten/Kota:'],
                            style='background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;'
                        )
                    ).add_to(m)

            # Legend dengan deskripsi yang lebih lengkap
            legend_html = """
            <div style="position: fixed; 
                        bottom: 50px; 
                        left: 50px; 
                        z-index: 1000; 
                        background-color: white; 
                        padding: 15px;
                        border: 2px solid grey; 
                        border-radius: 5px;
                        font-family: Arial, sans-serif;
                        box-shadow: 0 0 15px rgba(0,0,0,0.2);">
                <h4 style="margin-bottom: 10px; color: #333;">Keterangan Cluster:</h4>
            """

            # Informasi untuk setiap cluster
            cluster_info = [
                {
                    'color': '#4D96FF',
                    'number': 0,
                    'label': 'Wilayah Maju/Kota Besar',
                    'description': 'Wilayah maju dengan infrastruktur keuangan terbaik, IPM tinggi, dan kemiskinan rendah'
                },
                {
                    'color': '#FFD93D',
                    'number': 1,
                    'label': 'Wilayah Berkembang dengan Tantangan Kemiskinan',
                    'description': 'Wilayah berkembang dengan tantangan kemiskinan signifikan'
                },
                {
                    'color': '#FF6B6B',
                    'number': 2,
                    'label': 'Wilayah Tertinggal',
                    'description': 'Wilayah tertinggal dengan infrastruktur terbatas dan kemiskinan tinggi'
                },
                {
                    'color': '#6BCB77',
                    'number': 3,
                    'label': 'Wilayah Menengah/Transisi',
                    'description': 'Wilayah transisi dengan pertumbuhan ekonomi baik dan indikator terkendali'
                }
            ]

            for info in cluster_info:
                legend_html += f"""
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; align-items: center;">
                        <div style="display: inline-block; 
                                    width: 20px; 
                                    height: 20px; 
                                    background-color: {info['color']}; 
                                    margin-right: 8px;
                                    border: 1px solid #666;"></div>
                        <div>
                            <strong>Cluster {info['number']}: {info['label']}</strong>
                            <br>
                            <small style="color: #666;">{info['description']}</small>
                        </div>
                    </div>
                </div>
                """

            legend_html += """
            <div style="margin-top: 10px; font-size: 11px; color: #666;">
                <hr style="margin: 5px 0;">
                Sumber: Analisis Data SEFI 2024
            </div>
            </div>
            """

            # Tambahkan legend ke peta
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Tampilkan peta
            folium_static(m)

        with col2:
            # Tampilkan statistik
            st.write("### Statistik Cluster")
            cluster_counts = year_data['Cluster'].value_counts().sort_index()
            for cluster, count in cluster_counts.items():
                st.write(f"Cluster {cluster} ({cluster_labels[cluster]}): {count} kabupaten/kota")
            
            # Tampilkan data dalam tabel
            st.write(f"### Data Cluster Tahun {selected_year}")
            display_df = year_data[['kab_kota', 'Cluster']].copy()
            display_df['Keterangan'] = display_df['Cluster'].map(cluster_labels)
            st.dataframe(display_df, height=400)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
        st.write("Pastikan semua file berada di folder yang sama dan nama file sesuai")

with tab2:
   with tab2:
    # Buat subtabs
    subtab1, subtab2 = st.tabs(["Analisis Korelasi", "Model Prediksi"])
    
    with subtab1:
        st.markdown("### Analisis Feature Importance")
        
        # Data feature importance dari paper
        feature_importance_data = {
            'Features': ['Entitas Bank', 'Entitas Non-Bank', 'Rekening Kredit', 'Penyaluran Kredit'],
            'PPM': [0.505923, 0.091851, 0.143531, 0.234412],
            'TPT': [0.196143, 0.573377, 0.073034, 0.133190],
            'IPM': [0.251957, 0.562416, 0.087972, 0.081940],
            'PE': [0.020925, 0.014357, 0.016221, 0.016814]
        }
        
        # Buat layout dengan 2 kolom
        col1, col2 = st.columns([2,1])
        
        with col1:
            # Pilihan target variable
            target_var = st.selectbox(
                "Pilih Target Variable",
                ["PPM (Persentase Penduduk Miskin)", 
                 "TPT (Tingkat Pengangguran Terbuka)",
                 "IPM (Indeks Pembangunan Manusia)",
                 "PE (Pertumbuhan Ekonomi)"]
            )
            
            # Map selection to dataframe column
            target_map = {"PPM (Persentase Penduduk Miskin)": "PPM",
                         "TPT (Tingkat Pengangguran Terbuka)": "TPT",
                         "IPM (Indeks Pembangunan Manusia)": "IPM",
                         "PE (Pertumbuhan Ekonomi)": "PE"}
            
            selected_target = target_map[target_var]
            
            # Create bar plot using plotly
            fig = go.Figure(data=[
                go.Bar(
                    x=feature_importance_data['Features'],
                    y=[v*100 for v in feature_importance_data[selected_target]],
                    marker_color=['#4D96FF', '#FFD93D', '#FF6B6B', '#6BCB77']
                )
            ])
            
            fig.update_layout(
                title=f"Feature Importance untuk {target_var}",
                xaxis_title="Features",
                yaxis_title="Importance (%)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown("### Interpretasi")
            if selected_target == "PPM":
                st.write("""
                - Entitas Bank memiliki pengaruh dominan (50.59%)
                - Penyaluran Kredit menempati posisi kedua (23.44%)
                - Menunjukkan pentingnya akses perbankan dalam pengentasan kemiskinan
                """)
            elif selected_target == "TPT":
                st.write("""
                - Entitas Non-Bank memiliki pengaruh terbesar (57.34%)
                - Entitas Bank di posisi kedua (19.61%)
                - Mengindikasikan peran penting lembaga non-bank dalam penciptaan lapangan kerja
                """)
            elif selected_target == "IPM":
                st.write("""
                - Entitas Non-Bank mendominasi (56.24%)
                - Entitas Bank berkontribusi signifikan (25.20%)
                - Menunjukkan pentingnya keragaman layanan keuangan untuk pembangunan manusia
                """)
            else:  # PE
                st.write("""
                - Pengaruh faktor keuangan relatif kecil
                - Faktor temporal lebih dominan (93.17%)
                - Mengindikasikan pertumbuhan ekonomi lebih dipengaruhi faktor siklikal
                """)
    
    with subtab2:
        st.markdown("### Performa Model Machine Learning")
        
        # Data performa model
        model_performance = {
            'Target': ['PPM', 'TPT', 'IPM', 'PE'],
            'Model': ['Gradient Boosting', 'Random Forest', 'Random Forest', 'Gradient Boosting'],
            'R2_Train': [0.8620, 0.9597, 0.8355, 0.8286],
            'R2_Test': [0.8620, 0.6514, 0.8355, 0.8286],
            'RMSE_Train': [0.4496, 0.1293, 0.3383, 0.2702],
            'RMSE_Test': [0.4496, 0.3592, 0.3383, 0.2702]
        }
        
        # Convert to DataFrame
        df_performance = pd.DataFrame(model_performance)
        
        # Display model performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Create heatmap for R2 scores
            fig_r2 = go.Figure(data=go.Heatmap(
                z=[df_performance['R2_Train'], df_performance['R2_Test']],
                x=df_performance['Target'],
                y=['R² Train', 'R² Test'],
                colorscale='RdYlBu',
                text=[[f"{val:.3f}" for val in df_performance['R2_Train']],
                      [f"{val:.3f}" for val in df_performance['R2_Test']]],
                texttemplate="%{text}",
                textfont={"size": 14},
                hoverongaps=False
            ))
            
            fig_r2.update_layout(
                title="R² Score per Target Variable",
                height=300
            )
            
            st.plotly_chart(fig_r2, use_container_width=True)
            
        with col2:
            # Create heatmap for RMSE scores
            fig_rmse = go.Figure(data=go.Heatmap(
                z=[df_performance['RMSE_Train'], df_performance['RMSE_Test']],
                x=df_performance['Target'],
                y=['RMSE Train', 'RMSE Test'],
                colorscale='RdYlBu_r',
                text=[[f"{val:.3f}" for val in df_performance['RMSE_Train']],
                      [f"{val:.3f}" for val in df_performance['RMSE_Test']]],
                texttemplate="%{text}",
                textfont={"size": 14},
                hoverongaps=False
            ))
            
            fig_rmse.update_layout(
                title="RMSE per Target Variable",
                height=300
            )
            
            st.plotly_chart(fig_rmse, use_container_width=True)
        
        # Model Summary
        st.markdown("### Ringkasan Model")
        
        # Display model details in an expander
        with st.expander("Detail Performa Model per Target"):
            for idx, row in df_performance.iterrows():
                st.markdown(f"#### {row['Target']}")
                st.write(f"- Model Terbaik: {row['Model']}")
                st.write(f"- R² Score (Train/Test): {row['R2_Train']:.3f} / {row['R2_Test']:.3f}")
                st.write(f"- RMSE (Train/Test): {row['RMSE_Train']:.3f} / {row['RMSE_Test']:.3f}")
                
                if row['Target'] == 'TPT':
                    st.warning("""
                    ⚠️ Catatan: Model untuk TPT menunjukkan indikasi overfitting,
                    dengan perbedaan signifikan antara performa train dan test.
                    Interpretasi hasil perlu dilakukan dengan hati-hati.
                    """)
                st.markdown("---")
        
        # Rekomendasi
        st.markdown("### Rekomendasi Kebijakan")
        st.write("""
        Berdasarkan hasil analisis model machine learning, beberapa rekomendasi utama:
        
        1. **Pengentasan Kemiskinan**
           - Fokus pada perluasan akses perbankan
           - Optimalisasi program penyaluran kredit
           
        2. **Pengurangan Pengangguran**
           - Penguatan peran lembaga keuangan non-bank
           - Program pemberdayaan UMKM
           
        3. **Peningkatan IPM**
           - Diversifikasi layanan keuangan
           - Kolaborasi bank dan non-bank
           
        4. **Pertumbuhan Ekonomi**
           - Mempertimbangkan faktor siklikal
           - Kebijakan kontrasiklikal yang tepat
        """)

# Tambahkan kode ini di dalam subtab2 setelah bagian Rekomendasi Kebijakan

# What-If Analysis Section
st.markdown("""
### What-If Analysis
Simulasikan dampak perubahan indikator inklusi keuangan terhadap kesejahteraan masyarakat di Sumatera Utara.
Data baseline menggunakan rata-rata kabupaten/kota tahun 2023 sebagai dasar prediksi ke depan.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Parameters")
    
    try:
        # Load data 2023
        data = pd.read_excel('hasil_cluster_sumut.xlsx')
        data_2023 = data[data['tahun'] == 2023]
        
        if len(data_2023) == 0:
            st.error("Data tahun 2023 tidak ditemukan!")
        else:            
            # Hitung rata-rata provinsi untuk tahun 2023
            baseline_bank = data_2023['jumlah_entitas_bank'].mean()
            baseline_nonbank = data_2023['jumlah_entitas_nonbank'].mean()
            baseline_rekening = data_2023['jumlah_rekening_kredit'].mean()
            baseline_kredit = data_2023['penyaluran_kredit'].mean()
            
            # Update baseline targets untuk 2023
            baseline_targets = {
                "PPM": data_2023['persentase_penduduk_miskin'].mean(),
                "TPT": data_2023['tingkat_pengangguran'].mean(),
                "IPM": data_2023['ipm'].mean(),
                "PE": data_2023['pertumbuhan_ekonomi'].mean()
            }
            
            # Tampilkan informasi baseline 2023
            st.info(f"""
            **Nilai Baseline (Rata-rata Kabupaten/Kota 2023):**
            
            *Indikator Inklusi Keuangan:*
            - Jumlah Entitas Bank: {baseline_bank:,.0f} unit
            - Jumlah Entitas Non-Bank: {baseline_nonbank:,.0f} unit
            - Jumlah Rekening Kredit: {baseline_rekening:,.0f} rekening
            - Penyaluran Kredit: Rp {baseline_kredit/1e12:,.2f} Triliun
            
            *Indikator Kesejahteraan:*
            - Persentase Penduduk Miskin: {baseline_targets['PPM']:.2f}%
            - Tingkat Pengangguran: {baseline_targets['TPT']:.2f}%
            - Indeks Pembangunan Manusia: {baseline_targets['IPM']:.2f}
            - Pertumbuhan Ekonomi: {baseline_targets['PE']:.2f}%
            """)
            
            # Create sliders with percentage changes
            st.subheader("Simulasi Perubahan")
            bank_change = st.slider(
                "Perubahan Jumlah Entitas Bank (%)", 
                min_value=-50, 
                max_value=100, 
                value=0,
                help="Persentase perubahan dari kondisi 2023"
            )
            
            nonbank_change = st.slider(
                "Perubahan Jumlah Entitas Non-Bank (%)",
                min_value=-50,
                max_value=100,
                value=0,
                help="Persentase perubahan dari kondisi 2023"
            )
            
            rekening_change = st.slider(
                "Perubahan Jumlah Rekening Kredit (%)",
                min_value=-50,
                max_value=100,
                value=0,
                help="Persentase perubahan dari kondisi 2023"
            )
            
            kredit_change = st.slider(
                "Perubahan Penyaluran Kredit (%)",
                min_value=-50,
                max_value=100,
                value=0,
                help="Persentase perubahan dari kondisi 2023"
            )

            # Calculate new values
            new_bank = baseline_bank * (1 + bank_change/100)
            new_nonbank = baseline_nonbank * (1 + nonbank_change/100)
            new_rekening = baseline_rekening * (1 + rekening_change/100)
            new_kredit = baseline_kredit * (1 + kredit_change/100)

            with col2:
                st.subheader("Predicted Impact")
                
                # Function to calculate predicted values
                def predict_impact(bank, nonbank, rekening, kredit, target):
                    # Weights dengan tanda yang sudah disesuaikan
                    weights = {
                        "PPM": {
                            'bank': -0.505923,    # Negatif karena peningkatan X menurunkan kemiskinan
                            'nonbank': -0.091851,
                            'rekening': -0.143531,
                            'kredit': -0.234412
                        },
                        "TPT": {
                            'bank': -0.196143,    # Negatif karena peningkatan X menurunkan pengangguran
                            'nonbank': -0.573377,
                            'rekening': -0.073034,
                            'kredit': -0.133190
                        },
                        "IPM": {
                            'bank': 0.251957,     # Positif karena peningkatan X meningkatkan IPM
                            'nonbank': 0.562416,
                            'rekening': 0.087972,
                            'kredit': 0.081940
                        },
                        "PE": {
                            'bank': 0.020925,     # Positif karena peningkatan X meningkatkan pertumbuhan
                            'nonbank': 0.014357,
                            'rekening': 0.016221,
                            'kredit': 0.016814
                        }
                    }
                    
                    # Calculate percentage changes from baseline
                    bank_pct = (bank - baseline_bank) / baseline_bank
                    nonbank_pct = (nonbank - baseline_nonbank) / baseline_nonbank
                    rekening_pct = (rekening - baseline_rekening) / baseline_rekening
                    kredit_pct = (kredit - baseline_kredit) / baseline_kredit
                    
                    # Calculate weighted impact
                    total_impact = (
                        bank_pct * weights[target]['bank'] +
                        nonbank_pct * weights[target]['nonbank'] +
                        rekening_pct * weights[target]['rekening'] +
                        kredit_pct * weights[target]['kredit']
                    )
                    
                    # Calculate predicted value
                    predicted = baseline_targets[target] * (1 + total_impact)
                    
                    return predicted, total_impact * 100

                # Calculate predictions and changes
                predictions = {}
                for target in ["PPM", "TPT", "IPM", "PE"]:
                    pred_value, pct_change = predict_impact(new_bank, new_nonbank, new_rekening, new_kredit, target)
                    predictions[target] = {"value": pred_value, "change": pct_change}

                # Display metrics with more context
                st.subheader("Hasil Simulasi")
                col_metrics1, col_metrics2 = st.columns(2)
                
                with col_metrics1:
                    st.metric(
                        "Prediksi Persentase Penduduk Miskin", 
                        f"{predictions['PPM']['value']:.2f}%",
                        f"{predictions['PPM']['change']:.2f}%",
                        help="Perubahan dari baseline 2023"
                    )
                    st.metric(
                        "Prediksi Tingkat Pengangguran", 
                        f"{predictions['TPT']['value']:.2f}%",
                        f"{predictions['TPT']['change']:.2f}%",
                        help="Perubahan dari baseline 2023"
                    )
                
                with col_metrics2:
                    st.metric(
                        "Prediksi IPM", 
                        f"{predictions['IPM']['value']:.2f}",
                        f"{predictions['IPM']['change']:.2f}%",
                        help="Perubahan dari baseline 2023"
                    )
                    st.metric(
                        "Prediksi Pertumbuhan Ekonomi", 
                        f"{predictions['PE']['value']:.2f}%",
                        f"{predictions['PE']['change']:.2f}%",
                        help="Perubahan dari baseline 2023"
                    )
                
                # Visualization
                st.subheader("Visualisasi Perbandingan")
                fig = go.Figure()
                
                variables = ["PPM", "TPT", "IPM", "PE"]
                baseline_values = [baseline_targets[var] for var in variables]
                predicted_values = [predictions[var]['value'] for var in variables]
                
                fig.add_trace(go.Bar(
                    name='Baseline 2023',
                    x=variables,
                    y=baseline_values,
                    marker_color='#4D96FF'
                ))
                
                fig.add_trace(go.Bar(
                    name='Prediksi',
                    x=variables,
                    y=predicted_values,
                    marker_color='#6BCB77'
                ))
                
                fig.update_layout(
                    title='Perbandingan Baseline 2023 vs Prediksi',
                    barmode='group',
                    height=400,
                    yaxis_title='Nilai',
                    xaxis_title='Indikator'
                )
                
                st.plotly_chart(fig, use_container_width=True)

            # Add detailed interpretation
            st.markdown("### Interpretasi Hasil")
            st.write(f"""
            Hasil simulasi menunjukkan potensi perubahan dari kondisi baseline 2023:

            1. **Persentase Penduduk Miskin (PPM)**:
               - Baseline 2023: {baseline_targets['PPM']:.2f}%
               - Prediksi: {predictions['PPM']['value']:.2f}%
               - Perubahan: {predictions['PPM']['change']:.2f}%
               - *Insight*: Penurunan kemiskinan dipengaruhi terutama oleh peningkatan entitas bank (50.59%) dan penyaluran kredit (23.44%)

            2. **Tingkat Pengangguran**:
               - Baseline 2023: {baseline_targets['TPT']:.2f}%
               - Prediksi: {predictions['TPT']['value']:.2f}%
               - Perubahan: {predictions['TPT']['change']:.2f}%
               - *Insight*: Penurunan pengangguran sangat responsif terhadap peningkatan entitas non-bank (57.34%)

            3. **Indeks Pembangunan Manusia (IPM)**:
               - Baseline 2023: {baseline_targets['IPM']:.2f}
               - Prediksi: {predictions['IPM']['value']:.2f}
               - Perubahan: {predictions['IPM']['change']:.2f}%
               - *Insight*: Peningkatan seimbang antara entitas bank (25.20%) dan non-bank (56.24%)

            4. **Pertumbuhan Ekonomi**:
               - Baseline 2023: {baseline_targets['PE']:.2f}%
               - Prediksi: {predictions['PE']['value']:.2f}%
               - Perubahan: {predictions['PE']['change']:.2f}%
               - *Insight*: Peningkatan moderat seiring dengan perbaikan sektor keuangan

            ⚠️ **Catatan Penting**: 
            - Simulasi menggunakan rata-rata Kabupaten/Kota Sumatera Utara tahun 2023 sebagai baseline
            - Bobot pengaruh (*feature importance*) diperoleh dari analisis historis 2019-2023
            - Peningkatan variabel inklusi keuangan akan:
              * Menurunkan persentase penduduk miskin dan tingkat pengangguran
              * Meningkatkan IPM dan pertumbuhan ekonomi
            - Hasil aktual dapat berbeda tergantung kondisi makroekonomi dan kebijakan pemerintah
            """)
                
    except Exception as e:
        st.error(f"Terjadi kesalahan dalam membaca atau memproses data: {str(e)}")
        st.write("""
        Pastikan file Excel memiliki kolom-kolom berikut:
        - tahun
        - persentase_penduduk_miskin
        - tingkat_pengangguran
        - ipm
        - pertumbuhan_ekonomi
        - jumlah_entitas_bank
        - jumlah_entitas_nonbank
        - jumlah_rekening_kredit
        - penyaluran_kredit
        """)
