# Student Alcohol Consumption: A Descriptive Data Analysis

A non-interactive Streamlit dashboard based on the original Colab notebook. The cleaned mathematics-student dataset is included.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publish on Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py`, `student-mat-cleaned.csv`, and `requirements.txt` from this folder (not the ZIP itself).
2. Go to https://share.streamlit.io/ and create an app from your GitHub repository.
3. Set the main file path to `app.py` and deploy.
4. Edit `Prepared by: [Your Name]` in `app.py` to add your name.

## Notes

- The CSV has 395 rows, 10 columns and no missing cells. Seven columns are used for charts.
- One complete duplicate row was retained to keep analysis consistent with the notebook.
- Some notebook comments had arithmetic or interpretation errors. The Streamlit findings use calculations from the supplied CSV.
- The dataset is observational: associations do not imply causation.
- Dataset provenance and author information are in the final section of the app.
