import pandas as pd

# Read both datasets
sam_df = pd.read_csv("ml_training_dataset_sam.csv")
teammate_df = pd.read_csv("ml_training_dataset_teammate.csv")

# Combine them
combined_df = pd.concat(
    [sam_df, teammate_df],
    ignore_index=True
)

# Remove duplicate rows
combined_df.drop_duplicates(inplace=True)

# Shuffle the dataset
combined_df = combined_df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

# Save the combined dataset
combined_df.to_csv(
    "combined_training_dataset.csv",
    index=False
)

print("--------------------------------")
print("DATASETS MERGED SUCCESSFULLY")
print("Total samples:", len(combined_df))
print("Saved as: combined_training_dataset.csv")