# %%
import pandas as pd
import altair as alt
from vega_datasets import data
df = pd.read_csv(r'C:\Users\raoma\Documents\michigan\info_vis\group\649_COVID_travel\data\international-travel-covid.csv')
df["Day"] = pd.to_datetime(df["Day"])
codes = pd.read_csv(r'C:\Users\raoma\Documents\michigan\info_vis\group\649_COVID_travel\data\all.csv')
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
facet

# %%
#TODO
#make into streamlit



