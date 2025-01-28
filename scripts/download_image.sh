#!/bin/bash
#SBATCH --job-name=download_image       # Job name
#SBATCH --account=project_2012346       # Billing project, has to be defined!
#SBATCH --time=02:00:00             # Max. duration of the job
#SBATCH --cpus-per-task=8
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1G            # Memory to reserve per core
#SBATCH --partition=small           # Job queue (partition)
#SBATCH --gres=nvme:128
##SBATCH --mail-type=BEGIN          # Uncomment to enable mail

# sinteractive --account project_2012346 --time 1:00:00 -m 16G --tmp 128 --cores 8

# Let's use the fast local drive for temporary storage
export APPTAINER_TMPDIR=$LOCAL_SCRATCH
export APPTAINER_CACHEDIR=$LOCAL_SCRATCH

# This is just to avoid some annoying warnings
unset XDG_RUNTIME_DIR

# Change directory to where you wish to store the image
cd /projappl/project_2012346

# Do the actual conversion
apptainer build --force llm-ran.sif docker://chenseanxy/llm-ran 
