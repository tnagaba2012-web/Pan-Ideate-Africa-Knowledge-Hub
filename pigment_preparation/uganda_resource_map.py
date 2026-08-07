import streamlit as st
import folium
from streamlit_folium import st_folium


def uganda_resource_map():

    st.header("🗺️ Uganda Iron Oxide Resource Map")

    st.write("""
Explore potential iron oxide pigment locations in Uganda.

Click the coloured markers to view information about each location.
""")

    # Create Uganda map
    m = folium.Map(
        location=[1.3733, 32.2903],
        zoom_start=7,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # Kampala (Reference)
    folium.Marker(
        location=[0.3476, 32.5825],
        popup="""
<b>Kampala</b><br>
Reference Location
""",
        tooltip="Kampala",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    # Kabale
    folium.Marker(
        location=[-1.249, 29.989],
        popup="""
<b>Kabale District</b><br>
🔴 Hematite<br>
🎨 Red Iron Oxide<br>
🏭 Roofing tiles, paints, bricks
""",
        tooltip="Kabale",
        icon=folium.Icon(color="red")
    ).add_to(m)

    # Tororo
    folium.Marker(
        location=[0.684, 34.180],
        popup="""
<b>Tororo District</b><br>
⚫ Magnetite<br>
🎨 Black Iron Oxide
""",
        tooltip="Tororo",
        icon=folium.Icon(color="black")
    ).add_to(m)

    # Kasese
    folium.Marker(
        location=[0.183, 30.083],
        popup="""
<b>Kasese District</b><br>
🟤 Iron-rich lateritic soils
""",
        tooltip="Kasese",
        icon=folium.Icon(color="orange")
    ).add_to(m)

    # Moroto
    folium.Marker(
        location=[2.534, 34.666],
        popup="""
<b>Moroto District</b><br>
🪨 Iron-bearing rocks
""",
        tooltip="Moroto",
        icon=folium.Icon(color="green")
    ).add_to(m)
    st.markdown("""
### 🎨 Iron Oxide Pigment Legend

🔴 **Red Marker** – Hematite (Red Iron Oxide)

🟡 **Yellow Marker** – Goethite (Yellow Iron Oxide)

⚫ **Black Marker** – Magnetite (Black Iron Oxide)

🟤 **Orange Marker** – Lateritic Iron Deposits

🟢 **Green Marker** – Iron-bearing Rocks (Further Investigation)
""")
    # Display map
    st_folium(
        m,
        width=900,
        height=600
    )