import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio
pio.templates

#Set session variables
def set_sv_vars():
    for var_name in st.session_state.keys():
        if var_name.startswith("sv_"):
            var_name_no_prefix = var_name.replace("sv_","")
            st.session_state[var_name] = st.session_state[var_name_no_prefix]


#Get scatter plot fields
def scatter_plot_fields(nums_df,cats_df):
    col1, col2, col3 = st.columns(3)

    y_metric_val = col1.selectbox("Y-axis Field", options=nums_df.columns, key=f"y_metric_val")
    x_metric_val = col2.selectbox("X-axis Field", options=nums_df.columns, key=f"x_metric_val")
    data_point_cat_val = col3.selectbox("Data Point Field", options=cats_df.columns, key=f"data_point_cat_val")
    y_metric_agg = col1.selectbox("Y-axis Aggregation", options=['sum','mean','median','max','min','count'], key=f"y_metric_agg")
    x_metric_agg = col2.selectbox("X-axis Aggregation", options=['sum','mean','median','max','min','count'], key=f"x_metric_agg")

    return y_metric_val,x_metric_val,data_point_cat_val,y_metric_agg,x_metric_agg


#Create Scatterplot
def scatter_plot_build(df,y_metric_val,x_metric_val,data_point_cat_val,y_metric_agg,x_metric_agg):
    y_axis_nm = y_metric_val + ' (' + y_metric_agg + ')'
    x_axis_nm = x_metric_val + ' (' + x_metric_agg + ')'
    
    if x_metric_val == y_metric_val:
        plt_df = df.groupby([data_point_cat_val], as_index=False).agg({y_metric_val:[y_metric_agg, x_metric_agg]})
        if x_metric_val == y_metric_val:
            plt_df.columns = [data_point_cat_val, y_axis_nm, x_axis_nm + ' ']
        else:
            plt_df.columns = [data_point_cat_val, y_axis_nm, x_axis_nm]
    else:
        plt_df = df.groupby([data_point_cat_val], as_index=False).agg({y_metric_val:y_metric_agg,x_metric_val:x_metric_agg}).rename(columns={y_metric_val:y_axis_nm, x_metric_val:x_axis_nm})
    
    title = data_point_cat_val + ' by ' + y_axis_nm + ' and ' + x_axis_nm
    title = title.replace('_',' ').title()

    plot = px.scatter(plt_df, x=x_axis_nm, y=y_axis_nm, title=title, template="simple_white").update_traces(marker={'size': 12},marker_color='#efbb62',opacity=.4).update_layout(
            hoverlabel=dict(
                bgcolor="#f7e8c8",
                font_size=14,
                font_family="sans-serif"),
            font_family="sans-serif",
            font_size=8,
            font_color="#202c39",
            title_font_family="sans-serif",
            title_font_color="#202c39",
            title_font_size=14,
            xaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
    ),
    yaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
        ))
    st.plotly_chart(plot, use_container_width=True)


#Get bar chart fields
def bar_chart_fields(cats_df,nums_df):
    col1, col2, col3 = st.columns(3)

    display_bars = col3.selectbox("Bars Direction", options=['Horizontal','Vertical'], key=f"br_display_bars")
    cat_val = col1.selectbox("Categorical Field", options=cats_df.columns, key=f"br_cat_val")
    metric_val = col2.selectbox("Metric Field", options=nums_df.columns, key=f"br_metric_val")
    metric_agg = col2.selectbox("Metric Aggregation", options=['sum','mean','median','max','min','count'], key=f"br_metric_agg")

    return display_bars,cat_val,metric_val,metric_agg

#Create bar chart
def bar_chart_build(df,display_bars,cat_val,metric_val,metric_agg):
    metric_nm = metric_val + ' (' + metric_agg + ')'
    
    plt_df = df.groupby([cat_val], as_index=False).agg({metric_val:metric_agg})
    plt_df[metric_nm] = plt_df[metric_val]
    
    title = metric_val + ' by ' + cat_val
    title = title.replace('_',' ').title()

    if display_bars == 'Vertical':
        plot = px.bar(plt_df, x=cat_val, y=metric_val, title=title, template="simple_white").update_traces(marker_color='#efbb62',opacity=.4).update_layout(
            hoverlabel=dict(
                bgcolor="#f7e8c8",
                font_size=14,
                font_family="sans-serif"),
            font_family="sans-serif",
            font_size=8,
            font_color="#202c39",
            title_font_family="sans-serif",
            title_font_color="#202c39",
            title_font_size=14,
            xaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
    ),
    yaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
        ))
        plot.update_layout(xaxis={'categoryorder':'total descending'})
    else:
        plot = px.bar(plt_df, y=cat_val, x=metric_val, title=title, template="simple_white").update_traces(marker_color='#efbb62',opacity=.4).update_layout(
            hoverlabel=dict(
                bgcolor="#f7e8c8",
                font_size=14,
                font_family="sans-serif"),
            font_family="sans-serif",
            font_size=8,
            font_color="#202c39",
            title_font_family="sans-serif",
            title_font_color="#202c39",
            title_font_size=14,
            xaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
    ),
    yaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
        ))
        plot.update_layout(yaxis={'categoryorder':'total ascending'})

    st.plotly_chart(plot, use_container_width=True)


#Get line chart fields
def line_chart_fields(cats_df,nums_df,dates_df):
    col1, col2, col3 = st.columns(3)

    ln_cat_lst = ['None']
    ln_cat_lst.extend(cats_df.columns)
    cat_val = col1.selectbox("Legend Field", options=ln_cat_lst, key=f"ln_cat_val")
    x_val = col2.selectbox("Date Field", options=dates_df.columns, key=f"ln_x_val")
    dt_lvl = col2.selectbox("Date Level", options=['year','month','day'], key=f"ln_dt_lvl")
    y_val = col3.selectbox("Metric Field", options=nums_df.columns, key=f"ln_y_val")
    y_agg = col3.selectbox("Metric Aggregation", options=['sum','mean','median','max','min','count'], key=f"ln_y_agg")

    y_nm = y_val + ' (' + y_agg + ')'

    return cat_val,x_val,y_val,y_agg,y_nm,dt_lvl


#Create line chart
def line_chart_build(df,cat_val,x_val,y_val,y_agg,y_nm,dt_lvl):  
    if dt_lvl == 'year':
        df[x_val] = df[x_val].dt.year
    elif dt_lvl == 'month':
        df[x_val] = df[x_val].dt.to_period('M').dt.to_timestamp()

    title = y_val + ' by ' + x_val
    title = title.replace('_',' ').title()

    if cat_val == 'None':  
        plt_df = df.groupby([x_val], as_index=False).agg({y_val:y_agg})
        plt_df[y_nm] = plt_df[y_val]
        plot = px.line(plt_df, x=x_val, y=y_nm, title=title, template="simple_white").update_traces(line_color='#efbb62',connectgaps=False,opacity=.4).update_layout(
            hovermode="x",
            hoverlabel=dict(
                bgcolor="#f7e8c8",
                font_size=14,
                font_family="sans-serif"),
            font_family="sans-serif",
            font_size=8,
            font_color="#202c39",
            title_font_family="sans-serif",
            title_font_color="#202c39",
            title_font_size=14,
            xaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
    ),
    yaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
        ))
    else:
        plt_df = df.groupby([cat_val, x_val], as_index=False).agg({y_val:y_agg})
        plt_df[y_nm] = plt_df[y_val]
        plot = px.line(plt_df, x=x_val, y=y_nm, title=title, template="simple_white",color=cat_val).update_traces(connectgaps=False,opacity=.4).update_layout(
            hoverlabel=dict(
                bgcolor="#f7e8c8",
                font_size=14,
                font_family="sans-serif"),
            font_family="sans-serif",
            font_size=8,
            font_color="#202c39",
            title_font_family="sans-serif",
            title_font_color="#202c39",
            title_font_size=14,
            xaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
    ),
    yaxis=dict(
        title_font=dict(size=10, family='sans-serif', color='#202c39'),
        tickfont=dict(size=9, family='sans-serif', color='#202c39')
        ))

    st.plotly_chart(plot, use_container_width=True)

    return plt_df
