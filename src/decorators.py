import pandas as pd
import functools

def save_output_with_freq(file_name, file_type="csv"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Execute the function and get the result
            result = func(self, *args, **kwargs)

            # Check if the result can be converted to a DataFrame
            if isinstance(result, (pd.DataFrame, pd.Series)):
                data = result
            elif isinstance(result, (list, tuple)):
                data = pd.DataFrame(result)
            else:
                print("Error: Function output is not compatible with pandas DataFrame.")
                return result

            # Append filename with frequency
            fn = f"{file_name}_{self.frequency}.{file_type}"

            # Save to file based on the specified file type
            if file_type == "csv":
                data.to_csv(fn, index=False)
                print(f"Output written to {fn} as CSV.")
            elif file_type == "pickle":
                data.to_pickle(file_name)
                print(f"Output written to {fn} as a pickle file.")
            elif file_type == "parquet":
                data.to_parquet(file_name, index=False)
                print(f"Output written to {fn} as a Parquet file.")
            else:
                print(f"Error: Unsupported file type '{file_type}'.")

            return result

        return wrapper

    return decorator
