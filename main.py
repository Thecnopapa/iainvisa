from flask import Flask, redirect

app = Flask(__name__)

@app.route("/")
def github():
    return redirect("https://www.linkedin.com/in/iainvisa")

@app.route("/linkedin")
def github():
    return redirect("https://www.linkedin.com/in/iainvisa")


@app.route("/github")
def github():
    return redirect("https://github.com/Thecnopapa")

@app.route("/ProjectDimer")
def projectDimer():
    return redirect("https://github.com/Thecnopapa/projectDimer")