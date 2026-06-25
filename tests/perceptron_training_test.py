import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.engine.perceptron_train import train_perceptron
from app.engine.perceptron_predict import predict_label

# Minimal training dataset with user_id included
training_data = [
    {"user_id": "u1", "comments": 4, "assignments": 1, "transitions": 2, "label": 1},
    {"user_id": "u2", "comments": 0, "assignments": 0, "transitions": 0, "label": 0},
    {"user_id": "u3", "comments": 1, "assignments": 0, "transitions": 1, "label": 1},
]

def run_test():
    print("Training perceptron...")
    train_perceptron(training_data)

    print("Testing predictions...")
    test_stats = {"comments": 2, "assignments": 0, "transitions": 1}
    label = predict_label(test_stats)

    print("Predicted label:", label)

if __name__ == "__main__":
    run_test()
