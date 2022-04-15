from cProfile import label
from email.policy import default
from pickle import FALSE
from flask import Flask,make_response, render_template,request
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
import requests
from collections import defaultdict
from bs4 import BeautifulSoup
import json



# Create flast instance
app=Flask(__name__)

# Connect to database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///covid-cases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#connecting sqlachemy to the flask
db=SQLAlchemy(app)


# create database tables or in this case python class.
class Case(db.Model):

    sno=db.Column(db.Integer,primary_key=True)
    country=db.Column(db.String(50),nullable=False)
    active_cases=db.Column(db.Integer,primary_key=False)
    new_cases=db.Column(db.Integer,primary_key=False)
    recovered_cases=db.Column(db.Integer,primary_key=False)
    total_cases=db.Column(db.Integer,primary_key=False)
    new_deaths=db.Column(db.Integer,primary_key=False)
    total_deaths=db.Column(db.Integer,primary_key=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.country} - {self.active_cases} - {self.new_cases} - {self.recovered_cases} - {self.total_cases} - {self.new_deaths} - {self.total_deaths}"



#first route rendering the home page
@app.route("/",)
def my_main_function():
    return render_template('index.html')

#function to get data in json format to pass into html
def findinformation(search):
    
    country=search
    url = "https://covid-193.p.rapidapi.com/statistics"

    temp={"country":country}

    headers = {
	"X-RapidAPI-Host": "covid-193.p.rapidapi.com",
	"X-RapidAPI-Key": "9c83cfc637msh5e356fe3447f249p177e48jsnfa7571368693"}

    response = requests.request("GET", url, headers=headers, params=temp)

    # Cases
    active_cases=response.json()["response"][0]["cases"]["active"]
    new_cases=response.json()["response"][0]["cases"]["new"]
    recovered_cases=response.json()["response"][0]["cases"]["recovered"]
    total_cases=response.json()["response"][0]["cases"]["total"]

    # Deaths
    total_population=response.json()["response"][0]["population"]
    new_deaths=response.json()["response"][0]["deaths"]["new"]
    total_deaths=response.json()["response"][0]["deaths"]["total"]

    data={
        "active cases":active_cases,
        "new_cases":new_cases,
        "recovered_cases":recovered_cases,
        "total_cases":total_cases,
        "new_deaths":new_deaths,
        "total_deaths":total_deaths
    }

    return data

#function to insert data in the db
def findData(search):
    
    country=search
    url = "https://covid-193.p.rapidapi.com/statistics"

    temp={"country":country}

    headers = {
	"X-RapidAPI-Host": "covid-193.p.rapidapi.com",
	"X-RapidAPI-Key": "9c83cfc637msh5e356fe3447f249p177e48jsnfa7571368693"}

    response = requests.request("GET", url, headers=headers, params=temp)

    # Cases
    dict=defaultdict(list)
    dict["active_cases"]=response.json()["response"][0]["cases"]["new"]
    dict["new_cases"]=response.json()["response"][0]["cases"]["new"]
    dict["recovered_cases"]=response.json()["response"][0]["cases"]["recovered"]
    dict["total_cases"]=response.json()["response"][0]["cases"]["total"]

    dict["total_population"]=response.json()["response"][0]["population"]
    dict["new_deaths"]=response.json()["response"][0]["deaths"]["new"]
    dict["total_deaths"]=response.json()["response"][0]["deaths"]["total"]

    return dict

#first route rendering the Dashboard page
@app.route("/charts",)
def my_charts_function():    
    
    db.session.query(Case).delete()    
    db.session.commit()
    c1='Canada'
    data=findData(c1)
    case=Case(country=c1,active_cases=data['active_cases'],new_cases=data['new_cases'],recovered_cases=data['recovered_cases'],total_cases=data['total_cases'],new_deaths=data['new_deaths'],total_deaths=data['total_deaths'])
    db.session.add(case)
    db.session.commit()

    chart1=findinformation(c1)
    ch1=Markup(json.dumps(chart1))

    c2='Ghana'
    data2=findData(c2)
    case=Case(country=c2,active_cases=data2['active_cases'],new_cases=data2['new_cases'],recovered_cases=data2['recovered_cases'],total_cases=data2['total_cases'],new_deaths=data2['new_deaths'],total_deaths=data2['total_deaths'])
    db.session.add(case)
    db.session.commit()

    chart2=findinformation(c2)
    ch2=Markup(json.dumps(chart2))

    return make_response(render_template('charts.html',data=ch1,data2=ch2,country1=c1,country2=c2))

if __name__=="__main__":
    app.run(debug=True,port=4000)