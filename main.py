import streamlit as st
import pandas as pd
import io
import plotly.graph_objects as go

# Modülleri içe aktar (Aynı klasörde olmalılar)
import ui
import models
import algorithms
import visualization

# 1. UI ve CSS Yükle
st.set_page_config(page_title="TetraLog Pro", layout="wide", initial_sidebar_state="expanded")
ui.apply_custom_css()

# --- STATE YÖNETİMİ ---
def clear_results():
    if 'calc_done' in st.session_state: del st.session_state['calc_done']
    if 'truck' in st.session_state: del st.session_state['truck']

# --- HEADER ---
st.markdown('<div class="main-header">TetraLog Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Advanced Logistics Optimization Engine (v4.0)</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.header("Operational Config")
arac_tipi = st.sidebar.selectbox("Vehicle Type", ["Standard Trailer (13.6m)", "Truck (8m)", "Van"], on_change=clear_results)

if arac_tipi == "Standard Trailer (13.6m)": 
    v_dims = [240, 1360, 270]; max_tonaj = 24000
elif arac_tipi == "Truck (8m)": 
    v_dims = [240, 800, 270]; max_tonaj = 15000
else: 
    v_dims = [190, 350, 190]; max_tonaj = 3500

st.sidebar.markdown(f"**📏 Dims:** {v_dims[0]}x{v_dims[1]}x{v_dims[2]} cm")
st.sidebar.markdown(f"**⚖️ Cap:** {max_tonaj:,} kg")

st.sidebar.divider()
st.sidebar.subheader("Manifest")
tab1, tab2 = st.sidebar.tabs(["Manual", "Excel"])
duraklar = ["Istanbul", "Kocaeli", "Ankara", "Erzurum"]

if 'koli_listesi' not in st.session_state: st.session_state.koli_listesi = []

# --- TAB 1: MANUEL GİRİŞ ---
with tab1:
    dest = st.selectbox("Destination", duraklar[1:])
    stop_idx = duraklar.index(dest)
    with st.form("manual"):
        c1, c2 = st.columns(2)
        w = c1.number_input("Width", 10, 300, 80)
        l = c2.number_input("Length", 10, 300, 120)
        h = c1.number_input("Height", 10, 300, 100)
        kg = c2.number_input("Weight", 1, 2000, 20)
        qty = st.number_input("Qty", 1, 500, 10)
        
        # YENİ KISITLAMALAR
        fragile = st.checkbox("Fragile (Kırılabilir)")
        rotate = st.checkbox("Can Rotate?", value=True)
        
        if st.form_submit_button("Add Item", type="secondary"):
            colors = ['#e74c3c', '#3498db', '#f1c40f', '#8e44ad', '#27ae60']
            st.session_state.koli_listesi.append({
                "w":w, "l":l, "h":h, "kg":kg, "qty":qty, 
                "dest":dest, "stop":stop_idx, "c":colors[stop_idx%5],
                "fragile": fragile, "rotate": rotate
            })
            st.toast("Item Added", icon="✅")

# --- TAB 2: EXCEL YÜKLEME (DÜZELTİLDİ) ---
with tab2:
    st.write("Batch Upload (Excel)")
    
    # 1. Şablon İndirme Butonu
    sample_data = pd.DataFrame({
        'Width': [80, 100], 'Length': [120, 100], 'Height': [100, 150], 
        'Weight': [20, 15], 'Qty': [10, 5], 
        'Destination': ['Ankara', 'Kocaeli']
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        sample_data.to_excel(writer, index=False)
        
    st.download_button(
        label="📥 Download Template",
        data=buffer.getvalue(),
        file_name="tetralog_template.xlsx",
        mime="application/vnd.ms-excel",
        type="secondary"
    )
    
    # 2. Dosya Yükleme ve Okuma
    uploaded_file = st.file_uploader("Select Excel File", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        if st.button("Import Data", type="primary"):
            try:
                df = pd.read_excel(uploaded_file)
                # Listeyi Temizle
                st.session_state.koli_listesi = []
                colors = ['#e74c3c', '#3498db', '#f1c40f', '#8e44ad', '#27ae60']
                
                for index, row in df.iterrows():
                    # Durak Kontrolü
                    d_name = row['Destination'] if 'Destination' in row else 'Ankara'
                    try:
                        s_idx = duraklar.index(d_name)
                    except:
                        s_idx = 1 # Bulamazsa varsayılan
                    
                    color = colors[s_idx % 5]
                    
                    st.session_state.koli_listesi.append({
                        "w": int(row['Width']), 
                        "l": int(row['Length']), 
                        "h": int(row['Height']), 
                        "kg": int(row['Weight']), 
                        "qty": int(row['Qty']), 
                        "dest": d_name, 
                        "stop": s_idx, 
                        "c": color,
                        "fragile": False, # Excel'den gelmiyorsa varsayılan False
                        "rotate": True    # Excel'den gelmiyorsa varsayılan True
                    })
                
                st.success(f"{len(df)} rows imported successfully!")
                clear_results()
                st.rerun()
                
            except Exception as e:
                st.error(f"Error reading file: {e}")

if st.session_state.koli_listesi:
    st.sidebar.divider()
    st.sidebar.markdown(f"**📊 Total Items:** {len(st.session_state.koli_listesi)}")
    if st.sidebar.button("Clear Manifest", type="secondary"):
        st.session_state.koli_listesi = []
        clear_results()
        st.rerun()

# --- DASHBOARD ---
c1, c2 = st.columns([2, 3], gap="large")

with c1:
    st.subheader("Optimization Analysis")
    
    # Strateji Seçimi
    strategy = st.selectbox("Algo Strategy", ["Balanced (LIFO)", "Density (Heavy Bottom)"])
    
    if st.button("RUN OPTIMIZATION ENGINE", type="primary", use_container_width=True):
        if not st.session_state.koli_listesi:
            st.warning("Empty Manifest")
        else:
            # Nesneleri Oluştur
            truck = models.Container(v_dims[0], v_dims[1], v_dims[2], max_tonaj)
            items = []
            for i, k in enumerate(st.session_state.koli_listesi):
                for _ in range(k['qty']):
                    items.append(models.Item(
                        "Box", k['w'], k['l'], k['h'], k['kg'], 
                        k['dest'], k['stop'], k['c'], 
                        k['fragile'], k['rotate']
                    ))
            
            # Algoritmayı Çalıştır
            packer = algorithms.Packer(truck)
            with st.spinner("Calculating Physics, Stability & Axle Loads..."):
                packer.pack(items, strategy)
            
            st.session_state.calc_done = True
            st.session_state.truck = truck
            st.session_state.cargo_items = items
            st.session_state.fitted = len(truck.placed_items)

    if st.session_state.get('calc_done'):
        truck = st.session_state.truck
        items = st.session_state.cargo_items
        fitted = st.session_state.fitted
        
        # Hesaplamalar
        vol_usage = sum([i.volume for i in truck.placed_items]) / 1000000
        total_w = sum([i.weight for i in truck.placed_items])
        f_load, r_load = algorithms.Packer(truck).calculate_axle_loads() # Aks Yükü
        
        m1, m2 = st.columns(2)
        m1.metric("Fill Rate", f"{fitted}/{len(items)}")
        m2.metric("Vol Usage", f"{vol_usage:.2f} m3")
        
        st.divider()
        
        # Aks Yükü Görseli
        st.markdown(f"**🚛 Axle Load Distribution**")
        st.progress(f_load / (total_w + 1), text=f"Front Axle: {f_load:.0f}kg | Rear Axle: {r_load:.0f}kg")
        
        if total_w > max_tonaj:
            st.error(f"🚨 OVERWEIGHT: {total_w} / {max_tonaj} kg")
        else:
            st.success(f"✅ Weight Compliance: {total_w} / {max_tonaj} kg")
            
        st.divider()
        pdf_bytes = ui.create_pdf(truck, items, fitted, (f_load, r_load))
        st.download_button("Download Report", pdf_bytes, "report.pdf", "application/pdf", type="secondary")

with c2:
    st.markdown('<div class="plotly-container">', unsafe_allow_html=True)
    st.subheader("Digital Twin & Animation")
    
    if st.session_state.get('calc_done'):
        truck = st.session_state.truck
        
        # --- UX: GÖRÜNÜM AYARLARI ---
        vis_col1, vis_col2 = st.columns(2)
        with vis_col1:
            # ADIM ADIM ANİMASYON SLIDER
            step = st.slider("Loading Sequence (Time)", 0, fitted, fitted)
        with vis_col2:
            # RENK MODU SEÇİMİ
            color_mode = st.radio("Color Mode", ["Destination", "Weight Based"], horizontal=True)
        
        # Sadece seçilen adıma kadar olanları filtrele
        visible_items = truck.placed_items[:step]
        
        fig = go.Figure()
        fig.add_trace(visualization.draw_truck_borders(v_dims[0], v_dims[1], v_dims[2]))
        
        for item in visible_items:
            fig.add_trace(visualization.get_cube_trace(item, color_mode))
            
        fig.add_trace(visualization.get_wireframe_traces(visible_items))
        
        fig.update_layout(
            scene=dict(
                aspectmode='data',
                xaxis=dict(title="W", backgroundcolor="#f8f9fa"),
                yaxis=dict(title="L", backgroundcolor="#f8f9fa"),
                zaxis=dict(title="H", backgroundcolor="#f8f9fa"),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.1))
            ),
            margin=dict(l=0, r=0, b=0, t=0), height=600, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("System Ready. Please input manifest.")
    st.markdown('</div>', unsafe_allow_html=True)