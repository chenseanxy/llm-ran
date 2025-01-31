# llm-ran
LLM-RAN: Interactive Network Operations usingLarge Language Models in ORAN

## Project Structure

- `data`: input and output data files, small enough to fit in CSC's 50G `/projectappl` folder
- `logs`
- `llm_ran`: agents
- `deployment`
- `experiments`
- `scripts`: scripts for submitting jobs and running experiments
- `notebooks`: notebooks for result analysis

## Deployment

Experiments locally:

`poetry install && poetry run python experiments/xxx.py`

with docker:
```bash
docker run --rm -it --gpus=all \
    -v "$PWD:/app" \
    -v "$PWD/.kubeconfig:/root/.kube/config" \
    -v "/mnt/c/Users/chenx/.ollama/models:/root/.ollama/models" \
    chenseanxy/llm-ran \
    poetry run python experiments/xxx.py
```

Experiments on CSC:
- `sbatch scripts/download_image.sh`: download and convert docker image to apptainer format
- `sbatch scripts/run_experiment.sh`: submit job
    - -> launches a container with `apptainer exec` once scheduled
        - -> entrypoint being `deployment\apptainer_entry.sh`
            - -> runs `ollama` and `cloudflared` in the background
            - -> runs the command in `scripts/run_experiment.sh` in the foreground
                - -> `experiments/xxx.py`
