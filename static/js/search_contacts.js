const searchItem=document.querySelector("#searchItem");
const contactResult =document.querySelector(".contact_ajax_result");
const listAjaxContact =document.querySelector(".list_ajax_c");

contactResult.style.display ="none"
const list_display = document.querySelector(".list_div");
const result_c = document.querySelector(".result_c");
searchItem.addEventListener('keyup',function (e){
	const searchValue=e.target.value;

		if (searchValue.trim().length >0){
			console.log('searchValue',searchValue);
			listAjaxContact.innerHTML =""
			fetch("/main/search_contact/", {
				body: JSON.stringify({searchText: searchValue}),
				method: "POST",

			})
			.then((res)=>res.json())
				.then((data)=>{
					console.log('data',data);
					list_display.style.display ="none"
					contactResult.style.display ="block"

					if (data.length ===0){
						contactResult.innerHTML = "   NO Result found"
					}else{
						contactResult.innerHTML =""
						data.forEach((item)=>{
							contactResult.style.display ="none"
							listAjaxContact.innerHTML +=



										` <a href="/main/contact_detail/${item.id}"> <p>${item.name} - ${item.email}</p></a>`



						})
					}
				 });
		}else{
			listAjaxContact.innerHTML =""
			contactResult.style.display ="none";
			list_display.style.display ="block";
		}












});