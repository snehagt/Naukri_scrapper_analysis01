# Enums
from enum import Enum

class AnalysisMenuOptions(Enum):
    JOB_TITLE_CATEGORY = '1'
    HIGHEST_JOB_POSTING_COMPANIES = '2'
    JOBS_BY_COMPANY = '3'
    SALARY_RANGE_BY_COMPANY = '4'
    ANALYZE_LOCATION = '5'
    ANALYZE_SKILLS = '6'
    ANALYZE_COMPANY_REVIEWS = '7'
    EXPERIENCE_SUMMARY = '8'
    JOBS_BY_EXPERIENCE = '9'
    BEST_JOBS_BY_EXP_SALARY = '10'
    JOB_POSTINGS_MONTHLY = '11'
    JOB_POSTINGS_BY_DAY_FROM_MONTH = '12'
    KEYWORD_SEARCH_RESULTS = '13'
    EXIT = '0'

class VisualizationMenuOptions(Enum):
    PLOT_JOB_TITLE_CATEGORY = '1'
    PLOT_COMPANIES_WITH_HIGHEST_JOB_POSTINGS = '2'
    PLOT_LOCATION_DISTRIBUTION = '3'
    PLOT_EXPERIENCE_RANGE = '4'
    PLOT_SALARY_DIFFERENCE = '5'
    PLOT_JOB_POSTINGS_PER_MONTH = '6'
    PLOT_JOB_POSTINGS_PER_DAY = '7'
    PLOT_CORRELATION = '8'
    PLOT_REGRESSION = '9'
    PLOT_SALARY_CLUSTERING = '10'
    PLOT_TOP_SKILLS = '11'
    PLOT_WORD_CLOUD = '12'
    PLOT_COMPANY_REVIEWS = '13'
    EXIT = '0'

class LoginMenuOptions(Enum):
    EXIT = '0'
    LOGIN = '1'
    SIGNUP = '2'

    