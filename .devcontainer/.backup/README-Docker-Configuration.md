# MCP Python SDK - Global Docker Configuration System

## Overview

This document describes the dramatically enhanced Docker configuration system for the MCP Python SDK. The system implements a centralized global configuration approach using `GLOBAL_` prefixed environment variables to eliminate duplication and provide consistent configuration across all Docker containers, services, and swarm deployments.

## 🎯 Key Features

### Centralized Configuration
- **51+ global configuration variables** with `GLOBAL_` prefix to avoid conflicts
- **Single source of truth** in `config/docker-globals.env`
- **Consistent variable substitution** pattern: `${GLOBAL_VARIABLE_NAME:-default_value}`
- **Elimination of duplicate declarations** across all configuration files

### Performance Optimization
- **Unlimited resource allocation** (0 limits) with configurable minimum reservations
- **High-performance tmpfs volumes** for caching with configurable sizes
- **GPU passthrough** with full CUDA capabilities and device access
- **Network optimization** with jumbo frames (9000 MTU) and performance sysctls
- **Memory management** with jemalloc and optimized malloc configurations

### Developer Experience
- **Modular service architecture** using Docker Compose `include` pattern
- **Multi-stage Dockerfile builds** with comprehensive caching
- **Comprehensive validation** script for configuration verification
- **Development-specific overrides** in separate environment files

## 📁 File Structure

```
.devcontainer/
├── config/
│   ├── docker-globals.env          # Global configuration (GLOBAL_ variables)
│   ├── development.env             # Development-specific overrides
│   └── env/                        # Legacy individual env files (consolidated)
├── docker/
│   ├── Dockerfile.main             # Multi-stage optimized Dockerfile
│   ├── components/                 # Modular Dockerfile components
│   │   ├── dev-tools.Dockerfile
│   │   ├── gpu-support.Dockerfile
│   │   ├── network-optimize.Dockerfile
│   │   └── runtime.Dockerfile
│   ├── services/                   # Individual service definitions
│   │   ├── app-service.yml
│   │   ├── postgres-service.yml
│   │   └── redis-service.yml
│   └── swarm/                      # Docker Swarm stack files
│       ├── app-stack.yml
│       ├── postgres-stack.yml
│       ├── redis-stack.yml
│       ├── docker-stack.yml
│       └── docker-stack.simple.yml
├── scripts/
│   └── validate-config.sh          # Configuration validation script
└── docker-compose.modular.yml     # Main orchestration file
```

## 🔧 Global Configuration Variables

### Network Configuration
```bash
GLOBAL_NETWORK_MTU=9000                    # Jumbo frames for performance
GLOBAL_NETWORK_SUBNET=172.20.0.0/16       # Docker network subnet
GLOBAL_NETWORK_GATEWAY=172.20.0.1         # Gateway IP address
```

### Resource Limits
```bash
GLOBAL_CPU_LIMIT=0                         # Unlimited CPU (0 = no limit)
GLOBAL_MEMORY_LIMIT=0                      # Unlimited memory (0 = no limit)
GLOBAL_CPU_RESERVATION=4                   # Minimum CPU reservation
GLOBAL_MEMORY_RESERVATION=8G               # Minimum memory reservation
```

### Cache Configuration
```bash
GLOBAL_PYTHON_CACHE_SIZE=8G               # Python cache volume size
GLOBAL_WHEELS_CACHE_SIZE=4G               # Python wheels cache size
GLOBAL_BYTECODE_CACHE_SIZE=2G             # Bytecode cache size
GLOBAL_NUMBA_CACHE_SIZE=4G                # Numba JIT cache size
GLOBAL_PIP_CACHE_SIZE=2G                  # pip cache size
GLOBAL_CUDA_CACHE_SIZE=4G                 # CUDA cache size
GLOBAL_RUST_CACHE_SIZE=2G                 # Rust cache size
```

### GPU Configuration
```bash
GLOBAL_NVIDIA_VISIBLE_DEVICES=all         # All NVIDIA GPUs available
GLOBAL_NVIDIA_DRIVER_CAPABILITIES=all     # All CUDA capabilities
GLOBAL_CUDA_VISIBLE_DEVICES=all           # All CUDA devices
```

### Database Configuration
```bash
GLOBAL_POSTGRES_USER=postgres              # PostgreSQL username
GLOBAL_POSTGRES_DB=postgres                # Default database
GLOBAL_POSTGRES_PASSWORD=postgres          # Database password
GLOBAL_POSTGRES_PORT=5432                  # Database port
GLOBAL_REDIS_PORT=6379                     # Redis port
GLOBAL_REDIS_MAXMEMORY=4gb                 # Redis memory limit
```

### Build Configuration
```bash
GLOBAL_BUILDKIT_INLINE_CACHE=1            # Enable BuildKit inline cache
GLOBAL_DOCKER_BUILDKIT=1                  # Enable Docker BuildKit
```

### Python Optimization
```bash
GLOBAL_PYTHONOPTIMIZE=2                   # Maximum Python optimization
GLOBAL_PYTHONHASHSEED=0                   # Reproducible hash seed
GLOBAL_PYTHONDONTWRITEBYTECODE=1          # No .pyc files
GLOBAL_PYTHONUNBUFFERED=1                 # Unbuffered output
GLOBAL_PYTHONPATH=/workspaces/python-sdk/src  # Python module path
```

### Performance Tuning
```bash
GLOBAL_TMPFS_SIZE=32G                     # tmpfs volume size
GLOBAL_CONTAINER_SHM_SIZE=16G             # Shared memory size
GLOBAL_ULIMIT_NOFILE_SOFT=1048576         # File descriptor limit
GLOBAL_ULIMIT_MEMLOCK_SOFT=-1             # Memory lock limit
```

### Security Configuration
```bash
GLOBAL_PRIVILEGED_MODE=true               # Privileged container mode
GLOBAL_SECURITY_OPT=seccomp:unconfined   # Security options
GLOBAL_APPARMOR_PROFILE=apparmor:unconfined  # AppArmor profile
```

## 🚀 Usage Instructions

### Development Environment

1. **Start the development environment:**
   ```bash
   cd /workspaces/python-sdk/.devcontainer
   docker-compose -f docker-compose.modular.yml --env-file config/docker-globals.env up -d
   ```

2. **Validate configuration:**
   ```bash
   ./scripts/validate-config.sh
   ```

3. **Build with custom configuration:**
   ```bash
   GLOBAL_PYTHON_CACHE_SIZE=16G docker-compose build
   ```

### Docker Swarm Deployment

1. **Deploy simple stack:**
   ```bash
   docker stack deploy -c docker/swarm/docker-stack.simple.yml mcp-sdk
   ```

2. **Deploy full stack:**
   ```bash
   docker stack deploy -c docker/swarm/docker-stack.yml mcp-sdk
   ```

3. **Deploy individual services:**
   ```bash
   docker stack deploy -c docker/swarm/app-stack.yml mcp-app
   docker stack deploy -c docker/swarm/postgres-stack.yml mcp-db
   docker stack deploy -c docker/swarm/redis-stack.yml mcp-cache
   ```

### Configuration Customization

1. **Override global variables:**
   ```bash
   # Create local override file
   echo "GLOBAL_PYTHON_CACHE_SIZE=16G" > .env.local
   
   # Use with docker-compose
   docker-compose --env-file config/docker-globals.env --env-file .env.local up -d
   ```

2. **Development-specific settings:**
   ```bash
   # Use development configuration
   docker-compose --env-file config/development.env up -d
   ```

## 🔍 Validation and Testing

### Configuration Validation
The `validate-config.sh` script performs comprehensive validation:

- ✅ Checks all configuration files exist
- ✅ Validates 51+ global configuration variables
- ✅ Tests Docker Compose configuration parsing
- ✅ Validates all service and volume definitions
- ✅ Checks Docker Swarm stack configurations
- ✅ Verifies component Dockerfiles use global variables
- ✅ Validates performance optimizations
- ✅ Checks security configuration

### Build Testing
```bash
# Test configuration parsing
docker-compose config

# Build without cache to test from scratch
docker-compose build --no-cache

# Build with parallel processing
docker-compose build --parallel
```

### Runtime Testing
```bash
# Start services and check health
docker-compose up -d
docker-compose ps

# Check resource usage
docker stats

# Test GPU access (if available)
docker exec -it devcontainer_app_1 nvidia-smi
```

## 🎛️ Performance Features

### High-Performance Storage
- **tmpfs volumes** for all cache directories
- **Configurable cache sizes** via global variables
- **Optimized volume mount options** with uid/gid mapping
- **Persistent data volumes** with bind mounts for databases

### GPU Acceleration
- **Full NVIDIA GPU passthrough** with all capabilities
- **CUDA toolkit and libraries** pre-installed
- **AMD ROCm support** for AMD GPUs
- **Intel GPU support** with OpenCL and Level Zero

### Network Optimization
- **Jumbo frames (9000 MTU)** for reduced packet overhead
- **Optimized sysctls** for network performance
- **TCP congestion control** with BBR algorithm
- **High connection limits** and buffer sizes

### Memory Management
- **jemalloc allocator** for improved memory performance
- **Unlimited container memory** with minimum reservations
- **Large shared memory** for inter-process communication
- **Optimized malloc configuration** for performance

## 🔒 Security Considerations

### Development Mode
- **Privileged containers** for maximum compatibility
- **Relaxed security policies** for development flexibility
- **Unconfined profiles** for AppArmor and seccomp
- **Host network access** for development tools

### Production Recommendations
1. Set `GLOBAL_PRIVILEGED_MODE=false` for production
2. Configure stricter security profiles
3. Use specific GPU device mappings instead of "all"
4. Implement network segmentation
5. Use secrets management for passwords

## 📊 Monitoring and Observability

### Performance Monitoring
- **Prometheus metrics** (configurable)
- **Grafana dashboards** (optional)
- **Jaeger tracing** (optional)
- **Performance logging** in `/var/log/performance`

### Health Checks
- **PostgreSQL health checks** with `pg_isready`
- **Redis health checks** with `redis-cli ping`
- **Application health checks** with Python validation
- **Comprehensive service monitoring**

## 🔄 Migration from Previous Configuration

### Automated Migration
The global configuration system is designed to be backward compatible:

1. **Legacy environment variables** are still supported
2. **Gradual migration** is possible with coexistence
3. **Global variables take precedence** when both exist
4. **Validation script** identifies configuration conflicts

### Migration Steps
1. Review current environment variable usage
2. Map variables to corresponding `GLOBAL_` versions
3. Update custom configurations to use global variables
4. Run validation script to verify migration
5. Test thoroughly before production deployment

## 🚀 Future Enhancements

### Planned Improvements
- **Kubernetes deployment** configurations
- **Multi-architecture builds** (ARM64 support)
- **Advanced caching strategies** with registry caching
- **Automated performance tuning** based on system resources
- **Configuration templates** for different deployment scenarios

### Extension Points
- **Custom service definitions** in the services directory
- **Additional Dockerfile components** for specialized builds
- **Environment-specific configurations** for different stages
- **Plugin system** for additional functionality

## 📞 Support and Troubleshooting

### Common Issues

1. **Permission Issues:**
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 /opt/mcp-cache
   sudo chown -R 1000:1000 /opt/postgres-data
   ```

2. **GPU Access Issues:**
   ```bash
   # Check NVIDIA drivers
   nvidia-smi
   
   # Check Docker GPU support
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

3. **Network Issues:**
   ```bash
   # Check MTU settings
   ip link show
   
   # Test network connectivity
   docker exec -it devcontainer_app_1 ping google.com
   ```

### Debugging Commands
```bash
# View parsed configuration
docker-compose config

# Check service logs
docker-compose logs app

# Inspect container configuration
docker inspect devcontainer_app_1

# Monitor resource usage
docker stats --no-stream
```

### Getting Help
- Review the validation script output for configuration issues
- Check Docker Compose logs for service-specific problems
- Use `docker-compose config` to debug configuration parsing
- Consult the global configuration file for available variables

---

## 🎉 Conclusion

The MCP Python SDK now features a dramatically enhanced Docker configuration system that provides:

✅ **Centralized Configuration** - Single source of truth with 51+ global variables
✅ **Performance Optimization** - Maximum throughput with GPU acceleration
✅ **Developer Experience** - Modular architecture with comprehensive validation
✅ **Production Ready** - Scalable deployment with Docker Swarm support
✅ **Future Proof** - Extensible design for additional functionality

This configuration system eliminates duplicate declarations, provides consistent performance optimization, and offers a solid foundation for both development and production deployments of the MCP Python SDK.

🚀 **The MCP Python SDK Docker configuration is now complete and ready for use!**
