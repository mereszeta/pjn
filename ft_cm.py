import numpy as np
from sklearn.metrics import confusion_matrix


def parse_labels(path):
    with open(path, encoding="utf-8") as f:
        content = f.read().split()
        return np.array(list(map(lambda x: 1 if x[9:] == "updates" else 0, content)))


if __name__ == "__main__":
    variants = ['_full_text', "_ten_percents", "_ten_lines", "_one_line"]
    for variant in variants:
        test_labels = parse_labels("./test_labels" + variant)
        pred_labels = parse_labels("./pred_labels" + variant)
        eq = 0
        for i in range(len(test_labels)):
            if test_labels[i] == pred_labels[i]:
                eq += 1
        conf_mat = confusion_matrix(test_labels, pred_labels)
        precission_up = conf_mat[1][1] / (conf_mat[1][1] + conf_mat[0][1])
        recall_up = conf_mat[1][1] / (conf_mat[1][1] + conf_mat[1][0])
        f1_up = 2 * precission_up * recall_up / (precission_up + recall_up)
        print("variant: " + str(variant) + "label: updates" + " precission: " + str(precission_up) + " recall: " + str(
            recall_up) + " f1: " + str(f1_up))
        precission_st = conf_mat[0][0] / (conf_mat[0][0] + conf_mat[1][0])
        recall_st = conf_mat[0][0] / (conf_mat[0][0] + conf_mat[0][1])
        f1_st = 2 * precission_st * recall_st / (precission_st + recall_st)
        print("variant: " + str(variant) + "label: standalones" + " precission: " + str(
            precission_st) + " recall: " + str(
            recall_st) + " f1: " + str(f1_st))
