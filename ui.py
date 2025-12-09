import streamlit as st
from fpdf import FPDF
import datetime

def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
        .stApp { background-color: #f1f5f9; }
        
        [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #1e293b; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff !important; }
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] .stMarkdown { color: #94a3b8 !important; }
        [data-testid="stSidebar"] hr { border-color: #334155 !important; }
        
        [data-testid="stSidebar"] input, [data-testid="stSidebar"] div[data-baseweb="select"] > div, [data-testid="stSidebar"] div[data-baseweb="input"] > div {
            background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #475569 !important; border-radius: 6px;
        }
        div[data-baseweb="menu"] { background-color: #ffffff !important; }
        div[data-baseweb="option"] { color: #0f172a !important; }
        
        .main-header { font-size: 2.5rem; font-weight: 800; background: linear-gradient(to right, #0f172a, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; letter-spacing: -1px; }
        .sub-header { font-size: 1.1rem; color: #64748b; margin-bottom: 2rem; font-weight: 500; }
        
        div[data-testid="metric-container"], .plotly-container {
            background-color: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        div[data-testid="metric-container"] label { color: #64748b; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #0f172a; font-weight: 800; font-size: 2rem; }
        
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border-radius: 8px; border: none; padding: 0.75rem 1.5rem; font-weight: 700; box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3); transition: all 0.2s ease-in-out;
        }
        div.stButton > button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 8px -1px rgba(59, 130, 246, 0.4); }
        
        div.stButton > button[kind="secondary"] { background-color: #ffffff; border: 2px solid #e2e8f0; color: #475569; font-weight: 600; border-radius: 8px; }
        div.stButton > button[kind="secondary"]:hover { border-color: #cbd5e1; background-color: #f8f9fa; }
        
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: #ffffff; border-radius: 8px 8px 0 0; color: #64748b; font-weight: 600; }
        .stTabs [aria-selected="true"] { background-color: #ffffff !important; color: #3b82f6 !important; }
    </style>
    """, unsafe_allow_html=True)

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, 'TETRALOG | Enterprise Load Plan', 0, 0, 'L')
        self.ln(20)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(truck, items, fitted_count, axle_data):
    pdf = PDFReport()
    pdf.add_page()
    def tr(text):
        replacements = {'ğ': 'g', 'ü': 'u', 'ş': 's', 'ı': 'i', 'ö': 'o', 'ç': 'c', 
                        'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'İ': 'I', 'Ö': 'O', 'Ç': 'C'}
        for s, t in replacements.items(): text = text.replace(s, t)
        return text

    total_vol = truck.dims[0]*truck.dims[1]*truck.dims[2] / 1000000 
    used_vol = sum([i.volume for i in truck.placed_items]) / 1000000 
    total_weight = sum([i.weight for i in truck.placed_items])
    
    pdf.set_font('Arial', 'B', 11)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(0, 10, f'  EXECUTIVE SUMMARY - {datetime.datetime.now().strftime("%d-%m-%Y")}', 0, 1, fill=True)
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 10, tr('Loaded Units:'), 0, 0)
    pdf.cell(50, 10, f"{fitted_count} / {len(items)}", 0, 1)
    pdf.cell(50, 10, tr('Volume Usage:'), 0, 0)
    pdf.cell(50, 10, f"%{(used_vol/total_vol)*100:.1f} ({used_vol:.2f} m3)", 0, 1)
    
    pdf.cell(50, 10, tr('Total Weight:'), 0, 0)
    if total_weight > truck.max_weight:
        pdf.set_text_color(220, 38, 38)
        pdf.cell(50, 10, f"{total_weight} kg (OVERWEIGHT!)", 0, 1)
    else:
        pdf.set_text_color(0, 0, 0)
        pdf.cell(50, 10, f"{total_weight} kg", 0, 1)
    
    pdf.ln(5)
    pdf.set_text_color(0,0,0)
    pdf.cell(50, 10, 'Axle Load:', 0, 0)
    pdf.cell(50, 10, f"Front: {axle_data[0]:.0f}kg | Rear: {axle_data[1]:.0f}kg", 0, 1)

    pdf.ln(10)
    # Tablo Başlıkları
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(255, 255, 255)
    headers = ['#', 'Destination', 'Dims (cm)', 'Vol (m3)', 'Wgt (kg)', 'Status']
    widths = [10, 50, 35, 25, 25, 45]
    for h, w in zip(headers, widths):
        pdf.cell(w, 10, h, 1, 0, 'C', 1)
    pdf.ln()
    
    # Satırlar
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(0, 0, 0)
    counter = 1
    for item in truck.placed_items:
        fill = counter % 2 == 0
        pdf.set_fill_color(248, 250, 252)
        dims = item.get_dimension()
        row = [str(counter), tr(item.destination), f"{dims[0]}x{dims[1]}x{dims[2]}", 
               f"{item.volume/1000000:.3f}", str(item.weight), "LOADED"]
        for r, w in zip(row, widths):
            pdf.cell(w, 8, r, 1, 0, 'C', fill)
        pdf.ln()
        counter += 1
        
    return pdf.output(dest='S').encode('latin-1')