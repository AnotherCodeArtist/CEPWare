package main

import (
	"flag"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"strings"
)

func main() {
	strategy := flag.String("strategy", "normal", "generation strategy for data: normal, fire, failure")
	room := flag.Int("room", 1, "the room to which the data should be sent: 1 - 5")
	location := flag.String("location", "test", "where the data should be sent to: test, local, fh")
	flag.Parse()

	var url [5]string
	switch *location {
	case "test":
		url[0] = "https://httpbin.org/post"
		url[1] = "https://httpbin.org/post"
		url[2] = "https://httpbin.org/post"
		url[3] = "https://httpbin.org/post"
		url[4] = "https://httpbin.org/post"
	case "local":
		url[0] = "http://localhost:7896/iot/d?k=test&i=IoT-R1"
		url[1] = "http://localhost:7896/iot/d?k=test&i=IoT-R2"
		url[2] = "http://localhost:7896/iot/d?k=test&i=IoT-R3"
		url[3] = "http://localhost:7896/iot/d?k=test&i=IoT-R4"
		url[4] = "http://localhost:7896/iot/d?k=test&i=IoT-R5"
	case "fh":
		url[0] = "http://10.25.2.147:7896/iot/d?k=test&i=IoT-R1"
		url[1] = "http://10.25.2.147:7896/iot/d?k=test&i=IoT-R2"
		url[2] = "http://10.25.2.147:7896/iot/d?k=test&i=IoT-R3"
		url[3] = "http://10.25.2.147:7896/iot/d?k=test&i=IoT-R4"
		url[4] = "http://10.25.2.147:7896/iot/d?k=test&i=IoT-R5"
	}

	GenerateData(url[*room], *strategy)
}

func GenerateData(url string, strategy string) {
	switch strategy {
	case "normal":
		payload := "t|20"
		for {
			MakeRequest(url, payload)
		}
	case "fire":
		for i := 20; i < 50; i++ {
			payload := "t|" + strconv.Itoa(i)
			MakeRequest(url, payload)
		}
	case "failure":
		for i := 20; i < 100; i++ {
			payload := "t|" + strconv.Itoa(rand.Intn(i))
			MakeRequest(url, payload)
		}
	}
}

func MakeRequest(url string, payload string) {
	reader := strings.NewReader(payload)

	req, err := http.NewRequest("POST", url, reader)
	if err != nil {
		log.Fatalln(err)
	}
	req.Header.Set("Fiware-Service", "cepware")
	req.Header.Set("Content-Type", "text/plain")
	req.Header.Set("Fiware-ServicePath", "/rooms")

	client := &http.Client{}
	_, err = client.Do(req)
	if err != nil {
		log.Fatalln(err)
	}

	fmt.Println("Sent '" + payload + "' to " + url)
}
