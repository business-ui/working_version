from flask import Flask, render_template, url_for, request, redirect
from flask_apscheduler import APScheduler
from flask import Response
from flask_sqlalchemy import SQLAlchemy

import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
matplotlib.use('Agg')

import io
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
from collections import Counter
import datetime as dt

app = Flask(__name__)
scheduler = APScheduler()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

country_counts = Counter()
url = "https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/"
soup = BeautifulSoup(requests.get(url).text)
timeline_csvs = soup.select("a[href$='.csv']")
last_date = dt.datetime.strptime(timeline_csvs[-1]['href'].split("/")[-1][:-4],"%m-%d-%Y")

def scheduledTask():
    
    def update_countries(df):
        misspelled_countries = ["Taiwan","China","Russia","Bahamas","Gambia","Hong Kong","Iran","Moldova","Ireland","Taipei"]
        
        df.loc[(df['Country_Region']=="Macao SAR") | (df['Country_Region']=="Macau"),"Country_Region"] = "Macao"
        df.loc[(df['Country_Region']=="Republic of Korea") | (df['Country_Region']=="Korea, South"),"Country_Region"] = "South Korea"
        df.loc[(df['Country_Region']=="West Bank and Gaza") | (df['Country_Region'].str.contains("Palestin")),"Country_Region"] = "Palestinian Territory"
        df.loc[df['Country_Region']=="UK","Country_Region"] = "United Kingdom"
        df.loc[df['Country_Region']=="US","Country_Region"] = "United States"
        df.loc[df['Country_Region']=="Viet Nam","Country_Region"] = "Vietnam"
        df.loc[df['Country_Region']=="Burma","Country_Region"] = "Myanmar"
        df.loc[df['Country_Region']=="Cape Verde","Country_Region"] = "Cabo Verde"
        df.loc[df['Country_Region'].str.contains("Czech"),"Country_Region"] = "Czechia"
        df.loc[df['Country_Region'].str.startswith("Congo"),"Country_Region"] = "Congo"
        
        for country in range(len(misspelled_countries)):
            df.loc[df['Country_Region'].str.contains(misspelled_countries[country]),"Country_Region"] = misspelled_countries[country]
        
        return df

    df = pd.DataFrame()
    country_counts = Counter()
    for each in range(len(timeline_csvs)):
        csv_date = timeline_csvs[each]['href'].split("/")[-1][:-4]
        time_slice = pd.read_html(url + csv_date + ".csv")[0]
        time_slice.columns = time_slice.columns.str.replace("/","_")
        time_slice = update_countries(time_slice)
        for country in time_slice['Country_Region'].unique():
            country_counts[country] += 1
        if len(time_slice.columns) != 13:
            if len(time_slice.columns) == 9:
                del time_slice['Latitude']
                del time_slice['Longitude']
            del time_slice['Unnamed: 0']
            del time_slice['Last Update']
            time_slice['Active'] = time_slice['Confirmed'] - time_slice['Deaths'] - time_slice['Recovered']
            time_slice['Date'] = dt.datetime.strptime(csv_date,"%m-%d-%Y")
        else:
            del time_slice['Unnamed: 0']
            del time_slice['Lat']
            del time_slice['Long_']
            del time_slice['Last_Update']
            del time_slice['Combined_Key']
            del time_slice['FIPS']
            del time_slice['Admin2']
            time_slice['Date'] = dt.datetime.strptime(csv_date,"%m-%d-%Y")
        df = df.append(time_slice)
    
    df.to_sql("covid_data", db, if_exists='replace', index=False)
    # return render_template('index.html')

@app.route('/aggs.png')
def aggs_plot():
    fig,ax = plt.subplots(figsize=(8,8))

    totals.index = totals.index + 1
    ax.plot(totals.index,totals.drop('Fatality Rate',axis=1))
    for y in [1,3,5,7,30]:
        ax.plot(np.arange(1,ax.get_xlim()[1]),
                [2**(x * (1/y)) for x in np.arange(1,ax.get_xlim()[1])],
                linestyle=':',
                c="gray")

    ax.set_ylim([1,totals.max().max()**1.1])

    # ax.set_xlim([0,ax.get_xlim()[1]])
    ax.set_yscale("log")
    ax.annotate("doubles\nevery day",(16,10**5.5))
    ax.annotate("doubles\nevery 3 days",(48,10**5.5))
    ax.annotate("doubles\nevery 5 days",(57,10**3.5))
    ax.annotate("doubles\nevery 7 days",(57,10**2.5))
    ax.annotate("doubles\nevery 30 days",(57,10**0.75))
    ax.set_ylabel("Cases")
    ax.set_xlabel("Days")
    ax.legend(labels=totals.columns[0:-1],loc="lower right")
    ax.set_yticklabels(["0","1","10","100","1 thousand","10 thousand","100 thousand","1 million","10 million","100 million","1 billion"])
    ax.set_title("COVID-19 by Day")
    fig.tight_layout()
    
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/confirmed.png')
def country_aggs_plot():
    fig,ax = plt.subplots(figsize=(8,8))

    for x in range(len(confirmed_df)):
        country_df = confirmed_df.iloc[x,:-1].dropna().reset_index(drop=True)
        country_df.index = country_df.index + 1
        country_df.plot(ax=ax)
    for y in [1,3,5,7,30]:
        ax.plot(np.arange(1,ax.get_xlim()[1]),
                [2**(x * (1/y)) for x in np.arange(1,ax.get_xlim()[1])],
                linestyle=':',
                c="gray")
    ax.set_yscale("log")
    ax.set_ylim([1,totals.max().max()**1.1])

    ax.annotate("doubles\nevery day",(9,10**5.5))
    ax.annotate("doubles\nevery 3 days",(44,10**5.5))
    ax.annotate("doubles\nevery 5 days",(58.5,10**3.5))
    ax.annotate("doubles\nevery 7 days",(58.5,10**2.5))
    ax.annotate("doubles\nevery 30 days",(57,10**0.73))
    ax.set_ylabel("Confirmed Cases")
    ax.set_xlabel("Days")
    ax.set_yticklabels(["0","1","10","100","1 thousand","10 thousand","100 thousand","1 million","10 million","100 million","1 billion"])
    ax.set_title("Growth of Cases by Country by Day")
    ax.legend(loc="lower right")
    fig.tight_layout()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/dead.png')
def dead_plot():
    fig,ax = plt.subplots(figsize=(8,8))

    for x in range(len(death_df)):
        country_df = death_df.iloc[x,:-1].dropna().reset_index(drop=True)
        country_df.index = country_df.index + 1
        country_df.plot(ax=ax)
    for y in [1,3,5,7,30]:
        ax.plot(np.arange(1,ax.get_xlim()[1]),
                [2**(x * (1/y)) for x in np.arange(1,ax.get_xlim()[1])],
                linestyle=':',
                c="gray")
    ax.set_yscale("log")
    ax.set_ylim([1,totals.max().max()**1.01])# print(plt.gca())
    ax.annotate("doubles\nevery day",(16,ax.get_ylim()[1]*.1))
    ax.annotate("doubles\nevery 3 days",(34,10**4.5))
    ax.annotate("doubles\nevery 5 days",(58.5,10**4.15))
    ax.annotate("doubles\nevery 7 days",(60,10**2.3))
    ax.annotate("doubles\nevery 30 days",(57,10**0.73))
    ax.set_ylabel("Fatalities")
    ax.set_xlabel("Days")
    ax.set_yticklabels(["0","1","10","100","1 thousand","10 thousand","100 thousand","1 million","10 million","100 million","1 billion"])
    ax.set_title("Deaths by Country by Day")
    ax.legend(loc="lower right")
    fig.tight_layout()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/fatality_rate.png')
def fatality_plot():
    fig,ax = plt.subplots(figsize=(8,8))
    ax.plot(totals['Fatality Rate'],c="red")

    ax.scatter(marker='o',c='black',x = totals['Fatality Rate'].iloc[::10].index, y = totals['Fatality Rate'].iloc[::10])
        # ax.plot(x,y,marker="o",c="black")
    for index, val in zip(totals['Fatality Rate'].iloc[::10].index,totals['Fatality Rate'].iloc[::10]):
        ax.annotate("{:.1f}%".format(val*100),(index-2,val+0.001))
    
    ax.set_yticks(np.arange(0,totals['Fatality Rate'].max()+0.01,0.005))
    ax.set_yticklabels(list(map('{:.1f}%'.format,np.arange(0,totals['Fatality Rate'].max()+0.01,0.005)*100)))
    # plt.legend([""],bbox_to_anchor=(1.04,0.5), loc="center left")
    ax.set_title("Fatality Rate by Day")
    ax.set_ylabel("Fatality Rate")
    ax.set_xlabel("Days")
    ax.annotate("Current Rate {:.2f}%".format(totals['Fatality Rate'].iloc[-1]*100),
                (totals.index.max()/2.75,totals['Fatality Rate'][round(np.median(totals.index))]*1.75))
    

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/')
def index():
    def hover(hover_color="#ffff99"):
        return dict(selector="tr:hover",
            props=[("background-color", "%s" % hover_color)])
    styles = [
        hover(),
        dict(selector="th", props=[("font-size", "150%"),
                                ("text-align", "center")]),
        dict(selector="td", props=[("text-align", "center")]),
        dict(selector="caption", props=[("caption-side", "bottom")]),
        dict(selector="table",props=[("margin-left","auto"),
                                    ("margin-right","auto")])
    ]
    return render_template('index.html' , tables=["<h2 align='center'>Start Date: "+timeline_csvs[0]['href'].split("/")[-1][:-4]+"</h2>"+\
                                                 "<h2 align='center'>End Date: "+timeline_csvs[-1]['href'].split("/")[-1][:-4]+"</h2>"+\
                                                 "<h1 align='center'>World Totals</h1>"+\
                                                aggs.style.set_table_styles(styles)\
                                                    .set_caption("Hover to highlight.")\
                                                    .format({"Confirmed":"{:,.0f}",
                                                        "Deaths":"{:,.0f}",
                                                        "Recovered":"{:,.0f}",
                                                        "Active":"{:,.0f}",
                                                        "Fatality Rate":"{:.2f}%"})\
                                                    .set_table_attributes('border="1" align="center" class="dataframe table table-hover table-bordered"')\
                                                    .hide_index()\
                                                    .render(),
                                                "<h1 align='center'>Highest Fatality Rates for Countries with over 1,000 Cases</h1>" + \
                                                top_ten_df.style.set_table_styles(styles)\
                                                    .set_caption("Hover to highlight.")\
                                                    .format({"Confirmed":"{:,.0f}",
                                                                "Deaths":"{:,.0f}",
                                                                "Recovered":"{:,.0f}",
                                                                "Active":"{:,.0f}",
                                                                "Fatality Rate":"{:.2f}%"})\
                                                    .set_table_attributes('border="1" align="center" class="dataframe table table-hover table-bordered"')\
                                                    .render(),])

if __name__ == '__main__':
    
    df = pd.read_sql("SELECT * FROM covid_data",app.config['SQLALCHEMY_DATABASE_URI'], parse_dates=['Date'])

    confirmed_df = df.groupby(["Country_Region","Date"])['Confirmed'].sum().unstack().sort_values(df.Date.max(), ascending = False)
    death_df = df.groupby(["Country_Region","Date"])['Deaths'].sum().unstack().sort_values(df.Date.max(), ascending = False).loc[[x for x in confirmed_df.nlargest(10,df.Date.max()).replace(0,np.NaN).index]]#.nlargest(10,df.Date.max())
    totals = df.groupby("Date").sum().reset_index(drop=True)
    rates_df = df.groupby("Country_Region").sum()

    confirmed_df = confirmed_df.nlargest(10,df.Date.max()).replace(0,np.NaN)

    totals['Fatality Rate'] = totals['Deaths'] / totals['Confirmed']

    aggs = pd.DataFrame(totals.iloc[-1,:-1]).T
    aggs['Fatality Rate'] = aggs['Deaths'] / aggs['Confirmed'] * 100
    aggs['Active'] = aggs['Confirmed'] - aggs['Deaths'] - aggs['Recovered']

    rates_df['Fatality Rate'] = rates_df['Deaths']/rates_df['Confirmed']*100

    top_ten_df = rates_df.loc[rates_df['Confirmed']>1000].nlargest(10,"Fatality Rate")
    
    scheduler.add_job(id='Scheduled task',func = scheduledTask, trigger = 'interval', hours=24)
    scheduler.start()
    app.run()