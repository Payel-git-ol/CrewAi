# PowerShell script to generate gRPC code from proto file

$PROTO_PATH = "app/proto/agents.proto"
$OUTPUT_PATH = "app/proto"

Write-Host "🔨 Generating gRPC code from $PROTO_PATH..." -ForegroundColor Cyan

python -m grpc_tools.protoc `
    -I app/proto `
    --python_out=$OUTPUT_PATH `
    --grpc_python_out=$OUTPUT_PATH `
    $PROTO_PATH

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ gRPC code generated successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to generate gRPC code" -ForegroundColor Red
    exit 1
}
