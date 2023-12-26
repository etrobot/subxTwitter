package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"time"

	_ "github.com/godror/godror"
)

func indexHandler(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFiles("template.html")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = tmpl.Execute(w, nil)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func subscribeHandler(w http.ResponseWriter, r *http.Request) {
	email := r.FormValue("email")
	cs := "(DESCRIPTION=(RETRY_COUNT=20)(RETRY_DELAY=3)(ADDRESS=(PROTOCOL=TCPS)(PORT=1522)(HOST=adb.us-sanjose-1.oraclecloud.com))(CONNECT_DATA=(SERVICE_NAME=g6587d1fcad5014_subxtwitter_medium.adb.oraclecloud.com))(SECURITY=(SSL_SERVER_DN_MATCH=YES)))"

	// Connect to Oracle database
	db, err := sql.Open("godror", "ADMIN/Gnpw#0755#OC@"+cs)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	var count int
	err = db.QueryRow("SELECT COUNT(*) FROM users WHERE email = :email", sql.Named("email", email)).Scan(&count)
	if err != nil {
		log.Fatal(err)
	}

	if count > 0 {
		fmt.Println("The email already exists in the table.")
	} else {
		id := "i/lists/1733652180576686386"
		expireDate := time.Now().Add(7 * 24 * time.Hour)
		_, err := db.Exec("INSERT INTO users (email, target_id, mail_time, expire_date) VALUES (:email, :target_id, :mail_time, :expire_date)",
			sql.Named("email", email),
			sql.Named("target_id", id),
			sql.Named("mail_time", time.Now()),
			sql.Named("expire_date", expireDate),
		)
		if err != nil {
			log.Fatal(err)
		}
		fmt.Println("The values have been inserted into the table.")
	}

	fmt.Fprintf(w, "订阅成功！感谢您的订阅：%s", email)
}

func main() {
	http.HandleFunc("/", indexHandler)
	http.HandleFunc("/subscribe", subscribeHandler)

	http.ListenAndServe(":8080", nil)
}
