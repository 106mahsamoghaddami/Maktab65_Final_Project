const searchTxt=document.querySelector("#contactSearch");

const resultsBox=document.querySelector("#resultsBox");
resultsBox.style.display ="none"
searchTxt.addEventListener('keyup',(e)=>{
	const searchValue=e.target.value;

		console.log("searchValue",searchValue);
		fetch("/main/search_contact/",{
			body:JSON.stringify({searchText:searchValue}),
			method:"POST"
		})
			.then((res)=>res.json())
			.then((data)=>{
				console.log('data',data);
				resultsBox.style.display ="block"

				if(data.length ===0){
					resultsBox.innerHTML="No results found"


				}else{
					data.forEach(item=>{
						resultsBox.innerHTML += `<p>${item.names} </p>`
					})
				}

			});

});