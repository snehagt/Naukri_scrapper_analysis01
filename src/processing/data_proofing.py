import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta

# Load the data
df = pd.read_csv('../../data/raw/naukri_job_listings.csv')

# Check missing values and their percentage
features_na = [features for features in df.columns]
for feature in features_na:
    print(feature, np.round(df[feature].isnull().mean(), 4),  ' % missing values and actual count is '+str(df[feature].isnull().sum()))

print('Total entries:{}'.format(len(df)))

# Parse the 'Time Posted' column
def parse_time_posted(time_str):
    today = datetime.now()

    day_match = re.match(r'(\d+) Day[s]* Ago', time_str)
    if day_match:
        days_ago = int(day_match.group(1))
        return today - timedelta(days=days_ago)

    month_match = re.match(r'Starts in (\d+)-(\d+) months', time_str)
    if month_match:
        min_months, max_months = map(int, month_match.groups())
        average_days = (min_months + max_months) / 2 * 30
        return today + timedelta(days=average_days)

    month_match = re.match(r'Starts within (\d+) month[s]*', time_str)
    if month_match:
        months = int(month_match.group(1))
        return today + timedelta(days=months * 30)

    if 'Few Hours Ago' in time_str:
        return today - timedelta(hours=1)  # Assuming 1 hour ago for simplicity

    if 'Just Now' in time_str:
        return today

    if 'Today' in time_str:
        return today

    date_match = re.match(r"Starts : (\d{1,2}[a-z]{2} \w{3}' \d{2})", time_str)
    if date_match:
        date_str = date_match.group(1)
        try:
            return datetime.strptime(date_str, "%d%b'%y")
        except ValueError:
            return None

    plus_days_match = re.match(r'(\d+)\+ Days Ago', time_str)
    if plus_days_match:
        days_ago = int(plus_days_match.group(1))
        return today - timedelta(days=days_ago)

    return None

# Apply the function to the Time Posted column
df['TimeStamp'] = df['Time Posted'].apply(parse_time_posted)
df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], errors='coerce')

# Parse the 'Salary' column
def parse_salary(salary_str):
    if 'Not disclosed' in salary_str:
        return 0, 0
    else:
        try:
            salary_str = salary_str.replace('Lacs PA', '').strip()
            min_salary, max_salary = salary_str.split('-')
            return float(min_salary), float(max_salary)
        except ValueError:
            return 0, 0

df[['Min Salary', 'Max Salary']] = df['Salary'].apply(lambda x: pd.Series(parse_salary(x)))

# Standardize the 'Location' column
def standardize_location(location_str):
    location_mapping = {
        'Hyderabad': 'Hyderabad',
        'Bengaluru': 'Bengaluru',
        'Mumbai': 'Mumbai',
        'New Delhi': 'New Delhi',
        'Chennai': 'Chennai',
        'Pune': 'Pune',
        'Indore': 'Indore',
    }
    locations = [loc.strip() for loc in location_str.split(',') if loc.strip()]
    standardized_locations = [location_mapping.get(loc, loc) for loc in locations]
    return ', '.join(sorted(set(standardized_locations)))

df['Location'] = df['Location'].apply(standardize_location)

# Clean the 'Skills' column
def clean_skills(skills_str):
    if not isinstance(skills_str, str):
        return ["no data available"]
    try:
        skills_str = re.sub(r'[^\w\s,]', '', skills_str)
        skills_str = re.sub(r'\s+', ' ', skills_str)
        skills_list = [skill.strip().lower() for skill in skills_str.split(',') if skill.strip()]
        skills_list = list(set(skills_list))
        skills_list = [skill.title() for skill in skills_list]
        if not skills_list:
            return ["No skills listed"]
        return skills_list
    except Exception as e:
        print(f"Error cleaning skills: {e}")
        return ["Error processing skills"]

df['Skills'] = df['Skills'].apply(clean_skills)

# Parse the 'Reviews' column
def parse_review(review_str):
    parts = review_str.split()
    for part in parts:
        if part.isdigit():
            return int(part)
    return 0

df['Reviews'] = df['Reviews'].apply(parse_review)

# Parse the 'Experience Required' column
def parse_experience(experience_str):
    match = re.match(r'(\d+)-(\d+) Yrs', experience_str)
    if match:
        min_exp, max_exp = map(int, match.groups())
        return min_exp, max_exp
    return "No data available"

# Save the final cleaned DataFrame
df.to_csv('../../data/processed_data/naukri_job_listings_cleaned.csv', index=False)

print("Final cleaned data has been saved.")
