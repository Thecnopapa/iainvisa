import os, sys, json, subprocess

import flask
from flask import Flask, redirect, render_template, send_from_directory, request, send_file
from utils import *
from werkzeug.utils import secure_filename
from google.cloud import storage





FETCH_SECRETS = bool(int(os.environ.get("FETCH_SECRETS", 1)))

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

storage_client = storage.Client(project="iainvisa")
db = storage_client.bucket("iv_fts")


app = Flask(__name__)
with open(".secure/FLASK_KEY") as f:
    app.config["SECRET_KEY"] = f.read()

app.config['UPLOAD_FOLDER'] = "uploads"
app.config['PUBLIC_UPLOAD_FOLDER'] = "public_uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PUBLIC_UPLOAD_FOLDER'], exist_ok=True)
app.config['DOWNLOAD_FOLDER'] = "downloads"
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)


















@app.route("/")
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


@app.route("/files/")
def redirect_to_await():
    return redirect("/files/await/")
@app.route("/files/await/")
def await_files():

    key = request.args.get('key', None)
    with open(".secure/FILE_SEND_KEY") as f:
        file_send_key = f.read()
    DB_TIMEOUT = False
    public_files = {
        "fast": os.listdir(app.config['PUBLIC_UPLOAD_FOLDER'])
    }
    try:
        public_files["slow"] = [b.name.split("/")[-1] for b in db.list_blobs(prefix="public/", include_folders_as_prefixes=False) if not b.name.endswith("/")]
    except:
        DB_TIMEOUT=True

    if key == file_send_key and key is not None:
        files = {
            "fast": os.listdir(app.config['UPLOAD_FOLDER']),
        }
        try:
            files["slow"] = [b.name.split("/")[-1] for b in db.list_blobs(prefix="private/", include_folders_as_prefixes=False) if not b.name.endswith("/")]
        except:
            DB_TIMEOUT = True
        return render_template("file_waiting.html", request=request, files=files, public_files=public_files, DB_TIMEOUT=DB_TIMEOUT)
    else:
        return render_template("file_waiting.html", request=request, files=None, public_files=public_files, DB_TIMEOUT=DB_TIMEOUT)


@app.route("/files/download/<fname>/")
def download_file(fname=None):


    with open(".secure/FILE_SEND_KEY") as f:
        file_send_key = f.read()

    print("Downloading file...")

    key = request.args.get('key', None)

    if key == file_send_key and key is not None:
        fname = secure_filename(fname)
        fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
        return send_file(fpath)
    else:
        #return f"INVALID KEY: {key}", 403
        return render_template("login.html")


@app.route("/files/download/public/<fname>/")
def download_public_file(fname=None):

    print("Downloading file...")

    fname = secure_filename(fname)
    fpath = os.path.join(app.config['PUBLIC_UPLOAD_FOLDER'], fname)
    return send_file(fpath)


@app.route("/storage/download/<fname>/")
def download_file_storage(fname=None):


    with open(".secure/FILE_SEND_KEY") as f:
        file_send_key = f.read()

    print("Downloading file...")

    key = request.args.get('key', None)

    if key == file_send_key and key is not None:
        fname = secure_filename(fname)
        blob = db.blob(f"private/{fname}")
        path = os.path.join(app.config['DOWNLOAD_FOLDER'], fname)
        blob.download_to_file(open(path, "w"))
        return send_file(path, download_name=fname)
    else:
        #return f"INVALID KEY: {key}", 403
        return render_template("login.html")

@app.route("/storage/download/public/<fname>/")
def download_public_file_storage(fname=None):

    print("Downloading file...")

    fname = secure_filename(fname)
    blob = db.blob(f"public/{fname}")
    path = os.path.join(app.config['DOWNLOAD_FOLDER'], fname)
    blob.download_to_file(open(path, "w"))
    return send_file(path, download_name=fname)

@app.post("/storage/delete")
def delete_file_storage():


    with open(".secure/FILE_SEND_KEY") as f:
        file_send_key = f.read()

    print("Deleting file...")

    key = request.json.get('key', None)
    public = request.json.get('public', False)
    fname = secure_filename(request.json.get('fname', False))


    if key == file_send_key and key is not None:
        fname = secure_filename(fname)
        if public:
            blob = db.blob(f"public/{fname}")
        else:
            blob = db.blob(f"private/{fname}")
        blob.delete()
        return "Deleted file", 200
    else:
        return f"INVALID KEY: {key}", 403





@app.post("/files/send")
def send_files():

    key = request.args.get('key', "")

    with open(".secure/FILE_SEND_KEY") as f:
        file_send_key = f.read()

    print("KEY:", key)

    if key == file_send_key and key != "":
        print(request.headers)
        fname = secure_filename(request.headers.get("fname", "upload.file"))
        if fname == "":
            fname="upload.file"

        public = int(request.headers.get('public', False))
        store = int(request.headers.get('store', False))

        total_bytes = int(request.headers.get('content-length'))
        bytes_left = int(request.headers.get('content-length'))
        chunk_size = 5120


        target_folder = app.config['UPLOAD_FOLDER']
        if public:
            target_folder = app.config['PUBLIC_UPLOAD_FOLDER']
        path = os.path.join(target_folder, fname)
        with open(path, "wb") as f:
            while bytes_left > 0:
                chunk = request.stream.read(chunk_size)
                f.write(chunk)
                bytes_left -= len(chunk)
                if not FETCH_SECRETS:
                    print(f"Uploading file... {(total_bytes-bytes_left)/total_bytes*100:3.0f}%", end="\r")

        if store:

            bucket = "private"
            if public:
                bucket = "public"
            new_blob = db.blob(f"{bucket}/{fname}")
            new_blob.upload_from_filename(path)
            prefix="storage"
            os.remove(path)
        else:
            prefix="files"

        download_link = f"{request.host_url}/{prefix}/download/{fname}"
        if public:
            download_link = f"{request.host_url}/{prefix}/download/public/{fname}"
        return f"\n * [200] File uploaded! ({(total_bytes-bytes_left)/total_bytes*100:3.0f}% of {total_bytes/1000000:.2f} MB)\n * Download from: {download_link}\n", 200

    else:
        return f" * INVALID KEY: {key}\n", 403
