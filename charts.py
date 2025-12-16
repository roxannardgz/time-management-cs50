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
    return fig

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

    return fig


def fig_to_div(fig):
    return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
