from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import oracledb
app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("template.html", {"request": request})


@app.post("/subscribe")
async def subscribe(request: Request):
    form_data = await request.form()
    print(form_data)
    email = form_data["email"]
    cs = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-sanjose-1.oraclecloud.com))(connect_data=(service_name=g6587d1fcad5014_subxtwitter_medium.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"

    # Connect to Oracle database
    conn = oracledb.connect(user="ADMIN", password='Gnpw#0755#OC', dsn=cs)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = :email", email=email)
    count = cursor.fetchone()[0]

    if count > 0:
        print("The email already exists in the table.")
    else:
        id = "i/lists/1733652180576686386"
        expire_date = datetime.now() + timedelta(days=7)
        cursor.execute(
            "INSERT INTO users (email, target_id, mail_time, expire_date) VALUES (:email, :target_id, :mail_time, :expire_date)",
            email=email,
            target_id=id,
            mail_time=datetime.now(),
            expire_date=expire_date)
        conn.commit()
        print("The values have been inserted into the table.")

    conn.close()

    return "订阅成功！感谢您的订阅：" + email


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)