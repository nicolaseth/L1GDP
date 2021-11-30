import requests
import re
import plotly.express as px
import pandas as pd
from pandas_datareader import wb
import datetime

BILLION = 1000000000
MILLION = 1000000
formatted_date = datetime.date.strftime(datetime.date.today(), "%m/%d/%Y")

url = "https://defillama.com/chains"

response = requests.get(url).text

l1_list = []
tvl_list = []
mkvl_list = []

l1s = re.findall("href=[\"\'](.*?)[\"\']", response)
for p in l1s:#getting L1s from the link and appending them to a the l1_list
    if '/chain/' in p:

        split = p.split("/chain/")

        l1_list.append(split[1])

#-getting only the top 5 L1s --#
l1_list = l1_list[:5]

#-- getting the TVL- #

tvls = re.findall("[$][0-9.bm]*", response)
for tvl in tvls:
    tvl = tvl.split("$")

    if re.search('b', tvl[1]):
        tvl[1] = float(tvl[1].replace('b', ''))
        tvl[1] = tvl[1]*BILLION
    else:
        tvl[1] = float(tvl[1].replace('m', ''))
        tvl[1] = tvl[1] * MILLION

    tvl_list.append(round(tvl[1]))

#-getting only the top 5 L1s --#
tvl_list = tvl_list[:5]

#--Now getting the Market cap -#
string_mc = 'css-1n3zwju">*[0-9.][^><]*<'
mk_cap = re.findall(string_mc, response)

for mk in mk_cap:
    mk = mk.split(">")
    mk = mk[1].split("<")
    mkvl_list.append(round(float(mk[0]), 2))


#-getting only the top 5 L1s --#
mkvl_list = mkvl_list[:5]

# now putting together this info in a dataframe
d = {"L1": l1_list, "TVL": tvl_list, "mkt_cap/TVL": mkvl_list}

df_L1s = pd.DataFrame(d)

df_L1s["MktCap"] = round(df_L1s["mkt_cap/TVL"] * df_L1s["TVL"])
df_L1s["GDP (in Billions)"] = round(df_L1s["TVL"] / 3 / BILLION)
df_L1s["TVL (in Billions)"] = round(df_L1s["TVL"] / BILLION)

l1_gpd = df_L1s[['L1', 'GDP (in Billions)']]
l1_gpd.columns = l1_gpd.columns.str.replace('L1', 'L1/Country')

# # -- OK - Let's graph this thing as a scatter plot#

fig = px.scatter(df_L1s, x="MktCap", y="GDP (in Billions)", size="TVL (in Billions)",
                 text="L1", log_x=True, log_y=True, size_max=100, template="plotly_dark")

fig.update_xaxes(title_text="Market Cap")

fig.update_yaxes(title_text="GDP in USD (Billions)")


fig.update_layout(title_text=f"Layer 1 GDP Calculation based on TVL as of {formatted_date}",
                  title_font_size=30,
                  title_yanchor="top",
                  title_pad_t=35)

fig.write_html("L1GDP.html")
fig.show()

#----Getting the data from the world bank -- ##
#--- Start GDP Countries -- #
gdp_current_usd = "NY.GDP.MKTP.CD"

countries = ["UY", "SI", "SL", "GY", "LT", "HR"]

gdp_df = wb.download(indicator=gdp_current_usd, country=countries, start=2020,end=2020)

gdp_df['GDP (in Billions)'] = gdp_df['NY.GDP.MKTP.CD']/BILLION

gdp_df = gdp_df.reset_index()
gdp_df = gdp_df[['country', 'GDP (in Billions)']]
gdp_df.columns = gdp_df.columns.str.replace('country', 'L1/Country')

agg_df = l1_gpd.append(gdp_df, ignore_index=True)
agg_df = agg_df.sort_values(by='GDP (in Billions)')



#--- Graphing L1s and countries ----#
fig_gdp = px.bar(agg_df, x="L1/Country", y="GDP (in Billions)", template="plotly_dark")

fig_gdp.update_xaxes(title_text="L1/Countrry",
                # showgrid=False,
               #  title_font={"size:30"}
                   )

fig_gdp.update_yaxes(title_text="GDP in USD (Billions)")
#                  showgrid=False,
#                  title_font={"size:30"}


fig_gdp.update_layout(title_text=f"Layer 1 GDP and Country GPD (World Bank: 2020) as of  {formatted_date}",
                  title_font_size=30,
                  title_yanchor="top",
                  title_pad_t=35)




fig_gdp.write_html("L1CountriesGDP.html")
fig_gdp.show()