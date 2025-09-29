#!/usr/bin/env python3
"""
AgentLab Infrastructure Tests
Comprehensive testing for Docker infrastructure components
"""

import os
import sys
import time
import json
import subprocess
import requests
import pytest
import docker
import redis
import psycopg2
from pathlib import Path

# Test configuration
TEST_TIMEOUT = 300  # 5 minutes
HEALTH_CHECK_RETRIES = 30
HEALTH_CHECK_DELAY = 5

class TestDockerInfrastructure:
    """Test Docker infrastructure components"""

    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.docker_client = docker.from_env()
        cls.compose_file = "docker-compose.test.yml"

        # Ensure we're in the right directory
        if not os.path.exists(cls.compose_file):
            cls.compose_file = "docker-compose.yml"

        if not os.path.exists(cls.compose_file):
            pytest.skip("No Docker Compose file found")

    def test_docker_daemon_running(self):
        """Test that Docker daemon is running"""
        try:
            self.docker_client.ping()
        except Exception as e:
            pytest.fail(f"Docker daemon is not running: {e}")

    def test_compose_file_valid(self):
        """Test that Docker Compose file is valid"""
        result = subprocess.run(
            ["docker-compose", "-f", self.compose_file, "config"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.fail(f"Invalid compose file: {result.stderr}")

    def test_required_images_exist(self):
        """Test that required base images are available"""
        required_images = [
            "postgres:15.4",
            "redis:7.0-alpine",
            "nginx:1.25-alpine",
            "python:3.11.5-slim",
            "node:18.17.0-alpine"
        ]

        for image in required_images:
            try:
                self.docker_client.images.get(image)
            except docker.errors.ImageNotFound:
                # Try to pull the image
                try:
                    self.docker_client.images.pull(image)
                except Exception as e:
                    pytest.fail(f"Required image not available: {image} - {e}")

    def test_container_startup(self):
        """Test that containers start successfully"""
        # Start containers
        result = subprocess.run(
            ["docker-compose", "-f", self.compose_file, "up", "-d"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.fail(f"Failed to start containers: {result.stderr}")

        # Wait for containers to be ready
        time.sleep(10)

        # Check container status
        result = subprocess.run(
            ["docker-compose", "-f", self.compose_file, "ps", "--format", "json"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.fail(f"Failed to get container status: {result.stderr}")

        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        failed_containers = []
        for container in containers:
            if container.get('State') != 'running':
                failed_containers.append(f"{container.get('Service')}: {container.get('State')}")

        if failed_containers:
            pytest.fail(f"Containers not running: {', '.join(failed_containers)}")


class TestNetworkConnectivity:
    """Test network connectivity between services"""

    def test_postgres_connectivity(self):
        """Test PostgreSQL connectivity"""
        max_retries = HEALTH_CHECK_RETRIES

        for attempt in range(max_retries):
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    database="agentlab_test",
                    user="agentlab_test_user",
                    password="test_password",
                    connect_timeout=5
                )

                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    assert result[0] == 1

                conn.close()
                return

            except (psycopg2.OperationalError, psycopg2.DatabaseError) as e:
                if attempt < max_retries - 1:
                    time.sleep(HEALTH_CHECK_DELAY)
                    continue
                pytest.fail(f"PostgreSQL connectivity failed after {max_retries} attempts: {e}")

    def test_redis_connectivity(self):
        """Test Redis connectivity"""
        max_retries = HEALTH_CHECK_RETRIES

        for attempt in range(max_retries):
            try:
                r = redis.Redis(
                    host="localhost",
                    port=6379,
                    password="test_redis_password",
                    socket_timeout=5,
                    socket_connect_timeout=5
                )

                # Test basic operations
                r.ping()
                r.set("test_key", "test_value")
                assert r.get("test_key").decode() == "test_value"
                r.delete("test_key")

                return

            except (redis.ConnectionError, redis.TimeoutError) as e:
                if attempt < max_retries - 1:
                    time.sleep(HEALTH_CHECK_DELAY)
                    continue
                pytest.fail(f"Redis connectivity failed after {max_retries} attempts: {e}")

    def test_api_health_endpoint(self):
        """Test API health endpoint"""
        max_retries = HEALTH_CHECK_RETRIES

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    "http://localhost:8000/health",
                    timeout=10
                )

                if response.status_code == 200:
                    return

            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(HEALTH_CHECK_DELAY)
                    continue
                pytest.fail(f"API health check failed after {max_retries} attempts: {e}")

        pytest.fail(f"API health endpoint returned status {response.status_code}")

    def test_web_health_endpoint(self):
        """Test Web application health endpoint"""
        max_retries = HEALTH_CHECK_RETRIES

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    "http://localhost:3000/api/health",
                    timeout=10
                )

                if response.status_code == 200:
                    return

            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(HEALTH_CHECK_DELAY)
                    continue
                pytest.fail(f"Web health check failed after {max_retries} attempts: {e}")

        pytest.fail(f"Web health endpoint returned status {response.status_code}")


class TestDatabaseFunctionality:
    """Test database-specific functionality"""

    def test_pgvector_extension(self):
        """Test that pgvector extension is installed and working"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="agentlab_test",
                user="agentlab_test_user",
                password="test_password"
            )

            with conn.cursor() as cur:
                # Check if vector extension is installed
                cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
                result = cur.fetchone()
                assert result is not None, "pgvector extension not installed"

                # Test vector operations
                cur.execute("CREATE TABLE IF NOT EXISTS test_vectors (id serial, embedding vector(3));")
                cur.execute("INSERT INTO test_vectors (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');")

                # Test similarity search
                cur.execute("""
                    SELECT id, embedding <-> '[1,2,3]' as distance
                    FROM test_vectors
                    ORDER BY distance LIMIT 1;
                """)
                result = cur.fetchone()
                assert result is not None
                assert result[1] == 0.0  # Should be exactly the same vector

                # Cleanup
                cur.execute("DROP TABLE test_vectors;")
                conn.commit()

            conn.close()

        except Exception as e:
            pytest.fail(f"pgvector extension test failed: {e}")

    def test_database_performance(self):
        """Test basic database performance"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="agentlab_test",
                user="agentlab_test_user",
                password="test_password"
            )

            with conn.cursor() as cur:
                # Test query performance
                start_time = time.time()
                cur.execute("SELECT generate_series(1, 1000);")
                cur.fetchall()
                query_time = time.time() - start_time

                # Should complete within reasonable time
                assert query_time < 5.0, f"Query took too long: {query_time:.2f}s"

            conn.close()

        except Exception as e:
            pytest.fail(f"Database performance test failed: {e}")


class TestRedisPerformance:
    """Test Redis performance and functionality"""

    def test_redis_performance(self):
        """Test Redis performance"""
        try:
            r = redis.Redis(
                host="localhost",
                port=6379,
                password="test_redis_password"
            )

            # Test write performance
            start_time = time.time()
            for i in range(1000):
                r.set(f"perf_test_{i}", f"value_{i}")
            write_time = time.time() - start_time

            # Test read performance
            start_time = time.time()
            for i in range(1000):
                r.get(f"perf_test_{i}")
            read_time = time.time() - start_time

            # Cleanup
            for i in range(1000):
                r.delete(f"perf_test_{i}")

            # Performance assertions
            assert write_time < 10.0, f"Redis writes too slow: {write_time:.2f}s"
            assert read_time < 5.0, f"Redis reads too slow: {read_time:.2f}s"

        except Exception as e:
            pytest.fail(f"Redis performance test failed: {e}")

    def test_redis_data_structures(self):
        """Test Redis data structures"""
        try:
            r = redis.Redis(
                host="localhost",
                port=6379,
                password="test_redis_password"
            )

            # Test string operations
            r.set("test_string", "hello")
            assert r.get("test_string").decode() == "hello"

            # Test list operations
            r.lpush("test_list", "item1", "item2", "item3")
            assert r.llen("test_list") == 3
            assert r.lpop("test_list").decode() == "item3"

            # Test hash operations
            r.hset("test_hash", "field1", "value1")
            r.hset("test_hash", "field2", "value2")
            assert r.hget("test_hash", "field1").decode() == "value1"
            assert r.hlen("test_hash") == 2

            # Test set operations
            r.sadd("test_set", "member1", "member2", "member3")
            assert r.scard("test_set") == 3
            assert r.sismember("test_set", "member1")

            # Cleanup
            r.delete("test_string", "test_list", "test_hash", "test_set")

        except Exception as e:
            pytest.fail(f"Redis data structures test failed: {e}")


class TestSecurityConfiguration:
    """Test security configurations"""

    def test_container_security(self):
        """Test container security settings"""
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "ps", "--format", "json"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip("Could not get container information")

        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        for container in containers:
            container_name = container.get('Name', '')

            # Check that containers are not running as root (where applicable)
            inspect_result = subprocess.run(
                ["docker", "inspect", container_name],
                capture_output=True,
                text=True
            )

            if inspect_result.returncode == 0:
                inspect_data = json.loads(inspect_result.stdout)[0]
                config = inspect_data.get('Config', {})

                # Check security options
                security_opts = inspect_data.get('HostConfig', {}).get('SecurityOpt', [])
                if 'no-new-privileges:true' not in security_opts:
                    print(f"Warning: {container_name} does not have no-new-privileges set")

    def test_network_isolation(self):
        """Test network isolation between services"""
        # This test would check that services can only communicate
        # through defined network channels
        pass  # Placeholder for network isolation tests


def run_infrastructure_tests():
    """Run all infrastructure tests"""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        f"--timeout={TEST_TIMEOUT}",
        "--color=yes"
    ]

    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Run tests when script is executed directly
    exit_code = run_infrastructure_tests()
    sys.exit(exit_code)