#!/bin/bash
#SBATCH --job-name=direct_base
#SBATCH --account=project_2012346
#SBATCH --partition=gpu
#SBATCH --time=04:00:00
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --gres=gpu:v100:4
#SBATCH --gpus-per-task=1
#SBATCH --mail-type=END,FAIL

srun apptainer exec --nv \
    -B /projappl/project_2012346/llm-ran:/app \
    -B /scratch/project_2012346/ollama:/root/.ollama \
    -B /users/chenxiya:/users/chenxiya \
    /projappl/project_2012346/llm-ran.sif \
    /app/deployment/apptainer_entry.sh \
    python -m llm_ran.benchmark \
    --chain kubernetes_direct_chain \
    --model qwen2.5:32b \
    --trials 10 \
    --scenarios base \
    --pull-model \
    &

srun apptainer exec --nv \
    -B /projappl/project_2012346/llm-ran:/app \
    -B /scratch/project_2012346/ollama:/root/.ollama \
    -B /users/chenxiya:/users/chenxiya \
    /projappl/project_2012346/llm-ran.sif \
    /app/deployment/apptainer_entry.sh \
    python -m llm_ran.benchmark \
    --chain kubernetes_direct_chain \
    --model qwen2.5-coder:32b \
    --trials 10 \
    --scenarios base \
    --pull-model \
    &

srun apptainer exec --nv \
    -B /projappl/project_2012346/llm-ran:/app \
    -B /scratch/project_2012346/ollama:/root/.ollama \
    -B /users/chenxiya:/users/chenxiya \
    /projappl/project_2012346/llm-ran.sif \
    /app/deployment/apptainer_entry.sh \
    python -m llm_ran.benchmark \
    --chain kubernetes_direct_chain \
    --model medragondot/Sky-T1-32B-Preview \
    --trials 10 \
    --scenarios base \
    --pull-model \
    &

srun apptainer exec --nv \
    -B /projappl/project_2012346/llm-ran:/app \
    -B /scratch/project_2012346/ollama:/root/.ollama \
    -B /users/chenxiya:/users/chenxiya \
    /projappl/project_2012346/llm-ran.sif \
    /app/deployment/apptainer_entry.sh \
    python -m llm_ran.benchmark \
    --chain kubernetes_direct_chain \
    --model mixtral:8x7b \
    --trials 10 \
    --scenarios base \
    --pull-model

wait

# -B /users/chenxiya:/users/chenxiya : for kubeconfig

# apptainer shell /projappl/project_2012346/llm-ran.sif
