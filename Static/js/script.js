// Navbar scroll effect
const navbar = document.querySelector(".custom-navbar");

window.addEventListener("scroll", () => {
    if (window.scrollY > 60) {
        navbar.classList.add("scrolled");
    } else {
        navbar.classList.remove("scrolled");
    }
});

// Close mobile menu after clicking
const navLinks = document.querySelectorAll(".nav-link, .quote-btn");
const navbarCollapse = document.querySelector(".navbar-collapse");

navLinks.forEach((link) => {
    link.addEventListener("click", () => {
        if (navbarCollapse.classList.contains("show")) {
            new bootstrap.Collapse(navbarCollapse).hide();
        }
    });
});

// Back to top button
const topBtn = document.createElement("button");
topBtn.id = "topBtn";
topBtn.innerHTML = "↑";
document.body.appendChild(topBtn);

window.addEventListener("scroll", () => {
    topBtn.style.display = window.scrollY > 450 ? "block" : "none";
});

topBtn.addEventListener("click", () => {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});