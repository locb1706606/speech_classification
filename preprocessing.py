import argparse
from multiprocessing.pool import Pool
from os import listdir
import numpy as np
import librosa
from os.path import join
import tqdm
import joblib


def windows(data, window_size):
    start = 0
    i = 0
    max_i = 1000
    while (start < len(data)) and (i < max_i):
        yield int(start), int(start + window_size)
        start += window_size
        i += 1


def extract_features(file_data, bands=60, frames=11):
    label, filepath = file_data
    window_size = 512 * (frames - 1)
    log_specgrams = []

    sound_clip, s = librosa.load(filepath)
    for start, end in windows(sound_clip, window_size):
        if len(sound_clip[start:end]) == window_size:
            signal = sound_clip[start:end]
            melspec = librosa.feature.melspectrogram(signal, n_mels=bands)
            logspec = librosa.logamplitude(melspec)
            logspec = logspec.T.flatten()[:, np.newaxis].T
            log_specgrams.append(logspec)
    log_specgrams = np.asarray(log_specgrams).reshape(len(log_specgrams), bands, frames, 1)
    features = np.concatenate((log_specgrams, np.zeros(np.shape(log_specgrams))), axis=3)
    for i in range(len(features)):
        features[i, :, :, 1] = librosa.feature.delta(features[i, :, :, 0])
    return label, features


def get_duration(filepath):
    sound_clip, sr = librosa.load(filepath)
    duration = librosa.get_duration(y=sound_clip, sr=sr)
    return duration


def make_train_data():
    TRAIN_FOLDER = "data/train_10"
    folders = listdir(TRAIN_FOLDER)
    files = []
    for label in folders:
        tmp = listdir(join(TRAIN_FOLDER, label))
        tmp = [join(TRAIN_FOLDER, label, file) for file in tmp]
        tmp = [(label, file) for file in tmp]
        files.extend(tmp)

    p = Pool(20)
    n = len(files)
    features = list(tqdm.tqdm(p.imap(extract_features, files), total=n))

    joblib.dump(features, "tmp/train_full.data.bin")
    print(len(features))


def make_test_data():
    TEST_FOLDER = "data/test_10"
    tmp = listdir(TEST_FOLDER)
    files = []
    for label in tmp:
        file = join(TEST_FOLDER, label)
        files.append((label, file))
    p = Pool(20)
    n = len(files)
    features = list(tqdm.tqdm(p.imap(extract_features, files), total=n))

    joblib.dump(features, "tmp/test.data.bin")
    print(len(features))


if __name__ == '__main__':
    parser = argparse.ArgumentParser("preprocessing.py")
    parser.add_argument("--mode", help="train or test")

    args = parser.parse_args()
    mode = args.mode
    if mode == "train":
        make_train_data()
    elif mode == "test":
        make_test_data()