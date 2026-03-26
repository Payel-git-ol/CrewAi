package create

import (
	"context"
	"crewai/internal/fetcher/grpc/boss/bosspb"
	"crewai/pkg/requests"
	"fmt"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func CreateGrpcResponse(req requests.TaskRequest) (*bosspb.TaskResponse, error) {
	conn, err := grpc.Dial(
		"localhost:50051",
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithDefaultCallOptions(
			grpc.MaxCallRecvMsgSize(100*1024*1024),
			grpc.MaxCallSendMsgSize(100*1024*1024),
		),
	)

	if err != nil {
		return nil, fmt.Errorf("failed to connect: %w", err)
	}

	defer conn.Close()

	client := bosspb.NewTaskServiceClient(conn)

	type result struct {
		resp *bosspb.TaskResponse
		err  error
	}

	chResult := make(chan result, 1)

	go func() {
		grpcRequest := &bosspb.TaskRequest{
			Username:    req.Username,
			Taskname:    req.TaskName,
			Title:       req.Title,
			Description: req.Description,
			Tokens:      req.Tokens,
			Metadata:    req.Meta,
		}

		resp, err := client.Task(context.Background(), grpcRequest)
		chResult <- result{resp: resp, err: err}
	}()

	r := <-chResult
	if r.err != nil {
		return nil, fmt.Errorf("task rpc failed: %w", r.err)
	}

	return r.resp, nil
}
