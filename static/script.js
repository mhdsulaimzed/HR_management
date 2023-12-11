function DisplayEmployeeDetails(data) {
  console.log("display");

  let htmlDATA = `<div class="card mb-3" style="border-radius: .5rem;">
<div class="row g-0">
  <div class="col-md-4 gradient-custom text-center text-white"
    style="border-top-left-radius: .5rem; border-bottom-left-radius: .5rem;">
    <img src="https://cdn.pixabay.com/photo/2014/03/25/16/32/user-297330_1280.png"
      alt="Avatar" class="img-fluid my-5" style="width: 80px;" />
    <h5>${data.user.fname} ${data.user.lname}</h5>
    <p>${data.user.title}</p>
    <i class="far fa-edit mb-5"></i>
  </div>
  <div class="col-md-8">
    <div class="card-body p-4">
      <h6>Employee Details</h6>
      <hr class="mt-0 mb-4">
      <div class="row pt-1">
        <div class="col-2 mb-3">
            <h6>ID</h6>
            <p class="text-muted">${data.user.id}</p>
          </div>
        <div class="col-5 mb-3">
          <h6>Email</h6>
          <p class="text-muted">${data.user.email}</p>
        </div>
        <div class="col-5 mb-3">
          <h6>Phone</h6>
          <p class="text-muted">${data.user.phone}</p>
        </div>
      </div>
      <h6>Leaves</h6>
      <hr class="mt-0 mb-4">
      <div class="row pt-1">
        <div class="col-4 mb-3">
          <h6>Leave taken</h6>
          <p class="text-muted">${data.user.leave_taken}</p>
        </div>
        <div class="col-4 mb-3">
          <h6>Leave remaining</h6>
          <p class="text-muted">${data.user.max_leaves - data.user.leave_taken}</p>
        </div>
        <div class="col-4 mb-3">
          <h6>Maximum Leave</h6>
          <p class="text-muted">${data.user.max_leaves}</p>
        </div>
      </div>
      <div class="row pt-1 d-flex justify-content-around">
          <div class="col-4 text-center"><a onclick="FetchEmployeeDetails(${data.user.id - 1})" href="" class="btn btn-outline-warning">&lt;</a></div>
          <div class="col-4 text-center"><a onclick="FetchEmployeeDetails(${data.user.id + 1})" href="" class="btn btn-outline-warning"> &gt; </a></div>
      </div>
                                
      
    </div>
  </div>
</div>
</div>`


  document.querySelector("#id_display_det").innerHTML = htmlDATA

  AddLeaveForm(data.user.id, data.user.fname)
  searchForm()

}

function AddLeaveForm(id, name) {


  var htmlDATA2 = `<div class="card">
    <div class="card-body">
      <form action="/leave/${id}" method="post">
        <h4>Add Leaves for ${id} ${name}</h4>
        
        <input class="form-control mt-5" type="date" name="date" required>
        <textarea placeholder="Reason" class="form-control mt-5 " name="reason" id="" cols="30" rows="4"></textarea>

        <button class=" btn btn-danger form-control mt-5" type="submit" >Add</button>
      </form>
    </div>
  </div>`;

  $("#leave_form").html(htmlDATA2);
}



function FetchEmployeeDetails(id) {
  event.preventDefault()
  console.log(id);
  fetch(`http://127.0.0.1:5000/employee/${id}`).then(res => res.json()).then(data => DisplayEmployeeDetails(data)).catch(error => {
    notFound(id)

  });
}
function notFound(id) {
  let htmlData4 = `<p style="text-align: center;">Employee not found</p>`
  document.getElementById("not_found").innerHTML = htmlData4
}

function searchForm() {
  const htmlData3 = `
    <div class="card">
      <div class="card-body">
        <h4 class="mt-4 text-center">Search Employees by ID</h4>

        <form id="searchEmployeeForm" class="mt-4">
          <label for="employee_id" class="form-label">Employee ID:</label>
          <input type="text" id="employee_id" name="employee_id" class="form-control" required>
          <button type="submit" class="btn btn-primary mt-3">Search</button>
        </form>

      </div>
    </div>`;

  document.querySelector("#search_form").innerHTML = htmlData3;
  document.getElementById('searchEmployeeForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const id = document.getElementById('employee_id').value;

    FetchEmployeeDetails(id);
    // location.reload()
  });
}


// news api calling




function fetchNews() {
  event.preventDefault();

  fetch("https://newsapi.org/v2/top-headlines?country=in&apiKey=18b13ca2388148a0a6d7f426c124eeb3&category=technology")
    .then(res => {
      if (!res.ok) {
        throw new Error(`Network response was not ok: ${res.status}`);
      }
      return res.json();
    })
    .then(data => displayNews(data))
    .catch(error => console.error('Error:', error));
}


function displayNews(news) {
  console.log("display");
  let htmlData = ``
  for (let a of news.articles) {
    let image = a.image
    let author = a.author
    let dis = a.description
    let urlimage = a.urlToImage
    let content = a.content
    let date = a.publishedAt
    let title = a.title
    let source = a.source.name


    htmlData += ` 
    <div class="col-6 mr-3">
        <div class="card mt-4" style="width: 40rem;">
          <img src="${urlimage || 'https://www.unfe.org/wp-content/uploads/2019/04/SM-placeholder.png'}" class="card-img-top" alt="...">
          <div class="card-body">
            <h5 class="card-title">${title}</h5>
            <p class="card-text">${author || "unknown author"}.</p>
            <p class="card-text">${dis || "No discription"}.</p>
            <p class="card-text">${date}.</p>
            <p class="card-text"><i> - ${source}</i></p>
          </div>
      </div>
    </div>
      
      `
  }
  document.querySelector("#id_news").innerHTML = htmlData

}



document.getElementById('news_btn').addEventListener('click', fetchNews);


  document.addEventListener('DOMContentLoaded', function() {
    var anchors = document.querySelectorAll('a');

    anchors.forEach(function(anchor) {
      anchor.addEventListener('click', function(event) {
        
        anchors.forEach(function(a) {
          a.classList.remove('highlight');
        });

        
        this.classList.add('highlight');
      });
    });
  });




