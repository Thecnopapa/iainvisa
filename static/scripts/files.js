





let PAGE_IDLE = false;


async function reloadPage(){
	if (PAGE_IDLE){
		console.log("Reloading Page...");
		window.location.reload();
	}
}



async function goToFile(fname, download=false, public=false){
	PAGE_IDLE = false;
	let url = new URL(window.location.href);
	let key = url.searchParams.get("key");
	if (download){
		const link = document.createElement("a");
		link.href = "/files/download/" + fname +"?key=" + key;
		link.download = fname;
		link.click();

	} else {
		window.open("/files/download/" + fname +"?key=" + key, '_blank').focus();

	}

	PAGE_IDLE = true;
}


async function goToPublicFile(fname, download=false){
	return await goToFile(fname, download, true);
}


async function login(){
	window.open(window.location.pathname + "?key=" + document.querySelector("#password").value, "_self");
}


setTimeout(reloadPage, 10000);