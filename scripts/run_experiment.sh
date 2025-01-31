#!/bin/bash
#SBATCH --job-name=k8s-big
#SBATCH --account=project_2012346
#SBATCH --partition=gpu
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --gres=gpu:v100:2
#SBATCH --mail-type=END,FAIL

apptainer exec --nv \
    -B /projappl/project_2012346/llm-ran:/app \
    -B /scratch/project_2012346/ollama:/root/.ollama \
    -B /users/chenxiya:/users/chenxiya \
    /projappl/project_2012346/llm-ran.sif \
    /app/deployment/apptainer_entry.sh \
    python /app/experiments/k8s.py

# -B /users/chenxiya:/users/chenxiya : for kubeconfig

# apptainer shell /projappl/project_2012346/llm-ran.sif
