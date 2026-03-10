

async function uploadCif(fileInput, nameInput){
    let file = fileInput.files[0];
    if (!file) {
      console.error("No file selected. Please choose a file.");
      return;
    }
    let fname = nameInput.value;
    if (fname === "") {
      console.error("No name provided. Please write a file name");
      return;
    }
    console.log(`Uploading ${file.name} as ${fname}...`);



    let buffer = await file.arrayBuffer()
    console.log({buffer});
    let array = new DataView(buffer);
    await array.buffer;
    console.log(array);

    let resp = await fetch(`/files/send`, {
        method: "POST",
        headers: {
            "temp": 1,
            "fname": nameInput.value,
        },
        body: array,

    });
    console.log(await resp.text());

    if (resp.ok) {
        return resp.headers.get("fname");
    } else {
        console.error("upload failed");
        return undefined
    }
}

async function submitPrediction(){

    let fname = await uploadCif(document.getElementById("cif-file"), document.getElementById("cif-name"));
    if (fname === undefined) {return;}

    console.log("fname", fname);
    let modelName = document.getElementById("model").attributes.name.value;
    console.log("modelName", modelName);

    let resp = await fetch("/predict/submit", {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "fname":fname,
            "model_name": modelName,
        })
        }
    );
    if (resp.ok) {
        let jobInfo = await resp.json();
        let jobId = jobInfo.job_id;
        let jobUrl = jobInfo.job_url;
        console.log("Job submitted: "+ jobId);
        window.open("/predict/job/"+jobId, "_blank");
    }

}



