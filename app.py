import os
from datetime import datetime, timedelta
import requests
from fastapi import FastAPI, Request,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse,HTMLResponse
import httpx
from base64 import b64encode
from pydantic import BaseModel
import oracledb
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

cs = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-sanjose-1.oraclecloud.com))(connect_data=(service_name=g6587d1fcad5014_subxtwitter_medium.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"
favicon_path = 'favicon.ico'
PAYPAL_CLIENT_ID = os.environ['PAYPAL_CLIENT_ID']
PAYPAL_CLIENT_SECRET = os.environ['PAYPAL_CLIENT_SECRET']
base = "https://api-m.paypal.com"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class UserEmail(BaseModel):
    usermail: str

class AccessToken(BaseModel):
    access_token: str

@app.post("/api/orders")
async def create_order(usermail: UserEmail):
    try:
        access_token = await generate_access_token()
        url = f"{base}/v2/checkout/orders"
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": usermail.usermail,
                    "amount": {
                        "currency_code": "USD",
                        "value": "5.00",
                    },
                },
            ],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                json=payload,
            )

            order_data = await handle_response(response)
            order_id = order_data['jsonResponse'].get('id')  # Extract the order ID
            return {"id":order_id}# Return the order ID to the frontend

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create order.")

@app.post("/api/capture-paypal-order")
async def capture_paypal_order(request: Request):
    order_id_data = await request.json()
    try:
        orderID = order_id_data.get("orderID")  # Extract the orderID from the request data

        if not orderID:
            raise HTTPException(status_code=400, detail="Order ID is missing in the request.")

        access_token = await generate_access_token()
        url = f"{base}/v2/checkout/orders/{orderID}/capture"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
            )
            order_data = await handle_response(response)
            usermail=order_data['jsonResponse']['purchase_units'][0]["reference_id"]
            try:
                conn = oracledb.connect(user="ADMIN", password=os.environ['OCPWD'], dsn=cs)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = :email", email=usermail)
                row = cursor.fetchone()
                cursor.execute(
                    "UPDATE users SET expire_date = :expire_date WHERE email = :email",
                    expire_date=max(row[4], datetime.now()) + timedelta(days=90),
                )
                conn.commit()
                conn.close()
            except Exception as e:
                print(e)
            return order_data['jsonResponse']

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to capture order.")


async def generate_access_token():
    try:
        if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
            raise Exception("MISSING_API_CREDENTIALS")

        auth = b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
        url = f"{base}/v1/oauth2/token"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Basic {auth}",
                },
                data={"grant_type": "client_credentials"},
            )

            data = AccessToken(**response.json())
            return data.access_token

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate Access Token.")

async def handle_response(response):
    try:
        return {
            "jsonResponse": response.json(),
            "httpStatusCode": response.status_code,
        }
    except Exception as e:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

@app.get("/")
def index():
    return FileResponse(f"static/index.html")

@app.get("/lang/{lang}")
async def get_static_page(lang: str):
    try:
        return FileResponse(f"static/{lang}.html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Page not found")

@app.get("/pay", response_class=HTMLResponse)
async def pay(request: Request, email: str):
    return templates.TemplateResponse("pay.html", {"request": request, "usermail": email})

@app.get("/unsubscribe")
async def unsubscribe(email: str):
    conn = oracledb.connect(user="ADMIN", password=os.environ['OCPWD'], dsn=cs)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET unsub = :unsub WHERE email = :email", email=email, unsub=datetime.now(),)
    conn.commit()
    conn.close()
    return email+" Unsubscribed"

@app.post("/subscribe")
async def subscribe(request: Request):
    form_data = await request.form()
    print(form_data)
    nits = os.environ['NITTER'].split(';')
    nitter=None
    for site in nits:
        url = f"https://{site}/i/lists/{form_data['target_id']}/rss"
        response = requests.get(url)
        if response.status_code == 200:
            nitter = site
            break
    if nitter is None:
        return templates.TemplateResponse("base.html", {"request": request, "main": '<div class="w-full text-center m-4">%s</div>'%'❌ERROR: Not an Available List ID'})
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
        if row[5] is None:
            cursor.execute(
                "UPDATE users SET lang = :lang, target_id = :target_id, mail_time = :mail_time WHERE email = :email",
                target_id=form_data["target_id"],
                mail_time=mail_time,
                email=email,
                lang=form_data["current_language"]
            )
        elif row[4]-row[5]>0:
            expire_date=datetime.now()+timedelta(days=row[4]-row[5])
            cursor.execute(
                "UPDATE users SET lang = :lang, target_id = :target_id, mail_time = :mail_time, expire_date= :expire_date WHERE email = :email",
                target_id=form_data["target_id"],
                mail_time=mail_time,
                email=email,
                lang=form_data["current_language"],
                expire_date=expire_date
            )
        else:
            return templates.TemplateResponse("pay.html", {"request": request, "usermail": email})
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
    info = email+"<br>✅ Subscribed %s <br>daily push on Greenwich Mean Time (GMT) "%row[1]+row[3].strftime("%H:%M")+"<br>Expire Date："+expire_date.strftime("%Y/%m/%d")
    info = '<div class="w-full text-center m-4">%s</div>'%info
    return templates.TemplateResponse("base.html", {"request": request, "main": info})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)