import plotly.express as px
import plotly.io as pio
import pandas as pd


# Theme to apply to all charts
def apply_theme(fig, *, show_legend=False):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="system-ui, -apple-system, Segoe UI, Roboto",
            color="#1F1D20",
            size=12
        ),
        colorway=["#bc783d", "#4c2e19", "#e19b56", "#1F1D20"],
        showlegend=show_legend,
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(x=0, xanchor="left", font=dict(size=14, color="#1F1D20")),
    )

    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks="")
    fig.update_yaxes(showgrid=False, zeroline=False, showline=False, ticks="")

    return fig


# Bar chart: hours by category 
def today_by_category(df, selected_category):
    df = df.sort_values("total_time_spent_hours", ascending=True)

    fig = px.bar(
        df,
        x="total_time_spent_hours",
        y="category",
        orientation="h",
        title=None,
    )

    fig = apply_theme(fig)

    # color each bar: selected = accent, others muted
    colors = []
    for cat in df["category"]:
        if selected_category and cat == selected_category:
            colors.append("#bc783d")   # accent
        else:
            colors.append("#e0d8c8")   # muted
    fig.update_traces(marker_color=colors)

    # tooltip
    fig.update_traces(
        hovertemplate="%{y}<br>%{x:.2f} hours<extra></extra>"
    )

    return fig



# Bar chart for selected subcategory breakdown
def subcategories_breakdown(df, selected_category):
    df = df.sort_values("total_time_spent_hours", ascending=True)

    fig = px.bar(
        df,
        x="subcategory",
        y="total_time_spent_hours",
    )

    # One consistent color
    fig.update_traces(
        marker=dict(color="#bc783d"),
        marker_line_width=0,
        hovertemplate="%{x}<br>%{y:.2f} hours<extra></extra>",
    )

    # No chart title; axis labels optional (I’d remove to keep it clean)
    fig.update_layout(
        title=None,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    fig.update_yaxes(title=None, tickformat=".2f")
    fig.update_xaxes(title=None)
    fig.update_xaxes(tickangle=-25)


    return apply_theme(fig, show_legend=False)



# Donut chart for share of selected category of total time tracked
def category_share_donut(df):
    fig = px.pie(
        df,
        names="label",
        values="hours",
        hole=0.62,
    )

    fig.update_traces(
        marker=dict(colors=["#bc783d", "#e9e5dd"], line=dict(width=0)),
        textinfo="percent",
        textposition="inside",
        sort=False,
        hovertemplate="%{label}<br>%{value:.2f} hours (%{percent})<extra></extra>",
    )

    fig.update_layout(
        title=None,
        height=180,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return apply_theme(fig, show_legend=False)



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

    muted = "#c9c6c0"
    highlight = "#bc783d"

    selected_trace = None
    other_traces = []

    # Disable hover
    for tr in fig.data:
        tr.hoverinfo = "skip"
        tr.hovertemplate = None

    # Style + collect traces
    for tr in fig.data:
        if tr.name == selected_category:
            tr.line.color = highlight
            tr.line.width = 3.5
            tr.opacity = 1

            # turn hover back on only in highlighted category
            tr.hoverinfo = "text"
            tr.hovertemplate = "%{x|%b %d}<br>%{y:.2f} hours<extra></extra>"

            selected_trace = tr
        else:
            tr.line.color = muted
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

    return apply_theme(fig, show_legend=False)



def fig_to_div(fig):
    return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")





