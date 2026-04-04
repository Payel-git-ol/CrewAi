# PowerShell script to generate Go gRPC code from proto file

$PROTO_PATH = "proto/agents.proto"
$OUTPUT_DIR = "proto/pb"

Write-Host "🔨 Generating Go gRPC code from $PROTO_PATH..." -ForegroundColor Cyan

# Check if protoc is installed
if (-not (Get-Command protoc -ErrorAction SilentlyContinue)) {
    Write-Host "❌ protoc not found. Please install:" -ForegroundColor Red
    Write-Host "   1. protoc: https://github.com/protocolbuffers/protobuf/releases"
    Write-Host "   2. protoc-gen-go: go install google.golang.org/protobuf/cmd/protoc-gen-go@latest"
    Write-Host "   3. protoc-gen-go-grpc: go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest"
    exit 1
}

# Generate code
protoc -I proto --go_out=$OUTPUT_DIR --go-grpc_out=$OUTPUT_DIR $PROTO_PATH

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Go gRPC code generated successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to generate Go gRPC code" -ForegroundColor Red
    exit 1
}
