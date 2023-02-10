navbar = document.querySelector('.header .flex .navbar');

document.querySelector('#menu-btn').onclick = () =>{
	navbar.classList.toggle('active');
	profile.classList.remove('active');
}

profile = document.querySelector('.header .flex .profile');

document.querySelector('#user-btn').onclick = () =>{
	profile.classList.toggle('active');
	navbar.classList.remove('active');
}

window.onscroll = () =>{
	navbar.classList.remove('active');
	profile.classList.remove('active');
}

function loader(){
	document.querySelector('.loader').style.display = 'none';
}

function fadeOut(){
	setInterval(loader, 2000);
}

window.onload = fadeOut();


// price, qty, total
function TotalCalculator(){
	var product_id = (document.getElementById("product_name").value);
	const price_id = 'price'+product_id;
	const qty_id = 'qty'+product_id;
	const total_id = 'total'+product_id;

	var price = parseFloat(document.getElementById(price_id).value);
	var qty  = parseFloat(document.getElementById(qty_id).value);
	var total = price * qty;
	document.getElementById(total_id).value = total;
}