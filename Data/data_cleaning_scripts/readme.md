This folder contains scripts that clean data files so they can be used in classification models. Data cleaning scripts should take inputs from `../preliminary_data/` and ouput files to `../cleaned_data/` if the data has been sufficiently processed.

Contents:
* `full_text_data_cleaning_fulldataset.ipynb` - cleans the article text for entire dataset
* `fulltext_and_source_data_cleaning.ipynb` - cleans the quote text and speaker data for entire dataset
* `make_sample_dataset.ipynb` - creates a sample dataset containing only 2,000 rows from the original dataset
* `speaker_name_cleaning.ipynb` - cleans speaker name data
* `speaker_name_cleaning.py` - script for cleaning speaker name data
