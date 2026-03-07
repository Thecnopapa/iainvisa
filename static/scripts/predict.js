
async function readBytes(file) {
    console.log("Reading file... " + file.name);
    let reader = new ArrayBuffer();
    return reader.readAsArrayBuffer(file);

    let filedata = undefined;
    reader.onloadend = () => {
        console.log("File reading done")
        filedata = reader.result;
    };
    reader.onerror = () => {
        console.error("Error reading the file. Please try again.");
    };
    await reader.Array(file);
    while (!reader.result) {
        console.log(reader.result);
    }
    return reader.result;
}


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

    // let filedata = readBytes(file);
    // console.log(file);
    // console.log(filedata);
    // if (!filedata){
    //     console.error("No file data:");
    //     console.log(filedata)
    //     return;
    // }
    // console.log("File read successfully.");

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
        return resp.headers.get("download_url");
    } else {
        console.error("upload failed");
        return undefined
    }
}

async function submitPrediction(){

    let uploadUrl = await uploadCif(document.getElementById("cif-file"), document.getElementById("cif-name"));
    if (uploadUrl === undefined) {return;}

    console.log("uploadUrl", uploadUrl);
    let modelName = document.getElementById("model").attributes.name.value;
    console.log("modelName", modelName);

    let resp = await fetch(`https://predict.iainvisa.com`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "file": uploadUrl,
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