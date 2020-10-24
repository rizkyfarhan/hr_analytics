from flask import Flask, render_template, request, send_from_directory
import numpy as np
import pandas as pd
import seaborn as sb
import plotly
import plotly.graph_objs as go

import json
import joblib

app = Flask(__name__)

HRDATA = pd.read_csv('dashboard_data.csv')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/static/<path:x>')
def gal(x):
    return send_from_directory("static",x)

# # # # # # # # # #
# HISTOGRAM & BOX #
# # # # # # # # # #
   
def category_plot(cat_plot = 'histoplot', cat_x = 'MonthlyIncome', cat_y = 'JobSatisfaction', estimator ='count', hue='MaritalStatus'):
    
    if cat_plot == 'histoplot':
        data = []

        for val in HRDATA[hue].unique(): # [No, Yes]
            hist = go.Histogram(
                        x = HRDATA[HRDATA[hue] == val ][cat_x],
                        y = HRDATA[HRDATA[hue] == val ][cat_y],
                        histfunc=estimator,
                        name= val
                    )
            
            data.append(hist)

        title = 'Histogram'
    else :
        data = []

        for val in HRDATA[hue].unique(): # [No, Yes]
            hist = go.Box(
                        x = HRDATA[HRDATA[hue] == val ][cat_x],
                        y = HRDATA[HRDATA[hue] == val ][cat_y],
                        name= val
                    )
            
            data.append(hist)

        title = 'Box'

    layout = go.Layout(
        title=title,
        title_x=0.5,
        xaxis={"title" : cat_x},
        yaxis=dict(title=cat_y),
        boxmode='group'
    )

    final = {"data" : data, "layout" : layout}

    graphJSON = json.dumps(final, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/index')
def index():
    plot = category_plot()

    # list dropdown
    list_plot = [('histoplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('JobSatisfaction', 'JobSatisfaction'), ('MaritalStatus', 'MaritalStatus'), ('Attrition', 'Attrition')]
    list_y = [('MonthlyIncome', 'MonthlyIncome'), ('DistanceFromHome', 'DistanceFromHome'), ('NumCompaniesWorked', 'NumCompaniesWorked')]
    list_estimator = [('count', 'Count'), ('sum', 'Sum'),('avg','Average'), ('min', 'Minimum'), ('max', 'Maximum')]

    return render_template(
        'category.html', 
        plot=plot, 
        focus_plot='histoplot', 
        focus_x='JobSatisfaction', 
        focus_y='MonthlyIncome', 
        focus_estimator='count',
        drop_plot = list_plot,
        drop_x = list_x,
        drop_y = list_y,
        drop_estimator = list_estimator,
        drop_hue = list_x
    )

@app.route('/cat_fn')
def cat_fn():
    cat_plot = request.args.get('cat_plot') # histoplot
    cat_x = request.args.get('cat_x') # NewExist
    cat_y = request.args.get('cat_y') # Term
    estimator = request.args.get('estimator') # avg
    hue = request.args.get('hue') # MIS_Status

    # Ketika kita klik menu 'Histogram & Box' di Navigasi
    if cat_plot == None and cat_x == None and cat_y == None and estimator == None and hue == None:
        cat_plot = 'histoplot'
        cat_x = 'JobSatisfaction'
        cat_y = 'MonthlyIncome'
        estimator = 'count'
        hue = 'MaritalStatus'

    # Ketika kita pindah dari boxplot (disabled) ke histogram
    if estimator == None:
        estimator = 'count'

    plot = category_plot(cat_plot, cat_x, cat_y, estimator, hue)

    # list dropdown
    list_plot = [('histoplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('JobSatisfaction', 'JobSatisfaction'), ('MaritalStatus', 'MaritalStatus'), ('Attrition', 'Attrition')]
    list_y = [('MonthlyIncome', 'MonthlyIncome'), ('DistanceFromHome', 'DistanceFromHome'), ('NumCompaniesWorked', 'NumCompaniesWorked')]
    list_estimator = [('count', 'Count'), ('sum', 'Sum'),('avg','Average'), ('min', 'Minimum'), ('max', 'Maximum')]
                                                                                            
    return render_template(
        'category.html', 
        plot=plot, 
        focus_plot=cat_plot, 
        focus_x=cat_x, 
        focus_y=cat_y, 
        focus_estimator=estimator,
        focus_hue = hue,
        drop_plot = list_plot,
        drop_x = list_x,
        drop_y = list_y,
        drop_estimator = list_estimator,
        drop_hue = list_x
    )


# # # # # #
# SCATTER # 
# # # # # #

def scatter_plot(cat_x, cat_y , hue):

    data = []

    for val in HRDATA[hue].unique():
        scatt = go.Scatter(
            x = HRDATA[HRDATA[hue] == val][cat_x],
            y = HRDATA[HRDATA[hue] == val][cat_y],
            mode = 'markers',
            name = val
        )
    
        data.append(scatt)

    layout = go.Layout(
        title='Scatter',
        title_x=0.5,
        xaxis=dict(title=cat_x),
        yaxis=dict(title=cat_y)
    )

    res = {"data" : data, "layout" : layout}

    graphJSON = json.dumps(res,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/scatt_fn')
def scatt_fn():
    cat_x = request.args.get('cat_x')
    cat_y = request.args.get('cat_y')
    hue = request.args.get('hue')

    if cat_x == None and cat_y == None and hue == None:
        cat_x = 'JobSatisfaction'
        cat_y = 'MonthlyIncome'
        hue = 'MaritalStatus'

    # Dropdown Menu
    list_x = [('JobSatisfaction', 'JobSatisfaction'), ('MaritalStatus', 'MaritalStatus'), ('Attrition', 'Attrition'), ('MonthlyIncome', 'MonthlyIncome'), ('DistanceFromHome', 'DistanceFromHome'), ('NumCompaniesWorked', 'NumCompaniesWorked')]
    list_y = [('JobSatisfaction', 'JobSatisfaction'), ('MaritalStatus', 'MaritalStatus'), ('Attrition', 'Attrition'), ('MonthlyIncome', 'MonthlyIncome'), ('DistanceFromHome', 'DistanceFromHome'), ('NumCompaniesWorked', 'NumCompaniesWorked')]
    list_hue = [('JobSatisfaction', 'JobSatisfaction'), ('MaritalStatus', 'MaritalStatus'), ('Attrition', 'Attrition')]

    plot = scatter_plot(cat_x, cat_y, hue)   

    return render_template(
        'scatter.html', 
        plot=plot, 
        focus_x=cat_x, 
        focus_y=cat_y,
        focus_hue = hue,
        drop_x = list_x,
        drop_y = list_y,
        drop_hue = list_hue
    )


# # # #
# PIE #
# # # #

def pie_plot(hue):

    # result : list of tupple dari penghitungan banyak data secara unique 
    result = HRDATA[hue].value_counts()

    labels_source = []
    values_source = []

    for item in result.iteritems():
        labels_source.append(item[0])
        values_source.append(item[1])

    data_source = [
        go.Pie(
            labels=labels_source,
            values=values_source
        )
    ]

    layout_source = go.Layout(
        title='Pie',
        title_x=0.5
    )

    final = {"data" : data_source, "layout" : layout_source}

    # hasil json yang akan dikirim tidak harus menggunakan 'graphJSON'
    graphJSON = json.dumps(final, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/pie_fn')
def pie_fn():
    hue_source = request.args.get('hue')

    # Saat diakses melalui link, hue_sorce akan bernilai None
    if hue_source == None:
        hue_source = 'JobSatisfaction'

    plot_source = pie_plot(hue_source)

    return render_template('pie.html', plot=plot_source, focus_hue=hue_source)

# Prediction Page
@app.route('/predict')
def predict():
    return render_template('predict.html')

# Result Page
@app.route('/Attrition_Predict_Result', methods=["POST", "GET"])
def Attrition_Predict():
    if request.method == "POST":
        input = request.form
        # NUMERICAL FEATURES
        MonthlyIncome = float(input['MonthlyIncome'])
        DistanceFromHome = float(input['DistanceFromHome'])
        NumCompaniesWorked = float(input['NumCompaniesWorked'])
        # CATEGORICAL FEATURES
        MaritalStatus = float(input['MaritalStatus'])
        JobSatisfaction = float(input['JobSatisfaction'])

# Predict with Model
        pred = svc.predict([[MonthlyIncome, MaritalStatus, NumCompaniesWorked, DistanceFromHome, JobSatisfaction]])
        
        pred_proba = svc.predict_proba([[MonthlyIncome, MaritalStatus, NumCompaniesWorked, DistanceFromHome, JobSatisfaction]])
        
        pred_and_proba = f"{round(np.max(pred_proba)*100,2)}% {'YES' if pred == 1 else 'NO'}"

# Value Display for Predict Page
        # MaritalStatus
        if MaritalStatus == 0:
            MSVAL = 'Single'
        elif MaritalStatus == 1:
            MSVAL = 'Married'
        elif MaritalStatus == 2:
            MSVAL = 'Divorced'
        #JobSatisfaction
        if JobSatisfaction == 0:
            JSVAL = 'Low'
        elif JobSatisfaction == 1:
            JSVAL = 'Medium'
        elif JobSatisfaction == 2:
            JSVAL = 'High'
        elif JobSatisfaction == 3:
            JSVAL = 'Very High'

        return render_template('result.html',
        data=input, prediction=pred_and_proba, MonthlyIncome=input['MonthlyIncome'],
        DistanceFromHome=float(input['DistanceFromHome']), NumCompaniesWorked=input['NumCompaniesWorked'],
        MaritalStatus=MSVAL, JobSatisfaction=JSVAL)

if __name__ == '__main__':
    svc = joblib.load('svc_final')
    app.run(debug=True)