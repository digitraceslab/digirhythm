import pandas as pd
import functools

def to_file(file_name, file_type='csv'):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the function and get the result
            result = func(*args, **kwargs)
            
            # Convert result to a pandas DataFrame
            if isinstance(result, (list, tuple)):
                data = pd.DataFrame(result)
            elif isinstance(result, pd.DataFrame):
                data = result
            else:
                print("Error: Function output is not compatible with pandas DataFrame.")
                return result

            # Write to file based on file type
            if file_type == 'csv':
                data.to_csv(file_name, index=False)
                print(f"Output written to {file_name} as CSV.")
            elif file_type == 'pickle':
                data.to_pickle(file_name)
                print(f"Output written to {file_name} as a pickle file.")
            else:
                print(f"Error: Unsupported file type '{file_type}'.")
            
            return result
        
        return wrapper
    return decorator