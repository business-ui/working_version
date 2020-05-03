from flask import Flask, render_template, url_for, request, redirect
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Response
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
matplotlib.use('Agg')

import io
import numpy as np
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
# above will create the engine, below will only create a dataframe once
# df = pd.read_sql("SELECT * FROM covid_data",app.config['SQLALCHEMY_DATABASE_URI'], parse_dates=['Date'])

# @app.route('/aggs.png')
# def aggs_plot():

#     conn = engine.connect()
#     df = pd.read_sql("SELECT * FROM covid_data",con=conn)
#     totals = df.groupby("Date").sum().reset_index(drop=True)
#     totals.index = totals.index + 1
#     for col in totals:
#         totals[col+'_pct_ch'] = totals[col].pct_change()
#         totals[col+'_ch'] = totals[col].diff()
#     totals['Fatality Rate'] = totals['Deaths'] / totals['Confirmed']

#     fig,ax = plt.subplots(figsize=(10,8))

#     ax.plot(totals.index,totals[['Confirmed','Deaths','Recovered','Active']])
#     for y in [1,3,5,7,30]:
#         ax.plot(np.arange(1,ax.get_xlim()[1]),
#                 [2**(x * (1/y)) for x in np.arange(1,ax.get_xlim()[1])],
#                 linestyle=':',
#                 c="gray")

#     ax.set_ylim([1,totals['Confirmed'].max().max()**1.1])

#     # ax.set_xlim([0,ax.get_xlim()[1]])
#     ax.set_yscale("log")
#     ax.annotate("doubles\nevery day",(16,10**5.5))
#     ax.annotate("doubles\nevery 3 days",(48,10**5.5))
#     ax.annotate("doubles\nevery 5 days",(57,10**3.5))
#     ax.annotate("doubles\nevery 7 days",(57,10**2.5))
#     ax.annotate("doubles\nevery 30 days",(57,10**0.75))
#     ax.set_ylabel("Cases")
#     ax.set_xlabel("Days")
#     ax.legend(labels=totals.columns[0:4],loc="lower right")
#     ax.set_yticklabels(["0","1","10","100","1 thousand","10 thousand","100 thousand","1 million","10 million","100 million","1 billion"])
#     ax.set_title("COVID-19 by Day")
    
    
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     conn.close()
#     return Response(output.getvalue(), mimetype='image/png')

# @app.route('/pct_change.png')
# def pct_change_plot():
    
#     conn = engine.connect()
#     df = pd.read_sql("SELECT * FROM covid_data",con=conn)
#     totals = df.groupby("Date").sum().reset_index(drop=True)
#     totals.index = totals.index + 1
#     for col in totals:
#         totals[col+'_pct_ch'] = totals[col].pct_change()
#         totals[col+'_ch'] = totals[col].diff()
#     totals['Fatality Rate'] = totals['Deaths'] / totals['Confirmed']
    
#     fig,ax = plt.subplots(figsize=(10,8))
#     ax.plot(totals.index[1:],totals[['Confirmed_pct_ch','Active_pct_ch','Recovered_pct_ch','Deaths_pct_ch']].iloc[1:])
#     ax.set_title("Percentage Change by Day")
#     ax.set_ylabel("Percent")
#     ax.set_xlabel("Days")
#     ax.set_yticklabels(["{:.2f}%".format(x*100) for x in ax.get_yticks()])
#     ax.legend(totals[['Confirmed_pct_ch','Active_pct_ch','Recovered_pct_ch','Deaths_pct_ch']].columns)

#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     conn.close()
#     return Response(output.getvalue(), mimetype='image/png')

# @app.route('/confirmed.png')
# def country_aggs_plot():
    
#     conn = engine.connect()
#     df = pd.read_sql("SELECT * FROM covid_data",con=conn)
#     confirmed_df = df.groupby(["Country_Region","Date"])['Confirmed'].sum().unstack().sort_values(df.Date.max(), ascending = False)
#     confirmed_df = confirmed_df.nlargest(10,df.Date.max()).replace(0,np.NaN)

#     fig,ax = plt.subplots(figsize=(10,8))

#     for x in range(len(confirmed_df)):
#         country_df = confirmed_df.iloc[x,:-1].dropna().reset_index(drop=True)
#         country_df.index = country_df.index + 1
#         country_df.plot(ax=ax)
#     for y in [1,3,5,7,30]:
#         ax.plot(np.arange(1,ax.get_xlim()[1]),
#                 [2**(x * (1/y)) for x in np.arange(1,ax.get_xlim()[1])],
#                 linestyle=':',
#                 c="gray")
#     ax.set_yscale("log")
#     ax.set_ylim([1,df['Confirmed'].max()*1.1])

#     ax.annotate("doubles\nevery day",(9,10**5.5))
#     ax.annotate("doubles\nevery 3 days",(44,10**5.5))
#     ax.annotate("doubles\nevery 5 days",(58.5,10**3.5))
#     ax.annotate("doubles\nevery 7 days",(58.5,10**2.5))
#     ax.annotate("doubles\nevery 30 days",(57,10**0.73))
#     ax.set_ylabel("Confirmed Cases")
#     ax.set_xlabel("Days")
#     ax.set_yticklabels(["0","1","10","100","1 thousand","10 thousand","100 thousand","1 million","10 million","100 million","1 billion"])
#     ax.set_title("Growth of Cases by Country by Day")
#     ax.legend(loc="lower right")
    

#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     conn.close()
#     return Response(output.getvalue(), mimetype='image/png')

# @app.route('/dead.png')
# def dead_plot():

#     conn = engine.connect()
#     df = pd.read_sql("SELECT * FROM covid_data",con=conn)
#     confirmed_df = df.groupby(["Country_Region","Date"])['Confirmed'].sum().unstack().sort_values(df.Date.max(), ascending = False)
#     death_df = df.groupby(["Country_Region","Date"])['Deaths'].sum().unstack().sort_values(df.Date.max(), ascending = False).loc[[x for x in confirmed_df.nlargest(10,df.Date.max()).replace(0,np.NaN).index]]

#     fig,ax = plt.subplots(figsize=(10,8))

#     for x in range(len(death_df)):
#         country_df = death_df.iloc[x,:-1].dropna().reset_index(drop=True)
#         country_df.index = country_df.index + 1
#         country_df.plot(ax=ax)
#     for y in [1,3,5,7,30]:
#         ax.plot(np.arange(1,ax.get_xlim()[1]),
#                 [2**(x * (1/y)) for x in np.arange(1,ax.get_xlim()[1])],
#                 linestyle=':',
#                 c="gray")
#     ax.set_yscale("log")
#     ax.set_ylim([1,df['Deaths'].max()*1.01])# print(plt.gca())
#     ax.annotate("doubles\nevery day",(16,ax.get_ylim()[1]*.1))
#     ax.annotate("doubles\nevery 3 days",(34,10**4.5))
#     ax.annotate("doubles\nevery 5 days",(58.5,10**4.15))
#     ax.annotate("doubles\nevery 7 days",(60,10**2.3))
#     ax.annotate("doubles\nevery 30 days",(57,10**0.73))
#     ax.set_ylabel("Fatalities")
#     ax.set_xlabel("Days")
#     ax.set_yticklabels(["0","1","10","100","1 thousand","10 thousand","100 thousand","1 million","10 million","100 million","1 billion"])
#     ax.set_title("Deaths by Country by Day")
#     ax.legend(loc="lower right")
    

#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     conn.close()
#     return Response(output.getvalue(), mimetype='image/png')

# @app.route('/fatality_rate.png')
# def fatality_plot():
#     conn = engine.connect()
#     df = pd.read_sql("SELECT * FROM covid_data",con=conn)
#     totals = df.groupby("Date").sum().reset_index(drop=True)
#     totals.index = totals.index + 1
#     for col in totals:
#         totals[col+'_pct_ch'] = totals[col].pct_change()
#         totals[col+'_ch'] = totals[col].diff()
#     totals['Fatality Rate'] = totals['Deaths'] / totals['Confirmed']

#     fig,ax = plt.subplots(figsize=(8,8))
#     ax.plot(totals['Fatality Rate'],c="red")

#     ax.scatter(marker='o',c='black',x = totals['Fatality Rate'].iloc[::10].index, y = totals['Fatality Rate'].iloc[::10])
#         # ax.plot(x,y,marker="o",c="black")
#     for index, val in zip(totals['Fatality Rate'].iloc[::10].index,totals['Fatality Rate'].iloc[::10]):
#         ax.annotate("{:.1f}%".format(val*100),(index-2,val+0.001))
    
#     ax.set_yticks(np.arange(0,totals['Fatality Rate'].max()+0.01,0.005))
#     ax.set_yticklabels(list(map('{:.1f}%'.format,np.arange(0,totals['Fatality Rate'].max()+0.01,0.005)*100)))
#     # plt.legend([""],bbox_to_anchor=(1.04,0.5), loc="center left")
#     ax.set_title("Fatality Rate by Day")
#     ax.set_ylabel("Fatality Rate")
#     ax.set_xlabel("Days")
#     ax.annotate("Current Rate {:.2f}%".format(totals['Fatality Rate'].iloc[-1]*100),
#                 (totals.index.max()/2.75,totals['Fatality Rate'][round(np.median(totals.index))]*1.75))
    

#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     conn.close()
#     return Response(output.getvalue(), mimetype='image/png')

@app.route('/')
def index():
    conn = engine.connect()
    df = pd.read_sql("SELECT * FROM covid_data",con=conn)
    totals = df.groupby("Date").sum().reset_index(drop=True)
    totals.index = totals.index + 1
    for col in totals:
        totals[col+'_pct_ch'] = totals[col].pct_change()
        totals[col+'_ch'] = totals[col].diff()
    totals['Fatality Rate'] = totals['Deaths'] / totals['Confirmed']
    confirmed_df = df.groupby(["Country_Region","Date"])['Confirmed'].sum().unstack().sort_values(df.Date.max(), ascending = False)
    confirmed_df = confirmed_df.nlargest(10,df.Date.max()).replace(0,np.NaN)
    death_df = df.groupby(["Country_Region","Date"])['Deaths'].sum().unstack().sort_values(df.Date.max(), ascending = False).loc[[x for x in confirmed_df.index]]
    rates_df = df.groupby("Country_Region").sum()
    aggs = pd.DataFrame(totals[['Confirmed','Deaths','Recovered','Active']].iloc[-1]).T
    aggs['Fatality Rate'] = aggs['Deaths'] / aggs['Confirmed'] *100
    rates_df['Fatality Rate'] = rates_df['Deaths']/rates_df['Confirmed'] *100
    top_ten_df = rates_df.loc[rates_df['Confirmed']>1000].nlargest(10,"Fatality Rate")
    yesterdays_numbers = pd.DataFrame(totals[['Confirmed_ch','Deaths_ch','Recovered_ch','Active_ch']].iloc[-1]).T
    yesterdays_numbers.columns = yesterdays_numbers.columns.str[:-3]
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
                                        ("margin-right","auto"),
                                        ("background-color","white")])
        ]
    aggs_html = "<h2 align='center'>Start Date: "+df.Date.iloc[0][:10]+"</h2>"+\
                                                    "<h2 align='center'>End Date: "+df.Date.iloc[-1][:10]+"</h2>"+\
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
                                                    .render()

    top_ten_df = "<h1 align='center'>Highest Fatality Rates for Countries with over 1,000 Cases</h1>" + \
                top_ten_df.style.set_table_styles(styles)\
                    .set_caption("Hover to highlight.")\
                    .format({"Confirmed":"{:,.0f}",
                                "Deaths":"{:,.0f}",
                                "Recovered":"{:,.0f}",
                                "Active":"{:,.0f}",
                                "Fatality Rate":"{:.2f}%"})\
                    .set_table_attributes('border="1" align="center" class="dataframe table table-hover table-bordered"')\
                    .render()

    yesterdays_numbers = "<h1 align='center'>Yesterday's Numbers</h1>"+yesterdays_numbers.style.set_table_styles(styles)\
                        .set_caption("Hover to highlight.")\
                        .format({"Confirmed":"{:,.0f}",
                            "Deaths":"{:,.0f}",
                            "Recovered":"{:,.0f}",
                            "Active":"{:,.0f}"})\
                        .set_table_attributes('border="1" align="center" class="dataframe table table-hover table-bordered"')\
                        .hide_index()\
                        .render()
    conn.close()
    return render_template('index.html' , tables=[aggs_html,top_ten_df,yesterdays_numbers])


if __name__ == '__main__':
    app.run()
