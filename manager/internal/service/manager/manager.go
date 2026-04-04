package manager

import (
	"log"
	"manager/internal/fetcher/grpc/managerpb"
	"manager/internal/fetcher/grpc/worker"
	"manager/internal/service/agents"
	"os"
)

// ManagerService — сервис менеджеров
type ManagerService struct {
	managerpb.UnimplementedManagerServiceServer
	workerClient *worker.Client
	agentsClient *agents.AgentClientWrapper
}

func NewManagerService() *ManagerService {
	wClient, err := worker.NewClient(os.Getenv("WORKER_SERVICE_HOST"))
	if err != nil {
		log.Printf("Warning: failed to connect to worker service: %v", err)
	}

	agentsHost := os.Getenv("AGENTS_SERVICE_HOST")
	if agentsHost == "" {
		agentsHost = "localhost:50053"
	}
	aClient, err := agents.NewAgentClientWrapper()
	if err != nil {
		log.Printf("Warning: failed to connect to agents service: %v", err)
	}

	return &ManagerService{
		workerClient: wClient,
		agentsClient: aClient,
	}
}
