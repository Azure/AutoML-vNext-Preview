import sklearn
import pandas as pd
from sklearn.model_selection import train_test_split

data = sklearn.datasets.load_boston()
target_feature = 'y'
continuous_features = data.feature_names
data_df = pd.DataFrame(data.data, columns=data.feature_names)

X_train, X_test, y_train, y_test = train_test_split(
    data_df,
    data.target,
    test_size=0.2,
    random_state=7)

train_data = X_train.copy()
test_data = X_test.copy()
train_data[target_feature] = y_train
test_data[target_feature] = y_test

print("Saving to files")
train_data.to_parquet("boston_train.parquet", index=False)
test_data.to_parquet("boston_test.parquet", index=False)
