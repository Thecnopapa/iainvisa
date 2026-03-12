import os, sys, json, subprocess, requests, datetime, shutil

import flask
from flask import Flask, redirect, render_template, send_from_directory, request, send_file, session, make_response
from utils import *
from werkzeug.utils import secure_filename
from google.cloud import storage
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials






FETCH_SECRETS = bool(int(os.environ.get("FETCH_SECRETS", 0)))
os.makedirs(".secure", exist_ok=True)

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

        try:
            with open(".secure/job-exec.json", "w") as f:
                f.write(secret_client.access_secret_version(
                    request={"name": "projects/449194795494/secrets/job-exec/versions/latest"}).payload.data.decode(
                    "UTF-8"))
        except:
            print(" * Failed to read job-exec")

    except:
        print(" * Failed to load secrets")
        raise


if os.environ.get("FLASK_KEY", None) is None:
    with open(".secure/FLASK_KEY") as f:
        os.environ["FLASK_KEY"] = f.read()

if os.environ.get("FILE_SEND_KEY", None) is None:
    with open(".secure/FILE_SEND_KEY") as f:
        os.environ["FILE_SEND_KEY"] = f.read()

if os.environ.get("JOB_EXEC", None) is not None and os.environ.get("JOB_EXEC", None)  != ".secure/job-exec.json":
    with open(".secure/job-exec.json", "w") as f:
        f.write(os.environ["JOB_EXEC"])

os.environ["JOB_EXEC"] =".secure/job-exec.json"








app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["FLASK_KEY"]


if os.path.exists("/fts"):
    app.config["UPLOAD_FOLDER"] = "/fts/private"
    app.config['PUBLIC_UPLOAD_FOLDER'] = "/fts/public"
    app.config["TEMP_UPLOAD_FOLDER"] = "/fts/temp"
    app.config["PREDICT_FOLDER"] = "/fts/predictions"

else:
    app.config['UPLOAD_FOLDER'] = "uploads"
    app.config['PUBLIC_UPLOAD_FOLDER'] = "public_uploads"
    app.config["TEMP_UPLOAD_FOLDER"] = "temp"
    app.config["PREDICT_FOLDER"] = "predictions"



if os.path.exists("/runs"):
    app.config["RUNS_FOLDER"] = "/runs"

else:
    app.config["RUNS_FOLDER"] = "runs"

if os.path.exists("/models"):
    app.config["MODELS_FOLDER"] = "/models"

else:
    app.config["MODELS_FOLDER"] = "models"



os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PUBLIC_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RUNS_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODELS_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREDICT_FOLDER'], exist_ok=True)

















@app.route("/simple/")
def python_repo():
    return redirect("https://europe-west1-python.pkg.dev/iainvisa/python/simple/")

@app.route("/apt")
def apt_repo():
    return redirect("https://europe-west1-apt.pkg.dev/projects/iainvisa")


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


@app.route("/vib.ai/ppt")
def VIBAI_ppt():
    return redirect("https://docs.google.com/presentation/d/1tm3k5Y9stZzwMRF_8jb7F_THODlhkeoU2XzhKNN82NU/edit?usp=sharing")



@app.route("/Bio/<path:path>")
def redirect_biopython(path):
    target = "Bio." + ".".join([p for p in path.split("/") if p not in ["", "index.html"]])
    print(target)
    import Bio
    version = Bio.__version__
    return redirect(f"https://biopython.org/docs/{version}/api/{target}")



@app.route("/bioiain")
def bioiain_github():
    return redirect("https://github.com/Thecnopapa/bioiain")


#@app.route("/bioiain/")
#@app.route("/bioiain/<path:path>")
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
        elif folder == "models":
            return send_from_directory(app.config['MODEL_FOLDER'], fname)
        elif folder == "private":
            if key == os.environ["FILE_SEND_KEY"] and key is not None:
                return send_from_directory(app.config['UPLOAD_FOLDER'], fname)
            else:
                return render_template("login.html")
        elif folder == "temp":
            return send_from_directory(app.config['TEMP_UPLOAD_FOLDER'], fname)
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
        elif folder == "models":
            os.remove(os.path.join(app.config['MODEL_FOLDER'], fname))

        return "\n * [200] File deleted.\n", 200
    else:
        return f"\n * [403] INVALID KEY: {key}\n", 403


@app.route("/files/", methods=["PUT"])
def upload_file():
    req = request.get_json()
    file= req.get("file", None)
    print(file)
    print(req)
    return "\n * [200] File uploaded.\n", 200


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

            run_folder = os.path.join(app.config['RUNS_FOLDER'], folder, run)
            os.makedirs(run_folder, exist_ok=True)
            for old_file in os.listdir(run_folder):
                os.remove(os.path.join(run_folder, old_file))

            path = os.path.join(run_folder, fname)
            try:
                if os.path.exists(path):
                    os.remove(path)
                with open(path, "wb") as f:
                    while bytes_left > 0:
                        chunk = request.stream.read(chunk_size)
                        f.write(chunk)
                        bytes_left -= len(chunk)
                        if FETCH_SECRETS:
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


    if int(request.headers.get('temp', False)):
        target_folder = app.config['TEMP_UPLOAD_FOLDER']
        fname = request.headers.get("fname", None)
        if fname is None:
            return "\n * [406] No file name provided\n", 406
        fname = secure_filename(fname)
        total_bytes = int(request.headers.get('content-length'))
        bytes_left = int(request.headers.get('content-length'))
        chunk_size = 5120
        if total_bytes <= 0:
            return "\n * [406] Empty file provided\n", 406
        elif total_bytes / 1000000 > 3:
            return f"\n * [413] File too large (max 3 MB) provided: {total_bytes / 1000000:.2f} MB\n", 413



        path = os.path.join(target_folder, fname)
        try:
            with open(path, "wb") as f:
                while bytes_left > 0:
                    chunk = request.stream.read(chunk_size)
                    f.write(chunk)
                    bytes_left -= len(chunk)
                    if FETCH_SECRETS:
                        print(f"Uploading file... {(total_bytes-bytes_left)/total_bytes*100:3.0f}%", end="\r")
        except:
            os.remove(path)
            return f"\n * [500] File upload incomplete! ({(total_bytes-bytes_left)/total_bytes*100:3.0f}% of {total_bytes/1000000:.2f} MB)\n", 500


        download_link = f"{request.host_url}files/temp/{fname}"

        print(f"File uploaded: {fname}")
        resp = make_response(f"\n * [200] File uploaded! ({(total_bytes-bytes_left)/total_bytes*100:3.0f}% of {total_bytes/1000000:.2f} MB)\n * Download from: {download_link}\n", 200)
        print(resp.__dict__)
        resp.headers["download_url"] = download_link
        resp.headers["fname"] = fname

        resp.status_code = 200
        return resp


    elif key == os.environ["FILE_SEND_KEY"] and key is not None:
        print(request.headers)
        fname = secure_filename(request.headers.get("fname", "upload.file"))
        if fname == "":
            fname="upload.file"

        public = int(request.headers.get('public', False))
        model = int(request.headers.get('model', False))

        total_bytes = int(request.headers.get('content-length'))
        if total_bytes <= 0:
            return "\n * [406] Empty file provided\n", 406
        elif total_bytes / 1000000 > 256:
            return f"\n * [413] File too large (max 256 MB) provided: {total_bytes / 1000000:.2f} MB\n", 413
        bytes_left = int(request.headers.get('content-length'))
        chunk_size = 5120


        target_folder = app.config['UPLOAD_FOLDER']
        if model:
            target_folder = app.config['MODELS_FOLDER']
        elif public:
            target_folder = app.config['PUBLIC_UPLOAD_FOLDER']
        path = os.path.join(target_folder, fname)
        try:
            with open(path, "wb") as f:
                while bytes_left > 0:
                    chunk = request.stream.read(chunk_size)
                    f.write(chunk)
                    bytes_left -= len(chunk)
                    if FETCH_SECRETS:
                        print(f"Uploading file... {(total_bytes-bytes_left)/total_bytes*100:3.0f}%", end="\r")
        except:
            os.remove(path)
            return f"\n * [500] File upload incomplete! ({(total_bytes-bytes_left)/total_bytes*100:3.0f}% of {total_bytes/1000000:.2f} MB)\n", 500


        download_link = f"{request.host_url}files/private/{fname}"
        if model:
            download_link = f"{request.host_url}files/models/{fname}"
        elif public:
            download_link = f"{request.host_url}files/public/{fname}"

        print(f"File uploaded: {fname}")
        resp = make_response(f"\n * [200] File uploaded! ({(total_bytes-bytes_left)/total_bytes*100:3.0f}% of {total_bytes/1000000:.2f} MB)\n * Download from: {download_link}\n", 200)
        print(resp.__dict__)
        resp.headers["download_url"] = download_link
        resp.headers["fname"] = fname
        resp.status_code = 200
        return resp



    else:
        return f"\n * [403] INVALID KEY: {key}\n", 403





@app.route("/predict/", methods=["GET"])
def predict_landing():

    models = os.listdir(app.config['MODELS_FOLDER'])
    models = [m.replace(".data.json", "") for m in models if m.endswith(".data.json")]

    jobs = sorted(os.listdir(app.config['PREDICT_FOLDER']), reverse=True)


    return render_template("predict_landing.html", models=models, jobs=jobs)

@app.route("/predict/<model>", methods=["GET"])
def predict_setup(model=None):
    model = secure_filename(model)

    return render_template("predict.html", model=model)

@app.route("/predict/job/<jobid>", methods=["GET"])
def predict_result(jobid=None):
    from google.cloud import storage

    storage_client = storage.Client(project="iainvisa", credentials=Credentials.from_service_account_file(os.environ["JOB_EXEC"]))
    db = storage_client.bucket("iv_fts")

    jobid = secure_filename(jobid)

    in_info_file = os.path.join(app.config["PREDICT_FOLDER"], f"{jobid}/in/job_info.json")
    out_info_file = os.path.join(app.config["PREDICT_FOLDER"], f"{jobid}/out/job_info.json")
    prediction_url = ""
    info_url=""
    viewer = "<h3>Viewer failed</h3>"
    try:
        in_info = json.load(open(in_info_file))
    except FileNotFoundError:
        return f"\n * [406] Job not found", 406

    try:
        out_info = json.load(open(out_info_file))
    except FileNotFoundError:
        out_info = {"status": "pending"}
    if out_info["status"] == "ok":
        pred_path_db = out_info["prediction"]
        pred_fname = os.path.basename(out_info["prediction"])
        if pred_path_db.startswith("/"):
            pred_path_db = pred_path_db[1:]
        pred_blob = db.blob(pred_path_db)
        try:
            prediction_url = pred_blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(days=7),
                method="GET",
                response_disposition=f"attachment; filename={pred_fname}",
            )

            out_blob = db.blob(f"predictions/{jobid}/out/job_info.json")
            info_url = out_blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(days=7),
                method="GET",
                response_disposition=f"attachment; filename=job_info_{jobid}.json",
            )
        except Exception as e:
            print(e)

        try:
            viewer = molstar_viewer(prediction_url, save_folder=os.path.join(app.config["PREDICT_FOLDER"], f"{jobid}/out"))
        except Exception as e:
            print(e)

    return render_template("prediction_result.html", jobid=jobid, in_info=in_info, out_info=out_info,
     prediction_url=prediction_url, info_url=info_url, viewer=viewer)


def molstar_viewer(url, save_folder=None):
    import molviewspec
    builder = molviewspec.create_builder()
    palette = molviewspec.ContinuousPalette(kind="continuous",
                                            colors= ["blue", "green", "yellow", "red"],
                                            mode="absolute")
    structure = (builder
                 #.download(url="https://www.ebi.ac.uk/pdbe/entry-files/download/1cbs_updated.cif")
                 .download(url=url)
                 .parse(format="mmcif")
                 .model_structure()
                 .component()
                 .representation()
                 .color_from_source(palette=palette,
                                    field_name="B_iso_or_equiv",
                                    schema="atom",
                                    category_name="atom_site",
                                    )
                 )
    if save_folder is not None:
        save_path = os.path.join(save_folder, "state.mvsj")
        with open(save_path, "w") as f:
            f.write(builder.get_state().model_dump_json(indent=2 ,exclude_defaults=True))
        molviewspec.mvsj_to_mvsx(save_path, save_path.replace(".mvsj", ".mvsx"))

    return molviewspec.molstar_html(builder.get_state())



@app.route("/predict/submit", methods=["POST", "GET", "PUT"])
def predict_submit():
    from google.cloud import run_v2
    from google.oauth2.service_account import Credentials




    data = request.json
    try:
        fname = secure_filename(data["fname"])
        f_path = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], fname)
        model_name = secure_filename(data["model_name"])+".data.json"
        chain = secure_filename(data.get("chain", "A"))
    except:
        return " * [406] Missing info", 406

    job_id = datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S')


    job_folder = os.path.join(app.config["PREDICT_FOLDER"], f"{job_id}/in/")
    try:
        if os.path.exists(job_folder):
            shutil.rmtree(job_folder)
        os.makedirs(job_folder, exist_ok=True)
        os.makedirs(".tmp", exist_ok=True)
        #tmp = shutil.copy(f_path, ".tmp")
        shutil.copy(f_path, job_folder)
    except PermissionError as e:
        print(e)


    job_info = {
        "job_id": job_id,
        "model_name": model_name,
        "fname": fname,
        "chain": chain
    }
    print("JOBINFO:", job_info)
    json.dump(job_info, open(os.path.join(job_folder, "job_info.json"), "w"), indent=4)

    try:
        client = run_v2.JobsClient(credentials=Credentials.from_service_account_file(os.environ["JOB_EXEC"]))

        req = run_v2.RunJobRequest(
            name=f"projects/iainvisa/locations/europe-west1/jobs/predictrun",
            overrides={
                "container_overrides":
                    [
                        {"env": [{"name": "JOBID", "value": f"{job_id}"}],}
                    ]
            }
        )
        client.run_job(request=req)
    except Exception as e:
        print(job_info)
        print(e)
        return f"\n * [504] Job submission error\ne\n", 504

    if request.method == "PUT":
        return f"\n * [200] Job ({job_id}) submitted successfully\n * Await results at: https://iainvisa.com/predict/jobs/{job_id}\n", 200

    elif request.method == "POST":
        resp = make_response({
            "job_id": job_id,
            "job_url": "https://iainvisa.com/predict/jobs/{job_id}"
        })
        return resp, 200

    elif request.method == "GET":
        return redirect(f"https://iainvisa.com/predict/jobs/{job_id}\n")

    else:
        return "Not implemented", 404






