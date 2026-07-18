import json

def generate_report(data):

    data = data

    categories = list(data["salary"].keys())


    html = f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">

    <head>

    <meta charset="UTF-8">

    <title>Job Market Analytics</title>


    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>


    <style>

    * {{
        box-sizing:border-box;
        font-family:Tahoma, Arial;
    }}


    body {{
        margin:0;
        background:#f5f7fb;
        color:#222;
    }}


    .sidebar {{

        width:260px;
        height:100vh;
        position:fixed;
        right:0;
        top:0;

        background:#111827;
        padding:25px;

    }}


    .sidebar h2 {{

        color:white;
        text-align:center;

    }}


    .sidebar button {{

        width:100%;
        margin:8px 0;
        padding:12px;

        border:none;
        border-radius:10px;

        background:#1f2937;
        color:white;

        cursor:pointer;

    }}


    .sidebar button:hover {{

        background:#3758f9;

    }}



    .content {{

        margin-right:280px;
        padding:30px;

    }}



    .card {{

        background:white;
        padding:20px;

        border-radius:18px;

        box-shadow:
        0 5px 20px rgba(0,0,0,.08);

        margin-bottom:20px;

    }}



    .grid {{

        display:grid;
        grid-template-columns:
        repeat(auto-fit,minmax(250px,1fr));

        gap:20px;

    }}



    .number {{

        font-size:35px;
        font-weight:bold;
        color:#3758f9;

    }}



    .category {{

    display:none;

    }}


    .active {{

    display:block;

    }}


    canvas {{

    max-height:300px;

    }}

    </style>


    </head>


    <body>



    <div class="sidebar">

    <h2>
    📊 Job Analytics
    </h2>


    """


    for i,cat in enumerate(categories):

        html += f"""
        <button onclick="showCategory('{i}')">
        {cat}
        </button>
        """


    html += """

    </div>



    <div class="content">

    """


    for i,cat in enumerate(categories):

        salary=data["salary"][cat]
        remote=data["remote"][cat]
        gender=data["gender"][cat]
        work=data["work_type"][cat]
        exp=data["experience"][cat]


        html += f"""

    <div id="{i}" class="category {'active' if i==0 else ''}">


    <h1>
    {cat}
    </h1>


    <div class="grid">


    <div class="card">
    <h3>تعداد آگهی</h3>
    <div class="number">
    {salary['total_jobs']}
    </div>
    </div>



    <div class="card">
    <h3>آگهی دارای حقوق</h3>

    <div class="number">
    {salary['jobs_with_salary']}
    </div>

    </div>



    <div class="card">

    <h3>میانگین حقوق</h3>

    <div class="number">

    {salary['average_salary']}

    میلیون

    </div>

    </div>


    </div>



    <div class="card">

    <h3>
    دورکاری و حضوری
    </h3>

    <canvas id="remote{i}"></canvas>

    </div>




    <div class="card">

    <h3>
    جنسیت
    </h3>

    <canvas id="gender{i}"></canvas>

    </div>




    <div class="card">

    <h3>
    نوع همکاری
    </h3>


    <canvas id="work{i}"></canvas>


    </div>




    <div class="card">

    <h3>
    تجربه کاری
    </h3>


    <canvas id="exp{i}"></canvas>


    </div>


    </div>


    """


    html += """

    </div>


    <script>


    function showCategory(id){


    document
    .querySelectorAll('.category')
    .forEach(x=>x.classList.remove('active'));


    document
    .getElementById(id)
    .classList.add('active');


    }


    """


    for i,cat in enumerate(categories):

        remote=data["remote"][cat]


        html += f"""

    new Chart(
    document.getElementById('remote{i}'),
    {{
    type:'doughnut',

    data:{{
    labels:[
    'دورکاری',
    'حضوری'
    ],

    datasets:[{{
    data:[
    {remote['remote']['count']},
    {remote['onsite']['count']}
    ]
    }}]

    }}

    }}
    );



    """


        gender=data["gender"][cat]["gender_distribution"]


        html += f"""

    new Chart(
    document.getElementById('gender{i}'),
    {{
    type:'bar',

    data:{{
    labels:{list(gender.keys())},

    datasets:[{{
    label:'تعداد',
    data:{list(gender.values())}
    }}]

    }}

    }}
    );

    """


        work=data["work_type"][cat]


        html += f"""

    new Chart(
    document.getElementById('work{i}'),
    {{
    type:'bar',

    data:{{
    labels:{list(work.keys())},

    datasets:[{{
    label:'تعداد',
    data:{[x['count'] for x in work.values()]}
    }}]

    }}

    }}
    );

    """


        exp=data["experience"][cat]


        html += f"""

    new Chart(
    document.getElementById('exp{i}'),
    {{
    type:'line',

    data:{{
    labels:{list(exp.keys())},

    datasets:[{{
    label:'تعداد آگهی',
    data:{[x['count'] for x in exp.values()]}
    }}]

    }}

    }}
    );


    """


    html += """

    </script>


    </body>

    </html>

    """


    with open(
        "report.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)


    print("Report created successfully")
