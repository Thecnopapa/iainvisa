




async function goToFile(fpath, method, button=undefined) {
	let url = new URL(window.location.href);
	let folder = fpath.split("/")[0]
	let fname = fpath.split("/")[1]
	console.log(folder, fname)
	if (method === "DOWNLOAD"){
		const link = document.createElement("a");
		link.href = `/files/${folder}/${fname}`
		console.log(link.href);
		link.download = fname;
		link.click();

	} else if (method === "OPEN") {
		let u = `/files/${folder}/${fname}`
		console.log(u);
		window.open(u, '_blank').focus();

	} else if (method === "DELETE") {
		let resp = fetch(`/files/`, {
			method: "DELETE",
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				fname: fname,
				folder: folder,
			})
		}).then((response) => {
			if (response.ok) {
				button.style.backgroundColor = "lightgreen";
				console.log(response);
				window.location.reload();
			} else {
				console.log(response);
				button.style.backgroundColor = "red";
			}

		})
	}
}

async function login(){
	await fetch(`/files/login`, {
		method: "POST",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify({
			key:document.querySelector("#password").value
		})
	})
	window.location.reload();
}


