import shap
from sklearn.model_selection import train_test_split


X, y = shap.datasets.adult()
print("Data fetched")
target_feature = "income"
y = [1 if y_i else 0 for y_i in y]

full_data = X.copy()
full_data[target_feature] = y

data_train, data_test = train_test_split(
    full_data, test_size=4000, random_state=96132, stratify=full_data[target_feature]
)

# Don't write out the row indices to the CSV.....
print("Saving to files")
data_train.to_parquet("adult_train.parquet", index=False)
data_test.to_parquet("adult_test.parquet", index=False)
