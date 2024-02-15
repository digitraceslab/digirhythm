# 1. Process sensor with predetermined frequency
python3 -m src.features.momomood.sensors.run_processor processor.sensor=call processor.frequency=4epochs

# 2. Vectorize stuffs
python3 -m src.features.momomood.vectorize_momo

# 3. Compute similarity matrix
python3 -m src.features.similarity_matrix