from pathlib import Path
import io
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Student Alcohol Consumption: A Descriptive Data Analysis", layout="wide")
sns.set_theme(style="whitegrid")
DATA_PATH = Path(__file__).with_name('student-mat-cleaned.csv')
COLS = ['sex', 'Walc', 'Dalc', 'G3', 'health', 'failures', 'goout']
DEFINITIONS = {
    'sex': ('Student gender', 'F = Female; M = Male'),
    'Walc': ('Weekend alcohol consumption', '1 = very low; 5 = very high'),
    'Dalc': ('Workday alcohol consumption', '1 = very low; 5 = very high'),
    'G3': ('Final mathematics grade', '0–20 points; below 10 generally considered failing'),
    'health': ('Current self-reported health status', '1 = very bad; 5 = very good'),
    'failures': ('Number of past class failures', '0–4; source category 4 means 3 or more failures'),
    'goout': ('Frequency of going out with friends', '1 = very low; 5 = very high'),
}

def pct(v):
    return f'{v:.1f}%'

def plot_bar(data, title, xlabel, ylabel, legend_title=None):
    fig, ax = plt.subplots(figsize=(8.6, 4.5))
    data.plot(kind='bar', rot=0, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis='y', alpha=.3)
    if legend_title:
        ax.legend(title=legend_title)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def plot_heatmap(data, title, xlabel, ylabel, is_percent=False):
    fig, ax = plt.subplots(figsize=(8.6, 4.7))
    sns.heatmap(data, annot=True, fmt='.1f' if is_percent else 'd', cmap='Blues', ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.title('Student Alcohol Consumption: A Descriptive Data Analysis')
st.caption('Descriptive statistics and visualization | Portuguese secondary-school mathematics students')

st.header('1. About the Dataset')
st.write('This analysis examines reported workday and weekend alcohol consumption among secondary-school students in Portugal, and how consumption patterns differ by academic performance, health status, gender, and social activity. The mathematics-course records come from the Student Performance dataset collected from two Portuguese secondary schools, published by Paulo Cortez and Alice Silva, and distributed through Kaggle and the UCI Machine Learning Repository.')
st.write('This is an observational dataset. The comparisons and correlations describe associations, not cause-and-effect relationships.')

if DATA_PATH.exists():
    raw = pd.read_csv(DATA_PATH, sep=None, engine='python')
else:
    st.info('Upload **student-mat-cleaned.csv** to display the dashboard.')
    uploaded = st.file_uploader('Upload cleaned dataset (CSV)', type=['csv'])
    if uploaded is None:
        st.stop()
    raw = pd.read_csv(uploaded, sep=None, engine='python')

missing = [c for c in COLS if c not in raw.columns]
if missing:
    st.error('The CSV does not include the following required columns: ' + ', '.join(missing))
    st.stop()
a = raw[COLS].copy()
for col in ['Walc', 'Dalc', 'G3', 'health', 'failures', 'goout']:
    a[col] = pd.to_numeric(a[col], errors='coerce')
a['sex'] = a['sex'].astype('string').str.strip().str.upper()
valid = a.dropna(subset=COLS)
if len(valid) != len(a):
    st.warning(f'{len(a) - len(valid)} rows have missing or invalid values in selected variables and were excluded from charts. Total records still reflects the input CSV.')
a = valid
if a.empty:
    st.error('No complete records remain for the selected variables.')
    st.stop()

st.header('2. Dataset Overview')
c1, c2, c3 = st.columns(3)
c1.metric('Records in source file', f'{len(raw):,}')
c2.metric('Records used in plots', f'{len(a):,}')
c3.metric('Variables used', len(COLS))
st.subheader('Selected Variables and Their Meanings')
st.dataframe(pd.DataFrame([{'Variable': k, 'Description': v[0], 'Values / Scale': v[1]} for k, v in DEFINITIONS.items()]), hide_index=True, use_container_width=True)
with st.expander('Preview dataset'):
    st.dataframe(a.head(10), use_container_width=True)

st.header('3. Academic Performance')
st.subheader('Average Final Grade by Workday and Weekend Consumption')
grade_table = pd.DataFrame({'Weekend': a.groupby('Walc')['G3'].mean(), 'Workday': a.groupby('Dalc')['G3'].mean()}).reindex(range(1, 6))
plot_bar(grade_table, 'Average Final Grade by Alcohol Consumption Level', 'Consumption Level (1 = very low, 5 = very high)', 'Average Final Grade (0–20)', 'Period')
st.write(f"Students at the lowest consumption level had average final grades of {grade_table.loc[1, 'Weekend']:.2f} for Walc and {grade_table.loc[1, 'Workday']:.2f} for Dalc. The lowest averages were at Dalc {grade_table['Workday'].idxmin()} ({grade_table['Workday'].min():.2f}) and Walc {grade_table['Weekend'].idxmin()} ({grade_table['Weekend'].min():.2f}). Grades did not consistently drop as alcohol consumption levels increased.")
st.dataframe(grade_table.round(2).rename_axis('Consumption level'), use_container_width=True)

st.header('4. Health Analysis')
st.subheader('Weekend Consumption by Health Status')
health_weekend = pd.crosstab(a['health'], a['Walc']).reindex(index=range(1, 6), columns=range(1, 6), fill_value=0)
plot_bar(health_weekend, 'Health Status by Weekend Consumption Level', 'Health Status (1 = very bad, 5 = very good)', 'Number of Students', 'Walc Level')
st.write('Walc 1 appears across all health ratings, including students who rated their health poorly. Some students at Walc 3–5 also reported very good health. These counts alone do not show a clear link between weekend drinking and health.')

st.subheader('Workday Consumption by Health Status')
health_workday = pd.crosstab(a['health'], a['Dalc']).reindex(index=range(1, 6), columns=range(1, 6), fill_value=0)
plot_bar(health_workday, 'Health Status by Workday Consumption Level', 'Health Status (1 = very bad, 5 = very good)', 'Number of Students', 'Dalc Level')
st.write('Dalc 1 is the most common level across all health ratings. Among students with lower health ratings, more reported Dalc 1 than Walc 1. This comparison does not tell us whether drinking affects their health.')

st.subheader('Health Status and Past Class Failures')
health_failures_corr = a['health'].corr(a['failures'], method='spearman')
health_failures = pd.crosstab(a['health'], a['failures'])
plot_heatmap(health_failures, f'Health Status and Past Class Failures (Spearman: {health_failures_corr:.2f})', 'Number of Past Class Failures', 'Health Status (1 = very bad, 5 = very good)')
health_failure_rates = a.assign(any_failure=a['failures'] > 0).groupby('health')['any_failure'].mean() * 100
no_failure_pct = (a['failures'] == 0).mean() * 100
st.write(f"Around {no_failure_pct:.1f}% of students had no past class failures. Among students with health ratings of 3 and 5, about {health_failure_rates.loc[3]:.1f}% and {health_failure_rates.loc[5]:.1f}% had at least one past failure. The Spearman correlation of {health_failures_corr:.2f} shows very little relationship between health ratings and past failures.")

st.header('5. Gender Comparison')
st.caption('Each gender column sums to 100%. These plots compare within-gender distributions, not raw numbers of students.')
sex_walc = pd.crosstab(a['Walc'], a['sex'], normalize='columns').reindex(range(1, 6), fill_value=0) * 100
sex_dalc = pd.crosstab(a['Dalc'], a['sex'], normalize='columns').reindex(range(1, 6), fill_value=0) * 100
st.subheader('Weekend Alcohol Consumption by Gender')
plot_bar(sex_walc, 'Weekend Consumption Levels by Gender (%)', 'Consumption Level (1 = very low, 5 = very high)', 'Percentage of Students (%)', 'Gender')
if {'F', 'M'}.issubset(sex_walc.columns):
    hf = sex_walc.loc[[4, 5], 'F'].sum(); hm = sex_walc.loc[[4, 5], 'M'].sum()
    st.write(f'About {hm:.1f}% of male students reported high weekend consumption (Walc 4–5), compared with {hf:.1f}% of female students. Higher weekend consumption levels were more common among males.')
else:
    st.write('The chart compares the percentages of students within each reported gender across weekend consumption levels.')

st.subheader('Workday Alcohol Consumption by Gender')
plot_bar(sex_dalc, 'Workday Consumption Levels by Gender (%)', 'Consumption Level (1 = very low, 5 = very high)', 'Percentage of Students (%)', 'Gender')
if {'F', 'M'}.issubset(sex_dalc.columns):
    f_low = sex_dalc.loc[1, 'F']; m_high = sex_dalc.loc[[3,4,5], 'M'].sum(); f_high = sex_dalc.loc[[3,4,5], 'F'].sum()
    st.write(f'About {f_low:.1f}% of female students reported the lowest workday consumption level (Dalc 1). For Dalc 3–5, the figures were {m_high:.1f}% for males and {f_high:.1f}% for females. Males were more common in the higher workday consumption levels.')
else:
    st.write('The chart compares the percentages of students within each reported gender across workday consumption levels.')

st.header('6. Social Activity')
st.subheader('Going-Out Frequency and Weekend Alcohol Consumption')
goout_walc = pd.crosstab(a['goout'], a['Walc'], normalize='index').reindex(index=range(1,6), columns=range(1,6), fill_value=0) * 100
goout_corr = a['goout'].corr(a['Walc'], method='spearman')
plot_heatmap(goout_walc, f'Weekend Consumption by Going-Out Frequency (Spearman: {goout_corr:.2f})', 'Walc Level (1 = very low, 5 = very high)', 'Going-Out Frequency (1 = very low, 5 = very high)', is_percent=True)
if 1 in goout_walc.index and 5 in goout_walc.index:
    rare = goout_walc.loc[1,1]; rare_top = goout_walc.loc[1,5]
    middle_low = goout_walc.loc[3,[1,2]].sum(); frequent_low = goout_walc.loc[5,[1,2]].sum(); frequent_high=goout_walc.loc[5,[4,5]].sum()
    st.write(f'About {rare:.1f}% of students who rarely go out (goout 1) reported Walc 1, and none reported Walc 5.' if rare_top == 0 else f'About {rare:.1f}% of students who rarely go out (goout 1) reported Walc 1, while {rare_top:.1f}% reported Walc 5.')
    st.write(f'Among students at goout 3, {middle_low:.1f}% reported Walc 1–2, compared with {frequent_low:.1f}% at goout 5. Meanwhile, {frequent_high:.1f}% of students at goout 5 reported Walc 4–5. The Spearman correlation of {goout_corr:.2f} shows that students who go out more often tend to report higher weekend consumption levels, but it does not prove that going out causes more drinking.')

st.header('7. Dataset Source and References')
st.markdown('**Dataset:** Student Alcohol Consumption (Kaggle), based on the Student Performance dataset from the UCI Machine Learning Repository. **Original researchers:** Paulo Cortez and Alice Silva (2008).')
st.markdown('**Kaggle source:** https://www.kaggle.com/uciml/student-alcohol-consumption/home')
st.markdown('**Original dataset:** https://archive.ics.uci.edu/dataset/320/student+performance')
st.markdown('**Research reference:** Cortez, P., & Silva, A. (2008). *Using data mining to predict secondary school student performance*. Proceedings of the 5th Future Business Technology Conference.')
st.divider()
st.caption('Prepared by: Calma Nat')
