import os
import random
import pandas as pd


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

METADATA_FILE = "files_metadata.csv"
OUTPUT_FILE = "sampled_files.csv"

TARGET_SAMPLE_SIZE = 500
RANDOM_STATE = 42


# --------------------------------------------------
# RANDOM SEED
# --------------------------------------------------

random.seed(RANDOM_STATE)


# --------------------------------------------------
# LOAD REAL FILE METADATA
# --------------------------------------------------

df = pd.read_csv(METADATA_FILE)

print("--------------------------------")
print("REAL FILES LOADED:", len(df))


# --------------------------------------------------
# REMOVE FILES THAT NO LONGER EXIST
# --------------------------------------------------

df = df[
    df["file_path"].apply(os.path.isfile)
].copy()

print(
    "EXISTING FILES:",
    len(df)
)


# --------------------------------------------------
# CONVERT TIMESTAMPS
# --------------------------------------------------

df["created"] = pd.to_datetime(
    df["created"],
    format="mixed",
    errors="coerce"
)

df["modified"] = pd.to_datetime(
    df["modified"],
    format="mixed",
    errors="coerce"
)
invalid_created_dates = df["created"].isna().sum()

invalid_modified_dates = df["modified"].isna().sum()


print(
    "INVALID CREATED DATES:",
    invalid_created_dates
)

print(
    "INVALID MODIFIED DATES:",
    invalid_modified_dates
)

# --------------------------------------------------
# CALCULATE TEMPORARY SAMPLING FEATURES
# --------------------------------------------------

current_time = pd.Timestamp.now()

df["sampling_file_age_days"] = (
    current_time - df["created"]
).dt.days

df["sampling_days_since_modified"] = (
    current_time - df["modified"]
).dt.days


# --------------------------------------------------
# HANDLE INVALID VALUES
# --------------------------------------------------

df["sampling_file_age_days"] = (
    df["sampling_file_age_days"]
    .fillna(0)
    .clip(lower=0)
)

df["sampling_days_since_modified"] = (
    df["sampling_days_since_modified"]
    .fillna(0)
    .clip(lower=0)
)


# --------------------------------------------------
# SIZE CATEGORY
# --------------------------------------------------

def get_size_category(size_bytes):

    if size_bytes < 1024 * 1024:
        return "SMALL"

    if size_bytes < 100 * 1024 * 1024:
        return "MEDIUM"

    if size_bytes < 1024 * 1024 * 1024:
        return "LARGE"

    return "VERY_LARGE"


df["sampling_size_category"] = (
    df["size_bytes"].apply(
        get_size_category
    )
)


# --------------------------------------------------
# MODIFICATION RECENCY CATEGORY
# --------------------------------------------------

def get_recency_category(days):

    if days <= 7:
        return "VERY_RECENT"

    if days <= 30:
        return "RECENT"

    if days <= 180:
        return "MODERATE"

    if days <= 365:
        return "OLD"

    return "VERY_OLD"


df["sampling_recency_category"] = (
    df["sampling_days_since_modified"].apply(
        get_recency_category
    )
)


# --------------------------------------------------
# STORAGE CONTEXT
# --------------------------------------------------

def get_storage_context(file_path):

    normalized_path = os.path.normcase(
        os.path.abspath(file_path)
    )

    path_parts = [
        part.lower()
        for part in normalized_path.split(os.sep)
    ]

    contexts = {
        "desktop": "DESKTOP",
        "documents": "DOCUMENTS",
        "downloads": "DOWNLOADS",
        "videos": "VIDEOS",
        "pictures": "PICTURES",
        "music": "MUSIC"
    }

    for folder_name, context_name in contexts.items():

        if folder_name in path_parts:
            return context_name

    return "OTHER"


df["sampling_storage_context"] = (
    df["file_path"].apply(
        get_storage_context
    )
)
print("--------------------------------")
print(df["sampling_storage_context"].value_counts())

# --------------------------------------------------
# NORMALIZE EXTENSION
# --------------------------------------------------

df["extension"] = (
    df["extension"]
    .fillna("[NO_EXTENSION]")
    .astype(str)
    .str.lower()
)


# --------------------------------------------------
# BUILD INNER DIVERSITY GROUP
# --------------------------------------------------

df["sampling_diversity_group"] = (
    df["sampling_size_category"]
    + "|"
    + df["sampling_recency_category"]
    + "|"
    + df["extension"]
)


# --------------------------------------------------
# SHOW AVAILABLE STORAGE CONTEXTS
# --------------------------------------------------

storage_contexts = (
    df["sampling_storage_context"]
    .dropna()
    .unique()
    .tolist()
)


print(
    "STORAGE CONTEXTS FOUND:",
    len(storage_contexts)
)

print(
    storage_contexts
)


# --------------------------------------------------
# PREPARE DIVERSE FILE ORDER FOR EACH CONTEXT
# --------------------------------------------------

context_file_queues = {}


for storage_context in storage_contexts:

    context_df = df[
        df["sampling_storage_context"]
        == storage_context
    ].copy()


    diversity_groups = list(
        context_df.groupby(
            "sampling_diversity_group",
            sort=False
        )
    )


    random.shuffle(
        diversity_groups
    )


    group_positions = {
        group_name: 0
        for group_name, group_df in diversity_groups
    }


    context_rows = []


    while True:

        added_in_round = False


        for group_name, group_df in diversity_groups:

            position = group_positions[
                group_name
            ]


            if position >= len(group_df):
                continue


            context_rows.append(
                group_df.iloc[position]
            )


            group_positions[
                group_name
            ] += 1


            added_in_round = True


        if not added_in_round:
            break


    context_file_queues[
        storage_context
    ] = context_rows


# --------------------------------------------------
# DYNAMIC CONTEXT ROUND-ROBIN SAMPLING
# --------------------------------------------------

sampled_rows = []

context_positions = {
    storage_context: 0
    for storage_context in storage_contexts
}


active_contexts = storage_contexts.copy()


while (
    len(sampled_rows) < TARGET_SAMPLE_SIZE
    and active_contexts
):

    random.shuffle(
        active_contexts
    )


    next_active_contexts = []


    for storage_context in active_contexts:

        if len(sampled_rows) >= TARGET_SAMPLE_SIZE:
            break


        position = context_positions[
            storage_context
        ]


        context_queue = context_file_queues[
            storage_context
        ]


        if position >= len(context_queue):
            continue


        sampled_rows.append(
            context_queue[position]
        )


        context_positions[
            storage_context
        ] += 1


        if (
            context_positions[storage_context]
            < len(context_queue)
        ):

            next_active_contexts.append(
                storage_context
            )


    active_contexts = next_active_contexts


# --------------------------------------------------
# CREATE SAMPLE DATAFRAME
# --------------------------------------------------

sampled_df = pd.DataFrame(
    sampled_rows
)


# --------------------------------------------------
# KEEP METADATA + SAMPLING CONTEXT
# --------------------------------------------------

output_columns = [
    "file_id",
    "file_name",
    "file_path",
    "size_bytes",
    "extension",
    "created",
    "modified",
    "last_accessed",
    "sampling_file_age_days",
    "sampling_days_since_modified",
    "sampling_size_category",
    "sampling_recency_category",
    "sampling_storage_context"
]


sampled_df = sampled_df[
    output_columns
]


# --------------------------------------------------
# SAVE SAMPLE
# --------------------------------------------------

sampled_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

print("--------------------------------")
print("DIVERSE SAMPLING COMPLETED")

print(
    "Total real files:",
    len(df)
)

print(
    "Files selected:",
    len(sampled_df)
)


print("--------------------------------")
print("Storage contexts:")

print(
    sampled_df[
        "sampling_storage_context"
    ].value_counts()
)


print("--------------------------------")
print("Size categories:")

print(
    sampled_df[
        "sampling_size_category"
    ].value_counts()
)


print("--------------------------------")
print("Recency categories:")

print(
    sampled_df[
        "sampling_recency_category"
    ].value_counts()
)


print("--------------------------------")

print(
    "Unique extensions:",
    sampled_df[
        "extension"
    ].nunique()
)

print(
    "Sample saved to:",
    OUTPUT_FILE
)