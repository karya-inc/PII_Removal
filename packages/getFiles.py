import json

def get_ground_truth_from_json(file_path):
    """
    Reads a single JSON file and extracts the ground truth segments in seconds.
    
    Args:
        file_path (str): The full path to the JSON annotation file.
        
    Returns:
        list: A list of (start_sec, end_sec) tuples, or an empty list if
              the file is invalid or required data is missing.
    """
    ground_truth = []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            # Extract and convert segments to seconds
            if "data" in data and "segments" in data["data"]:
                for segment in data["data"]["segments"]:
                    start_sec = segment["start"] / 1000
                    end_sec = segment["end"] / 1000
                    ground_truth.append((start_sec, end_sec))
            
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}. Skipping.")
    except KeyError:
        print(f"Missing expected keys in {file_path}. Skipping.")
        
    return ground_truth



# Get the ground_truth list
# ground_truth = get_ground_truth_from_json(file_path)

# print(f"Ground truth segments for the file: {ground_truth}")