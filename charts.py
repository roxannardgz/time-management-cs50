import plotly.express as px
import plotly.io as pio
import pandas as pd

from config import CATEGORY_SHORT, SUBCAT_SHORT

# Colors
accent_color = "#D6AB86"
muted_color = "#e0d8c8"
font_color = "#3E2C1C"

# Category mapping: short labels for display
def short_label(name: str, mapping: dict[str, str]) -> str:
    return mapping.get(name, name)

# Theme to apply to all charts
def apply_theme(fig, *, show_legend=False):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="system-ui, -apple-system, Segoe UI, Roboto",
            color=font_color,
            size=12
        ),
        #colorway=["#bc783d", "#4c2e19", "#e19b56", "#1F1D20"],
        showlegend=show_legend,
        margin=dict(l=10, r=10, t=30, b=10),
    )

    fig.update_xaxes(showgrid=False, zeroline=True, showline=False, ticks="")
    fig.update_yaxes(showgrid=False, zeroline=True, showline=False, ticks="")

    return fig


# Bar chart: hours by category 
def today_by_category(df, selected_category):
    df = df.sort_values("total_time_spent_hours", ascending=True)

    df = df.copy()
    df["category_short"] = df["category"].map(lambda x: short_label(x, CATEGORY_SHORT))

    fig = px.bar(
        df,
        x="total_time_spent_hours",
        y="category_short",
        orientation="h",
        title=None,
    )

    fig = apply_theme(fig)

    # color each bar: selected = accent, others muted
    colors = []
    for cat in df["category"]:
        if selected_category and cat == selected_category:
            colors.append(accent_color)   # accent
        else:
            colors.append(muted_color)   # muted
    fig.update_traces(marker_color=colors)

    # tooltip
    fig.update_traces(
        hovertemplate="%{customdata[0]}<br>%{x:.2f} hours<extra></extra>",
        customdata=df[["category"]].to_numpy(),
    )

    fig.update_xaxes(title_text="Total time (hours)")
    fig.update_yaxes(title_text=None)
    fig.update_layout(height=500) 

    return fig


# Bar chart for selected subcategory breakdown
def subcategories_breakdown(df, selected_category):
    df = df.copy()
    df = df.sort_values("total_time_spent_hours", ascending=True)

    # % within selected category
    total = df["total_time_spent_hours"].sum()
    df["pct"] = (df["total_time_spent_hours"] / total * 100) if total > 0 else 0

    # Category mapping: short labels for x-axis
    df["subcategory_short"] = df["subcategory"].map(lambda x: short_label(x, SUBCAT_SHORT))
    
    fig = px.bar(
        df,
        x="subcategory_short",
        y="pct",
    )

    fig = apply_theme(fig)

    fig.update_traces(
        marker=dict(color=accent_color),
        marker_line_width=0,

        # show % on top of each bar
        text=df["pct"].round(0).astype(int).astype(str) + "%", 
        textposition="outside",
        cliponaxis=False,

        # tooltip: full name + hours and %
        customdata=df[["subcategory", "total_time_spent_hours"]].to_numpy(),
        hovertemplate="%{customdata[0]}<br>%{y:.0f}% of category<br>%{customdata[1]:.2f} hours<extra></extra>",
    )

    fig.update_layout(
        title=None,
        margin=dict(l=10, r=10, t=10, b=10),
    )

    # Keep short names on x, remove axis title
    fig.update_xaxes(title_text=None, tickangle=0)

    # Hide y-axis completely
    fig.update_yaxes(
        title_text=None,
        showticklabels=False,
        ticks="",
        showgrid=False,
        zeroline=True,
        showline=False,
        rangemode="tozero",
    )

    fig.update_layout(height=240)

    return fig


# Donut chart for share of selected category of total time tracked
def category_share_donut(df):
    
    total = df["hours"].sum()
    selected_hours = float(df.iloc[0]["hours"]) if len(df) else 0
    pct = (selected_hours / total * 100) if total > 0 else 0

    fig = px.pie(
        df,
        names="label",
        values="hours",
        hole=0.8,
    )

    fig = apply_theme(fig)

    # Keep tooltips, remove slice text
    fig.update_traces(
        marker=dict(colors=[accent_color, muted_color]),
        textinfo="none",
        hovertemplate="%{label}<br>%{value:.2f} hours<extra></extra>",
        sort=False,
        
    )

    # Put only the selected % in the center
    fig.update_layout(
        height=170,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        annotations=[
            dict(
                text=f"{pct:.0f}%",
                x=0.5, y=0.5,
                font=dict(size=22, color=font_color),
                showarrow=False
            )
        ],
    )

    return fig


# Line chart for weekly trend - only week view
def weekly_trend_by_category(df, selected_category):
    df = df.copy()
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.normalize()

    # Build a full daily index for the last 7 days shown in the data
    start = df["event_date"].min()
    end = df["event_date"].max()
    all_days = pd.date_range(start=start, end=end, freq="D")

    # Use all categories (from the df)
    categories = sorted(df["category"].unique())

    # Create full grid (day x category)
    grid = pd.MultiIndex.from_product(
        [all_days, categories],
        names=["event_date", "category"]
    ).to_frame(index=False)

    # Merge + fill missing with 0
    df = grid.merge(df[["event_date", "category", "hours"]], on=["event_date", "category"], how="left")
    df["hours"] = df["hours"].fillna(0)

    fig = px.line(
        df,
        x="event_date",
        y="hours",
        color="category",
        markers=True,
    )

    fig = apply_theme(fig)

    selected_trace = None
    other_traces = []

    # Disable hover
    for tr in fig.data:
        tr.hoverinfo = "skip"
        tr.hovertemplate = None

    # Style + collect traces
    for tr in fig.data:
        if tr.name == selected_category:
            tr.line.color = accent_color
            tr.line.width = 3.5
            tr.opacity = 1

            # turn hover back on only in highlighted category
            tr.hoverinfo = "text"
            tr.hovertemplate = "%{x|%b %d}<br>%{y:.2f} hours<extra></extra>"

            selected_trace = tr
        else:
            tr.line.color = muted_color
            tr.line.width = 2
            tr.opacity = 0.35
            other_traces.append(tr)

    # Keep highlighted line on top
    if selected_trace is not None:
        fig.data = tuple(other_traces + [selected_trace])

    # Smooth lines without resetting hover
    for tr in fig.data:
        tr.line.shape = "spline"
        tr.line.smoothing = 0.4

    fig.update_yaxes(title_text="Total time (hours)")
    fig.update_xaxes(title_text=None, showgrid=False, zeroline=True, showline=False, ticks="")


    fig.update_layout(height=280) 

    return fig


def fig_to_div(fig):
    return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")





