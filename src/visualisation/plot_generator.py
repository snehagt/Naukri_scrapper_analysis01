import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
from wordcloud import WordCloud
from sklearn.cluster import KMeans
from collections import Counter
from re import search
from decorators.decorator import save_plot_decorator, save_to_excel

from ..processing.data_analysis import get_location

df = pd.read_csv('data/processed_data/naukri_job_listings_cleaned.csv')

def get_location(df):
    df_new = pd.DataFrame()
    for index, row in df.iterrows():
        for loc in row['Location'].split(','):
            loc_df = pd.DataFrame([loc])
            df_new = pd.concat([df_new, loc_df], ignore_index=True)
    return df_new

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

df['Job Title Category'] = df['Job Title'].apply(categorize_by_frequency)

#categorize location data

from re import search
def get_comman_location(x):
    x = x.replace(",", " /")
    if (search('bengaluru', x.lower()) or search('bangalore', x.lower())):
        return 'Bengaluru'
    elif (search('ahmedabad', x.lower())):
        return 'Ahmedabad'
    elif (search('chennai', x.lower())):
        return 'Chennai'
    elif (search('coimbatore', x.lower())):
        return 'Coimbatore'
    elif (search('delhi', x.lower()) or search('noida', x.lower()) or search('gurgaon', x.lower())):
        return 'Delhi NCR'
    elif (search('hyderabad', x.lower())):
        return 'Hyderabad'
    elif (search('kolkata', x.lower())):
        return 'Kolkata'
    elif (search('mumbai', x.lower())):
        return 'Mumbai'
    elif (search('Pune', x.lower())):
        return 'pune'
    elif (search('other', x.lower())):
        return 'Others'
    else:
        return x.strip()

@save_plot_decorator
def plot_job_title_category():
    plt.figure(figsize=(10, 6))
    df['Job Title Category'].value_counts().plot(kind='bar', color='skyblue')
    plt.xlabel('Job Title Category')
    plt.ylabel('Number of Listings')
    plt.title('Distribution of Job Title Categories')
    plt.xticks(rotation=45, ha='right')
    plt.show()

@save_plot_decorator
def plot_companies_with_highest_job_postings():
    company_counts = df['Company Name'].value_counts().head(5)
    plt.figure(figsize=(10, 6))
    company_counts.plot(kind='bar', color='skyblue')
    plt.xlabel('Company Name')
    plt.ylabel('Number of Job Postings')
    plt.title('Companies with Highest Job Postings')
    plt.xticks(rotation=45, ha='right')
    plt.show()

@save_plot_decorator
def plot_location_distribution():
    Location_df = get_location(df)
    Location_df.columns = ['Location']
    Location_df['New_Location']=Location_df['Location'].apply(get_comman_location)
    Location_df.groupby('New_Location',sort=True)['New_Location'].count().sort_values(ascending=False)[0:15]
    top_locations = Location_df['New_Location'].value_counts().head(10)
    plt.figure(figsize=(10, 8), facecolor='white')
    plt.pie(top_locations, labels=top_locations.index, autopct='%1.1f%%', colors=plt.cm.Paired(range(len(top_locations))), explode=[0.1] * len(top_locations))
    plt.title('Distribution of Top 15 Locations (Exploded)')
    plt.show()

@save_plot_decorator
def plot_experience_range():
    df.groupby('Experience Required', sort=True)['Experience Required'].count().sort_values(ascending=False)[0:15].plot.bar(color="orange")
    plt.xlabel('Job Exp Required in Years')
    plt.ylabel('Count')
    plt.title('Distribution of Top 15 Job Experience Year Range Required')
    plt.show()

@save_plot_decorator
def plot_salary_difference():
    company_salary_stats = df.groupby('Company Name').agg({'Min Salary': 'min', 'Max Salary': 'max'}).reset_index()
    company_salary_stats['Salary_Difference'] = company_salary_stats['Max Salary'] - company_salary_stats['Min Salary']
    company_salary_stats_sorted = company_salary_stats.sort_values(by='Salary_Difference', ascending=False).head(10)
    plt.figure(figsize=(14, 8))
    sns.barplot(data=company_salary_stats_sorted, y='Company Name', x='Salary_Difference', palette='viridis')
    plt.ylabel('Company Name')
    plt.xlabel('Salary Difference')
    plt.title('Difference Between Minimum and Maximum Salaries by Company')
    plt.tight_layout()
    plt.show()

@save_plot_decorator
def plot_job_postings_per_month():
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], errors='coerce')
    jobs_per_month = df.groupby(df['TimeStamp'].dt.to_period('M')).size().reset_index(name='Job Postings')
    jobs_per_month['YearMonth'] = jobs_per_month['TimeStamp'].dt.strftime('%Y-%m')
    plt.figure(figsize=(14, 8))
    sns.lineplot(data=jobs_per_month, x='YearMonth', y='Job Postings', marker='o', color='b')
    plt.xlabel('Month-Year')
    plt.ylabel('Number of Job Postings')
    plt.title('Number of Job Postings per Month')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

@save_plot_decorator
def plot_job_postings_per_day():
    df['Date'] = pd.to_datetime(df['TimeStamp'], errors='coerce').dt.date
    jobs_per_day = df.groupby('Date').size()
    plt.figure(figsize=(14, 8))
    jobs_per_day.plot(kind='bar', color='lightcoral')
    plt.xlabel('Date')
    plt.ylabel('Number of Job Postings')
    plt.title('Number of Job Postings per Day')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

@save_plot_decorator
def plot_correlation_experience_salary():
    df['Min Salary'] = pd.to_numeric(df['Min Salary'], errors='coerce')
    df['Max Salary'] = pd.to_numeric(df['Max Salary'], errors='coerce')

    df['Experience_Min'] = df['Experience Required'].str.extract(r'(\d+)-\d+').astype(float)
    df['Experience_Max'] = df['Experience Required'].str.extract(r'\d+-(\d+)').astype(float)

    filtered_df = df[df['Max Salary'] > 0]

    correlation_min = filtered_df[['Experience_Min', 'Min Salary']].corr().iloc[0, 1]
    correlation_max = filtered_df[['Experience_Max', 'Max Salary']].corr().iloc[0, 1]

    print(f"Correlation between Min Experience and Min Salary (filtered): {correlation_min}")
    print(f"Correlation between Max Experience and Max Salary (filtered): {correlation_max}")

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Experience_Min', y='Min Salary', data=filtered_df, label='Min Experience vs Min Salary')
    sns.scatterplot(x='Experience_Max', y='Max Salary', data=filtered_df, label='Max Experience vs Max Salary', color='orange')
    plt.title('Correlation - Experience vs Salary (Filtered)')
    plt.xlabel('Experience (Years)')
    plt.ylabel('Salary')
    plt.legend()
    plt.show()
    
@save_plot_decorator
def plot_regression_experience_salary():
    plt.figure(figsize=(12, 6))
    sns.regplot(x='Experience_Min', y='Min Salary', data=df, scatter_kws={'s':50}, line_kws={'color':'red'})
    plt.title('Regression Plot - Min Experience vs Min Salary')
    plt.xlabel('Min Experience (Years)')
    plt.ylabel('Min Salary')
    plt.show()

    plt.figure(figsize=(12, 6))
    sns.regplot(x='Experience_Max', y='Max Salary', data=df, scatter_kws={'s':50}, line_kws={'color':'blue'})
    plt.title('Regression Plot - Max Experience vs Max Salary')
    plt.xlabel('Max Experience (Years)')
    plt.ylabel('Max Salary')
    plt.show()

@save_plot_decorator
def plot_salary_clustering():
    kmeans = KMeans(n_clusters=3, random_state=0)
    df_cluster = df.dropna(subset=['Min Salary', 'Max Salary'])
    X = df_cluster[['Min Salary', 'Max Salary']]
    df_cluster['Salary_Cluster'] = kmeans.fit_predict(X)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Min Salary', y='Max Salary', hue='Salary_Cluster', data=df_cluster, palette='viridis')
    plt.title('Salary Clustering Analysis')
    plt.xlabel('Min Salary')
    plt.ylabel('Max Salary')
    plt.show()

@save_plot_decorator
def plot_top_skills():
    skill_df = analyze_skills(df)
    top_skills = skill_df.head(20)
    sizes = top_skills['Count']
    labels = top_skills['Skill']
    colors = plt.cm.tab20c(range(len(labels)))
    squarify.plot(sizes=sizes, label=labels, color=colors, alpha=0.8, text_kwargs={'fontsize':8})
    plt.show()

@save_plot_decorator
def plot_word_cloud():
    skill_df = analyze_skills(df)
    word_freq = dict(zip(skill_df['Skill'], skill_df['Count']))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
    plt.figure(figsize=(15, 7.5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Skills Word Cloud', fontsize=18)
    plt.show()

@save_plot_decorator
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

@save_plot_decorator
def plot_company_reviews():
    highest_reviews, lowest_reviews = analyze_company_reviews(df)
    plot_horizontal_company_reviews(highest_reviews, lowest_reviews)

def main():
    while True:
        print("Menu:")
        print("1. Plot Job Title Category")
        print("2. Plot Companies with Highest Job Postings")
        print("3. Plot Location Distribution")
        print("4. Plot Experience Range")
        print("5. Plot Salary Difference")
        print("6. Plot Job Postings per Month")
        print("7. Plot Job Postings per Day")
        print("8. Plot Correlation - Experience vs Salary")
        print("9. Plot Regression - Experience vs Salary")
        print("10. Plot Salary Clustering")
        print("11. Plot Top Skills")
        print("12. Plot Word Cloud")
        print("13. Plot Company Reviews")
        print("14. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            plot_job_title_category()
        elif choice == "2":
            plot_companies_with_highest_job_postings()
        elif choice == "3":
            plot_location_distribution()
        elif choice == "4":
            plot_experience_range()
        elif choice == "5":
            plot_salary_difference()
        elif choice == "6":
            plot_job_postings_per_month()
        elif choice == "7":
            plot_job_postings_per_day()
        elif choice == "8":
            plot_correlation_experience_salary()
        elif choice == "9":
            plot_regression_experience_salary()
        elif choice == "10":
            plot_salary_clustering()
        elif choice == "11":
            plot_top_skills()
        elif choice == "12":
            plot_word_cloud()
        elif choice == "13":
            plot_company_reviews()
        elif choice == "14":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()