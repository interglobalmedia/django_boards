//Get the button
export const scrollTopButton = document.getElementById("btn-back-to-top");

export function scrollFunction() {
	if (
		document.body.scrollTop > 20 ||
		document.documentElement.scrollTop > 20
	) {
		scrollTopButton.style.display = "block";
	} else {
		scrollTopButton.style.display = "none";
	}
}

export function backToTop() {
	document.body.scrollTop = 0;
	document.documentElement.scrollTop = 0;
}