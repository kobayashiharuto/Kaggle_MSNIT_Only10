from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from data_controller import get_image_and_labels
import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, BatchNormalization
from sklearn.model_selection import train_test_split


# 学習結果をpltで表示
def show_train_history(train_history, train, validation):
    plt.plot(train_history.history[train])
    plt.plot(train_history.history[validation])
    plt.title('Train History')
    plt.ylabel(train)
    plt.xlabel('Epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.show()


test_df = pd.read_csv("data/test.csv")
train_df = pd.read_csv("data/train.csv")

# 訓練用データを読み込む
train_images, train_labels = get_image_and_labels(
    path=r'C:\Users\owner\Desktop\Image_tool\image_randomizer\out\mnist_data')
train_images = train_images.reshape(train_images.shape + (1,))

# テスト用データを読み込む
test_data = pd.read_csv("data/train.csv")

# test_data から、画像とラベルを取り出し、numpyの配列に変換
test_images = test_data.iloc[:, 1:].values
test_images = test_images.astype(np.float)
test_labels = test_data.iloc[:, 0].values
test_labels = test_labels.astype(np.float)

# CNN で扱えるように次元を変換
test_images = test_images.reshape(test_images.shape[0], 28, 28, 1)

# 正規化
test_images = test_images / 255
train_images = train_images / 255

print(train_images.shape)
print(train_labels.shape)
print(test_images.shape)
print(test_labels.shape)

# CNN でMNISTを分類するモデルを構築
model = Sequential([
    Conv2D(64, (5, 5), padding='Same',
           activation='relu', input_shape=(28, 28, 1), kernel_initializer='he_normal'),
    BatchNormalization(),
    Conv2D(128, (5, 5),
           padding='Same', activation='relu', kernel_initializer='he_normal'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.3),
    Conv2D(128, (3, 3),
           padding='Same', activation='relu', kernel_initializer='he_normal'),
    BatchNormalization(),
    Conv2D(256, (3, 3),
           padding='Same', activation='relu', kernel_initializer='he_normal'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.3),
    Conv2D(256, (3, 3),
           padding='Same', activation='relu', kernel_initializer='he_normal'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.3),
    Flatten(),
    Dense(256, activation="relu", kernel_initializer='he_normal'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(10, activation="softmax"),
])
model.summary()

model.compile(
    optimizer=tf.keras.optimizers.Adam(lr=0.003),
    loss='sparse_categorical_crossentropy',
    metrics=['acc']
)

history = model.fit(
    train_images, train_labels, epochs=500,
    batch_size=512,
    validation_data=(test_images, test_labels),
    callbacks=[
        EarlyStopping(min_delta=0.001, patience=10, verbose=1)
    ],
)

show_train_history(history, 'acc', 'val_acc')

model.save('models/model.h5')

# test_df から、画像を取り出し、numpyの配列に変換
test_images = test_df.values
test_images = test_images.astype(np.float)
test_images = test_images.reshape(test_images.shape[0], 28, 28, 1)
test_images = test_images / 255

# test
model = tf.keras.models.load_model('models/model.h5')
predict = model.predict(test_images)
predict = np.argmax(predict, axis=1)
predict = predict.astype(np.int32)

# 結果をcsvで出力
predict_df = pd.DataFrame(
    {"ImageId": range(1, len(predict)+1), "Label": predict})
predict_df.to_csv("result/result.csv", index=False)

# 結果を64枚一覧で表示
plt.figure(figsize=(10, 10))
for i in range(64):
    plt.subplot(8, 8, i+1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(test_images[i].reshape(28, 28), cmap=plt.cm.binary)
    plt.xlabel(f'{predict[i]}')
plt.show()
