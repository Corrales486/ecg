from builtins import str
import argparse
import numpy as np
import json
import load
import util
from joblib import Memory

memory = Memory(cachedir='./cache')

@memory.cache
def get_model_pred_probs(model_path, x):
    from keras.models import load_model
    model = load_model(model_path)
    probs = model.predict(x, verbose=1)
    return probs


def get_ensemble_pred_probs(model_paths, x):
    print("Averaging " + str(len(model_paths)) + " model predictions...")
    all_model_probs = [get_model_pred_probs(model_path, x)
                       for model_path in model_paths]
    probs = np.mean(all_model_probs, axis=0)
    return probs

def get_saved_pred_probs(path):
    return np.load(path)


def predict(args, train_params, test_params):
    x, gt, processor, loader = load.load_test(
        test_params,
        train_params=train_params,
        split=args.split)
    probs = get_ensemble_pred_probs(args.model_paths, x)
    save_prediction_probs(probs)

def save_prediction_probs(probs):
    np.save('./preds', probs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("test_config_file", help="path to config file")
    parser.add_argument(
        'model_paths',
        nargs='+',
        help="path to models")
    parser.add_argument("--split", help="train/val", choices=['train', 'test'],
                        default='test')
    args = parser.parse_args()
    train_params = util.get_model_params(args.model_paths[0])  # FIXME: bug
    test_params = train_params.copy()
    test_new_params = json.load(open(args.test_config_file, 'r'))
    test_params.update(test_new_params)
    if "label_review" in test_new_params["data_path"]:
        assert(args.split == 'test')
    predict(args, train_params, test_params)
