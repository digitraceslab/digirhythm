### Analysis pipeline
# 1. Process sensor with predetermined frequency
python3 -m src.features.momomood.sensors.run_processor processor.sensor=call processor.frequency=4epochs
python3 -m src.features.corona.sensors.run_processor corona.sensor=activity corona.frequency=4epochs

# 2. Vectorize stuffs
python3 -m src.features.momomood.vectorize_momo vectorize.frequency=4epochs
python3 -m src.features.corona.vectorize_corona vectorize.frequency=4epochs,7ds,14ds --multirun

# 3. Compute baseline rhythm
python3 -m src.features.baseline_rhythm baseline_rhythm.study=momo baseline_rhythm.frequency=4epochs

### Util script
# Folder backup
rsync -av --progress --delete data/ data.backup

### Rapids on the queue
#!/bin/bash

#SBATCH --time=00:10:00
#SBATCH --mem=1G
#SBATCH --output=out.log
SING_IMAGE=../RAPIDS_27032024.sif 
singularity run -B /scratch -B /m ../RAPIDS_27032024.sif  
srun  --cpus-per-task 4 singularity exec -B /scratch -B /m ../RAPIDS_27032024.sif ./rapids "$1" --cores 4