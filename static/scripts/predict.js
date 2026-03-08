

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

    let resp = await fetch("https://predict-449194795494.europe-west1.run.app", {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "fname":fname,
            "model": modelName,
        })
        }
    );
    if (resp.ok) {
        let jobInfo = await resp.json();
        let jobId = jobInfo.jobid;
        window.open(`/predict/job/${jobId}`, "_blank");
    }

}