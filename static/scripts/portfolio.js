

const pages = ["academic", "developer", "other"]

let currentPage = document.querySelector('.portfolio-page.current').id;
window.history.replaceState(document.title, "", document.location.href);
document.documentElement.className = currentPage;
let pageChangers = document.querySelectorAll('.page-changer');


function goToPage(target){
    console.log("goToPage: ", target);
    document.documentElement.className = target;
    window.history.pushState(document.title, "", document.location.href)
    const targetClass = ".page-"+target;
    const oldPage = currentPage
    currentPage = target;
    let targetelements = document.querySelectorAll(targetClass);
    targetelements.forEach((element) => {
        [...element.parentElement.children].forEach((elem) => {elem.classList.remove("current");});
        element.classList.add("current");
    })
    pageChangers.forEach((element) => {
        pages.forEach(page => {
            element.classList.remove(page);
        })
        element.classList.add(currentPage);

    })

    document.title = "Portfolio: " + currentPage;
    window.history.replaceState(document.title, "", "/portfolio/"+target);
}



window.addEventListener("popstate", () => {
    console.log(window.location.pathname);
    updatePage()
})

function updatePage() {
    let target = window.location.pathname.split("/")[2];
    if (target === undefined || target === "") {
        target = "academic"
    }
    goToPage(target);
}


updatePage();