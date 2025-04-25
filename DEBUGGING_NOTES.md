# Docker Build Debugging Notes (airflow-hub)

**Date:** 2025-04-25

**Goal:** Resolve Docker build failures for the `airflow-hub-test` image defined in `Dockerfile.test`.

**Context:**
The project uses Python 3.11. We encountered several issues during the `pip install -r requirements.txt` step within the Docker build process.

**Issues Resolved So Far:**

1.  **`numpy` / `pandas` / Python 3.11 Compatibility:**
    *   Updated `numpy==1.21.6` to `numpy~=1.23.5`.
    *   Updated `pandas==1.3.5` to `pandas~=1.5.3`.
2.  **`scikit-learn==1.0.2` Compilation Errors:**
    *   Added system build dependencies to `Dockerfile.test`: `build-essential`, `gcc`, `g++`, `libblas-dev`, `liblapack-dev`, `libpq-dev`.
    *   Added an explicit `RUN pip install --no-cache-dir cython` step before installing requirements.
    *   Updated `scikit-learn==1.0.2` to `scikit-learn~=1.4.0` in `requirements.txt`.
3.  **`apache-airflow-providers-cncf-kubernetes==8.12.0` Not Found:**
    *   Updated to `apache-airflow-providers-cncf-kubernetes==8.4.2` in `requirements.txt` as `8.12.0` was unavailable for the current environment.
4.  **`dag-factory~=1.4` Not Found:**
    *   Updated to `dag-factory~=0.23.0` in `requirements.txt` as `1.4` seemed incorrect and `0.23.0` is the latest compatible version.

**Current Status:**

*   The `docker build -t airflow-hub-test -f Dockerfile.test .` command *still* fails during the `RUN pip install --no-cache-dir -r requirements.txt` step.
*   The exact error causing the failure is **unknown** because the Docker build output log gets truncated before showing the specific package error.
*   We are currently using an interactive debugging method:
    *   The failing `pip install` command in `Dockerfile.test` is **commented out**.
    *   An intermediate image named `airflow-hub-debug` has been successfully built using `docker build -t airflow-hub-debug -f Dockerfile.test .`.

**Next Steps:**

1.  **Run the debug container interactively:**
    ```bash
    docker run -it --rm airflow-hub-debug /bin/bash
    ```
2.  **Inside the container's shell (`root@...:/app#`), run the installation command:**
    ```bash
    pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
    ```
3.  **Capture the FULL output:** Copy all text from the command execution, especially the final error message.
4.  **Analyze the error:** Identify the specific package causing the installation failure.
5.  **Fix the dependency issue:** Update `requirements.txt` or `Dockerfile.test` as needed.
6.  **Uncomment the `pip install` line** in `Dockerfile.test`.
7.  **Attempt the full build again:** `docker build -t airflow-hub-test -f Dockerfile.test .`

**Files Modified:**

*   `requirements.txt`
*   `Dockerfile.test`
*   `DEBUGGING_NOTES.md` (this file)
