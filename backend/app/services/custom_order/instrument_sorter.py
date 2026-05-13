import re
from pathlib import Path
from backend.app.utils.settings import get_server_settings

def load_instruments_order(file_path: str|None = None) -> list[str]:
    if file_path is None:
        file_path = get_server_settings().instruments_order_file
    return [line.strip() for line in Path(file_path).read_text(encoding="utf-8").splitlines()]

class InstrumentSorter:
    NON_MATCH_INDEX = float('inf')

    ORDER_LIST = load_instruments_order()

    # We pre-calculate the lowercase versions of the order list.
    # This prevents us from running .lower() on the order list N times per file.
    # We store: (original_index, lowercase_word, length_of_word)
    _PROCESSED_ORDER_LIST = [
        (i, word.lower(), len(word)) 
        for i, word in enumerate(ORDER_LIST)
    ]

    @staticmethod
    def sort_instruments(target_list:list[str]) -> list[str]:
        """
        Sorts target_list based on order_list (case-insensitive matching),
        but preserves case-sensitive sorting for the remaining text.
        """

        def get_sort_key(filename: str):
            # We work with a lowercase version of the filename ONLY for matching
            filename_lower = filename.lower()
            
            match_index = InstrumentSorter.NON_MATCH_INDEX
            matched_length = 0
            
            # 1. Check against our pre-processed lowercase order list
            for index, word_lower, word_len in InstrumentSorter._PROCESSED_ORDER_LIST:
                if filename_lower.startswith(word_lower):
                    match_index = index
                    matched_length = word_len
                    break 
            
            # 2. If no match, send to the end
            if match_index == InstrumentSorter.NON_MATCH_INDEX:
                return (InstrumentSorter.NON_MATCH_INDEX, 0, filename)

            # 3. Analyze "Extra Text"
            # IMPORTANT: We slice the ORIGINAL filename, preserving case for the sub-sort
            remainder = filename[matched_length:]

            # Rule A: Exact match ending in .pdf (case-insensitive check)
            # We check if the lower version of remainder is just '.pdf'
            if remainder.lower() == '.pdf':
                return (match_index, 0, "")
            
            # Rule B: Extra text is _digit
            if re.match(r'^_\d+', remainder):
                return (match_index, 1, remainder)
                
            # Rule C: All other extra text
            return (match_index, 2, remainder)

        return sorted(target_list, key=get_sort_key)
