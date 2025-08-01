from flask import Flask, redirect, render_template
from utils import *

app = Flask(__name__)

@app.route("/cv")
@app.route("/portfolio")
def home():
    return render_template("portfolio.html", start="academic")

@app.route("/")
@app.route("/linkedin")
def linkedin():
    return redirect("https://www.linkedin.com/in/iainvisa")


@app.route("/github")
def github():
    return redirect("https://github.com/Thecnopapa")
    
@app.route("/projectdimer")    
@app.route("/projectDimer")
@app.route("/ProjectDimer")
def projectDimer():
    return redirect("https://github.com/Thecnopapa/projectDimer")

@app.route("/projectdimer/ppt")    
@app.route("/projectDimer/ppt")
@app.route("/ProjectDimer/PPT")
def projectDimerPPT():
    return redirect("https://docs.google.com/presentation/d/1HGT1u9emPj-3RmbbPaktof1PfAYAaBjy0TO_0LxUf3E/edit?usp=sharing")



