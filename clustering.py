import numpy as np
from sklearn.cluster import KMeans

SAMPLE_N = 100
FEATURE_N = 3
CLUSTER_N = 4
OUT_CSV_FILE = r'd:\temp\data_with_4_cluster.csv'


def bench_k_means(estimator, model_name, input_data):
    print model_name
    estimator.fit(input_data)
    return estimator.labels_


def clustering_using_k_means():
    np.random.seed(42)
    raw_data = np.random.uniform(-1, 1, size=SAMPLE_N * FEATURE_N)
    data = raw_data.reshape([SAMPLE_N, FEATURE_N])
    print("n_digits: %d, \t n_samples %d, \t n_features %d"
          % (CLUSTER_N, SAMPLE_N, FEATURE_N))

    labels = bench_k_means(KMeans(init='k-means++', n_clusters=CLUSTER_N, n_init=10),
                           model_name="k-means++", input_data=data)
    print labels
    label_col = np.array(labels).reshape([SAMPLE_N, 1])
    data_with_label = np.append(data, label_col, axis=1)
    np.savetxt(OUT_CSV_FILE, data_with_label, delimiter=',')


def main():
    # print config.directory['windows']
    clustering_using_k_means()

if __name__ == "__main__":
    main()
