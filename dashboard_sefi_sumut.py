import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json
from branca.colormap import LinearColormap

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
                vmax=3,
                caption='Cluster Level'
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

            # Legend box di kanan atas
            legend_html = """
            <div style="
                position: fixed; 
                top: 10px;
                right: 10px;
                z-index: 1000;
                background-color: white;
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                max-width: 300px;
            ">
                <div style="margin-bottom: 5px;"><strong>Keterangan Cluster:</strong></div>
            """

            # Informasi untuk setiap cluster
            cluster_info = [
                {
                    'color': '#4D96FF',
                    'label': 'Wilayah Maju/Kota Besar',
                    'number': '0'
                },
                {
                    'color': '#FFD93D',
                    'label': 'Wilayah Berkembang dengan Tantangan Kemiskinan',
                    'number': '1'
                },
                {
                    'color': '#FF6B6B',
                    'label': 'Wilayah Tertinggal',
                    'number': '2'
                },
                {
                    'color': '#6BCB77',
                    'label': 'Wilayah Menengah/Transisi',
                    'number': '3'
                }
            ]

            for info in cluster_info:
                legend_html += f"""
                <div style="
                    display: flex;
                    align-items: center;
                    margin-bottom: 5px;
                    padding: 2px;
                ">
                    <div style="
                        width: 20px;
                        height: 20px;
                        background-color: {info['color']};
                        margin-right: 8px;
                        border: 1px solid #666;
                    "></div>
                    <div>Cluster {info['number']}: {info['label']}</div>
                </div>
                """

            legend_html += "</div>"

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
    st.markdown("### Analisis Korelasi dan Prediksi")
    st.write("Konten untuk analisis korelasi dan prediksi akan ditambahkan di sini.")
