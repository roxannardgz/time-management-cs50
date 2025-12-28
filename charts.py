import plotly.express as px
import plotly.io as pio

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



def fig_to_div(fig):
    return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")

def apply_theme(fig, *, show_legend=False):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1F1D20"),
        showlegend=show_legend,
        margin=dict(l=10, r=10, t=40, b=10),
    )

    fig.update_xaxes(showgrid=False, zeroline=True, showline=True)
    fig.update_yaxes(showgrid=False, zeroline=True, showline=True)

    return fig


