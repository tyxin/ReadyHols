const currentDate = document.querySelector(".current-date");
daysTag = document.querySelector(".days");
prevNextIcon = document.querySelectorAll(".icons span");
var strStartDate = document.getElementById("start_date").textContent;
var strEndDate = document.getElementById("end_date").textContent;

let date = new Date();
currYear = date.getFullYear();
currMonth = date.getMonth();

var processedStartDate = (strStartDate.split(" ")[2]).split("-");
const startDate = new Date(processedStartDate[0], parseInt(processedStartDate[1]) - 1, processedStartDate[2]); 
var processedEndDate = (strEndDate.toString().split(" ")[2]).split("-");
const endDate = new Date(processedEndDate[0], parseInt(processedEndDate[1]) - 1, processedEndDate[2]); 

console.log(startDate)
console.log(endDate)

const months = ["January","February","March","April","May","June","July",
                "August","September","October","November","December"];


const renderCalendar = () => {
    let firstDayOfMonth = new Date(currYear, currMonth,1).getDay();
    let lastDateOfMonth = new Date(currYear, currMonth + 1,0).getDate();
    let lastDateOfLastMonth = new Date(currYear, currMonth,0).getDate();
    let lastDayOfMonth = new Date(currYear, currMonth,lastDateOfMonth).getDay();
    let liTag = "";

    for (let i = firstDayOfMonth; i>0; i--){
        liTag += `<li class="inactive">${lastDateOfLastMonth -i + 1}</li>`;
    }

    for (let i = 1; i<= lastDateOfMonth; i++){
        let isToday = "";

        if ((i >= startDate.getDate() && currMonth==startDate.getMonth() && currYear==startDate.getFullYear()) 
            && (i <= endDate.getDate() && currMonth==endDate.getMonth() && currYear==endDate.getFullYear())){
            console.log("selected")
            isToday = "selected";
        }

        if (i == date.getDate()&&currMonth == new Date().getMonth() 
            && currYear == new Date().getFullYear()){
            isToday = "active";
        }

        liTag += `<li class="${isToday}">${i}</li>`;
    }

    for (let i = lastDayOfMonth; i< 6; i++){
        liTag += `<li class="inactive">${i - lastDayOfMonth + 1}</li>`;
    }

    console.log(liTag)

    currentDate.innerText = `${months[currMonth]} ${currYear}`;
    daysTag.innerHTML = liTag;
}

renderCalendar();

prevNextIcon.forEach(icon => {
    icon.addEventListener("click", () =>{
        if (icon.id == "month_prev"){
            currMonth = currMonth - 1;
        }
        if (icon.id == "month_next"){
            currMonth = currMonth + 1;
        }

        if (currMonth < 0 || currMonth > 11){
            date = new Date(currYear,currMonth);
            currYear = date.getFullYear();
            currMonth = date.getMonth();
        }else{
            date = new Date();
        }
        console.log(currMonth)
        renderCalendar();
    });
});
