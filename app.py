import os
try:
    import psycopg2
except ImportError as e:
    raise ImportError("psycopg2 is required to run this app. Install it with: pip install psycopg2-binary") from e
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

# Ensure required secrets are present
if not os.getenv("DB_PASSWORD"):
    raise EnvironmentError("DB_PASSWORD environment variable is required. Set it in your .env file or environment.")

def get_data():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "aws-1-us-west-2.pooler.supabase.com"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres.jaluakardtzemqerpdpk"),
        password=os.getenv("DB_PASSWORD")
    )
    df = pd.read_sql("SELECT * FROM staging_environmental_raw ORDER BY timestamp_local", conn)
    conn.close()
    df["timestamp_local"] = pd.to_datetime(df["timestamp_local"])
    return df

app = Dash(__name__)
server = app.server

GREEN_DARK  = "#2D6A4F"
GREEN_MID   = "#52B788"
GREEN_LIGHT = "#B7E4C7"
AMBER       = "#F4A261"
RED         = "#E76F51"
SOIL        = "#6B4226"
BG          = "#F8FAF5"
CARD        = "#FFFFFF"
TEXT        = "#1B2E1F"
MUTED       = "#6B8C72"

def kpi_card(label, value, color=GREEN_DARK):
    return html.Div([
        html.P(label, style={"margin": 0, "fontSize": "12px", "color": MUTED, "textTransform": "uppercase", "letterSpacing": "0.08em"}),
        html.P(value, style={"margin": "4px 0 0", "fontSize": "28px", "fontWeight": "700", "color": color}),
    ], style={"background": CARD, "borderRadius": "12px", "padding": "18px 22px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)", "flex": "1", "minWidth": "140px"})

app.layout = html.Div(style={"background": BG, "minHeight": "100vh", "fontFamily": "'Segoe UI', sans-serif", "color": TEXT}, children=[
    html.Div([
        html.Div("🌿", style={"fontSize": "32px"}),
        html.Div([
            html.H1("Garden & Allergy Forecast", style={"margin": 0, "fontSize": "22px", "fontWeight": "700", "color": GREEN_DARK}),
            html.P("Louisville, KY · 7-Day Outlook", style={"margin": 0, "fontSize": "13px", "color": MUTED}),
        ]),
    ], style={"display": "flex", "alignItems": "center", "gap": "14px", "padding": "24px 32px 12px"}),
    dcc.Interval(id="refresh", interval=60*60*1000, n_intervals=0),
    dcc.Store(id="store"),
    html.Div(id="kpi-row", style={"display": "flex", "gap": "14px", "padding": "0 32px 20px", "flexWrap": "wrap"}),
    html.Div([
        html.Div([
            html.Div([html.P("Planting Readiness & Allergy Risk", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}), dcc.Graph(id="chart-readiness", config={"displayModeBar": False})], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
            html.Div([html.P("Temperature & Humidity", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}), dcc.Graph(id="chart-temp", config={"displayModeBar": False})], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
        ], style={"display": "flex", "gap": "14px", "marginBottom": "14px"}),
        html.Div([
            html.Div([html.P("Pollen Levels", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}), dcc.Graph(id="chart-pollen", config={"displayModeBar": False})], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
            html.Div([html.P("Air Quality Index (US AQI)", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}), dcc.Graph(id="chart-aqi", config={"displayModeBar": False})], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
        ], style={"display": "flex", "gap": "14px", "marginBottom": "14px"}),
        html.Div([
            html.Div([html.P("Soil Temperature & Moisture", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}), dcc.Graph(id="chart-soil", config={"displayModeBar": False})], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
            html.Div([html.P("Precipitation Probability", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}), dcc.Graph(id="chart-precip", config={"displayModeBar": False})], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
        ], style={"display": "flex", "gap": "14px"}),
    ], style={"padding": "0 32px 32px"}),
])

@callback(Output("store", "data"), Input("refresh", "n_intervals"))
def load_data(_):
    df = get_data()
    return df.to_json(date_format="iso", orient="split")

@callback(Output("kpi-row", "children"), Input("store", "data"))
def update_kpis(json_data):
    if not json_data:
        return []
    df = pd.read_json(json_data, orient="split")
    now = df.iloc[0]
    high_pollen_hours = df["high_pollen_flag"].sum()
    temp_color = AMBER if now["temperature_2m"] > 85 else GREEN_DARK
    allergy_color = RED if now["allergy_risk"] > 60 else AMBER if now["allergy_risk"] > 30 else GREEN_DARK
    return [
        kpi_card("Current Temp", f'{now["temperature_2m"]:.0f}°F', temp_color),
        kpi_card("Planting Score", f'{now["planting_readiness"]:.0f}/100', GREEN_DARK),
        kpi_card("Allergy Risk", f'{now["allergy_risk"]:.0f}/100', allergy_color),
        kpi_card("US AQI Now", f'{now["us_aqi"]:.0f}', GREEN_MID),
        kpi_card("High Pollen Hours", f'{int(high_pollen_hours)} hrs', RED if high_pollen_hours > 12 else AMBER),
    ]

def base_layout(yaxis_title, yaxis2_title=None):
    layout = dict(plot_bgcolor=CARD, paper_bgcolor=CARD, margin=dict(l=10, r=10, t=10, b=10), font=dict(family="Segoe UI", size=11, color=TEXT), legend=dict(orientation="h", y=-0.2, x=0), xaxis=dict(showgrid=False, tickformat="%a %-m/%d"), yaxis=dict(title=yaxis_title, gridcolor="#EEF2EE"), height=240)
    if yaxis2_title:
        layout["yaxis2"] = dict(title=yaxis2_title, overlaying="y", side="right", showgrid=False)
    return layout

@callback(Output("chart-readiness", "figure"), Input("store", "data"))
def chart_readiness(json_data):
    df = pd.read_json(json_data, orient="split")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["planting_readiness"], name="Planting Readiness", fill="tozeroy", line=dict(color=GREEN_MID, width=2)))
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["allergy_risk"], name="Allergy Risk", line=dict(color=RED, width=2, dash="dot")))
    fig.update_layout(**base_layout("Score (0-100)"))
    return fig

@callback(Output("chart-temp", "figure"), Input("store", "data"))
def chart_temp(json_data):
    df = pd.read_json(json_data, orient="split")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["temperature_2m"], name="Temp (F)", line=dict(color=AMBER, width=2)))
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["relative_humidity_2m"], name="Humidity (%)", line=dict(color=GREEN_MID, width=2, dash="dot"), yaxis="y2"))
    fig.update_layout(**base_layout("Temperature (F)", "Humidity (%)"))
    return fig

@callback(Output("chart-pollen", "figure"), Input("store", "data"))
def chart_pollen(json_data):
    df = pd.read_json(json_data, orient="split")
    fig = go.Figure()
    colors = [GREEN_MID, AMBER, RED, SOIL, GREEN_DARK, GREEN_LIGHT]
    for col, color in zip(["grass_pollen", "ragweed_pollen", "birch_pollen", "alder_pollen", "mugwort_pollen", "olive_pollen"], colors):
        fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df[col].fillna(0), name=col.replace("_pollen", "").title(), line=dict(width=1.5, color=color)))
    fig.update_layout(**base_layout("Pollen (grains/m3)"))
    return fig

@callback(Output("chart-aqi", "figure"), Input("store", "data"))
def chart_aqi(json_data):
    df = pd.read_json(json_data, orient="split")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["us_aqi"], name="Overall AQI", fill="tozeroy", line=dict(color=AMBER, width=2)))
    fig.add_hrect(y0=0, y1=50, fillcolor=GREEN_LIGHT, opacity=0.15, line_width=0, annotation_text="Good", annotation_position="top left")
    fig.add_hrect(y0=50, y1=100, fillcolor=AMBER, opacity=0.1, line_width=0, annotation_text="Moderate")
    fig.add_hrect(y0=100, y1=300, fillcolor=RED, opacity=0.08, line_width=0, annotation_text="Unhealthy")
    fig.update_layout(**base_layout("US AQI"))
    return fig

@callback(Output("chart-soil", "figure"), Input("store", "data"))
def chart_soil(json_data):
    df = pd.read_json(json_data, orient="split")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["soil_temperature_0cm"], name="Soil Temp (F)", line=dict(color=SOIL, width=2)))
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["soil_moisture_0_to_1cm"], name="Soil Moisture", line=dict(color=GREEN_MID, width=2, dash="dot"), yaxis="y2"))
    fig.update_layout(**base_layout("Soil Temp (F)", "Moisture"))
    return fig

@callback(Output("chart-precip", "figure"), Input("store", "data"))
def chart_precip(json_data):
    df = pd.read_json(json_data, orient="split")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["timestamp_local"], y=df["precipitation_probability"], name="Rain Probability (%)", marker_color=GREEN_MID, opacity=0.7))
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["precipitation"], name="Precipitation (in)", line=dict(color=GREEN_DARK, width=2), yaxis="y2"))
    fig.update_layout(**base_layout("Probability (%)", "Inches"))
    return fig

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
