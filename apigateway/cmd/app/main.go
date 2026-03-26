package main

import (
	"crewai/internal/fetcher"
	"github.com/Payel-git-ol/azure"
	"log"
)

func main() {
	a := azure.Defoult
	fetcher.HttpManager(a)

	if err := a.Run("3111"); err != nil {
		log.Fatal("HTTP server error:", err)
	}
}
