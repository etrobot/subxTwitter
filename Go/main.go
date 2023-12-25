package main

import (
	"fmt"
	"html/template"
	"net/http"
)

func indexHandler(w http.ResponseWriter, r *http.Request) {
	// 解析模板文件
	tmpl, err := template.ParseFiles("template.html")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 渲染模板并发送给客户端
	err = tmpl.Execute(w, nil)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func subscribeHandler(w http.ResponseWriter, r *http.Request) {
	// 获取用户提交的订阅信息
	email := r.FormValue("email")

	// 执行订阅操作，例如将邮箱地址存储到数据库中或发送确认邮件

	// 返回响应给用户
	fmt.Fprintf(w, "订阅成功！感谢您的订阅：%s", email)
}

func main() {
	// 设置路由
	http.HandleFunc("/", indexHandler)
	http.HandleFunc("/subscribe", subscribeHandler)

	// 启动HTTP服务器，监听指定端口
	http.ListenAndServe(":8080", nil)
}
