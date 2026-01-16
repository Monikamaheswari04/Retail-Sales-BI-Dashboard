import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# -----------------------------
# 1. Load Dataset
# -----------------------------
file_path = r"C:\Users\ADMIN\Desktop\Sales_Project\retail_sales.csv"
df = pd.read_csv(file_path)

# -----------------------------
# 2. Preprocessing
# -----------------------------
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Postal Code'] = df['Postal Code'].fillna(0)
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month

# -----------------------------
# 3. App Init
# -----------------------------
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Retail Sales BI Dashboard"

# -----------------------------
# 4. Dropdown options
# -----------------------------
year_options = [{'label': str(y), 'value': y} for y in sorted(df['Year'].unique())]
region_options = [{'label': r, 'value': r} for r in sorted(df['Region'].unique())]
category_options = [{'label': c, 'value': c} for c in sorted(df['Category'].unique())]

# -----------------------------
# 5. Styles
# -----------------------------
GLASS_STYLE = {
    "background": "rgba(255,255,255,0.08)",
    "backdrop-filter": "blur(12px)",
    "-webkit-backdrop-filter": "blur(12px)",
    "border-radius": "16px",
    "border": "1px solid rgba(255,255,255,0.15)",
    "box-shadow": "0 8px 32px rgba(0,0,0,0.37)"
}

CARD_STYLE = {
    **GLASS_STYLE,
    "padding": "20px",
    "margin": "10px",
    "flex": "1 1 30%",
    "minWidth": "240px",
    "textAlign": "center",
    "cursor": "pointer",
    "transition": "all 0.3s ease-in-out"
}

GRAPH_STYLE = {
    **GLASS_STYLE,
    "padding": "10px",
    "margin": "10px",
    "flex": "1 1 45%",
    "minWidth": "300px"
}

# -----------------------------
# 6. Layout
# -----------------------------
app.layout = html.Div([

    # Sidebar
    html.Div([
        html.H2("📊 Sales BI", style={"color": "#00f5d4", "textAlign": "center", "marginBottom": "30px"}),

        html.Label("Year", style={"color": "#cbd5e1"}),
        dcc.Dropdown(id="year-dropdown", options=year_options, placeholder="All Years",
                     style={"marginBottom": "20px"}),

        html.Label("Region", style={"color": "#cbd5e1"}),
        dcc.Dropdown(id="region-dropdown", options=region_options, placeholder="All Regions",
                     style={"marginBottom": "20px"}),

        html.Label("Category", style={"color": "#cbd5e1"}),
        dcc.Dropdown(id="category-dropdown", options=category_options, placeholder="All Categories"),

    ], style={
        "width": "260px",
        "padding": "20px",
        "background": "linear-gradient(180deg, #020617, #020617, #0f172a)",
        "height": "100vh",
        "position": "fixed",
        "left": "0",
        "top": "0",
        "overflowY": "auto",
        "boxShadow": "4px 0 20px rgba(0,0,0,0.5)"
    }),

    # Main Content
    html.Div([

        html.H1("Retail Sales Dashboard", style={
            "color": "white",
            "textAlign": "center",
            "marginBottom": "25px",
            "letterSpacing": "1px"
        }),

        # KPI Cards
        html.Div(id="summary-cards", style={
            "display": "flex",
            "flexWrap": "wrap",
            "justifyContent": "space-around"
        }),

        # Tabs (Always visible in dark theme)
        dcc.Tabs([
            dcc.Tab(label="📈 Overview", children=[
                html.Div([
                    html.Div(dcc.Graph(id="category-bar"), style=GRAPH_STYLE),
                    html.Div(dcc.Graph(id="region-bar"), style=GRAPH_STYLE),
                    html.Div(dcc.Graph(id="segment-bar"), style=GRAPH_STYLE),
                    html.Div(dcc.Graph(id="top-products-bar"), style=GRAPH_STYLE),
                    html.Div(dcc.Graph(id="top-states-bar"), style=GRAPH_STYLE),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-around"})
            ], style={"backgroundColor": "#020617", "color": "white"},
               selected_style={"backgroundColor": "#020617", "color": "#00f5d4", "borderTop": "3px solid #00f5d4"}),

            dcc.Tab(label="📊 Trends", children=[
                html.Div([
                    html.Div(dcc.Graph(id="yearly-line"), style=GRAPH_STYLE),
                    html.Div(dcc.Graph(id="monthly-line"), style=GRAPH_STYLE),
                    html.Div(dcc.Graph(id="subcategory-bar"), style=GRAPH_STYLE),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-around"})
            ], style={"backgroundColor": "#020617", "color": "white"},
               selected_style={"backgroundColor": "#020617", "color": "#00f5d4", "borderTop": "3px solid #00f5d4"}),

            dcc.Tab(label="🔥 Heatmap", children=[
                html.Div(dcc.Graph(id="heatmap-month-year"), style={
                    **GRAPH_STYLE,
                    "width": "95%"
                })
            ], style={"backgroundColor": "#020617", "color": "white"},
               selected_style={"backgroundColor": "#020617", "color": "#00f5d4", "borderTop": "3px solid #00f5d4"}),
        ])

    ], style={
        "marginLeft": "280px",
        "padding": "20px",
        "minHeight": "100vh",
        "background": "linear-gradient(135deg, #020617, #020617, #0f172a)"
    })

])

# -----------------------------
# 7. Callback
# -----------------------------
@app.callback(
    Output("summary-cards", "children"),
    Output("category-bar", "figure"),
    Output("subcategory-bar", "figure"),
    Output("region-bar", "figure"),
    Output("segment-bar", "figure"),
    Output("top-products-bar", "figure"),
    Output("top-states-bar", "figure"),
    Output("yearly-line", "figure"),
    Output("monthly-line", "figure"),
    Output("heatmap-month-year", "figure"),
    Input("year-dropdown", "value"),
    Input("region-dropdown", "value"),
    Input("category-dropdown", "value"),
)
def update_dashboard(year, region, category):

    dff = df.copy()
    if year:
        dff = dff[dff["Year"] == year]
    if region:
        dff = dff[dff["Region"] == region]
    if category:
        dff = dff[dff["Category"] == category]

    total_sales = dff["Sales"].sum()
    top_product = dff.groupby("Product Name")["Sales"].sum().idxmax()
    top_region = dff.groupby("Region")["Sales"].sum().idxmax()

    # KPI Cards with hover + glow
    cards = [
        html.Div([
            html.H4("💰 Total Sales", style={"color": "#00f5d4"}),
            html.H2(f"${total_sales:,.0f}", style={"color": "white"})
        ], style={**CARD_STYLE, "boxShadow": "0 0 15px rgba(0,245,212,0.4)"}),

        html.Div([
            html.H4("🏆 Top Product", style={"color": "#00f5d4"}),
            html.H5(top_product, style={"color": "white"})
        ], style={**CARD_STYLE, "boxShadow": "0 0 15px rgba(0,245,212,0.4)"}),

        html.Div([
            html.H4("🌍 Top Region", style={"color": "#00f5d4"}),
            html.H5(top_region, style={"color": "white"})
        ], style={**CARD_STYLE, "boxShadow": "0 0 15px rgba(0,245,212,0.4)"}),
    ]

    # Charts
    fig_category = px.bar(dff.groupby("Category")["Sales"].sum().sort_values(),
                          orientation="h", title="Sales by Category")

    fig_subcategory = px.bar(dff.groupby("Sub-Category")["Sales"].sum().sort_values(),
                             orientation="h", title="Sales by Sub-Category")

    fig_region = px.bar(dff.groupby("Region")["Sales"].sum().sort_values(),
                        orientation="h", title="Sales by Region")

    fig_segment = px.bar(dff.groupby("Segment")["Sales"].sum().sort_values(),
                         orientation="h", title="Sales by Segment")

    fig_top_products = px.bar(dff.groupby("Product Name")["Sales"].sum().nlargest(10),
                              title="Top 10 Products")

    fig_top_states = px.bar(dff.groupby("State")["Sales"].sum().nlargest(10),
                            title="Top 10 States")

    fig_yearly = px.line(dff.groupby("Year")["Sales"].sum(), markers=True, title="Yearly Trend")
    fig_monthly = px.line(dff.groupby("Month")["Sales"].sum(), markers=True, title="Monthly Trend")

    heatmap_data = dff.pivot_table(values="Sales", index="Month", columns="Year", aggfunc="sum")
    fig_heatmap = px.imshow(heatmap_data, title="Sales Heatmap", aspect="auto")

    # Dark theme for all charts
    for fig in [fig_category, fig_subcategory, fig_region, fig_segment,
                fig_top_products, fig_top_states, fig_yearly, fig_monthly, fig_heatmap]:
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            title_font_color="#00f5d4",
            hoverlabel=dict(bgcolor="#020617", font_color="white")
        )

    return cards, fig_category, fig_subcategory, fig_region, fig_segment, \
           fig_top_products, fig_top_states, fig_yearly, fig_monthly, fig_heatmap


# -----------------------------
# 8. Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
