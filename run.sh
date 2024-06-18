### Analysis pipeline
# 1. Process sensor with predetermined frequency
srun  --cpus-per-task 4 python3 -m src.features.momomood.sensors.run_processor processor.sensor=call processor.frequency=4epochs
srun  --cpus-per-task 4 python3 -m src.features.corona.sensors.run_processor processor.sensor=activity processor.frequency=4epochs

srun  --cpus-per-task 4 python3 -m src.features.momomood.eigenbehav.run_processor 
python3 -m src.features.corona.sensors.run_processor corona.sensor=survey corona.frequency=all

# 2. Vectorize stuffs
srun  --cpus-per-task 4 python3 -m src.features.momomood.vectorize_momo vectorize.frequency=4epochs
srun  --cpus-per-task 4 python3 -m src.features.corona.vectorize_corona vectorize.frequency=4epochs,7ds,14ds --multirun

# 3. Compute baseline rhythm
python3 -m src.baseline_behav.baseline_rhythm baseline_rhythm.study=corona baseline_rhythm.frequency=4epochs baseline_rhythm.method=cluster

# 3.1 Compute outliers
python3 -m src.baseline_behav.behavioral_outliers outliers.study=corona outliers.frequency=4epochs outliers.method=std outliers.threshold=2

# 4. Create dataset for analysis
python3 -m src.data.make_dataset 

### Util script
# Folder backup
rsync -av --progress data/ data.backup

### Rapids on the queue
#!/bin/bash

#SBATCH --time=00:10:00
#SBATCH --mem=1G
#SBATCH --output=out.log
SING_IMAGE=../RAPIDS_27032024.sif 
singularity run -B /scratch -B /m ../RAPIDS.sif
singularity shell -B /m -B /scratch -B $PWD:/rapids --cwd /rapids -s /bin/bash ../RAPIDS.sif
singularity exec -B /m -B /scratch -B $PWD:/rapids --cwd /rapids -s /bin/bash ../RAPIDS.sif

srun  --cpus-per-task 4 singularity exec -B /scratch -B /m ../RAPIDS.sif ./rapids "$1" --cores 4
