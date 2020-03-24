package main

import (
	"log"
	"net/http"
	"time"

	"github.com/gorilla/mux"
)

const PORT = "9000"

func main() {
	router := mux.NewRouter()

	router.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("hi!"))
	})

	address := "0.0.0.0:" + PORT
	srv := &http.Server{
		Handler: router,
		Addr:    address,
		// Good practice: enforce timeouts for servers you create!
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}

	log.Printf("Running webserver on http://%s", address)
	log.Fatal(srv.ListenAndServe())
}
