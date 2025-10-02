# train_imaging_model.py
import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam


def create_synthetic_dataset():
    """Create a small synthetic dataset for demo purposes"""
    base_dir = "data/xrays"

    # Create directories if they don't exist
    for category in ["normal", "pneumonia", "covid_suspect"]:
        os.makedirs(f"{base_dir}/{category}", exist_ok=True)

    print(f"Creating synthetic dataset in {base_dir}")

    # Create simple synthetic images
    for i in range(20):
        # Normal: mostly uniform with some noise
        img = np.random.randint(200, 255, (64, 64, 3), dtype=np.uint8)
        Image.fromarray(img).save(f"{base_dir}/normal/normal_{i}.png")

        # Pneumonia: with some cloudy regions
        img = np.random.randint(180, 255, (64, 64, 3), dtype=np.uint8)
        # Add some cloudy regions
        for _ in range(5):
            x, y = np.random.randint(0, 64, 2)
            r = np.random.randint(5, 15)
            y, x = np.ogrid[-x:64 - x, -y:64 - y]
            mask = x * x + y * y <= r * r
            img[mask] = np.random.randint(100, 180, 3)
        Image.fromarray(img).save(f"{base_dir}/pneumonia/pneumonia_{i}.png")

        # COVID suspect: with more distinct patterns
        img = np.random.randint(150, 255, (64, 64, 3), dtype=np.uint8)
        # Add some ground glass-like patterns
        for _ in range(8):
            x, y = np.random.randint(0, 64, 2)
            r = np.random.randint(3, 10)
            y, x = np.ogrid[-x:64 - x, -y:64 - y]
            mask = x * x + y * y <= r * r
            img[mask] = np.random.randint(150, 200, 3)
        Image.fromarray(img).save(f"{base_dir}/covid_suspect/covid_{i}.png")

    print(f"Created 20 synthetic images for each class in {base_dir}")

    # Verify the images were created
    for category in ["normal", "pneumonia", "covid_suspect"]:
        path = f"{base_dir}/{category}"
        count = len([f for f in os.listdir(path) if f.endswith('.png')])
        print(f"Found {count} images in {path}")


def train_model():
    # Dataset path
    data_dir = "data/xrays"

    # Create synthetic dataset if it doesn't exist
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        create_synthetic_dataset()
    else:
        # Check if we have images
        has_images = False
        for category in ["normal", "pneumonia", "covid_suspect"]:
            if os.path.exists(f"{data_dir}/{category}") and os.listdir(f"{data_dir}/{category}"):
                has_images = True
                break

        if not has_images:
            create_synthetic_dataset()

    # Image preprocessing
    img_size = (64, 64)
    batch_size = 4  # Reduced batch size to avoid issues with small dataset

    datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

    try:
        train_gen = datagen.flow_from_directory(
            data_dir,
            target_size=img_size,
            batch_size=batch_size,
            class_mode="categorical",
            subset="training"
        )

        val_gen = datagen.flow_from_directory(
            data_dir,
            target_size=img_size,
            batch_size=batch_size,
            class_mode="categorical",
            subset="validation"
        )

        # Check if we have data
        if train_gen.samples == 0:
            raise ValueError("No training data found")

    except Exception as e:
        print(f"Error creating data generators: {e}")
        print("Creating new synthetic dataset...")
        create_synthetic_dataset()

        # Try again
        train_gen = datagen.flow_from_directory(
            data_dir,
            target_size=img_size,
            batch_size=batch_size,
            class_mode="categorical",
            subset="training"
        )

        val_gen = datagen.flow_from_directory(
            data_dir,
            target_size=img_size,
            batch_size=batch_size,
            class_mode="categorical",
            subset="validation"
        )

    # Simple CNN
    model = Sequential([
        Conv2D(16, (3, 3), activation="relu", input_shape=(64, 64, 3)),
        MaxPooling2D(2, 2),
        Conv2D(32, (3, 3), activation="relu"),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(64, activation="relu"),
        Dropout(0.3),
        Dense(3, activation="softmax")  # 3 classes
    ])

    model.compile(optimizer=Adam(0.001),
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])

    print("Starting model training...")
    history = model.fit(train_gen, epochs=10, validation_data=val_gen)

    # Save model
    os.makedirs("models", exist_ok=True)
    model.save("models/imaging_cnn.h5")
    print("✅ Model saved to models/imaging_cnn.h5")

    return model

if __name__ == "__main__":
    train_model()