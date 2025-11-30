import os, sys, json, subprocess

import flask
from flask import Flask, redirect, render_template, send_from_directory,request
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

@app.route("/bioiain/")
@app.route("/bioiain/<path:path>")
def bioiain_docs(path=None):
    import pdoc
    import bioiain
    import builtins
    #builtins.__import__(f"bioiain.{".".join(path.split("/"))}")
    import bioiain.visualisation
    pdoc.tpl_lookup.directories.append("templates")


    mod = pdoc.Module(pdoc.import_module("bioiain", skip_errors=True), skip_errors=True)
    pdoc.link_inheritance()
    if path is None:
        return mod.html()
    path = path.split("/")
    print(path)
    target_mod = "bioiain." + ".".join([p for p in path if p not in ["", "index.html"]])
    target_mod = target_mod.replace(".html", "")
    if target_mod.endswith("."):
        target_mod = target_mod[:-1]
    print("TARGET:", target_mod)
    try:
        builtins.__import__(target_mod)
    except ModuleNotFoundError:
        print(request.__dict__)
        return redirect(request.referrer)

    while mod.name != target_mod:
        found = False
        print(" >", mod.name, target_mod, mod.name == target_mod)
        for s in mod.submodules():
            print("  > ", s.name, target_mod, s.name in target_mod)
            print("  > ",s.name == target_mod)
            print("  > ",s.name in target_mod)
            if s.name in target_mod or s.name == target_mod:
                mod = s
                found = True
                print(mod)
                break
        if not found:
            flask.abort(404)
    print("MODULE:", mod.name)
    print("SUBMODULES:", mod.submodules())
    return mod.html()





