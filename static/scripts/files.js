





let PAGE_IDLE = true;


async function reloadPage(){
	if (PAGE_IDLE){
		console.log("Reloading Page...");
		window.location.reload();
	}
}



async function downloadFile(fname){
	PAGE_IDLE = false;
	let url = new URL(window.location.href);
	let key = url.searchParams.get("key");
	console.log(key);
	window.open("/files/download/" + fname +"?key=" + key, '_blank').focus();
	PAGE_IDLE = true;
}




setTimeout(reloadPage, 10000);