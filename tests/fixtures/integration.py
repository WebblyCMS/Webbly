"""Integration testing utilities and helpers."""

import os
import time
import docker
import requests
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from dataclasses import dataclass

from .config import TEST_REPORTS_DIR
from .logging import logger

@dataclass
class ServiceConfig:
    """Service configuration data."""
    name: str
    image: str
    ports: Dict[str, str]
    environment: Dict[str, str]
    volumes: Dict[str, str]
    command: Optional[str] = None
    healthcheck: Optional[Dict[str, Any]] = None

class IntegrationTestEnvironment:
    """Integration test environment manager."""
    
    def __init__(self):
        self.client = docker.from_env()
        self.containers = {}
        self.networks = {}
    
    def start_service(self, config: ServiceConfig) -> str:
        """Start a service container."""
        try:
            # Create container
            container = self.client.containers.run(
                image=config.image,
                name=f"test_{config.name}",
                ports=config.ports,
                environment=config.environment,
                volumes=config.volumes,
                command=config.command,
                detach=True,
                remove=True
            )
            
            self.containers[config.name] = container
            
            # Wait for service to be healthy
            if config.healthcheck:
                self._wait_for_healthy(container, config.healthcheck)
            
            logger.info(f"Started service: {config.name}")
            return container.id
        
        except Exception as e:
            logger.error(f"Failed to start service {config.name}: {e}")
            raise
    
    def stop_service(self, name: str):
        """Stop a service container."""
        try:
            if name in self.containers:
                container = self.containers[name]
                container.stop()
                del self.containers[name]
                logger.info(f"Stopped service: {name}")
        
        except Exception as e:
            logger.error(f"Failed to stop service {name}: {e}")
            raise
    
    def create_network(self, name: str) -> str:
        """Create a Docker network."""
        try:
            network = self.client.networks.create(
                name=f"test_{name}",
                driver="bridge"
            )
            self.networks[name] = network
            logger.info(f"Created network: {name}")
            return network.id
        
        except Exception as e:
            logger.error(f"Failed to create network {name}: {e}")
            raise
    
    def remove_network(self, name: str):
        """Remove a Docker network."""
        try:
            if name in self.networks:
                network = self.networks[name]
                network.remove()
                del self.networks[name]
                logger.info(f"Removed network: {name}")
        
        except Exception as e:
            logger.error(f"Failed to remove network {name}: {e}")
            raise
    
    def _wait_for_healthy(self, container: docker.models.containers.Container, 
                         healthcheck: Dict[str, Any]):
        """Wait for container to be healthy."""
        url = healthcheck.get('url')
        timeout = healthcheck.get('timeout', 30)
        interval = healthcheck.get('interval', 1)
        expected_status = healthcheck.get('status', 200)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url)
                if response.status_code == expected_status:
                    return
            except:
                pass
            time.sleep(interval)
        
        raise TimeoutError(f"Service did not become healthy within {timeout} seconds")
    
    def cleanup(self):
        """Clean up all resources."""
        # Stop all containers
        for name in list(self.containers.keys()):
            self.stop_service(name)
        
        # Remove all networks
        for name in list(self.networks.keys()):
            self.remove_network(name)

class DatabaseTestHelper:
    """Database integration test helper."""
    
    def __init__(self, env: IntegrationTestEnvironment):
        self.env = env
    
    def start_postgres(self, name: str = 'postgres', port: str = '5432') -> str:
        """Start PostgreSQL database."""
        config = ServiceConfig(
            name=name,
            image='postgres:13',
            ports={port: port},
            environment={
                'POSTGRES_USER': 'test',
                'POSTGRES_PASSWORD': 'test',
                'POSTGRES_DB': 'test'
            },
            volumes={},
            healthcheck={
                'url': f'http://localhost:{port}',
                'timeout': 30,
                'interval': 1,
                'status': 200
            }
        )
        return self.env.start_service(config)
    
    def start_mysql(self, name: str = 'mysql', port: str = '3306') -> str:
        """Start MySQL database."""
        config = ServiceConfig(
            name=name,
            image='mysql:8',
            ports={port: port},
            environment={
                'MYSQL_ROOT_PASSWORD': 'test',
                'MYSQL_DATABASE': 'test',
                'MYSQL_USER': 'test',
                'MYSQL_PASSWORD': 'test'
            },
            volumes={},
            healthcheck={
                'url': f'http://localhost:{port}',
                'timeout': 30,
                'interval': 1,
                'status': 200
            }
        )
        return self.env.start_service(config)

class CacheTestHelper:
    """Cache integration test helper."""
    
    def __init__(self, env: IntegrationTestEnvironment):
        self.env = env
    
    def start_redis(self, name: str = 'redis', port: str = '6379') -> str:
        """Start Redis cache."""
        config = ServiceConfig(
            name=name,
            image='redis:6',
            ports={port: port},
            environment={},
            volumes={},
            healthcheck={
                'url': f'http://localhost:{port}',
                'timeout': 30,
                'interval': 1,
                'status': 200
            }
        )
        return self.env.start_service(config)
    
    def start_memcached(self, name: str = 'memcached', port: str = '11211') -> str:
        """Start Memcached cache."""
        config = ServiceConfig(
            name=name,
            image='memcached:1.6',
            ports={port: port},
            environment={},
            volumes={},
            healthcheck={
                'url': f'http://localhost:{port}',
                'timeout': 30,
                'interval': 1,
                'status': 200
            }
        )
        return self.env.start_service(config)

class EmailTestHelper:
    """Email integration test helper."""
    
    def __init__(self, env: IntegrationTestEnvironment):
        self.env = env
    
    def start_mailhog(self, name: str = 'mailhog', smtp_port: str = '1025', 
                     http_port: str = '8025') -> str:
        """Start MailHog email testing service."""
        config = ServiceConfig(
            name=name,
            image='mailhog/mailhog',
            ports={
                smtp_port: '1025',
                http_port: '8025'
            },
            environment={},
            volumes={},
            healthcheck={
                'url': f'http://localhost:{http_port}',
                'timeout': 30,
                'interval': 1,
                'status': 200
            }
        )
        return self.env.start_service(config)

@contextmanager
def integration_test_environment():
    """Context manager for integration test environment."""
    env = IntegrationTestEnvironment()
    try:
        yield env
    finally:
        env.cleanup()

# Global environment instance
environment = IntegrationTestEnvironment()
db_helper = DatabaseTestHelper(environment)
cache_helper = CacheTestHelper(environment)
email_helper = EmailTestHelper(environment)
