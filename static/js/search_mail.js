const searchField=document.querySelector("#searchField");

const resultsBox=document.querySelector("#resultsBox")
resultsBox.style.display ="none"
searchField.addEventListener('keyup',(e)=>{
	const searchValue=e.target.value;

		console.log("searchValue",searchValue);
		fetch("/main/search_email/",{
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
						resultsBox.innerHTML += `<p>${item.subject} </p>`
					})
				}

			});

});