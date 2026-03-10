

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

// Setup to load data from rawgit
NGL.DatasourceRegistry.add(
    "data", new NGL.StaticDatasource( "http://files.rcsb.org/download/" ),
    "cloud", new NGL.StaticDatasource( "https://storage.googleapis.com/iv_fts/" ), 
);

// Create NGL Stage object
var stage = new NGL.Stage( "viewport" );

// Handle window resizing
window.addEventListener( "resize", function( event ){
    stage.handleResize();
}, false );


// Code for example: color/atomindex


stage.loadFile( "data://1m2z.cif" ).then( function( comp ){
    comp.addRepresentation( "cartoon", { multipleBond: true, color: "bfactor"} );
} );




