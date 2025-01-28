#!/bin/bash
#SBATCH --job-name=k8s-big
#SBATCH --account=project_2012346
#SBATCH --partition=test
#SBATCH --time=00:10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=2G
##SBATCH --gres=gpu:v100:2
#SBATCH --mail-type=END,FAIL

apptainer exec \
    -B /projappl/project_2012346/llm-ran:/app \
    -B /scratch/project_2012346/ollama:/root/.ollama \
    -B /users/chenxiya:/users/chenxiya \
    /projappl/project_2012346/llm-ran.sif \
    /app/deployment/apptainer_entry.sh \
    /bin/bash
    # python /app/experiments/k8s.py

# apptainer shell /projappl/project_2012346/llm-ran.sif
