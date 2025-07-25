import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

# Example: Load sequence data (replace with real FASTQ/VCF parser)
X = np.random.rand(100, 1000)  # 100 samples, 1000 features
y = np.random.randint(0, 2, 100)

model = models.Sequential([
    layers.Input(shape=(1000,)),
    layers.Dense(256, activation='relu'),
    layers.Dense(128, activation='relu'),
    layers.Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X, y, epochs=10, batch_size=16)

model.save('models/diabetes_seq_tf.h5')
