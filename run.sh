### Analysis pipeline
# 1. Process sensor with predetermined frequency
python3 -m src.features.momomood.sensors.run_processor processor.sensor=call processor.frequency=4epochs
python3 -m src.features.corona.sensors.run_processor corona.sensor=activity corona.frequency=4epochs

# 2. Vectorize stuffs
python3 -m src.features.momomood.vectorize_momo vectorize.frequency=4epochs
python3 -m src.features.corona.vectorize_corona vectorize.frequency=4epochs,7ds,14ds --multirun

# 3. Compute baseline rhythm
python3 -m src.features.baseline_rhythm


### Util script
# Folder backup
rsync -av --progress --delete data/ data.backup
