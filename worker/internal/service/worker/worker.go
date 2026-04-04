package worker

import (
	"log"
	"os"
	"sync"

	"worker/internal/fetcher/grpc/workerpb"
	"worker/internal/service/agents"
)

// WorkerService — worker service
type WorkerService struct {
	workerpb.UnimplementedWorkerServiceServer
	agentsClient *agents.AgentClientWrapper
	mu           sync.Mutex
}

func NewWorkerService() *WorkerService {
	agentsHost := os.Getenv("AGENTS_SERVICE_HOST")
	if agentsHost == "" {
		agentsHost = "localhost:50053"
	}

	agentsClient, err := agents.NewAgentClientWrapper()
	if err != nil {
		log.Printf("Warning: failed to connect to agents service: %v", err)
	}

	return &WorkerService{
		agentsClient: agentsClient,
	}
}
