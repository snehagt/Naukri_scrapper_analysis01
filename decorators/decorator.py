import os
import hashlib
import datetime
import pandas as pd
import matplotlib.pyplot as plt

def save_plot_decorator(func):
    @log_function_call('logs/plot_logs.log')
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        save_choice = input("Do you want to save this plot? (yes/no): ").strip().lower()
        
        if save_choice == 'yes':
            # Generate a unique filename based on function name and hash
            func_name = func.__name__
            hash_value = hashlib.md5(str(args).encode('utf-8')).hexdigest()[:6]
            filename = os.path.join('data', f"{func_name}_{hash_value}.png") 
            
            if os.path.exists(filename):
                override_choice = input(f"File '{filename}' already exists. Do you want to override it? (yes/no): ").strip().lower()
                if override_choice != 'yes':
                    print("Plot not saved.")
                    return
            
            plt.savefig(filename)
            print(f"Plot saved as '{filename}'")
        else:
            print("Plot not saved.")
    
    return wrapper

def log_function_call(log_file):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Log the function call
            with open(log_file, 'a') as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message = f"{timestamp} - Function '{func.__name__}' called.\n"
                f.write(log_message)
            # Call the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator

def save_to_excel(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
    
        user_response = input("Do you want to save the data to an Excel file? (yes/no): ")
        if user_response.lower() == "yes":
            if isinstance(result, pd.DataFrame):
                # Get the filename from the function arguments
                func_name = func.__name__
                hash_value = hashlib.md5(str(args).encode('utf-8')).hexdigest()[:6]
                filename = kwargs.get("filename", f"{func_name}_{hash_value}.xlsx")
                folder_path = "data/analysis_data"
                os.makedirs(folder_path, exist_ok=True)
                full_path = os.path.join(folder_path, filename)
                
                if os.path.exists(full_path):
                    override_choice = input(f"File '{full_path}' already exists. Do you want to override it? (yes/no): ").strip().lower()
                    if override_choice != 'yes':
                        print("Not saved.")
                        return
                result.to_excel(full_path, index=False)
                print(f"Data saved to {full_path}")
            else:
                print("The result is not a pandas DataFrame. Cannot save to Excel.")
        else:
            print("Data not saved.")
        return result
    return wrapper
