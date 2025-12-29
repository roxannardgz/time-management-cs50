import plotly.express as px
import plotly.io as pio


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
def today_by_category(df):
    df = df.sort_values("total_time_spent_hours", ascending=True)

    fig = px.bar(
        df,
        x="total_time_spent_hours",
        y="category",
        orientation="h",
        title="Hours by Category"
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    fig.update_xaxes(title="Hours", tickformat=".2f")
    fig.update_traces(
        marker=dict(color="#fbd6a3"),
        marker_line_width=0
    )
    return apply_theme(fig, show_legend=False)


# Bar chart for selected subcategory breakdown
def subcategories_breakdown(df, selected_category):
    df = df.sort_values("total_time_spent_hours", ascending=True)

    fig = px.bar(
        df,
        x="subcategory",
        y="total_time_spent_hours",
        title=f"{selected_category} - subcategories"
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    fig.update_yaxes(title="Hours", tickformat=".2f")

    fig.update_traces(
        marker=dict(color="#fbd6a3"),
        marker_line_width=0
    )
    return apply_theme(fig, show_legend=False)


# Donut chart for share of selected category of total time tracked
def category_share_donut(df):
    fig = px.pie(
        df,
        names="label",
        values="hours",
        hole=0.6,
    )

    fig.update_traces(
        marker=dict(colors=["#1F1D20", "#fbd6a3"]),
        textinfo="percent",
        textposition="inside",
        sort=False,
    )

    fig.update_layout(height=180, margin=dict(l=0, r=0, t=0, b=0))

    return apply_theme(fig, show_legend=False)


# Line chart for weekly trend - only week view
def weekly_trend(df):
    fig = px.line(df, x="event_date", y="hours", markers=True, title=None)
    fig.update_traces(line_width=3, marker_size=7)
    fig.update_layout(height=220)

    fig = apply_theme(fig, show_legend=False)

    fig.update_traces(line=dict(color="#bc783d"), marker=dict(color="#bc783d"))

    # tooltip
    fig.update_traces(hovertemplate="%{x}<br>%{y:.2f} hours<extra></extra>")

    return fig


def fig_to_div(fig):
    return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")





