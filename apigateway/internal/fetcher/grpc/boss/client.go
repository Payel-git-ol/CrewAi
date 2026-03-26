package boss

import (
	"context"
	"fmt"

	"crewai/internal/fetcher/grpc/boss/bosspb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// Client — gRPC клиент для связи с boss сервисом
type Client struct {
	client bosspb.TaskServiceClient
	conn   *grpc.ClientConn
}

// NewClient создаёт подключение к boss сервису
func NewClient(address string) (*Client, error) {
	conn, err := grpc.Dial(
		address,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithDefaultCallOptions(
			grpc.MaxCallRecvMsgSize(100*1024*1024), // 100 MB
			grpc.MaxCallSendMsgSize(100*1024*1024),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to boss service: %w", err)
	}

	return &Client{
		client: bosspb.NewTaskServiceClient(conn),
		conn:   conn,
	}, nil
}

// Close закрывает соединение
func (c *Client) Close() error {
	return c.conn.Close()
}

// SendTask отправляет задачу в boss сервис и получает решение (ZIP архив)
func (c *Client) SendTask(ctx context.Context, username, taskname, title, description string, tokens []string, metadata map[string]string) (*bosspb.TaskResponse, error) {
	req := &bosspb.TaskRequest{
		Username:    username,
		Taskname:    taskname,
		Title:       title,
		Description: description,
		Tokens:      tokens,
		Metadata:    metadata,
	}

	resp, err := c.client.Task(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("task rpc failed: %w", err)
	}

	return resp, nil
}
