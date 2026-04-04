package agents

import (
	"context"
	"fmt"
	"log"
	"os"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// AgentClientWrapper wraps the gRPC client to Agents service
type AgentClientWrapper struct {
	conn *grpc.ClientConn
}

// NewAgentClientWrapper creates a new gRPC client wrapper for Agents service
func NewAgentClientWrapper() (*AgentClientWrapper, error) {
	agentsHost := os.Getenv("AGENTS_SERVICE_HOST")
	if agentsHost == "" {
		agentsHost = "agents:50053"
	}

	log.Printf("🔗 [Worker] Connecting to Agents service at %s...", agentsHost)

	conn, err := grpc.Dial(
		agentsHost,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithDefaultCallOptions(
			grpc.MaxCallRecvMsgSize(100*1024*1024),
			grpc.MaxCallSendMsgSize(100*1024*1024),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to agents service: %w", err)
	}

	log.Printf("✅ [Worker] Connected to Agents service at %s", agentsHost)

	return &AgentClientWrapper{conn: conn}, nil
}

// Generate calls the Agents service to generate content via gRPC
func (w *AgentClientWrapper) Generate(ctx context.Context, provider, model, prompt string, tokens map[string]string, maxTokens int, temperature float64) (string, error) {
	log.Printf("🤖 [Worker] Calling Agents service (provider=%s, model=%s) via gRPC", provider, model)

	// TODO: Implement actual gRPC call once proto stubs are generated
	// See: AGENTS_MIGRATION_STATUS.md for instructions

	return "", fmt.Errorf("Agents gRPC client stubs not yet generated. See AGENTS_MIGRATION_STATUS.md")
}

// Close closes the gRPC connection
func (w *AgentClientWrapper) Close() error {
	if w.conn != nil {
		log.Printf("🔌 [Worker] Closing connection to Agents service")
		return w.conn.Close()
	}
	return nil
}
