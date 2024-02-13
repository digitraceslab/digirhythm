# Process sensor with predetermined frequency
python3 -m src.features.momomood.sensors.run_processor processor.sensor=call processor.frequency=4epochs

# Vectorize stuffs
python3 -m src.features.momomood.vectorize_momo
