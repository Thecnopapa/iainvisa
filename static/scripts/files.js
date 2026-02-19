





let PAGE_IDLE = false;


async function reloadPage(){
	if (PAGE_IDLE){
		console.log("Reloading Page...");
		window.location.reload();
	}
}



async function goToFile(fname, download=false, publicfile=false, storage_type="fast"){
	PAGE_IDLE = false;
	let url = new URL(window.location.href);
	let key = url.searchParams.get("key");
	let prefix="files"
	if (storage_type==="fast"){
		prefix="files"
	} else if (storage_type==="slow"){
		prefix="storage"
	}
	if (download){
		const link = document.createElement("a");
		if (publicfile){
			link.href = "/"+prefix+"/download/public/" + fname +"?key=" + key;

		} else{
			link.href = "/"+prefix+"/download/" + fname +"?key=" + key;
		}
		console.log(link.href);
		link.download = fname;
		link.click();

	} else {
		let u = undefined
		if (publicfile){
			u = "/"+prefix+"/download/public/" + fname +"?key=" + key;
			

		} else {
			u = "/"+prefix+"/download/" + fname +"?key=" + key;
		}
		//u = window.location.protocol+window.location.host + u;
		console.log(u);

		window.open(u, '_blank').focus();
	}

	PAGE_IDLE = true;
}


async function deleteFile(fname, publicfile=false){
	let url = new URL(window.location.href);
	let key = url.searchParams.get("key");
	let resp = fetch(`/storage/delete`, {
		method: "POST",
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			fname: fname,
			public: publicfile,
			key:key,
		})
	}).then((response) => {
		console.log(response);
		window.location.reload();
	})
}




async function login(){
	window.open(window.location.pathname + "?key=" + document.querySelector("#password").value, "_self");
}


//setTimeout(reloadPage, 10000);