# RAG Multi-Agent QA System - Development Environment Management Script (PowerShell Version)

# Color definitions
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$Cyan = "Cyan"

# Show help information
function Show-Help {
    Write-Host "🚀 RAG Multi-Agent QA System - Development Environment Management Script" -ForegroundColor $Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor $Blue
    Write-Host "  .\dev.ps1 [command] [options]"
    Write-Host ""
    Write-Host "Common Commands:" -ForegroundColor $Blue
    Write-Host "  up         Start all services"
    Write-Host "  down       Stop all services"
    Write-Host "  down -v    Stop all services and remove volumes"
    Write-Host "  restart    Restart all services"
    Write-Host "  logs       View service logs"
    Write-Host "  ps         Check service status"
    Write-Host "  build      Rebuild services"
    Write-Host "  exec       Enter container (e.g., .\dev.ps1 exec rag-app bash)"
    Write-Host "  setup      Initial setup (create directories, download models)"
    Write-Host "  help       Show this help information"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor $Blue
    Write-Host "  .\dev.ps1 up -d          # Start services in background"
    Write-Host "  .\dev.ps1 down -v        # Stop services and cleanup"
    Write-Host "  .\dev.ps1 logs -f        # Follow logs"
    Write-Host "  .\dev.ps1 exec rag-app bash  # Enter app container"
}

# Create necessary directories
function New-Directories {
    Write-Host "📁 Creating necessary directories..." -ForegroundColor $Blue
    $directories = @(
        "data/vector_store",
        "data/uploads", 
        "data/workspace",
        "data/ollama",
        "data/logs"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "Created: $dir" -ForegroundColor $Green
        } else {
            Write-Host "Exists: $dir" -ForegroundColor $Yellow
        }
    }
    Write-Host "✅ Directory creation completed" -ForegroundColor $Green
}

# Check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Initial setup
function Initialize-Environment {
    Write-Host "🔧 Performing initial setup..." -ForegroundColor $Blue
    
    if (!(Test-Docker)) {
        Write-Host "❌ Docker is not running, please start Docker Desktop first" -ForegroundColor $Red
        return
    }
    
    New-Directories
    
    # Start services
    Write-Host "🔨 Starting services..." -ForegroundColor $Blue
    docker compose -f compose.dev.yml up -d
    
    # Wait for services to start
    Write-Host "⏳ Waiting for services to start..." -ForegroundColor $Blue
    Start-Sleep -Seconds 10
    
    # Check service status
    Write-Host "📊 Checking service status..." -ForegroundColor $Blue
    docker compose -f compose.dev.yml ps
    
    # Model download prompt
    Write-Host ""
    Write-Host "🤖 Model Download (Required Step):" -ForegroundColor $Yellow
    Write-Host "   Choose a model suitable for your laptop:" -ForegroundColor $Yellow
    Write-Host "   - Lightweight (2-4GB RAM): gemma:2b, phi:2.7b" -ForegroundColor $Yellow
    Write-Host "   - Medium (4-6GB RAM): llama2:7b:q4_0, mistral:7b:q4_0" -ForegroundColor $Yellow
    Write-Host "   - Standard (6GB+ RAM): llama2:7b, mistral:7b" -ForegroundColor $Yellow
    Write-Host ""
    
    # Ask user to select model
    $MODEL_NAME = Read-Host "Please enter the model name to download (press Enter for default gemma:2b)"
    
    # If user didn't input, use default lightweight model
    if ([string]::IsNullOrWhiteSpace($MODEL_NAME)) {
        $MODEL_NAME = "gemma:2b"
        Write-Host "🤖 Using default model: $MODEL_NAME (suitable for laptop environment)" -ForegroundColor $Green
    }
    
    Write-Host "📥 Downloading model: $MODEL_NAME" -ForegroundColor $Blue
    docker exec rag-multiagent-qa-ollama-1 ollama pull $MODEL_NAME
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Model download completed!" -ForegroundColor $Green
    } else {
        Write-Host "❌ Model download failed, please check network connection or model name" -ForegroundColor $Red
        Write-Host "💡 You can manually execute later: docker exec rag-multiagent-qa-ollama-1 ollama pull gemma:2b" -ForegroundColor $Yellow
    }
    
    Show-AccessInfo
}

# Show access information
function Show-AccessInfo {
    Write-Host ""
    Write-Host "✅ Development environment startup completed!" -ForegroundColor $Green
    Write-Host ""
    Write-Host "🌐 Access Addresses:" -ForegroundColor $Blue
    Write-Host "   - Web Interface: http://localhost:8501" -ForegroundColor $Blue
    Write-Host "   - Ollama Service: http://localhost:11434" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "🔧 Development Commands:" -ForegroundColor $Blue
    Write-Host "   - Enter Container: .\dev.ps1 exec rag-app bash" -ForegroundColor $Blue
    Write-Host "   - View Logs: .\dev.ps1 logs -f" -ForegroundColor $Blue
    Write-Host "   - Restart Services: .\dev.ps1 restart" -ForegroundColor $Blue
    Write-Host "   - Stop Services: .\dev.ps1 down" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "📝 Notes:" -ForegroundColor $Blue
    Write-Host "   - Code changes will automatically reload" -ForegroundColor $Blue
    Write-Host "   - You can use git commands directly in the container" -ForegroundColor $Blue
    Write-Host "   - All development operations are performed in the container" -ForegroundColor $Blue
    Write-Host "   - Supports complete version control operations" -ForegroundColor $Blue
}

# Main execution logic
if ($args.Count -eq 0) {
    Show-Help
} elseif ($args[0] -eq "setup") {
    Initialize-Environment
} elseif ($args[0] -eq "help" -or $args[0] -eq "-h" -or $args[0] -eq "--help") {
    Show-Help
} elseif ($args[0] -eq "exec") {
    if ($args.Count -lt 2) {
        Write-Host "❌ Please specify the command to execute, e.g., .\dev.ps1 exec rag-app bash" -ForegroundColor $Red
    } else {
        $execArgs = $args[1..($args.Count-1)]
        docker compose -f compose.dev.yml exec $execArgs
    }
} else {
    # Check if Docker is running for other commands
    if (!(Test-Docker)) {
        Write-Host "❌ Docker is not running, please start Docker Desktop first" -ForegroundColor $Red
    } else {
        # Pass all arguments to docker compose
        Write-Host "🔧 Executing command: docker compose -f compose.dev.yml $args" -ForegroundColor $Blue
        docker compose -f compose.dev.yml $args
    }
}
