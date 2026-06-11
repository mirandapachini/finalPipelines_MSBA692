import os
import io
import psycopg2
import pandas as pd
from datetime import datetime, date
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------------------------
# DB CONNECTION
# -----------------------------------------------------------
def get_data():
    from sqlalchemy import create_engine
    password = os.getenv("DB_PASSWORD")
    user = os.getenv("DB_USER", "postgres.jaluakardtzemqerpdpk")
    host = os.getenv("DB_HOST", "aws-1-us-west-2.pooler.supabase.com")
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/postgres")
    df = pd.read_sql("SELECT * FROM staging_environmental_raw ORDER BY timestamp_local", engine)
    df["timestamp_local"] = pd.to_datetime(df["timestamp_local"])
    return df

# -----------------------------------------------------------
# APP
# -----------------------------------------------------------
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
BLUE        = "#4A90D9"

def kpi_card(label, value, color=GREEN_DARK, subtitle=None):
    children = [
        html.P(label, style={"margin": 0, "fontSize": "11px", "color": MUTED, "textTransform": "uppercase", "letterSpacing": "0.08em"}),
        html.P(value, style={"margin": "4px 0 0", "fontSize": "26px", "fontWeight": "700", "color": color}),
    ]
    if subtitle:
        children.append(html.P(subtitle, style={"margin": "2px 0 0", "fontSize": "11px", "color": MUTED}))
    return html.Div(children, style={
        "background": CARD,
        "borderRadius": "12px",
        "padding": "16px 20px",
        "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
        "flex": "1",
        "minWidth": "130px",
    })

def weather_emoji(precip_prob, wind_speed):
    if precip_prob >= 70:
        return "🌧️"
    elif precip_prob >= 40:
        return "🌦️"
    elif precip_prob >= 20:
        return "⛅"
    elif wind_speed > 15:
        return "💨"
    else:
        return "☀️"

def aqi_label(aqi):
    if aqi <= 50:   return ("Good", GREEN_MID)
    if aqi <= 100:  return ("Moderate", AMBER)
    if aqi <= 150:  return ("Unhealthy for Sensitive", "#E59A2F")
    if aqi <= 200:  return ("Unhealthy", RED)
    return ("Very Unhealthy", "#8B0000")

app.layout = html.Div(style={"background": BG, "minHeight": "100vh", "fontFamily": "'Segoe UI', sans-serif", "color": TEXT}, children=[

    # INTERVAL + STORE
    dcc.Interval(id="refresh", interval=60*60*1000, n_intervals=0),
    dcc.Store(id="store"),

    # HEADER
    html.Div(id="header", style={"padding": "20px 32px 8px"}),

    # SMART BANNERS ROW
    html.Div(id="banners", style={"padding": "0 32px 12px", "display": "flex", "gap": "12px", "flexWrap": "wrap"}),

    # DAY SELECTOR
    html.Div([
        html.P("Select Day", style={"margin": "0 12px 0 0", "fontSize": "13px", "fontWeight": "600", "color": GREEN_DARK}),
        dcc.RadioItems(id="day-selector", inline=True,
            inputStyle={"marginRight": "4px"},
            labelStyle={"marginRight": "16px", "fontSize": "13px", "cursor": "pointer", "color": TEXT},
        ),
    ], style={"display": "flex", "alignItems": "center", "padding": "0 32px 16px", "flexWrap": "wrap"}),

    # KPI ROW
    html.Div(id="kpi-row", style={"display": "flex", "gap": "12px", "padding": "0 32px 16px", "flexWrap": "wrap"}),

    # CHARTS
    html.Div([
        # Row 1
        html.Div([
            html.Div([
                html.P("Planting Readiness & Allergy Risk", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}),
                dcc.Graph(id="chart-readiness", config={"displayModeBar": False}),
            ], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
            html.Div([
                html.P("Temperature & Humidity", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}),
                dcc.Graph(id="chart-temp", config={"displayModeBar": False}),
            ], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
        ], style={"display": "flex", "gap": "14px", "marginBottom": "14px"}),

        # Row 2
        html.Div([
            html.Div([
                html.P("Pollen Levels", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}),
                dcc.Graph(id="chart-pollen", config={"displayModeBar": False}),
            ], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
            html.Div([
                html.P("Air Quality Index (US AQI)", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}),
                dcc.Graph(id="chart-aqi", config={"displayModeBar": False}),
            ], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
        ], style={"display": "flex", "gap": "14px", "marginBottom": "14px"}),

        # Row 3
        html.Div([
            html.Div([
                html.P("Soil Temperature & Moisture", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}),
                dcc.Graph(id="chart-soil", config={"displayModeBar": False}),
            ], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
            html.Div([
                html.P("Precipitation Probability & Rainfall", style={"margin": "0 0 4px", "fontWeight": "600", "color": GREEN_DARK}),
                dcc.Graph(id="chart-precip", config={"displayModeBar": False}),
            ], style={"background": CARD, "borderRadius": "12px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.07)", "flex": "1"}),
        ], style={"display": "flex", "gap": "14px"}),

    ], style={"padding": "0 32px 32px"}),
])

# -----------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------
@callback(Output("store", "data"), Input("refresh", "n_intervals"))
def load_data(_):
    df = get_data()
    return df.to_json(date_format="iso", orient="split")

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
@callback(Output("header", "children"), Input("store", "data"))
def update_header(json_data):
    if not json_data:
        return []
    df = pd.read_json(io.StringIO(json_data), orient="split")
    df["timestamp_local"] = pd.to_datetime(df["timestamp_local"])
    now_row = df.iloc[0]
    today_str = datetime.now().strftime("%A, %B %-d, %Y")
    emoji = weather_emoji(now_row["precipitation_probability"], now_row["wind_speed_10m"])
    return html.Div([
        html.Div([
            html.Span(emoji, style={"fontSize": "36px", "marginRight": "14px"}),
            html.Div([
                html.H1("Garden & Allergy Forecast", style={"margin": 0, "fontSize": "22px", "fontWeight": "700", "color": GREEN_DARK}),
                html.P(f"Louisville, KY · {today_str}", style={"margin": 0, "fontSize": "13px", "color": MUTED}),
            ]),
        ], style={"display": "flex", "alignItems": "center"}),
    ])

# -----------------------------------------------------------
# SMART BANNERS
# -----------------------------------------------------------
@callback(Output("banners", "children"), Input("store", "data"))
def update_banners(json_data):
    if not json_data:
        return []
    df = pd.read_json(io.StringIO(json_data), orient="split")
    df["timestamp_local"] = pd.to_datetime(df["timestamp_local"])
    today = df[df["timestamp_local"].dt.date == df["timestamp_local"].dt.date.min()].copy()
    banners = []

    def banner(emoji, text, color, bg):
        return html.Div([
            html.Span(emoji, style={"fontSize": "20px", "marginRight": "8px"}),
            html.Span(text, style={"fontSize": "13px", "fontWeight": "500"}),
        ], style={
            "background": bg, "color": color, "border": f"1px solid {color}",
            "borderRadius": "10px", "padding": "10px 16px",
            "display": "flex", "alignItems": "center",
        })

    # Best time to garden
    today_valid = today.dropna(subset=["allergy_risk", "planting_readiness"])
    if not today_valid.empty:
        today_valid = today_valid.copy()
        today_valid["garden_score"] = today_valid["planting_readiness"] - today_valid["allergy_risk"]
        best = today_valid.loc[today_valid["garden_score"].idxmax()]
        best_time = pd.to_datetime(best["timestamp_local"]).strftime("%-I%p").lower()
        banners.append(banner("🌱", f"Best time to garden today: around {best_time} (low allergy + good conditions)", GREEN_DARK, "#E8F5EE"))

    # Next rain
    future_rain = df[df["precipitation_probability"] >= 50]
    if not future_rain.empty:
        next_rain = pd.to_datetime(future_rain.iloc[0]["timestamp_local"])
        now = df["timestamp_local"].min()
        hours_away = int((next_rain - now).total_seconds() / 3600)
        if hours_away == 0:
            rain_msg = "Rain likely now — hold off on gardening"
        elif hours_away <= 3:
            rain_msg = f"Rain expected in ~{hours_away} hour{'s' if hours_away != 1 else ''} — plan accordingly"
        else:
            rain_msg = f"Next rain in ~{hours_away} hours ({next_rain.strftime('%-I%p %a').lower()})"
        banners.append(banner("🌧️", rain_msg, BLUE, "#EAF2FB"))
    else:
        banners.append(banner("☀️", "No rain expected in the next 7 days", GREEN_MID, "#E8F5EE"))

    # Wind advisory
    max_wind = today["wind_speed_10m"].max() if not today.empty else 0
    if max_wind > 20:
        banners.append(banner("💨", f"Wind advisory: gusts up to {max_wind:.0f} mph today — avoid spraying or seeding", RED, "#FEF0EC"))
    elif max_wind > 12:
        banners.append(banner("🌬️", f"Breezy today (up to {max_wind:.0f} mph) — light outdoor work is fine", AMBER, "#FEF7EC"))

    return banners

# -----------------------------------------------------------
# DAY SELECTOR
# -----------------------------------------------------------
@callback(Output("day-selector", "options"), Output("day-selector", "value"), Input("store", "data"))
def update_day_selector(json_data):
    if not json_data:
        return [], None
    df = pd.read_json(io.StringIO(json_data), orient="split")
    df["timestamp_local"] = pd.to_datetime(df["timestamp_local"])
    days = df["timestamp_local"].dt.date.unique()
    options = []
    for d in sorted(days):
        label = "Today" if d == date.today() else pd.Timestamp(d).strftime("%a %-m/%d")
        options.append({"label": label, "value": str(d)})
    default = str(date.today()) if str(date.today()) in [o["value"] for o in options] else options[0]["value"]
    return options, default

# -----------------------------------------------------------
# KPI ROW
# -----------------------------------------------------------
@callback(Output("kpi-row", "children"), Input("store", "data"), Input("day-selector", "value"))
def update_kpis(json_data, selected_day):
    if not json_data or not selected_day:
        return []
    df = pd.read_json(io.StringIO(json_data), orient="split")
    df["timestamp_local"] = pd.to_datetime(df["timestamp_local"])
    day_df = df[df["timestamp_local"].dt.date == pd.Timestamp(selected_day).date()]
    if day_df.empty:
        return []
    now = day_df.iloc[0]
    high_pollen_hours = int(day_df["high_pollen_flag"].sum())
    aqi_val = now["us_aqi"] if pd.notna(now["us_aqi"]) else 0
    aqi_text, aqi_color = aqi_label(aqi_val)
    temp_color = AMBER if now["temperature_2m"] > 85 else GREEN_DARK
    allergy_color = RED if now["allergy_risk"] > 60 else AMBER if now["allergy_risk"] > 30 else GREEN_DARK
    max_wind = day_df["wind_speed_10m"].max()
    wind_color = RED if max_wind > 20 else AMBER if max_wind > 12 else GREEN_DARK

    return [
        kpi_card("Temp", f'{now["temperature_2m"]:.0f}°F', temp_color, f'High {day_df["temperature_2m"].max():.0f}° / Low {day_df["temperature_2m"].min():.0f}°'),
        kpi_card("Planting Score", f'{now["planting_readiness"]:.0f}/100', GREEN_DARK),
        kpi_card("Allergy Risk", f'{now["allergy_risk"]:.0f}/100', allergy_color),
        kpi_card("AQI", f'{aqi_val:.0f}', aqi_color, aqi_text),
        kpi_card("High Pollen Hours", f'{high_pollen_hours} hrs', RED if high_pollen_hours > 12 else AMBER),
        kpi_card("Max Wind", f'{max_wind:.0f} mph', wind_color),
    ]

# Helper for chart layout
def base_layout(yaxis_title, yaxis2_title=None):
    layout = dict(
        plot_bgcolor=CARD, paper_bgcolor=CARD,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Segoe UI", size=11, color=TEXT),
        legend=dict(orientation="h", y=-0.25, x=0),
        xaxis=dict(showgrid=False, tickformat="%-I%p"),
        yaxis=dict(title=yaxis_title, gridcolor="#EEF2EE"),
        height=240,
    )
    if yaxis2_title:
        layout["yaxis2"] = dict(title=yaxis2_title, overlaying="y", side="right", showgrid=False)
    return layout

def filter_day(json_data, selected_day):
    df = pd.read_json(io.StringIO(json_data), orient="split")
    df["timestamp_local"] = pd.to_datetime(df["timestamp_local"])
    return df[df["timestamp_local"].dt.date == pd.Timestamp(selected_day).date()]

# -----------------------------------------------------------
# CHART CALLBACKS
# -----------------------------------------------------------
@callback(Output("chart-readiness", "figure"), Input("store", "data"), Input("day-selector", "value"))
def chart_readiness(json_data, selected_day):
    if not json_data or not selected_day: return go.Figure()
    df = filter_day(json_data, selected_day)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["planting_readiness"], name="Planting Readiness", fill="tozeroy", line=dict(color=GREEN_MID, width=2)))
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["allergy_risk"], name="Allergy Risk", line=dict(color=RED, width=2, dash="dot")))
    fig.update_layout(**base_layout("Score (0-100)"))
    return fig

@callback(Output("chart-temp", "figure"), Input("store", "data"), Input("day-selector", "value"))
def chart_temp(json_data, selected_day):
    if not json_data or not selected_day: return go.Figure()
    df = filter_day(json_data, selected_day)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["temperature_2m"], name="Temp (F)", line=dict(color=AMBER, width=2)))
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["relative_humidity_2m"], name="Humidity (%)", line=dict(color=GREEN_MID, width=2, dash="dot"), yaxis="y2"))
    fig.update_layout(**base_layout("Temperature (F)", "Humidity (%)"))
    return fig

@callback(Output("chart-pollen", "figure"), Input("store", "data"), Input("day-selector", "value"))
def chart_pollen(json_data, selected_day):
    if not json_data or not selected_day: return go.Figure()
    df = filter_day(json_data, selected_day)
    fig = go.Figure()
    colors = [GREEN_MID, AMBER, RED, SOIL, GREEN_DARK, GREEN_LIGHT]
    for col, color in zip(["grass_pollen", "ragweed_pollen", "birch_pollen", "alder_pollen", "mugwort_pollen", "olive_pollen"], colors):
        fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df[col].fillna(0), name=col.replace("_pollen", "").title(), line=dict(width=1.5, color=color)))
    fig.update_layout(**base_layout("Pollen (grains/m3)"))
    return fig

@callback(Output("chart-aqi", "figure"), Input("store", "data"), Input("day-selector", "value"))
def chart_aqi(json_data, selected_day):
    if not json_data or not selected_day: return go.Figure()
    df = filter_day(json_data, selected_day)
    fig = go.Figure()
    aqi_vals = df["us_aqi"].fillna(0)
    colors_list = []
    for v in aqi_vals:
        if v <= 50:   colors_list.append(GREEN_MID)
        elif v <= 100: colors_list.append(AMBER)
        elif v <= 150: colors_list.append("#E59A2F")
        else:          colors_list.append(RED)
    fig.add_trace(go.Bar(x=df["timestamp_local"], y=aqi_vals, name="AQI", marker_color=colors_list, opacity=0.85))
    fig.add_hrect(y0=0,   y1=50,  fillcolor=GREEN_MID, opacity=0.04, line_width=0, annotation_text="Good",     annotation_position="top left", annotation_font_size=10)
    fig.add_hrect(y0=50,  y1=100, fillcolor=AMBER,     opacity=0.04, line_width=0, annotation_text="Moderate", annotation_position="top left", annotation_font_size=10)
    fig.add_hrect(y0=100, y1=300, fillcolor=RED,       opacity=0.04, line_width=0, annotation_text="Unhealthy",annotation_position="top left", annotation_font_size=10)
    fig.update_layout(**base_layout("US AQI"))
    return fig

@callback(Output("chart-soil", "figure"), Input("store", "data"), Input("day-selector", "value"))
def chart_soil(json_data, selected_day):
    if not json_data or not selected_day: return go.Figure()
    df = filter_day(json_data, selected_day)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["soil_temperature_0cm"], name="Soil Temp (F)", line=dict(color=SOIL, width=2)))
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["soil_moisture_0_to_1cm"], name="Soil Moisture", line=dict(color=GREEN_MID, width=2, dash="dot"), yaxis="y2"))
    fig.update_layout(**base_layout("Soil Temp (F)", "Moisture"))
    return fig

@callback(Output("chart-precip", "figure"), Input("store", "data"), Input("day-selector", "value"))
def chart_precip(json_data, selected_day):
    if not json_data or not selected_day: return go.Figure()
    df = filter_day(json_data, selected_day)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["timestamp_local"], y=df["precipitation_probability"], name="Rain Probability (%)", marker_color=BLUE, opacity=0.6))
    fig.add_trace(go.Scatter(x=df["timestamp_local"], y=df["precipitation"], name="Precipitation (in)", line=dict(color=GREEN_DARK, width=2), yaxis="y2"))
    fig.update_layout(**base_layout("Probability (%)", "Inches"))
    return fig

# -----------------------------------------------------------
# RUN
# -----------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
