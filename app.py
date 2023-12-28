from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import oracledb
app = FastAPI()
templates = Jinja2Templates(directory="templates")
cs = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-sanjose-1.oraclecloud.com))(connect_data=(service_name=g6587d1fcad5014_subxtwitter_medium.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("template.html", {"request": request})


@app.post("/unsubscribe")
async def unsubscribe(email: str):
    conn = oracledb.connect(user="ADMIN", password='Gnpw#0755#OC', dsn=cs)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = :email", email=email)
    conn.commit()
    conn.close()
    return email+" Unsubscribed"

@app.post("/subscribe")
async def subscribe(request: Request):
    form_data = await request.form()
    print(form_data)
    email = form_data["email"]
    mail_time = datetime.utcfromtimestamp(int(form_data["mail_time"]))
    expire_date = datetime.now() + timedelta(days=7)

    # Connect to Oracle database
    conn = oracledb.connect(user="ADMIN", password='Gnpw#0755#OC', dsn=cs)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = :email", email=email)
    row = cursor.fetchone()

    if row is not None:
        expire_date = row[4]
        cursor.execute(
            "UPDATE users SET lang = :lang, target_id = :target_id, mail_time = :mail_time WHERE email = :email",
            target_id=form_data["target_id"],
            mail_time=mail_time,
            email=email,
            lang=form_data["current_language"]
        )
        conn.commit()
        print("The record has been updated.")
    else:
        cursor.execute("INSERT INTO users (email, target_id, mail_time, expire_date,lang) VALUES (:email, :target_id, :mail_time, :expire_date, :lang)",
            email=email,
            target_id=form_data["target_id"],
            mail_time=mail_time,
            expire_date=expire_date,
            lang=form_data["current_language"]
        )
        conn.commit()
        print("A new record has been inserted.")

    conn.close()

    return email+" Subscribed, Expire Date："+expire_date.strftime("%Y-%m-%d")+" Push Time:"+row[3]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)