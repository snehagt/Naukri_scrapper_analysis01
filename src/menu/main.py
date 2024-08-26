import time
from tqdm import tqdm
from colorama import Fore, Style
from ..visualisation.plot_generator import *
from src.processing.data_analysis import *
from models.sql_connection import db_service
from decorators.decorator import log_function_call
from exceptions.exception import InvalidOptionException

from Enums.enums import (AnalysisMenuOptions, 
                         VisualizationMenuOptions, LoginMenuOptions)

df = pd.read_csv('C:/Users/sneha.gupta/Crash_course/Naukri_scrapper_analysis/data/processed_data/naukri_job_listings_cleaned.csv')

def loading_bar():
    """
    Displays a loading bar with varying colors
    """
    for i in tqdm(range(101), desc="Loading…", ascii=False, ncols=75):
        time.sleep(0.01)
        if i < 30:
            color = Fore.GREEN
        elif i < 70:
            color = Fore.YELLOW
        else:
            color = Fore.RED
        print(f"{color}{i}%{Style.RESET_ALL}", end="\r")

def login_signup_menu():
    '''
    Login signup fucntionality implemented with mysql
    '''
    loading_bar()
    is_logged_in = False
    current_user = None
    
    while True:
        print(f"\n{Fore.CYAN}Login/Signup Menu: {Style.RESET_ALL}")
        print("1. Login")
        print("2. Signup")
        print("0. Logout ")
        
        if is_logged_in:
            print(f"{Fore.GREEN}User '{current_user}' is currently logged in. Please logout!{Style.RESET_ALL}")
            choice = input("Enter your choice: ").strip()
            
            if choice == LoginMenuOptions.EXIT.value:  # Exit
                print(f"{Fore.GREEN}Logging out...{Style.RESET_ALL}")
                is_logged_in = False
                current_user = None
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please logout to perform other actions.{Style.RESET_ALL}")
                continue
        else:
            choice = input("Enter your choice: ").strip()
            
            if choice == LoginMenuOptions.LOGIN.value:  # Login
                username = input("Enter username: ").strip()
                password = input("Enter password: ").strip()

                if db_service.check_login(username, password):
                    print(f"{Fore.GREEN}Welcome back, {username}!{Style.RESET_ALL}")
                    is_logged_in = True
                    current_user = username
                    main()  
                else:
                    print(f"{Fore.RED}Invalid username or password.{Style.RESET_ALL}")

            elif choice == LoginMenuOptions.SIGNUP.value:  
                username = input("Enter new username: ").strip()
                password = input("Enter new password: ").strip()
                email = input("Enter email: ").strip()

                if db_service.get_user(username):
                    print(f"{Fore.RED}Username '{username}' already exists. Please choose another username.{Style.RESET_ALL}")
                else:
                    if db_service.register_user(username, password, email):
                        print(f"{Fore.GREEN}User '{username}' registered successfully!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Failed to register user. Please try again.{Style.RESET_ALL}")

            elif choice == LoginMenuOptions.EXIT.value:  
                print(f"{Fore.RED}Exiting program.{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a valid option.{Style.RESET_ALL}")

@log_function_call('logs/main_logs.log')
def print_main_menu() -> str:

    """Prints the main menu options and prompts the user for input.

    Returns:
        str: The user's choice as a string.
    """

    print("\nMain Menu:")
    print("1. Show Data")
    print("2. Show Columns")
    print("3. Show dataset size")
    print("4. Basic Statistics")
    print("5. Analysis Menu")
    print("6. Visualization Menu")
    print("0. Exit")
    choice = input("Enter your choice: ")
    return choice

@log_function_call('logs/main_logs.log')
def print_analysis_menu() -> str:

    """Prints the analysis menu options and prompts the user for input.

    Returns:
        str: The user's choice as a string.
    """

    print("\nAnalysis Menu:")
    for option in AnalysisMenuOptions:
        print(f"{option.value}. {option.name.replace('_', ' ')}")
    choice = input("Enter your choice: ")
    return choice

@log_function_call('logs/main_logs.log')
def print_visualization_menu() -> str:

    """Prints the visualization menu options and prompts the user for input.

    Returns:
        str: The user's choice as a string.
    """

    print("\nVisualization Menu:")
    for option in VisualizationMenuOptions:
        print(f"{option.value}. {option.name.replace('_', ' ')}")
    choice = input("Enter your choice: ")
    return choice

@log_function_call('logs/main_logs.log')
def handle_analysis_choice(choice: str) -> bool:

    """Executes the corresponding analysis based on the user's choice.

    Args:
        choice (str): The user's choice from the analysis menu.

    Returns:
        bool: True to continue running the main loop, False to exit.
    """

    if choice == AnalysisMenuOptions.JOB_TITLE_CATEGORY.value:
        print(get_job_title_category(df))
    elif choice == AnalysisMenuOptions.HIGHEST_JOB_POSTING_COMPANIES.value:
        print(get_companies_with_highest_job_postings(df))
    elif choice == AnalysisMenuOptions.JOBS_BY_COMPANY.value:
        company_name = input("Enter Company Name: ")
        print(get_jobs_by_company(df, company_name))
    elif choice == AnalysisMenuOptions.SALARY_RANGE_BY_COMPANY .value:
        company_name = input("Enter Company Name: ")
        print(get_salary_range_by_company(df, company_name))
    elif choice == AnalysisMenuOptions.ANALYZE_LOCATION.value:
        location_df = analyze_location(df)
        print(location_df.groupby('New_Location',sort=True)['New_Location'].count().sort_values(ascending=False)[0:15])
    elif choice == AnalysisMenuOptions.ANALYZE_SKILLS.value:
        print(analyze_skills(df))
        plot_choice = input("Do you want to plot a graph for this analysis? (yes/no): ")
        if plot_choice.lower() == 'yes':
            plot_word_cloud()
    elif choice == AnalysisMenuOptions. ANALYZE_COMPANY_REVIEWS.value:
        print(analyze_company_reviews(df))
        plot_choice = input("Do you want to plot a graph for this analysis? (yes/no): ")
        if plot_choice.lower() == 'yes':
            highest_df, lowest_df = analyze_company_reviews(df)
            plot_horizontal_company_reviews(highest_df, lowest_df)
    elif choice == AnalysisMenuOptions.EXPERIENCE_SUMMARY.value:
        print(get_experience_range_for_job_posting(df))
        plot_choice = input("Do you want to plot a graph for this analysis? (yes/no): ")
        if plot_choice.lower() == 'yes':
            plot_experience_range()
    elif choice == AnalysisMenuOptions.JOBS_BY_EXPERIENCE.value:
        experience_yrs = int(input("Enter the experience you have: "))
        print(filter_jobs_by_experience(df, experience_yrs))
    elif choice == AnalysisMenuOptions. BEST_JOBS_BY_EXP_SALARY.value:
        experience_yrs = int(input("Enter the experience you have: "))
        print(get_jobs_for_max_salary_for_your_exp(df, experience_yrs))
    elif choice == AnalysisMenuOptions.JOB_POSTINGS_MONTHLY.value:
        print(get_job_listing_monthly(df))
        plot_choice = input("Do you want to plot a graph for this analysis? (yes/no): ")
        if plot_choice.lower() == 'yes':
            plot_job_postings_per_month()
    elif choice == AnalysisMenuOptions.JOB_POSTINGS_BY_DAY_FROM_MONTH.value:
        date_input = input("Enter the date (e.g., 24 January 2024): ")
        print(get_job_postings_for_date(df, date_input))
        plot_choice = input("Do you want to plot a graph for this analysis? (yes/no): ")
        if plot_choice.lower() == 'yes':
            plot_job_postings_per_day(df)
    elif choice == AnalysisMenuOptions.EXIT.value:
        return False
    else:
        print("Invalid choice. Please enter a valid option.")
    return True

@log_function_call('logs/main_logs.log')
def handle_visualization_choice(choice: str) -> bool:

    """Executes the corresponding visualization based on the user's choice.

    Args:
        choice (str): The user's choice from the visualization menu.

    Returns:
        bool: True to continue running the main loop, False to exit.
    """

    if choice == VisualizationMenuOptions.PLOT_JOB_TITLE_CATEGORY.value:
        plot_job_title_category()
    elif choice == VisualizationMenuOptions.PLOT_COMPANIES_WITH_HIGHEST_JOB_POSTINGS.value:
        plot_companies_with_highest_job_postings()
    elif choice == VisualizationMenuOptions.PLOT_LOCATION_DISTRIBUTION.value:
        plot_location_distribution()
    elif choice == VisualizationMenuOptions.PLOT_EXPERIENCE_RANGE.value:
        plot_experience_range()
    elif choice == VisualizationMenuOptions.PLOT_SALARY_DIFFERENCE.value:
        plot_salary_difference()
    elif choice == VisualizationMenuOptions.PLOT_JOB_POSTINGS_PER_MONTH.value:
        plot_job_postings_per_month()
    elif choice == VisualizationMenuOptions.PLOT_JOB_POSTINGS_PER_DAY.value:
        plot_job_postings_per_day(df)
    elif choice == VisualizationMenuOptions.PLOT_CORRELATION.value:
        plot_correlation_experience_salary()
    elif choice == VisualizationMenuOptions.PLOT_REGRESSION.value:
        plot_regression_experience_salary()
    elif choice == VisualizationMenuOptions.PLOT_SALARY_CLUSTERING.value:
        plot_salary_clustering()
    elif choice == VisualizationMenuOptions.PLOT_TOP_SKILLS.value:
        plot_top_skills()
    elif choice == VisualizationMenuOptions.PLOT_WORD_CLOUD.value:
        plot_word_cloud()
    elif choice == VisualizationMenuOptions.PLOT_COMPANY_REVIEWS.value:
        plot_company_reviews()
    elif choice == VisualizationMenuOptions.EXIT.value:
        return False
    else:
        print("Invalid choice. Please enter a valid option.")
    return True

@log_function_call('logs/main_logs.log')
def show_basic_statistics():

    """
    Displays basic statistics about the dataframe.
    """

    print("\nBasic Statistics:")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"Column Names: {list(df.columns)}")
    print(f"Data Shape: {df.shape}")
    print(f"Data Size: {df.size}")
    print(f"Data Types:\n{df.dtypes}")

@log_function_call('logs/main_logs.log')
def main():

    """
    Main function to run the interactive analysis and visualization tool.
    """

    print('...................')
    while True:
        choice = print_main_menu()
        
        if choice == '1':
            print(df.head(10))
        
        elif choice == '2':
            print(df.columns)
        
        elif choice == '3':
            print(df.shape)
        
        elif choice == '4':
            show_basic_statistics()
        
        elif choice == '5':
            while True:
                analysis_choice = print_analysis_menu()
                if analysis_choice == AnalysisMenuOptions.EXIT.value:
                    break
                else:
                    continue_analysis = handle_analysis_choice(analysis_choice)
                    if not continue_analysis:
                        break
        
        elif choice == '6':
            while True:
                visualization_choice = print_visualization_menu()
                if visualization_choice == VisualizationMenuOptions.EXIT.value:
                    break
                else:
                    continue_visualization = handle_visualization_choice(visualization_choice)
                    if not continue_visualization:
                        break
        
        elif choice == '0':
            print("Exiting the program...")
            break
        
        else:
            print("Invalid choice. Please enter a valid option.")
