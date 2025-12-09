import plotly.graph_objects as go
import numpy as np

def get_cube_trace(item, color_mode="Destination"):
    pos = item.position
    dims = item.get_dimension()
    x, y, z = pos[0], pos[1], pos[2]
    dx, dy, dz = dims[0], dims[1], dims[2]
    
    # Renk Mantığı
    final_color = item.color
    if color_mode == "Weight Based":
        # Ağırlığa göre koyuluk (Basit gradyan)
        # Ağır -> Koyu Kırmızı, Hafif -> Açık
        opacity = min(1.0, max(0.4, item.weight / 500)) # 500kg ref
        final_color = f"rgba(255, 0, 0, {opacity})"
    
    # 8 Köşe
    x_c = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    y_c = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    z_c = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    rot = " (Rotated)" if item.rotation_type == 1 else ""
    fragile = " | 🥚 FRAGILE" if item.fragile else ""
    
    hover_text = (f"<b>{item.destination}</b>{rot}{fragile}<br>"
                  f"Dims: {dims[0]}x{dims[1]}x{dims[2]}<br>"
                  f"Weight: {item.weight} kg")

    return go.Mesh3d(
        x=x_c, y=y_c, z=z_c, i=i, j=j, k=k,
        color=final_color, opacity=0.9, flatshading=True,
        name=item.destination, hoverinfo="text", text=hover_text
    )

def get_wireframe_traces(items):
    x_lines, y_lines, z_lines = [], [], []
    for item in items:
        pos = item.position
        dims = item.get_dimension()
        x, y, z = pos[0], pos[1], pos[2]
        dx, dy, dz = dims[0], dims[1], dims[2]
        
        # Küp kenarları
        x_lines.extend([x, x+dx, x+dx, x, x, None, x, x+dx, x+dx, x, x, None, x, x, None, x+dx, x+dx, None, x+dx, x+dx, None, x, x, None])
        y_lines.extend([y, y, y+dy, y+dy, y, None, y, y, y+dy, y+dy, y, None, y, y, None, y, y, None, y+dy, y+dy, None, y+dy, y+dy, None])
        z_lines.extend([z, z, z, z, z, None, z+dz, z+dz, z+dz, z+dz, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz, None])
        
    return go.Scatter3d(x=x_lines, y=y_lines, z=z_lines, mode='lines', line=dict(color='#1e293b', width=2), hoverinfo='skip', showlegend=False)

def draw_truck_borders(width, length, height):
    x = [0, width, width, 0, 0, 0, width, width, 0, 0, width, width, width, width, 0, 0]
    y = [0, 0, length, length, 0, 0, 0, length, length, 0, 0, 0, length, length, length, length]
    z = [0, 0, 0, 0, 0, height, height, height, height, height, 0, height, height, 0, 0, height]
    return go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='#cbd5e1', width=4), name='Borders', hoverinfo='skip')