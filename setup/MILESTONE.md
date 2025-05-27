
# ZATRUST BIO-MCP PYTHON SETUP LAYER — HIGH-FIDELITY ALIGNMENT BRIEF**

This milestone is a **precise, non-deviating, AI-assisted development directive** to realign the foundational Python setup orchestration layer responsible for provisioning the biometric MCP platform containers (API gateway, backend, frontend, portal, database) using Docker Swarm, and preparing the system for modular, whitelabeled deployment in enterprise client environments.

Below is the **explicit, traceable, and unambiguous set of actions** required to complete this milestone.

---

## 🚀 **MILESTONE: PYTHON SETUP DIRECTORY REALIGNMENT + DEPENDENCY REFACTORING**

---

### 📋 **TASK SUMMARY**

You are to:
✅ Realign and reorganize the Python file system into a structured, DRY, SRP-compliant monolithic package
✅ Explicitly rename and relocate existing files
✅ Maintain a clear dependency hierarchy and chronological refactor
✅ Ensure no ambiguity, overlap, or duplicate responsibility remains
✅ Establish a clean entry point (`python -m setup`)
✅ Preserve working `setup.py` at project root as user-facing CLI bridge
✅ Document the final directory tree and relative paths for traceable validation

---

---

### 🏗 **1️⃣ DIRECTORY REALIGNMENT**

#### **NEW TARGET STRUCTURE**

```structure
setup/
├── __init__.py
├── __main__.py                     ← NEW: primary entry point for `python -m setup`
├── main.py                         ← main orchestration runner
├── orchestrator.py                 ← orchestrates phased setup flow
├── sequence.py                     ← defines ordered setup steps
├── packages.py                     ← manages Python/system packages, dependencies
├── validators.py                   ← shared validation utilities
├── config/
│   ├── __init__.py
│   ├── constants.py                ← from environment/constants.py
│   ├── manager.py                  ← from environment/manager.py
│   └── utils.py                    ← from environment/utils.py
├── infra/
│   ├── __init__.py
│   ├── docker/
│   │   ├── __init__.py
│   │   ├── config.py               ← from docker/config.py
│   │   ├── images.py               ← from docker/images.py
│   │   ├── volume_config.py        ← from docker/volume_config.py
│   │   ├── volumes.py              ← from docker/volumes.py
│   │   └── dockerfiles/
│   │       └── Dockerfile.dev      ← from docker/dockerfiles/Dockerfile.dev
│   └── host/
│       ├── __init__.py
│       └── package_manager.py      ← from host/package_manager.py
├── typings/
│   ├── __init__.py
│   ├── config.py
│   ├── core.py
│   ├── enums.py
│   ├── environment.py
│   ├── protocols.py
│   └── tools.py
├── validation/
│   ├── __init__.py
│   ├── base.py
│   ├── composite.py
│   ├── decorators.py
│   ├── registry.py
│   └── reporters.py
├── vscode/
│   ├── __init__.py
│   ├── extensions.py
│   ├── integration.py
│   ├── launch.py
│   ├── settings.py
│   └── tasks.py
├── pyrightconfig.basic.json
├── pyrightconfig.intermediate.json
└── pyrightconfig.json
```

---

---

### 📦 **2️⃣ FILE MOVEMENT AND RENAMING (EXPLICIT ACTIONS)**

| **Current File**                         | **New Location**                                 | **Action**                                    |
| ---------------------------------------- | ------------------------------------------------ | --------------------------------------------- |
| `environment.py` (root)                  | REMOVE / INTEGRATE into `config/` if needed      | Eliminate root ambiguity; no duplicate env.py |
| `environment/constants.py`               | `config/constants.py`                            | Move                                          |
| `environment/manager.py`                 | `config/manager.py`                              | Move                                          |
| `environment/utils.py`                   | `config/utils.py`                                | Move                                          |
| `docker/config.py`                       | `infra/docker/config.py`                         | Move                                          |
| `docker/images.py`                       | `infra/docker/images.py`                         | Move                                          |
| `docker/volume_config.py`                | `infra/docker/volume_config.py`                  | Move                                          |
| `docker/volumes.py`                      | `infra/docker/volumes.py`                        | Move                                          |
| `docker/dockerfiles/Dockerfile.dev`      | `infra/docker/dockerfiles/Dockerfile.dev`        | Move                                          |
| `host/package_manager.py`                | `infra/host/package_manager.py`                  | Move                                          |
| `main.py` (root)                         | `main.py` (keep under setup/)                    | Keep, under centralized setup runner          |
| `orchestrator.py` (root)                 | `orchestrator.py` (keep under setup/)            | Keep                                          |
| `sequence.py` (root)                     | `sequence.py` (keep under setup/)                | Keep                                          |
| `packages.py` (root)                     | `packages.py` (keep under setup/)                | Keep                                          |
| `validators.py` (root)                   | `validators.py` (keep under setup/)              | Keep                                          |
| `pyrightconfig.basic.json` (root)        | `pyrightconfig.basic.json` (keep at setup root)  | Keep                                          |
| `pyrightconfig.intermediate.json` (root) | `pyrightconfig.intermediate.json` (keep at root) | Keep                                          |
| `pyrightconfig.json` (root)              | `pyrightconfig.json` (keep at root)              | Keep                                          |
| `typings/*`                              | `typings/*` (no change)                          | Preserve existing structure                   |
| `validation/*`                           | `validation/*` (no change)                       | Preserve existing structure                   |
| `vscode/*`                               | `vscode/*` (no change)                           | Preserve existing structure                   |

---

---

### ⚙ **3️⃣ DEPENDENCY + ENTRY POINT REFAC**

✅ **Add `__main__.py` under `setup/`:**

```python
from setup.main import run_setup

if __name__ == "__main__":
    run_setup()
```

✅ **Ensure `setup/main.py` contains main orchestration call:**
Define:

```python
def run_setup():
    from setup.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    orchestrator.run()
```

✅ **Ensure `setup.py` (root) bridges CLI call for legacy or simple user entry:**

```python
from setup.main import run_setup

if __name__ == "__main__":
    run_setup()
```

✅ **Chronologically refactor imports:**

* `main.py` → imports only orchestrator interface
* `orchestrator.py` → imports sequence + infra layers
* `sequence.py` → calls infra/docker, infra/host, config layers
* infra/docker + infra/host → only handle system-level calls, no orchestrator logic
* shared modules (typings, validation) → imported only where needed, no circular deps

✅ **Idempotency checks inside `orchestrator.py` + `sequence.py`:**

* Check Docker services, networks, volumes before creating
* Check system package states before re-installing
* Validate setup stage markers to avoid re-running finished phases

---

---

### 🧩 **4️⃣ FINAL VALIDATION CHECKPOINTS**

✅ Ensure all imports reflect **new relative paths** after moves.
✅ Run `python -m setup` — confirm CLI triggers orchestrator successfully.
✅ Run `setup.py` — confirm legacy compatibility.
✅ Check static typing (`pyright`) — no broken references or path errors.
✅ Commit directory changes + refactor commits **with traceable commit messages per moved module**.

---

---

### 📍 **DELIVERABLE CHECKLIST**

| Deliverable                                  | Status |
| -------------------------------------------- | ------ |
| Restructured directory as per outlined tree  | ☐      |
| File moves and renaming completed            | ☐      |
| Dependencies updated for new import paths    | ☐      |
| Added `__main__.py` entry point              | ☐      |
| `setup.py` CLI integration confirmed         | ☐      |
| Chronological import refactor completed      | ☐      |
| Orchestrator idempotency checks in place     | ☐      |
| Final test runs + static typing check passed | ☐      |

---

---

### 🏁 **SUMMARY**

This milestone explicitly reorganizes and refactors the Python setup orchestration layer to ensure:

* Alignment with DRY, SRP, SOLID, idempotent design
* Modern Python package standards
* Clear, single responsibility orchestration architecture
* Maintainability for future enterprise client deployments

By following this brief **step by step without deviation**, you will establish a **high-fidelity, traceable, aligned foundation** for the Zatrust Bio-MCP platform.

---
