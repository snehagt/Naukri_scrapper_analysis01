import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import squarify
from datetime import datetime
from sklearn.cluster import KMeans
from collections import Counter
import re
from decorators.decorator import save_to_excel, log_function_call

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

def categorize_by_frequency(title):
    title = title.lower()
    if 'lead' in title or 'lead software engineer' in title:
        return 'Lead Software Engineer'
    elif 'frontend' in title:
        return 'Frontend Engineer'
    elif 'backend' in title:
        return 'Backend Engineer'
    elif 'principal' in title:
        return 'Principal Software Engineer'
    elif 'senior' in title or 'sr' in title:
        return 'Senior Software Engineer'
    elif 'development' in title:
        return 'Software Development Engineer'
    elif 'full stack' in title:
        return 'Full Stack Engineer'
    elif '.net' in title:
        return '.Net Engineer'
    elif 'qa' in title or 'testing' in title:
        return 'QA/Testing Engineer'
    elif 'python' or 'java' or 'C++' in title:
        return 'Specialized Engineer'
    elif 'AWS' or 'Azure' in title:
        return 'Cloud Engineer'
    else:
        return 'Other'

@save_to_excel
@log_function_call('logs/analysis_logs.log')
def get_job_title_category(df):
    df['Job Title Category'] = df['Job Title'].apply(categorize_by_frequency)
    return df

def get_companies_with_highest_job_postings(df):
    
    company_counts = df['Company Name'].value_counts()
    return company_counts

def get_jobs_by_company(df, company_name):
    df['Company Name'] = df['Company Name'].str.title()
    filtered_df = df[df['Company Name'] == company_name]
    return filtered_df

def get_salary_range_by_company(df, company_name):
    df['Company Name'] = df['Company Name'].str.title()
    filtered_df = df[df['Company Name'] == company_name]
    min_salary = filtered_df['Min Salary'].min()
    max_salary = filtered_df['Max Salary'].max()
    return min_salary, max_salary

def get_location(df):
    df_new = pd.DataFrame()
    for index, row in df.iterrows():
        for loc in row['Location'].split(','):
            loc_df = pd.DataFrame([loc])
            df_new = pd.concat([df_new, loc_df], ignore_index=True)
    return df_new

def analyze_location(df):
    location_df = get_location(df)
    location_df.columns = ['Location']
    location_df['New_Location'] = location_df['Location'].apply(get_comman_location)
    return location_df

def get_comman_location(x):
    x = x.replace(",", " /")
    if re.search('bengaluru', x.lower()) or re.search('bangalore', x.lower()):
        return 'Bengaluru'
    elif re.search('ahmedabad', x.lower()):
        return 'Ahmedabad'
    elif re.search('chennai', x.lower()):
        return 'Chennai'
    elif re.search('coimbatore', x.lower()):
        return 'Coimbatore'
    elif re.search('delhi', x.lower()) or re.search('noida', x.lower()) or re.search('gurgaon', x.lower()):
        return 'Delhi NCR'
    elif re.search('hyderabad', x.lower()):
        return 'Hyderabad'
    elif re.search('kolkata', x.lower()):
        return 'Kolkata'
    elif re.search('mumbai', x.lower()):
        return 'Mumbai'
    elif re.search('pune', x.lower()):
        return 'Pune'
    elif re.search('other', x.lower()):
        return 'Others'
    else:
        return x.strip()

def analyze_skills(df):
    df['Skills'] = df['Skills'].astype(str)
    def clean_skills(skill_str):
        cleaned = skill_str.strip("[]'").split(',')
        return [skill.strip().lower() for skill in cleaned if skill.strip()]
    skills_df = df['Skills'].apply(clean_skills)
    all_skills = [skill for sublist in skills_df for skill in sublist]
    skill_counts = Counter(all_skills)
    skill_df = pd.DataFrame(skill_counts.items(), columns=['Skill', 'Count']).sort_values(by='Count', ascending=False)
    return skill_df

def analyze_company_reviews(df):
    df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
    df = df.dropna(subset=['Reviews'])
    avg_reviews = df.groupby('Company Name')['Reviews'].mean().reset_index()
    highest_reviews = avg_reviews.sort_values(by='Reviews', ascending=False).head(10)
    lowest_reviews = avg_reviews.sort_values(by='Reviews').head(10)
    return highest_reviews, lowest_reviews

def plot_horizontal_company_reviews(highest_df, lowest_df):
    plt.figure(figsize=(14, 10))
    combined_df = pd.concat([
        highest_df.assign(Category='Highest Reviews'),
        lowest_df.assign(Category='Lowest Reviews')
    ])
    sns.barplot(x='Reviews', y='Company Name', hue='Category', data=combined_df, palette={'Highest Reviews': 'b', 'Lowest Reviews': 'r'})
    plt.xlabel('Average Reviews')
    plt.ylabel('Company Name')
    plt.title('Top 5 Companies with Highest and Lowest Average Reviews')
    plt.legend(title='Review Category')
    plt.tight_layout()
    plt.show()
    
def get_experience_range_for_job_posting(df):
    return df.groupby('Experience Required',sort=True)['Experience Required'].count()[0:30]

def parse_experience(exp_range):
    """Extract minimum and maximum experience from a range string."""
    try:
        min_exp, max_exp = exp_range.split('-')
        min_exp = int(min_exp.strip().split()[0])
        max_exp = int(max_exp.strip().split()[0]) if max_exp.strip() else None
        return min_exp, max_exp
    except (ValueError, IndexError):
        return None, None

def filter_jobs_by_experience(df, exp_input):
    """Filter jobs where minimum experience < exp_input < maximum experience."""
    min_exp_input = exp_input
    
    def is_within_range(exp):
        exp_min, exp_max = parse_experience(exp)
        if exp_min is None:  
            return False
        if exp_max is None: 
            return exp_min < min_exp_input
        return exp_min <= min_exp_input <= exp_max
    
    return df[df['Experience Required'].apply(is_within_range)]

def get_jobs_by_experience(df, experience_yrs):
    filtered_jobs = filter_jobs_by_experience(df, experience_yrs)
    return filtered_jobs[['Job Title', 'Company Name']].head(5)

def get_jobs_for_max_salary_for_your_exp(df, experience_yrs):
    filtered_df = filter_jobs_by_experience(df, experience_yrs)
    company_salary_df = filtered_df.groupby('Company Name')['Max Salary'].max().reset_index()
    sorted_company_salary_df = company_salary_df.sort_values(by='Max Salary', ascending=False)
    return sorted_company_salary_df.head(10)

def get_avg_salaries_of_companies(df: pd.DataFrame):
    salary_df : pd.DataFrame = df[(df['Min Salary'] > 0) & (df['Max Salary'] > 0)]

    salary_df['Average Salary'] = (salary_df['Min Salary'] + salary_df['Max Salary']) / 2
    company_avg_salary : pd.DataFrame = salary_df.groupby('Company Name')['Average Salary'].mean().reset_index()
    return company_avg_salary.sort_values(by='Average Salary', ascending=False)
    
def get_job_listing_monthly(df):
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], errors='coerce')
    month_counts = df['TimeStamp'].dt.strftime('%B %Y').value_counts().sort_index()
    print(month_counts)

def get_job_postings_for_date(df, date_str):
    try:
        df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], errors='coerce')
        date_obj = datetime.strptime(date_str, '%d %B %Y').date()
        
        df['Date'] = df['TimeStamp'].dt.date
        jobs_per_day = df.groupby('Date').size()

        if date_obj in jobs_per_day.index:
            return jobs_per_day[date_obj]
        else:
            return "No job postings available for this date."

    except ValueError:
        return "Invalid date format. Please use 'DD Month YYYY' format."

def plot_job_postings_per_day(df):
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], errors='coerce')

    df['Date'] = df['TimeStamp'].dt.date

    jobs_per_day = df.groupby('Date').size()

    jobs_per_day.index = pd.to_datetime(jobs_per_day.index).strftime('%B %d, %Y')

    Q1 = jobs_per_day.quantile(0.25)
    Q3 = jobs_per_day.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    jobs_per_day_filtered = jobs_per_day[(jobs_per_day >= lower_bound) & (jobs_per_day <= upper_bound)]

    jobs_per_day_filtered.index = pd.to_datetime(jobs_per_day_filtered.index).strftime('%B %d, %Y')
    plt.figure(figsize=(14, 8))
    jobs_per_day_filtered.plot(kind='bar', color='lightcoral')
    plt.xlabel('Date')
    plt.ylabel('Number of Job Postings')
    plt.title('Number of Job Postings per Day (Outliers Removed)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_job_postings_per_day_per_month(df):
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], errors='coerce')

    df['Date'] = df['TimeStamp'].dt.date
    jobs_per_day = df.groupby('Date').size()
    Q1 = jobs_per_day.quantile(0.25)
    Q3 = jobs_per_day.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    jobs_per_day_filtered = jobs_per_day[(jobs_per_day >= lower_bound) & (jobs_per_day <= upper_bound)]

    jobs_per_day_filtered.index = pd.to_datetime(jobs_per_day_filtered.index)
    return jobs_per_day_filtered

def plot_jobs_for_month(df, month_number):
    import matplotlib.dates as mdates
    jobs_per_day_filtered = plot_job_postings_per_day_per_month(df)
    month_data = jobs_per_day_filtered[jobs_per_day_filtered.index.month == month_number]
    
    if month_data.empty:
        print(f"No data available for month number {month_number}.")
        return
    
    plt.figure(figsize=(14, 8))
    plt.plot(month_data.index, month_data, marker='o', linestyle='-', color='b')

    plt.xlabel('Date')
    plt.ylabel('Number of Job Postings')
    plt.title(f'Number of Job Postings per Day in Month {month_number} (Outliers Removed)')
    plt.grid(True)

    date_format = mdates.DateFormatter('%b %d')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gca().xaxis.set
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    print("Welcome to the Job Analysis System!")
    df = load_data('../../data/processed_data/naukri_job_listings_cleaned.csv')

    while True:
        print("\nMenu:")
        print("1. Get Job Title Category")
        print("2. Get Companies with Highest Job Postings")
        print("3. Get Jobs by Company")
        print("4. Get Salary Range by Company")
        print("5. Analyze Location")
        print("6. Analyze Skills")
        print("7. Analyze Company Reviews")
        print("8. Get Experince Summary")
        print("9: Get Jobs by Experience")
        print("10: Get best Jobs for your Experience")
        print("11: Get Best Average Salaried Companies")
        print("12: Get Company Job Posting by Monthly Basis")
        print("13: Get Company Job Posting by day")
        print("14: Get Job Posting By Month")
        print("X: To Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            df = get_job_title_category(df)
            print(df['Job Title Category'].value_counts())

        elif choice == "2":
            company_counts = get_companies_with_highest_job_postings(df)
            print(company_counts.head(10))

        elif choice == "3":
            company_name = input("Enter company name: ")
            jobs = get_jobs_by_company(df, company_name)
            print(jobs)

        elif choice == "4":
            company_name = input("Enter company name: ")
            min_salary, max_salary = get_salary_range_by_company(df, company_name)
            print(f"Minimum salary: {min_salary}, Maximum salary: {max_salary}")

        elif choice == "5":
            location_df = get_location(df)
            location_df.columns = ['Location']
            location_df['New_Location'] = location_df['Location'].apply(get_comman_location)
            print(location_df['New_Location'].sample())
            print(location_df.groupby('New_Location',sort=True)['New_Location'].count().sort_values(ascending=False)[0:15])

        elif choice == "6":
            
            skill_df = analyze_skills(df)
            print(skill_df.head(10))

        elif choice == "7":
            highest_reviews, lowest_reviews = analyze_company_reviews(df)
            # plot_horizontal_company_reviews(highest_reviews, lowest_reviews)
            print(highest_reviews.head(10),"\n" ,lowest_reviews.head(10))
            
        elif choice == "8":
            print(get_experience_range_for_job_posting(df))
                
        elif choice == "9":
            experience_yrs = int(input("Enter the experience you have: "))
            print(get_jobs_by_experience(df, experience_yrs))
        
        elif choice == "10":
            experience_yrs = int(input("Enter the experience you have: "))
            print(get_jobs_for_max_salary_for_your_exp(df, experience_yrs))
            
        elif choice == "11":
            company_avg_salary = get_avg_salaries_of_companies(df)
            print(company_avg_salary.head(10))
            
        elif choice == "12":
            get_job_listing_monthly(df)
            
        elif choice == "13":
            plot_job_postings_per_day(df)
            
        elif choice == "14":
            month_number = int(input("Enter the month number (1-12): "))
            plot_jobs_for_month(df, month_number)
            
        elif choice == "X":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()