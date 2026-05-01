from backend.app.massive_import.file_decompressor.strategies import base_extractor, zip_extractor, rar_extractor, tar_extractor

import io

# --- 3. Strategy Router ---
# Map file extensions to their corresponding instantiated strategy
STRATEGIES = {
    '.zip': zip_extractor.ZipExtractor(),
    '.rar': rar_extractor.RarExtractor(),
    '.tar': tar_extractor.TarExtractor(),
    '.tar.gz': tar_extractor.TarExtractor(),
    '.tgz': tar_extractor.TarExtractor(),
    #'.7z': SevenZipExtractor() -> Not implemented
}

def get_strategy(filename: str) -> base_extractor.BaseExtractor | None:
    """Helper to find the correct strategy based on the file extension."""
    lower_name = filename.lower()
    # Iterate through keys to properly catch double extensions like .tar.gz
    for ext, strategy in STRATEGIES.items():
        if lower_name.endswith(ext):
            return strategy
    return None


# --- 4. The Core Recursive Engine (The Context) ---
def extract_nested_archives_in_memory(file_data: str | io.BytesIO, filename: str, current_depth: int = 0, max_depth: int = 10):
    """
    Recursively decompresses nested files using the Strategy Pattern.
    Params:
        - file_data: Can be a file path (str) or an in-memory file object (io.BytesIO).
        - filename: The name of the file (used for strategy selection).
        - current_depth: Current recursion depth (used for max depth control).
        - max_depth: Maximum allowed recursion depth to prevent infinite loops.
    Yields:
        - (final_filename, final_bytes): Tuples of the final extracted file's name and its bytes.
    """
    strategy = get_strategy(filename)

    # Base case: The file is a normal file, not a compressed file
    if not strategy:
        if isinstance(file_data, io.BytesIO):
            yield filename, file_data.getvalue()
        else:
            with open(file_data, 'rb') as f:
                yield filename, f.read()
        return
    # If it is an a compressed file, process it
    try:
        if not isinstance(file_data, io.BytesIO): 
            with open(filename, 'rb') as f:
                file_data = io.BytesIO(f.read())
        
        # Ask the strategy to extract the items (it doesn't matter WHICH format it is now)
        for base_name, file_bytes in strategy.extract_items(file_data):
            # Check if the extracted file is ALSO a compressed file
            nested_strategy = get_strategy(base_name)
            
            if nested_strategy:
                if current_depth < max_depth:
                    # Recurse deeper
                    yield from extract_nested_archives_in_memory(
                        io.BytesIO(file_bytes), 
                        base_name,
                        current_depth=current_depth + 1,
                        max_depth=max_depth
                    )
                else:
                    # Failsafe: Max depth reached
                    print(f"Warning: Max depth ({max_depth}) reached at '{base_name}'. Yielding raw archive.")
                    yield base_name, file_bytes
            else:
                # Normal file
                yield base_name, file_bytes

    except Exception as e:
        print(f"Warning: Failed to process archive '{filename}': {e}")


# --- 5. Execution ---
if __name__ == "__main__":
    initial_archive_path = "D:\\22\\programacion\\archivo\\musicPdfManager\\backend\\tests\\file_decompressor\\assets\\assets.rar" 
    
    # Notice how the execution call remains exactly the same
    for final_filename, final_bytes in extract_nested_archives_in_memory(initial_archive_path, initial_archive_path):
        print(f"Successfully extracted: {final_filename} (Size: {len(final_bytes)} bytes)")