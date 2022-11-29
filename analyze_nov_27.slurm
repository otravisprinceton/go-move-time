#!/bin/bash
#SBATCH --job-name=Travis-job-8  # create a short name for your job
#SBATCH --output=slurm-%A.%a.out # stdout file
#SBATCH --error=slurm-%A.%a.err  # stderr file
#SBATCH --nodes=1                # node count
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --cpus-per-task=8        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --memory=32G             # memory (4G per core)
#SBATCH --time=020:00:00         # total run time limit (HH:MM:SS)
#SBATCH --array=1-2000           # job array with index values 0, 1, 2, 3, 4
#SBATCH --mail-type=all          # send email on job start, end and fault
#SBATCH --mail-user=otravis@princeton.edu

echo "My SLURM_ARRAY_JOB_ID is $SLURM_ARRAY_JOB_ID."
echo "My SLURM_ARRAY_TASK_ID is $SLURM_ARRAY_TASK_ID"
echo "Executing on the machine:" $(hostname)

module purge
module load anaconda3/2021.11
conda activate kata-env

python -u katashell_della.py
