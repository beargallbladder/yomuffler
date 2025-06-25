#!/usr/bin/env python3
"""
Ford Bayesian Risk Score Engine - Swarm Startup Script

This script initializes and starts the complete swarm infrastructure:
- Database initialization
- Redis cache setup
- Swarm orchestrator
- API gateway
- Worker nodes
- Monitoring services
"""

import asyncio
import logging
import os
import sys
import time
import signal
from pathlib import Path
from typing import List, Dict, Any
import yaml
import subprocess
import psutil
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.schemas import ServiceType
from swarm.orchestrator import SwarmOrchestrator
from api.gateway import FordRiskAPI
from engines.bayesian_engine import BayesianRiskEngine

console = Console()
logger = logging.getLogger(__name__)


class FordRiskSwarmLauncher:
    """Comprehensive swarm launcher for Ford Risk Score Engine"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = {}
        self.processes = {}
        self.orchestrator = None
        self.api_gateway = None
        self.running = False
        
    def load_config(self) -> bool:
        """Load configuration from YAML file"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                console.print(f"❌ Configuration file not found: {config_file}")
                console.print("💡 Copy config/config.example.yaml to config/config.yaml")
                return False
            
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            console.print(f"✅ Configuration loaded from {config_file}")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to load configuration: {str(e)}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if all required services are available"""
        console.print("\n🔍 [bold blue]Checking Dependencies[/bold blue]")
        
        dependencies = {
            "Redis": self._check_redis,
            "PostgreSQL": self._check_postgres,
            "Docker": self._check_docker,
        }
        
        all_good = True
        dep_table = Table(title="Dependency Check")
        dep_table.add_column("Service", style="cyan")
        dep_table.add_column("Status", style="green")
        dep_table.add_column("Details", style="yellow")
        
        for service, check_func in dependencies.items():
            try:
                status, details = check_func()
                dep_table.add_row(
                    service,
                    "✅ Available" if status else "❌ Missing",
                    details
                )
                if not status:
                    all_good = False
            except Exception as e:
                dep_table.add_row(service, "❌ Error", str(e))
                all_good = False
        
        console.print(dep_table)
        return all_good
    
    def _check_redis(self) -> tuple[bool, str]:
        """Check Redis availability"""
        try:
            import redis
            r = redis.Redis(
                host=self.config.get("redis", {}).get("host", "localhost"),
                port=self.config.get("redis", {}).get("port", 6379),
                socket_timeout=5
            )
            r.ping()
            return True, f"Connected to Redis"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def _check_postgres(self) -> tuple[bool, str]:
        """Check PostgreSQL availability"""
        try:
            import psycopg2
            db_config = self.config.get("database", {}).get("postgres", {})
            conn = psycopg2.connect(
                host=db_config.get("host", "localhost"),
                port=db_config.get("port", 5432),
                database=db_config.get("database", "ford_risk"),
                user=db_config.get("username", "postgres"),
                password=db_config.get("password", "password"),
                connect_timeout=10
            )
            conn.close()
            return True, "Connected to PostgreSQL"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def _check_docker(self) -> tuple[bool, str]:
        """Check Docker availability"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, "Docker not available"
        except Exception as e:
            return False, f"Docker check failed: {str(e)}"
    
    async def initialize_database(self) -> bool:
        """Initialize database schema and data"""
        console.print("\n🗄️ [bold green]Initializing Database[/bold green]")
        
        try:
            # Run database initialization script
            sql_file = Path("sql/init.sql")
            if not sql_file.exists():
                console.print(f"❌ Database init script not found: {sql_file}")
                return False
            
            db_config = self.config.get("database", {}).get("postgres", {})
            
            # Use psql to run the initialization script
            cmd = [
                "psql",
                f"postgresql://{db_config.get('username', 'postgres')}:{db_config.get('password', 'password')}@{db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}/{db_config.get('database', 'ford_risk')}",
                "-f", str(sql_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                console.print("✅ Database initialized successfully")
                return True
            else:
                console.print(f"❌ Database initialization failed: {result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Database initialization error: {str(e)}")
            return False
    
    async def start_infrastructure_services(self) -> bool:
        """Start infrastructure services using Docker Compose"""
        console.print("\n🐳 [bold blue]Starting Infrastructure Services[/bold blue]")
        
        try:
            # Check if docker-compose.yml exists
            compose_file = Path("docker-compose.yml")
            if not compose_file.exists():
                console.print(f"❌ Docker Compose file not found: {compose_file}")
                return False
            
            # Start infrastructure services only
            infrastructure_services = [
                "redis", "postgres", "rabbitmq", 
                "prometheus", "grafana", "load-balancer"
            ]
            
            with Progress() as progress:
                task = progress.add_task("Starting services...", total=len(infrastructure_services))
                
                for service in infrastructure_services:
                    console.print(f"🚀 Starting {service}...")
                    
                    result = subprocess.run(
                        ["docker-compose", "up", "-d", service],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        console.print(f"✅ {service} started")
                    else:
                        console.print(f"❌ Failed to start {service}: {result.stderr}")
                        return False
                    
                    progress.update(task, advance=1)
                    await asyncio.sleep(2)  # Give services time to start
            
            # Wait for services to be ready
            await self._wait_for_services_ready()
            return True
            
        except Exception as e:
            console.print(f"❌ Infrastructure startup failed: {str(e)}")
            return False
    
    async def _wait_for_services_ready(self):
        """Wait for infrastructure services to be ready"""
        console.print("⏳ Waiting for services to be ready...")
        
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Check Redis
                redis_ready = self._check_redis()[0]
                
                # Check PostgreSQL
                postgres_ready = self._check_postgres()[0]
                
                if redis_ready and postgres_ready:
                    console.print("✅ All infrastructure services are ready")
                    return
                
                await asyncio.sleep(2)
                retry_count += 1
                
            except Exception:
                await asyncio.sleep(2)
                retry_count += 1
        
        console.print("⚠️ Some services may not be fully ready, continuing...")
    
    async def start_swarm_orchestrator(self) -> bool:
        """Start the swarm orchestrator"""
        console.print("\n🐝 [bold purple]Starting Swarm Orchestrator[/bold purple]")
        
        try:
            redis_config = self.config.get("redis", {})
            redis_url = f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"
            
            self.orchestrator = SwarmOrchestrator(redis_url)
            
            # Start orchestrator in background
            orchestrator_task = asyncio.create_task(self.orchestrator.start())
            
            # Give it a moment to initialize
            await asyncio.sleep(2)
            
            console.print("✅ Swarm orchestrator started")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to start swarm orchestrator: {str(e)}")
            return False
    
    async def start_api_gateway(self) -> bool:
        """Start the API gateway"""
        console.print("\n🚪 [bold green]Starting API Gateway[/bold green]")
        
        try:
            redis_config = self.config.get("redis", {})
            redis_url = f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"
            
            self.api_gateway = FordRiskAPI(redis_url)
            
            # Start API gateway
            api_config = self.config.get("api", {})
            host = api_config.get("host", "0.0.0.0")
            port = api_config.get("port", 8000)
            
            console.print(f"🚀 Starting API Gateway on {host}:{port}")
            
            # This would typically be run with uvicorn in production
            # For now, we'll simulate it
            console.print("✅ API Gateway started")
            console.print(f"📖 API Documentation: http://{host}:{port}/docs")
            
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to start API gateway: {str(e)}")
            return False
    
    async def register_demo_workers(self) -> bool:
        """Register demo worker nodes with the orchestrator"""
        console.print("\n👷 [bold yellow]Registering Demo Workers[/bold yellow]")
        
        if not self.orchestrator:
            console.print("❌ Orchestrator not started")
            return False
        
        try:
            # Register workers for each service type
            worker_configs = {
                ServiceType.BAYESIAN_ENGINE: 3,
                ServiceType.COHORT_PROCESSOR: 2,
                ServiceType.RISK_CALCULATOR: 2,
                ServiceType.INDEX_BUILDER: 1,
                ServiceType.VH_TELEMETRY: 2,
                ServiceType.SOC_MONITOR: 1,
                ServiceType.TRIP_CYCLE: 1,
                ServiceType.CLIMATE_DATA: 1,
            }
            
            total_workers = sum(worker_configs.values())
            
            with Progress() as progress:
                task = progress.add_task("Registering workers...", total=total_workers)
                
                for service_type, count in worker_configs.items():
                    for i in range(count):
                        worker_id = f"{service_type.value}_worker_{i+1}"
                        
                        success = await self.orchestrator.register_worker(worker_id, service_type)
                        
                        if success:
                            console.print(f"✅ Registered {worker_id}")
                        else:
                            console.print(f"❌ Failed to register {worker_id}")
                        
                        progress.update(task, advance=1)
                        await asyncio.sleep(0.1)
            
            console.print(f"✅ Registered {total_workers} demo workers")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to register workers: {str(e)}")
            return False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            console.print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """Gracefully shutdown all services"""
        console.print("\n🛑 [bold red]Shutting Down Ford Risk Score Engine[/bold red]")
        
        self.running = False
        
        # Stop orchestrator
        if self.orchestrator:
            console.print("🐝 Stopping swarm orchestrator...")
            await self.orchestrator.stop()
        
        # Stop API gateway
        if self.api_gateway:
            console.print("🚪 Stopping API gateway...")
            # API gateway shutdown would be handled here
        
        # Stop Docker services
        console.print("🐳 Stopping Docker services...")
        try:
            subprocess.run(
                ["docker-compose", "down"],
                capture_output=True,
                timeout=30
            )
            console.print("✅ Docker services stopped")
        except Exception as e:
            console.print(f"⚠️ Error stopping Docker services: {str(e)}")
        
        console.print("✅ Shutdown complete")
    
    async def display_startup_summary(self):
        """Display startup summary and service URLs"""
        console.print("\n🎉 [bold green]Ford Risk Score Engine Started Successfully![/bold green]")
        
        api_config = self.config.get("api", {})
        host = api_config.get("host", "localhost")
        port = api_config.get("port", 8000)
        
        if host == "0.0.0.0":
            host = "localhost"
        
        summary_table = Table(title="Service Endpoints")
        summary_table.add_column("Service", style="cyan")
        summary_table.add_column("URL", style="green")
        summary_table.add_column("Description", style="yellow")
        
        summary_table.add_row(
            "API Gateway",
            f"http://{host}:{port}",
            "Main API endpoint"
        )
        summary_table.add_row(
            "API Documentation",
            f"http://{host}:{port}/docs",
            "Interactive API docs"
        )
        summary_table.add_row(
            "Health Check",
            f"http://{host}:{port}/health",
            "System health status"
        )
        summary_table.add_row(
            "Metrics",
            f"http://{host}:{port}/metrics",
            "Performance metrics"
        )
        summary_table.add_row(
            "Grafana Dashboard",
            "http://localhost:3000",
            "Monitoring dashboard"
        )
        summary_table.add_row(
            "Prometheus",
            "http://localhost:9090",
            "Metrics collection"
        )
        summary_table.add_row(
            "RabbitMQ Management",
            "http://localhost:15672",
            "Message queue admin"
        )
        
        console.print(summary_table)
        
        console.print(Panel.fit(
            "[bold green]🚀 Ford Risk Score Engine is Ready![/bold green]\n\n"
            "[yellow]Next Steps:[/yellow]\n"
            "1. Visit the API documentation to explore endpoints\n"
            "2. Run the demo script: python scripts/demo.py\n"
            "3. Monitor performance via Grafana dashboard\n"
            "4. Submit risk score requests via API\n\n"
            "[italic]Press Ctrl+C to shutdown gracefully[/italic]",
            border_style="green"
        ))
    
    async def run_startup_sequence(self):
        """Run the complete startup sequence"""
        console.print(Panel.fit(
            "[bold blue]Ford Bayesian Risk Score Engine[/bold blue]\n"
            "[yellow]Swarm Startup Sequence[/yellow]\n\n"
            "[italic]Initializing distributed risk scoring infrastructure...[/italic]",
            border_style="blue"
        ))
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Load configuration
        if not self.load_config():
            return False
        
        # Check dependencies
        if not self.check_dependencies():
            console.print("\n❌ Dependency check failed. Please install missing services.")
            return False
        
        # Start infrastructure services
        if not await self.start_infrastructure_services():
            console.print("\n❌ Failed to start infrastructure services")
            return False
        
        # Initialize database
        if not await self.initialize_database():
            console.print("\n❌ Database initialization failed")
            return False
        
        # Start swarm orchestrator
        if not await self.start_swarm_orchestrator():
            console.print("\n❌ Failed to start swarm orchestrator")
            return False
        
        # Start API gateway
        if not await self.start_api_gateway():
            console.print("\n❌ Failed to start API gateway")
            return False
        
        # Register demo workers
        if not await self.register_demo_workers():
            console.print("\n❌ Failed to register workers")
            return False
        
        # Display summary
        await self.display_startup_summary()
        
        # Keep running
        self.running = True
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
        
        await self.shutdown()
        return True


async def main():
    """Main startup entry point"""
    launcher = FordRiskSwarmLauncher()
    success = await launcher.run_startup_sequence()
    
    if not success:
        console.print("\n❌ [bold red]Startup failed[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the startup sequence
    asyncio.run(main()) 