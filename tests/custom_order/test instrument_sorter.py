import pytest
from classes.custom_order.instrument_sorter import InstrumentSorter

# 1. Define the Fixture
# This fixture runs BEFORE the test. It reads the parameter passed to it
# (the order_list) and performs the monkeypatching.
@pytest.fixture
def setup_sorter_rules(request, monkeypatch:pytest.MonkeyPatch):
    order_list = request.param  # This grabs the data from parametrize
    
    # Apply the mock to ORDER_LIST
    monkeypatch.setattr(InstrumentSorter, "ORDER_LIST", order_list)
    
    # Apply the mock to _PROCESSED_ORDER_LIST (recreating the logic)
    mocked_processed = [
        (i, word.lower(), len(word)) for i, word in enumerate(order_list)
    ]
    monkeypatch.setattr(InstrumentSorter, "_PROCESSED_ORDER_LIST", mocked_processed)


@pytest.mark.parametrize(
         "original_list, setup_sorter_rules, expected_sorted",
        [
            # --- SCENARIO 1: Basic Category Ordering ---
            # Verifies that items follow the main order list.
            (
                ["Piano.pdf", "Guitar.pdf", "Drums.pdf"], 
                ["Guitar", "Piano", "Drums"], 
                ["Guitar.pdf", "Piano.pdf", "Drums.pdf"]
            ),

            # --- SCENARIO 2: The 3 Sub-Rules (Priority Check) ---
            # 1. Exact match (.pdf)
            # 2. Underscore + Digit (_01)
            # 3. Other text (_old)
            (
                ["Guitar_old.pdf", "Guitar.pdf", "Guitar_01.pdf"], 
                ["Guitar"], 
                ["Guitar.pdf", "Guitar_01.pdf", "Guitar_old.pdf"]
            ),

            # --- SCENARIO 3: Digit Sorting (Alphabetical) ---
            # Ensures that _02 comes before _10 (standard string sort).
            (
                ["Flute_10.pdf", "Flute_02.pdf", "Flute.pdf"], 
                ["Flute"], 
                ["Flute.pdf", "Flute_02.pdf", "Flute_10.pdf"]
            ),

            # --- SCENARIO 4: Case Insensitivity (Matching) ---
            # "piano" in file should match "Piano" in order list.
            (
                ["piano.pdf", "PIANO_01.pdf"], 
                ["Piano"], 
                ["piano.pdf", "PIANO_01.pdf"]
            ),

            # --- SCENARIO 5: Non-Matching Items (The "Infinity" Rule) ---
            # Items not in the list go to the end, sorted alphabetically among themselves.
            (
                ["Z_Unknown.pdf", "Guitar.pdf", "A_Unknown.pdf"], 
                ["Guitar"], 
                ["Guitar.pdf", "A_Unknown.pdf", "Z_Unknown.pdf"]
            ),

            # --- SCENARIO 6: Tie-Breaker (Alphabetical Suffix) ---
            # If two items fall into "Rule 3" (Other text), they sort alphabetically by the suffix.
            (
                ["Bass_v2.pdf", "Bass_v1.pdf"], 
                ["Bass"], 
                ["Bass_v1.pdf", "Bass_v2.pdf"]
            ),
            
            # --- SCENARIO 7: Mixed Complex Case ---
            (
                ["Oboe_old.pdf", "Violin.pdf", "Oboe.pdf", "Unknown.pdf", "Oboe_01.pdf"],
                ["Violin", "Oboe"],
                ["Violin.pdf", "Oboe.pdf", "Oboe_01.pdf", "Oboe_old.pdf", "Unknown.pdf"]
            ),

            # --- SCENARIO 8: Edge Case - Empty Lists ---
            (
                [], 
                ["Guitar"], 
                []
            ),
            (
            # 1. THE INPUT LIST (25 Mixed Elements)
            [
                "Oboe_old_version.pdf",     # Oboe (Rule 3)
                "Viola.pdf",                # Viola (Rule 1)
                "random_file_B.txt",        # No Match (End)
                "Cello_02.pdf",             # Cello (Rule 2)
                "violin.pdf",               # Violin (Rule 1 - Case insensitive match)
                "Harp_final.pdf",           # Harp (Rule 3)
                "Bass_10.pdf",              # Bass (Rule 2 - Alphabetical check vs _2)
                "Piccolo.pdf",              # Piccolo (Rule 1)
                "Flute_01.pdf",             # Flute (Rule 2)
                "Clarinet.pdf",             # Clarinet (Rule 1)
                "Sax_Alto.pdf",             # Sax (Rule 3)
                "Cello.pdf",                # Cello (Rule 1)
                "Bass.pdf",                 # Bass (Rule 1)
                "random_file_A.txt",        # No Match (End)
                "Violin_1.pdf",             # Violin (Rule 2)
                "Harp.pdf",                 # Harp (Rule 1)
                "Sax.pdf",                  # Sax (Rule 1)
                "Oboe.pdf",                 # Oboe (Rule 1)
                "Bass_2.pdf",               # Bass (Rule 2 - "2" > "10" alphabetically? No. "2" > "1" yes)
                "Viola_new.pdf",            # Viola (Rule 3)
                "Cello_01.pdf",             # Cello (Rule 2)
                "Piccolo_15.pdf",           # Piccolo (Rule 2)
                "Sax_Tenor.pdf",            # Sax (Rule 3 - Alphabetical tie break vs Alto)
                "Flute.pdf",                # Flute (Rule 1)
                "Clarinet_backup.pdf"       # Clarinet (Rule 3)
            ],
            # 2. THE ORDER LIST (10 Elements)
            [
                "Violin",       # Index 0
                "Viola",        # Index 1 (Similar prefix to Violin)
                "Cello",        # Index 2
                "Bass",         # Index 3
                "Harp",         # Index 4
                "Flute",        # Index 5
                "Piccolo",      # Index 6
                "Oboe",         # Index 7
                "Clarinet",     # Index 8
                "Sax"           # Index 9 (Short name)
            ],
            # 3. THE EXPECTED OUTPUT
            # Logic: Order List Index -> Priority (Exact, _digit, Other) -> Alphabetical
            [
                # -- Violin (Index 0) --
                "violin.pdf",               # Exact match (Rule 1)
                "Violin_1.pdf",             # _digit (Rule 2)

                # -- Viola (Index 1) --
                "Viola.pdf",                # Exact match (Rule 1)
                "Viola_new.pdf",            # Other text (Rule 3)

                # -- Cello (Index 2) --
                "Cello.pdf",                # Exact match (Rule 1)
                "Cello_01.pdf",             # _digit (Rule 2)
                "Cello_02.pdf",             # _digit (Rule 2)

                # -- Bass (Index 3) --
                "Bass.pdf",                 # Exact match (Rule 1)
                # NOTE: String sort "_10" vs "_2". 
                # '_1' comes before '_2'. So "_10" is first.
                "Bass_10.pdf",              # _digit (Rule 2) 
                "Bass_2.pdf",               # _digit (Rule 2)

                # -- Harp (Index 4) --
                "Harp.pdf",                 # Exact match (Rule 1)
                "Harp_final.pdf",           # Other text (Rule 3)

                # -- Flute (Index 5) --
                "Flute.pdf",                # Exact match (Rule 1)
                "Flute_01.pdf",             # _digit (Rule 2)

                # -- Piccolo (Index 6) --
                "Piccolo.pdf",              # Exact match (Rule 1)
                "Piccolo_15.pdf",           # _digit (Rule 2)

                # -- Oboe (Index 7) --
                "Oboe.pdf",                 # Exact match (Rule 1)
                "Oboe_old_version.pdf",     # Other text (Rule 3)

                # -- Clarinet (Index 8) --
                "Clarinet.pdf",             # Exact match (Rule 1)
                "Clarinet_backup.pdf",      # Other text (Rule 3)

                # -- Sax (Index 9) --
                "Sax.pdf",                  # Exact match (Rule 1)
                "Sax_Alto.pdf",             # Other text (Rule 3 - 'A'lto)
                "Sax_Tenor.pdf",            # Other text (Rule 3 - 'T'enor)

                # -- No Match (Sorted Alphabetically at the end) --
                "random_file_A.txt",
                "random_file_B.txt"
            ]
            )
        ],
        indirect=["setup_sorter_rules"]

)
def test_instrument_sorter(original_list:list[str], setup_sorter_rules:list[str], expected_sorted:list[str]):
    sorted_list = InstrumentSorter.sort_instruments(original_list)
    assert sorted_list == expected_sorted
