# Cleaned Data
This folder should house the final cleaned data, ready for use in classification models. When adding files, be sure to edit this readme file with a description of the data you've added:

## Data Files
- `GNI88_cleaned_data.csv`: This dataset is the result of `gni88 02DEC21.json.zip`[full texts] and `GNI88.csv`[labelled, quote-level data] being run through the `fulltext_and_source_data_cleaning.ipynb` notebook, which cleans the full texts, cleans the source names in the labelled data, and adds the full texts to the labelled data as a column. The dataset is too large to be uploaded to GitHub, so here is the [link](https://drive.google.com/file/d/1CdHkJ2yEV1gJiOfuHWNz4vVLEECWK6I3/view?usp=sharing) to the dataset for download. 
- `GNI88_cleaned_sample.csv`: A sample of 2,000 rows from the full dataset for students to familiarize themselves with the data and use in EDA/feature creation stages. This sample dataset was created with `Data/data_cleaning_scripts/make_sample_dataset.ipynb`.
- `data.csv`: *Desription of data goes here*
