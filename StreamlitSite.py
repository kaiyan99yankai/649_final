import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data
import geopandas as gpd

st.title('SI649 Covid Traveling Dashboard')

st.header('Introduction')

st.text("This is a tool for you, the travel agents and group travel planners, to compare travelers' needs and behaviors before, during and after the COVID pandemic")

st.header('Plane Travels')
tsa_df = pd.read_excel('tsa.xlsx')
tsa_df_date = tsa_df.set_index('Date')
tsa_df_year = tsa_df_date.stack().reset_index().rename(columns={'level_1':'year'})
tsa_df_stack = tsa_df_year.join(tsa_df_date)
tsa_df_stack = tsa_df_stack[['Date', 'year', 0]]
tsa_df_stack = tsa_df_stack.rename(columns={0:'data'})

line = alt.Chart(tsa_df_stack).mark_line().encode(
        x = alt.X('Date'),
        y = alt.Y('data', title = 'Passenger volumes'),
        color = 'year:N',
        strokeWidth = alt.value(1)
)

# 添加交互式选择器
selector = alt.selection_single(
    on='mouseover',
    nearest=True,
    empty='none',
    fields=['Date'],
    init={'Date': '2022-01-01'}
)

# 创建一个点图层，用于显示选择器位置的信息
points = line.mark_point().encode(
    opacity=alt.condition(selector, alt.value(1), alt.value(0))
).add_selection(selector)

# 创建一个文本图层，用于显示选择器位置对应的y值
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(selector, 'data:Q', alt.value(' '))
)

# 添加一条垂直线
vline = alt.Chart(tsa_df_stack).mark_rule(color='red').encode(
    x='Date',
    size=alt.value(0.1)
).transform_filter(
    selector
)

# 将图表和交互式元素组合在一起
chart = alt.layer(line, points, text, vline)

# 显示图表
chart.properties(
    width=2000, 
    title='TSA checkpoint travel numbers'
)

# chart

df_2022 = pd.read_excel('US-Outbound-to-World-Regions_2022.xlsx')
df_2022.columns = df_2022.iloc[2]
df_2022_select = df_2022.iloc[3:10].set_index('Regions')
df_2022_select.columns.name = None
df_2022_select = df_2022_select.iloc[:, : 12]
df_2022_final = df_2022_select.reset_index()
df_2022_stack = df_2022_final.iloc[:, 1:12].stack().reset_index().set_index('level_0').join(df_2022_final).iloc[:, 0:3].rename(columns = {'level_1':'Month', 0:'Data'})
bar_2022 = alt.Chart(df_2022_stack).mark_bar().encode(
        x = alt.X('Month'),
        y = alt.Y('Data'),
        color = 'Regions:N',
)
bar_2022 = bar_2022.properties(title='2022 US citizens travel to international regions')

df_2021 = pd.read_excel('US-Outbound-to-World-Regions_2021.xlsx')
df_2021.columns = df_2021.iloc[2]
df_2021_select = df_2021.iloc[3:10].set_index('Regions')
df_2021_select.columns.name = None
df_2021_select = df_2021_select.iloc[:, : 12]
df_2021_final = df_2021_select.reset_index()
df_2021_stack = df_2021_final.iloc[:, 1:12].stack().reset_index().set_index('level_0').join(df_2021_final).iloc[:, 0:3].rename(columns = {'level_1':'Month', 0:'Data'})
# 创建一个选择器，用于捕获用户在2022年数据的月份柱状图上的鼠标悬停操作
month_selector_2022 = alt.selection_single(fields=['Month'], empty='none', on='mouseover')

# 创建一个选择器，用于捕获用户在2021年数据的月份柱状图上的鼠标悬停操作
month_selector_2021 = alt.selection_single(fields=['Month'], empty='none', on='mouseover')

# Create the bar chart for 2022 data
bar_2022 = alt.Chart(df_2022_stack).mark_bar().encode(
        x = alt.X('Month'),
        y = alt.Y('Data'),
        color = 'Regions:N',
).properties(title='2022 US citizens travel to international regions', width=300).add_selection(
    month_selector_2022
)

pie_2022 = alt.Chart(df_2022_stack).mark_arc(innerRadius=50, outerRadius=100).encode(
    theta='sum(Data)',
    color='Regions:N',
    tooltip='Regions'
).transform_filter(
    month_selector_2022
).properties(width=300)

# Create the bar chart for 2021 data
bar_2021 = alt.Chart(df_2021_stack).mark_bar().encode(
        x = alt.X('Month'),
        y = alt.Y('Data'),
        color = 'Regions:N',
).properties(title='2021 US citizens travel to international regions', width=300).add_selection(
    month_selector_2021
)

pie_2021 = alt.Chart(df_2021_stack).mark_arc(innerRadius=50, outerRadius=100).encode(
    theta='sum(Data)',
    color='Regions:N',
    tooltip='Regions'
).transform_filter(
    month_selector_2021
).properties(width=300)

# Combine the charts
combined_charts = ((bar_2022 & pie_2022) | (bar_2021 & pie_2021)).resolve_scale(y='shared')

# Display the combined charts
combined_charts


alt.data_transformers.disable_max_rows()
destination_df = pd.read_csv('air-passengers-carried.csv')
# 使用GeoPandas读取内置的世界地图数据
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# 将地图数据与您的数据合并
merged_data = world.set_index('iso_a3').join(destination_df.set_index('Code')).reset_index()

# 创建选择器
year_selector = alt.selection_single(
    name='Select',
    fields=['Year'],
    init={'Year': 2018},
    bind=alt.binding_range(min=2018, max=2020, step=1)
)

# 创建一个图表，根据所选年份显示地图
choropleth = alt.Chart(merged_data).mark_geoshape().encode(
    alt.Color('Air transport, passengers carried:Q', scale=alt.Scale(scheme='plasma', domain=[1e4, 1e8])),
    tooltip=['Entity:N', 'Air transport, passengers carried:Q']
).transform_filter(
    year_selector
).project('equirectangular').properties(
    title='Air Transport Passengers Carried',
    width=800,
    height=400
).add_selection(
    year_selector
)

# 显示地图
choropleth



st.header('Hotel Booking')

st.header('Destination Capacity')

#%%
df = pd.read_excel('./data/unwto-tourism-industries-data.xlsx', usecols = 'A,B,E:AE')
df_coords = pd.read_csv('./data/GoogleDevCountryGeoCoords.csv')
df.rename(columns={'Basic data and indicators':'Country','Unnamed: 1':'Statistics'}, inplace=True)

alt.data_transformers.disable_max_rows()

#%%
for i in range(0, len(df)-1, 8):
    for j in range(1,8):
        df.loc[i+j,'Country'] = df.loc[i,'Country']

df['Country'] = df['Country'].str.title()
df['Country_key'] = df['Country'].str.lower()
df_coords['Country_key2'] = df_coords['name'].str.lower()

df_merged = df.merge(right = df_coords, how='left', left_on = 'Country_key', right_on = 'Country_key2')
df_merged.tail(20)

#%%
df_merged['Country'] = df_merged['name'] #Change country names to appropriate format
df_merged.drop(columns=['Country_key','Country_key2','country','name'], inplace=True)

df_bed_places_coords = df_merged[df_merged['Statistics'] == 'Number of bed-places'].copy()
df_bed_places = df_merged[df_merged['Statistics'] == 'Number of bed-places'].copy()

df_bed_places.drop(columns=['latitude','longitude'], inplace=True)
df_bed_places.drop(columns='Statistics', inplace=True)
df_bed_places.dropna(inplace=True)
df_bed_places = pd.melt(df_bed_places.loc[:,:], id_vars='Country', var_name='Year',value_name='Number of bed-places')
# df_bed_places['Number of bed-places'] = df_bed_places['Number of bed-places'].replace('..', '0')

df_bed_places_coords = df_merged[df_merged['Statistics'] == 'Number of bed-places']
df_bed_places_coords.drop(columns='Statistics', inplace=True)
df_bed_places_coords = pd.melt(df_bed_places_coords.loc[:,:], id_vars=['Country','latitude','longitude'], var_name='Year',value_name='Number of bed-places')
df_bed_places_coords.dropna(inplace=True)
df_bed_places_coords['dataAvailable'] = (df_bed_places_coords['Number of bed-places'] != '..')

#%%

countries = list(df_bed_places['Country'].unique())

country_checkbox = alt.binding_select(options=countries)
country_selector = alt.selection_single(
    fields=['Country'],
    init = {'Country':countries[1]},
    bind = country_checkbox,
    name='Country'
)

mouseSelection = alt.selection_single(encodings = ['x'], nearest=True, on='mouseover', empty='none')
opacityCondition = alt.condition(mouseSelection, alt.value(1), alt.value(0))

click_selector = alt.selection_multi(fields=['Country'])
# click_selector = alt.selection_interval()

bedPlaceChart = alt.Chart(df_bed_places).mark_line().encode(
    x = alt.X('Year:O'),
    y = alt.Y('Number of bed-places:Q'),
    color = alt.Color('Country:N'),
).transform_filter(
    country_selector | click_selector
).add_selection(
    country_selector,
    click_selector
).properties(
    width=600,
    height=400
)

interactionDots = alt.Chart(df_bed_places).mark_point(size=90).encode(
    x = alt.X('Year:O'),
    y = alt.Y('Number of bed-places:Q'),
    color = alt.Color('Country:N'),
    opacity = opacityCondition
).transform_filter(
    country_selector | click_selector
)

verticalLine = alt.Chart(df_bed_places).mark_rule(size=2, color='black', strokeDash=[15,15]).encode(
    x = alt.X('Year:O'),
    y = alt.Y('Number of bed-places:Q'),
    opacity=opacityCondition
).transform_filter(
    country_selector | click_selector
).add_selection(
    mouseSelection
)

textLabels = interactionDots.mark_text(
    align='left',
    fontSize=14,
    dx = 7, 
).encode(
    alt.Text('Number of bed-places:Q', formatType='number'),
    opacity = opacityCondition
)







countries_url = data.world_110m.url
countries = alt.topo_feature(countries_url, 'countries')

slider = alt.binding_range(min=1995, max=2021, step=1, name='Year: ')
year_selector = alt.selection_single(
    name='year selector',
    fields=['Year'],
    bind=slider,
    init={'Year': 2021}
)



worldMap = alt.Chart(countries).mark_geoshape(
    fill = '#F2F3F4',
    stroke = 'white',
    strokeWidth = 0.5
).properties(
    width = 900,
    height = 500,
).project(
    'naturalEarth1'
)

circles = alt.Chart(df_bed_places_coords).mark_circle(size=100).encode(
    latitude='latitude:Q',
    longitude='longitude:Q',
    tooltip=['Country:N','Year:O','Number of bed-places:Q'],
    color='Number of bed-places:Q',
    opacity=alt.condition(click_selector, alt.value(1), alt.value(0.4)),
    size=alt.condition(click_selector, alt.value(200), alt.value(100))
).transform_filter(
    year_selector
).add_selection(
    click_selector,
    year_selector
)

circlesNoData = alt.Chart(df_bed_places_coords).mark_circle(size=100).encode(
    latitude='latitude:Q',
    longitude='longitude:Q',
    tooltip=['Country:N','Year:O','Number of bed-places:Q'],
    color= alt.value('lightgray'),
    opacity=alt.condition(click_selector, alt.value(1), alt.value(0.4)),
    size=alt.condition(click_selector, alt.value(200), alt.value(150))
).transform_filter(
    year_selector
).transform_filter(
    alt.datum.dataAvailable == False
)

st.altair_chart((worldMap + circles + circlesNoData) & (bedPlaceChart + interactionDots + verticalLine + textLabels), use_container_width=True)
# st.altair_chart((worldMap + circles + circlesNoData) & (bedPlaceChart + interactionDots + verticalLine + textLabels))

# st.a
#%%
st.header('Covid Restrictions')


df = pd.read_csv(r'./data/international-travel-covid.csv')
df["Day"] = pd.to_datetime(df["Day"])
codes = pd.read_csv('./data/all.csv')
df["id"] = 0
df.rename(columns={'international_travel_controls': 'restrictions'}, inplace=True)

# %%
#codes.head()

# %%
for index, row in codes.iterrows():
    df.loc[(df['Code'] == row["alpha-3"]),'id'] = row["country-code"]

# %%
df['restrictions'] = df['restrictions'].replace([0,1,2,3,4], 
                                        ["No measures","Screening","Quarantine from high-risk regions","Ban on high-risk regions","total border closure"])

# %%
#df.head(15)

# %%
#df.dtypes

# %%
df['year'] = df.Day.map(lambda x: x.year)
df['month'] = df.Day.map(lambda x: x.month)
df['day'] = df.Day.map(lambda x: x.day)

# %%
df_first = df[df["day"] == 1]

# %%
#drop anything before 2023
df_first = df_first[(df_first["Day"] < '2023-01-01')]

# %%
#df_first

# %%
alt.data_transformers.disable_max_rows()

source = alt.topo_feature(data.world_110m.url, "countries")

background = alt.Chart(source).mark_geoshape(fill="white")

years=list(df_first['year'].unique())
years.sort()

selectorYear = alt.selection_single(
    name='Y',
    fields=['year'],
    init={"year":years[0]},
    bind=alt.binding_select(options=years, name="Year: ")
)

months=list(df_first['month'].unique())
months.sort()

selectorMonth = alt.selection_single(
    name='Months',
    fields=['month'],
    init={"month":months[0]},
    bind=alt.binding_select(options=months, name="Month: "),
)

highlight = alt.selection_single(fields=['restrictions'], bind='legend')
opacityCondition = alt.condition(highlight, alt.value(1.0), alt.value(0.2))

foreground = alt.Chart(df_first,title="The COVID restrictions in each country on the 1st of the month").mark_geoshape(
        stroke="black", strokeWidth=0.15
    ).encode(
        alt.Color(
            "restrictions:N",
            scale=alt.Scale(domain=["No measures","Screening","Quarantine from high-risk regions","Ban on high-risk regions","total border closure"],
                            range=['#ffffcc','#fbec5d','#ffbf00','#ff4d00','#e62020']),
            legend=alt.Legend(title="", orient="top")
            
        )
        ,tooltip=[alt.Tooltip('Entity:N', title="Country"), alt.Tooltip('restrictions:N', title="Restrictions")],
        opacity=opacityCondition
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(source, key='id',
                             fields=["type", "properties", "geometry"])
    ).project("naturalEarth1").transform_filter(
    selectorYear & selectorMonth
)

foreground = foreground.add_selection(selectorYear, selectorMonth, highlight).properties(width=700, height=400)
foreground

# %%
alt.renderers.set_embed_options(
    padding={"left": 0, "right": 0, "bottom": 0, "top": 0}
)
selectorYear2 = alt.selection_single(
    name='Years',
    fields=['year'],
    init={"year":years[0]},
    bind=alt.binding_radio(options=years,name="Year: ")
    #bind=alt.binding_select(options=years, name="Year")
)
highlight2 = alt.selection_single(fields=['restrictions'], bind='legend')
opacityCondition = alt.condition(highlight, alt.value(1.0), alt.value(0.2))
monthNames = ["","January","February","March","April","May","June","July","August","September","October","November","December"]
facet = alt.concat(*(
 alt.Chart(df_first[df_first["month"] == month], title=monthNames[month]).mark_geoshape(
        stroke="black", strokeWidth=0.15
    ).encode(
        alt.Color(
            "restrictions:N",
            scale=alt.Scale(domain=["No measures","Screening","Quarantine from high-risk regions","Ban on high-risk regions","total border closure"],
                            range=['#ffffcc','#fbec5d','#ffbf00','#ff4d00','#e62020']),
            legend=alt.Legend(title="", orient="top")
        )
        ,tooltip=[alt.Tooltip('Entity:N', title="Country"), alt.Tooltip('restrictions:N', title="Restrictions")],
        opacity=opacityCondition
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(source, key='id',
                             fields=["type", "properties", "geometry"])
    ).project("naturalEarth1").transform_filter(
    selectorYear2
).add_selection(selectorYear2, highlight)
for month in range(1,13)
), columns=3
).properties(background = '#f9f9f9',
                    title = alt.TitleParams(text = 'The COVID restrictions throughout the different months of the year')
                  )
st.altair_chart(facet)