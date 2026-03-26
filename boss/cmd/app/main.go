package main

import (
	"boss/internal/fetcher/grpc"
	"boss/internal/fetcher/grpc/bosspb"
	"context"
	"log"
)

type ProjectGenerator struct{}

// GenerateProject генерирует ZIP архив с проектом
func (g *ProjectGenerator) GenerateProject(ctx context.Context, req *bosspb.TaskRequest) ([]byte, error) {
	log.Printf("Генерация проекта для пользователя %s, задача: %s", req.Username, req.Taskname)

	testData := []byte("Hello from boss service! Project: " + req.Title)

	log.Printf("Сгенерировано %d байт", len(testData))

	return testData, nil
}

func main() {
	generator := &ProjectGenerator{}

	if err := grpc.Start("50051", generator); err != nil {
		log.Fatalf("Ошибка запуска сервера: %v", err)
	}
}
