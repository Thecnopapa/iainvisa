import os, sys, json, subprocess

import flask
from flask import Flask, redirect, render_template, send_from_directory, request, send_file, session, make_response
from utils import *
from werkzeug.utils import secure_filename
from google.cloud import storage





FETCH_SECRETS = bool(int(os.environ.get("FETCH_SECRETS", 0)))

if FETCH_SECRETS:
    from google.cloud import secretmanager
    from google.oauth2 import service_account
    print(" * Updating secrets")
    os.makedirs(".secure", exist_ok=True)
    try:
        secret_client = secretmanager.SecretManagerServiceClient()
        print(" * Secret manager initialised")

        try:
            with open(".secure/FLASK_KEY", "w") as f:
                f.write(secret_client.access_secret_version(request={"name": "projects/449194795494/secrets/FLASK_KEY/versions/latest"}).payload.data.decode("UTF-8"))
        except:
            print(" * Failed to read FLASK_KEY")
            raise

        try:
            with open(".secure/FILE_SEND_KEY", "w") as f:
                f.write(secret_client.access_secret_version(request={"name": "projects/449194795494/secrets/FILE_SEND_KEY/versions/latest"}).payload.data.decode("UTF-8"))
        except:
            print(" * Failed to read FILE_SEND_KEY")
    except:
        print(" * Failed to load secrets")
        raise


if os.environ.get("FLASK_KEY", None) is None:
    with open(".secure/FLASK_KEY") as f:
        os.environ["FLASK_KEY"] = f.read()

if os.environ.get("FILE_SEND_KEY", None) is None:
    with open(".secure/FILE_SEND_KEY") as f:
        os.environ["FILE_SEND_KEY"] = f.read()


storage_client = storage.Client(project="iainvisa")
db = storage_client.bucket("iv_fts")
runs_db = storage_client.bucket("iv_tensorboard")


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["FLASK_KEY"]


if os.path.exists("/fts"):
    app.config["UPLOAD_FOLDER"] = "/fts/private"
    app.config['PUBLIC_UPLOAD_FOLDER'] = "/fts/public"

else:
    app.config['UPLOAD_FOLDER'] = "uploads"
    app.config['PUBLIC_UPLOAD_FOLDER'] = "public_uploads"


if os.path.exists("/runs"):
    app.config["RUNS_FOLDER"] = "/runs"

else:
    app.config["RUNS_FOLDER"] = "runs"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PUBLIC_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RUNS_FOLDER'], exist_ok=True)



















@app.route("/")
def menu():
    return render_template("menu.html")


@app.route("/cv")
@app.route("/portfolio/")
@app.route("/portfolio/academic")
def acedemic_home():
    return render_template("portfolio.html", start="academic")

@app.route("/portfolio/developer")
def developer_home():
    return render_template("portfolio.html", start="developer")

@app.route("/portfolio/other")
def other_home():
    return render_template("portfolio.html", start="other")




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



@app.route("/Bio/<path:path>")
def redirect_biopython(path):
    target = "Bio." + ".".join([p for p in path.split("/") if p not in ["", "index.html"]])
    print(target)
    import Bio
    version = Bio.__version__
    return redirect(f"https://biopython.org/docs/{version}/api/{target}")



@app.route("/bioiain")
@app.route("/bioiain/")
@app.route("/bioiain/<path:path>")
def bioiain_docs(path=None):
    import pdoc
    import bioiain
    import builtins
    #builtins.__import__(f"bioiain.{".".join(path.split("/"))}")
    import bioiain.visualisation
    pdoc.tpl_lookup.directories = ["templates"] + pdoc.tpl_lookup.directories



    context = pdoc.Context()
    bp_mod = pdoc.Module(pdoc.import_module("Bio.PDB", skip_errors=True), skip_errors=True, context=context)
    mod = pdoc.Module(pdoc.import_module("bioiain", skip_errors=True), skip_errors=True, context=context)
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
    print("MODULE:", mod)
    print("SUBMODULES:", mod.submodules())

    return mod.html()





@app.post("/files/login")
def fts_login():
    key = request.json.get("key", None)

    resp = make_response("Key saved")
    resp.set_cookie("key", key)
    return resp



@app.route("/files/")
def await_files():

    key = request.cookies.get("key", None)

    DB_TIMEOUT = False
    public_files = os.listdir(app.config['PUBLIC_UPLOAD_FOLDER'])

    if key == os.environ["FILE_SEND_KEY"] and key is not None:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template("file_waiting.html", request=request, files=files, public_files=public_files, DB_TIMEOUT=DB_TIMEOUT)
    else:
        return render_template("file_waiting.html", request=request, files=None, public_files=public_files, DB_TIMEOUT=DB_TIMEOUT)


@app.route("/files/<folder>/<fname>/", methods=["GET", "POST"])
def download_file(fname, folder):
    key = request.cookies.get("key", None)
    fname = secure_filename(fname)
    folder = secure_filename(folder)

    try:
        if folder == "public":
            return send_from_directory(app.config['PUBLIC_UPLOAD_FOLDER'], fname)
        elif folder == "private":
            if key == os.environ["FILE_SEND_KEY"] and key is not None:
                return send_from_directory(app.config['UPLOAD_FOLDER'], fname)
            else:
                return render_template("login.html")
        else:
            return f"\n * [404] Folder not found: {folder}\n", 404
    except:
        return f"\n * [404] File not found: {folder}/{fname}\n", 404



@app.route("/files/", methods=["DELETE"])
def delete_file():
    key = request.cookies.get("key", None)
    if key == os.environ["FILE_SEND_KEY"] and key is not None:
        fname = secure_filename(request.json.get("fname", None))
        folder = secure_filename(request.json.get("folder", None))
        if folder == "public":
            os.remove(os.path.join(app.config['PUBLIC_UPLOAD_FOLDER'], fname))
        elif folder == "private":
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fname))

        return "\n * [200] File deleted.\n", 200
    else:
        return f"\n * [403] INVALID KEY: {key}\n", 403


@app.route("/files/", methods=["PUT"])
def upload_file():
    req = request.get_json()
    file= req.get("file", None)
    print(file)
    print(req)
    return "\n * [200] File deleted.\n", 200


@app.route("/runs/", methods=["GET", "DELETE", "PUT"])
def update_run():

    key = request.headers.get("key", None)

    if key == os.environ["FILE_SEND_KEY"] and key is not None:
        try:
            folder = secure_filename(request.headers.get("folder", None))
            fname = secure_filename(request.headers.get("fname", None))
            run = secure_filename(request.headers.get("run", None))
            assert folder is not None
            assert fname is not None
            assert run is not None
        except:
            return f"\n * [404] File not found\n", 404

        if request.method == "GET":
            print(request.__dict__)
            return send_from_directory(app.config['RUNS_FOLDER'], folder, run, fname)
        elif request.method == "DELETE":
            try:
                os.remove(os.path.join(app.config['RUNS_FOLDER'], folder, run, fname))
                return f"\n * [200] File deleted.\n", 200
            except:
                return f"\n * [500] File not deleted: {folder}/{run}/{fname}\n", 404

        elif request.method == "PUT":
            total_bytes = int(request.headers.get('content-length'))
            if total_bytes <= 0:
                return "\n * [406] Empty file provided\n", 406
            elif total_bytes / 1000000 > 256:
                return f"\n * [413] File too large (max 256 MB) provided: {total_bytes / 1000000:.2f} MB\n", 413
            bytes_left = int(request.headers.get('content-length'))
            chunk_size = 5120

            path = os.path.join(app.config['RUNS_FOLDER'], folder, run, fname)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                with open(path, "wb") as f:
                    while bytes_left > 0:
                        chunk = request.stream.read(chunk_size)
                        f.write(chunk)
                        bytes_left -= len(chunk)
                        if not FETCH_SECRETS:
                            print(f"Uploading file... {(total_bytes - bytes_left) / total_bytes * 100:3.0f}%", end="\r")
            except:
                os.remove(path)
                return f"\n * [500] File upload incomplete! ({(total_bytes - bytes_left) / total_bytes * 100:3.0f}% of {total_bytes / 1000000:.2f} MB)\n", 500
            return f"\n * [200] File uploaded! ({(total_bytes - bytes_left) / total_bytes * 100:3.0f}% of {total_bytes / 1000000:.2f} MB)\n", 200
        else:
            return f"\n * [503] METHOD NOT VALID: {request.method}\n", 503

    else:
        return f"\n * [403] INVALID KEY: {key}\n", 403





@app.post("/files/send")
def send_files():

    key = request.args.get('key', "")

    print("KEY:", key)
    if key == "":
        key = None

    if key == os.environ["FILE_SEND_KEY"] and key is not None:
        print(request.headers)
        fname = secure_filename(request.headers.get("fname", "upload.file"))
        if fname == "":
            fname="upload.file"

        public = int(request.headers.get('public', False))

        total_bytes = int(request.headers.get('content-length'))
        if total_bytes <= 0:
            return "\n * [406] Empty file provided\n", 406
        elif total_bytes / 1000000 > 256:
            return f"\n * [413] File too large (max 256 MB) provided: {total_bytes / 1000000:.2f} MB\n", 413
        bytes_left = int(request.headers.get('content-length'))
        chunk_size = 5120


        target_folder = app.config['UPLOAD_FOLDER']
        if public:
            target_folder = app.config['PUBLIC_UPLOAD_FOLDER']
        path = os.path.join(target_folder, fname)
        try:
            with open(path, "wb") as f:
                while bytes_left > 0:
                    chunk = request.stream.read(chunk_size)
                    f.write(chunk)
                    bytes_left -= len(chunk)
                    if not FETCH_SECRETS:
                        print(f"Uploading file... {(total_bytes-bytes_left)/total_bytes*100:3.0f}%", end="\r")
        except:
            os.remove(path)
            return f"\n * [500] File upload incomplete! ({(total_bytes-bytes_left)/total_bytes*100:3.0f}% of {total_bytes/1000000:.2f} MB)\n", 500


        download_link = f"{request.host_url}files/private/{fname}"
        if public:
            download_link = f"{request.host_url}files/public/{fname}"
        return f"\n * [200] File uploaded! ({(total_bytes-bytes_left)/total_bytes*100:3.0f}% of {total_bytes/1000000:.2f} MB)\n * Download from: {download_link}\n", 200

    else:
        return f"\n * [403] INVALID KEY: {key}\n", 403
