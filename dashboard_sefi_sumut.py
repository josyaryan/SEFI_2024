import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json
from branca.colormap import LinearColormap

# Konfigurasi awal dashboard
st.set_page_config(
    layout="wide", 
    page_title="Dashboard Cluster Sumatera Utara",
    initial_sidebar_state="collapsed"  # Sembunyikan sidebar
)

# Sembunyikan menu hamburger dan footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Definisi warna dan label cluster
cluster_colors = {
    0: '#FF0000',  # Merah untuk Wilayah Berkembang
    1: '#FFA500',  # Orange untuk Wilayah Maju
    2: '#FFFF00',  # Kuning untuk Wilayah Sangat Maju
    3: '#008000'   # Hijau untuk Wilayah Paling Maju
}

cluster_labels = {
    0: 'Wilayah Kesejahteraan Menengah dengan Inklusi Keuangan Tinggi',
    1: 'Wilayah Kesejahteraan Rendah dengan Inklusi Keuangan Sedang',
    2: 'Wilayah Kesejahteraan Sangat Rendah dengan Inklusi Keuangan Rendah',
    3: 'Wilayah Kesejahteraan Tinggi dengan Inklusi Keuangan Tinggi - Pusat Ekonomi'
}

# Baca data
try:
    data = pd.read_excel('hasil_cluster_sumut.xlsx')
    with open('prov_bykabkota.geojson') as f:
        geojson_data = json.load(f)

    # Judul Dashboard
    st.title("Dashboard Analisis Cluster Inklusi Keuangan Terhadap Kesejahteraan Masyarakat Sumatera Utara 2019-2023")
    st.write("Periode 2019-2023")

    # Buat layout dengan 2 kolom
    col1, col2 = st.columns([4,1])  # Ubah rasio kolom untuk peta yang lebih besar

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

        # Tambahkan legend
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; 
        padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4 style="margin-bottom: 10px;">Keterangan Cluster:</h4>
        """
        for cluster, label in cluster_labels.items():
            legend_html += f"""
            <p style="margin: 5px 0;"><div style="display: inline-block; width: 20px; height: 20px; 
            background-color: {cluster_colors[cluster]}; margin-right: 5px;"></div> Cluster {cluster}: {label}</p>
            """
        legend_html += "</div>"
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
