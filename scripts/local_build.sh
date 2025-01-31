docker build -t chenseanxy/llm-ran .
docker run --rm -it --gpus=all \
    -v "$PWD:/app" \
    -v "$PWD/.kubeconfig:/root/.kube/config" \
    -v /mnt/c/Users/chenx/.ollama/models:/root/.ollama/models \
    chenseanxy/llm-ran \
    /bin/bash
