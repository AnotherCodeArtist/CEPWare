/*
 * Copyright (c) 2018 CEPWare-Team (GregorFernbach, heiderst16, sweiland)
 * For licensing information see LICENSE
 */

// package for data-generator for CEPWare
package main

import (
	"flag"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"strings"
	"time"
)

func main() {
	// define command line flags and add default values
	strategy := flag.String("strategy", "normal", "generation strategy for data: normal, fire, failure")
	location := flag.String("location", "test", "where the data should be sent to: test, local, fh")
	flag.Parse()

	// react to "location" flag
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
		url[0] = "http://10.25.2.146:7896/iot/d?k=test&i=IoT-R1"
		url[1] = "http://10.25.2.146:7896/iot/d?k=test&i=IoT-R2"
		url[2] = "http://10.25.2.146:7896/iot/d?k=test&i=IoT-R3"
		url[3] = "http://10.25.2.146:7896/iot/d?k=test&i=IoT-R4"
		url[4] = "http://10.25.2.146:7896/iot/d?k=test&i=IoT-R5"
	}

	// react to "room" and "strategy" flags
	GenerateData(url, *strategy)
}

// function that generates data in UL2.0 format based on a strategy
func GenerateData(url [5]string, strategy string) {
	switch strategy {
	case "normal":
		payload := "t|20"
		for {
			for r := 0; r < 5; r++ {
				MakeRequest(url[r], payload)
			}
		}
	case "fire":
		for i := 20; i < 50; i++ {
			payload := "t|" + strconv.Itoa(i)
			for r := 0; r < 5; r++ {
				MakeRequest(url[r], payload)
			}
		}
		for {
			payload := "t|50"
			for r := 0; r < 5; r++ {
				MakeRequest(url[r], payload)
			}
		}
	case "failure":
		for i := 20; i < 100; i++ {
			payload := "t|" + strconv.Itoa(rand.Intn(i))
			for r := 0; r < 5; r++ {
				MakeRequest(url[r], payload)
			}
		}
		for {
			payload := "t|" + strconv.Itoa(rand.Intn(100))
			for r := 0; r < 5; r++ {
				MakeRequest(url[r], payload)
			}
		}
	}
}

// function that sends out data to an URL
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
	time.Sleep(200 * time.Millisecond)
}
