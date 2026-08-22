"""
Puzzle Bank — 20+ Categorized Interview Logic Puzzles
Used in the Situational / Puzzle Round of interviews.
Commonly asked in MNC placements (TCS, Amazon, Google, Microsoft, etc.)
"""

import random

PUZZLES = {
    "easy": [
        {
            "id": "easy-1",
            "title": "Three Switches and Three Bulbs",
            "description": "You are outside a room. There are 3 switches outside and 3 bulbs inside. Each switch controls exactly one bulb. You can enter the room only once. How do you determine which switch controls which bulb?",
            "difficulty": "Easy",
            "category": "Logic",
            "solution": "Turn Switch 1 ON for 10 minutes, then turn it OFF. Turn Switch 2 ON. Enter the room. The warm but OFF bulb = Switch 1. The ON bulb = Switch 2. The cold OFF bulb = Switch 3.",
            "evaluation_criteria": ["Uses heat as a distinguishing factor", "Mentions turning one switch on for some time then off", "Correctly identifies all three bulbs", "Logical step-by-step reasoning"],
            "time_limit": 180
        },
        {
            "id": "easy-2",
            "title": "Missing Number in Sequence",
            "description": "What comes next in this sequence?\n\n2, 6, 12, 20, 30, ?",
            "difficulty": "Easy",
            "category": "Pattern Recognition",
            "solution": "42. The differences between consecutive terms are 4, 6, 8, 10, 12 (increasing by 2). Or equivalently, the nth term = n × (n+1), so the 7th term = 7 × 6 = 42.",
            "evaluation_criteria": ["Identifies the pattern of differences", "Calculates 42 as the answer", "Shows clear reasoning", "Bonus: recognizes n*(n+1) formula"],
            "time_limit": 120
        },
        {
            "id": "easy-3",
            "title": "Two Ropes Timing Problem",
            "description": "You have two ropes. Each rope takes exactly 60 minutes to burn completely, but they do not burn at a uniform rate. How can you measure exactly 45 minutes?",
            "difficulty": "Easy",
            "category": "Logic",
            "solution": "Light Rope 1 from BOTH ends and Rope 2 from ONE end simultaneously. Rope 1 burns out in 30 minutes. At that moment, light Rope 2's other end. Rope 2 now has 30 minutes worth of rope left, but burning from both ends takes 15 minutes. Total: 30 + 15 = 45 minutes.",
            "evaluation_criteria": ["Lights one rope from both ends", "Understands non-uniform burn rate doesn't matter with both-end approach", "Correctly chains the two rope events", "Gets 45 minutes total"],
            "time_limit": 180
        },
        {
            "id": "easy-4",
            "title": "Bat and Ball Cost",
            "description": "A bat and ball together cost ₹110. The bat costs ₹100 more than the ball. How much does the ball cost?",
            "difficulty": "Easy",
            "category": "Algebra",
            "solution": "The ball costs ₹5. If ball = x, then bat = x + 100. So x + (x + 100) = 110 → 2x = 10 → x = 5. The bat costs ₹105.",
            "evaluation_criteria": ["Does NOT answer ₹10 (common trap)", "Sets up the equation correctly", "Shows algebraic reasoning", "Gets ₹5 as the answer"],
            "time_limit": 90
        },
        {
            "id": "easy-5",
            "title": "Clock Angle at 3:15",
            "description": "At exactly 3:15, what is the angle between the hour and minute hands of an analog clock?",
            "difficulty": "Easy",
            "category": "Math",
            "solution": "At 3:15, the minute hand is at 90° (pointing at 3). The hour hand moves 0.5° per minute, so at 3:15 it has moved 15 × 0.5 = 7.5° past the 3 o'clock position. The angle between them is 7.5°.",
            "evaluation_criteria": ["Knows minute hand is at 90° (at 3)", "Accounts for hour hand movement (0.5° per minute)", "Calculates 7.5° correctly", "Does NOT just say 0° or 90°"],
            "time_limit": 120
        }
    ],
    
    "medium": [
        {
            "id": "med-1",
            "title": "Eight Balls — Find the Heavier One",
            "description": "You have 8 identical-looking balls. One is heavier than the others. You have a balance scale and can use it only twice. How do you find the heavier ball?",
            "difficulty": "Medium",
            "category": "Logic",
            "solution": "Divide into groups of 3, 3, and 2. Weigh first 3 vs second 3. If balanced, weigh the remaining 2 against each other. If unbalanced, take the heavier group of 3, pick any 2 and weigh them. If balanced, the third is heavy. If not, the heavier one is found.",
            "evaluation_criteria": ["Divides into groups of 3-3-2", "Handles both balanced and unbalanced cases", "Solves in exactly 2 weighings", "Clear logical reasoning"],
            "time_limit": 180
        },
        {
            "id": "med-2",
            "title": "Bridge and Torch Problem",
            "description": "Four people need to cross a bridge at night. They have one torch. Only two people can cross at a time. Their crossing times are: A=1 min, B=2 min, C=7 min, D=10 min. When two cross together, they move at the slower person's speed. What is the minimum total crossing time?",
            "difficulty": "Medium",
            "category": "Optimization",
            "solution": "17 minutes. A&B cross (2 min). A returns (1 min). C&D cross (10 min). B returns (2 min). A&B cross (2 min). Total: 2+1+10+2+2 = 17 minutes.",
            "evaluation_criteria": ["Gets 17 minutes as the answer", "Sends fastest person back with torch", "Pairs slowest two together (C&D)", "Shows step-by-step crossing sequence"],
            "time_limit": 240
        },
        {
            "id": "med-3",
            "title": "Poisoned Bottle — 1000 Bottles, 10 Strips",
            "description": "You have 1,000 bottles of water. Exactly one is poisoned. You have 10 test strips that turn positive after 24 hours if they touch poison. How can you identify the poisoned bottle in exactly 24 hours?",
            "difficulty": "Medium",
            "category": "Binary Logic",
            "solution": "Use binary representation. Number bottles 1-1000. Each bottle number can be represented in 10 binary digits. For each strip i (1-10), apply a drop from every bottle whose binary representation has a 1 in position i. After 24 hours, the pattern of positive strips gives the binary number of the poisoned bottle. 2^10 = 1024 > 1000, so this works.",
            "evaluation_criteria": ["Uses binary encoding approach", "Maps each strip to a bit position", "Explains how to decode the result", "Understands 2^10 covers 1000"],
            "time_limit": 300
        },
        {
            "id": "med-4",
            "title": "Farmer, Wolf, Goat, and Cabbage",
            "description": "A farmer needs to cross a river with a wolf, a goat, and a cabbage. His boat can carry only the farmer and one item. He cannot leave: wolf alone with goat, or goat alone with cabbage. How does he get everything across safely?",
            "difficulty": "Medium",
            "category": "Constraint Logic",
            "solution": "1) Take goat across. 2) Return alone. 3) Take wolf across. 4) Bring goat back. 5) Take cabbage across. 6) Return alone. 7) Take goat across. Done in 7 trips.",
            "evaluation_criteria": ["Takes goat first (key insight)", "Brings goat back at the right step", "Never violates constraints", "Completes in 7 crossings"],
            "time_limit": 180
        },
        {
            "id": "med-5",
            "title": "100 Doors Problem",
            "description": "There are 100 closed doors. Person 1 opens every door. Person 2 toggles every 2nd door. Person 3 toggles every 3rd door. This continues until Person 100. Which doors remain open?",
            "difficulty": "Medium",
            "category": "Number Theory",
            "solution": "Doors with perfect square numbers remain open: 1, 4, 9, 16, 25, 36, 49, 64, 81, 100. A door is toggled once for each of its divisors. Most numbers have an even number of divisors (paired), but perfect squares have an odd number (one divisor pairs with itself), so they end up open.",
            "evaluation_criteria": ["Identifies perfect squares as the answer", "Explains the divisor pairing logic", "Lists correct doors (1,4,9,16,25,36,49,64,81,100)", "Shows understanding of odd vs even divisor count"],
            "time_limit": 240
        }
    ],
    
    "hard": [
        {
            "id": "hard-1",
            "title": "12 Coins — Find the Odd One",
            "description": "You have 12 identical-looking coins. One is either heavier or lighter than the others (you don't know which). Using a balance scale only 3 times, identify which coin is different AND whether it is heavier or lighter.",
            "difficulty": "Hard",
            "category": "Advanced Logic",
            "solution": "Divide into 3 groups of 4. Weigh Group A vs Group B. Case analysis based on balanced/unbalanced results, systematically narrowing down using the third weighing to determine both the odd coin and whether it's heavy or light.",
            "evaluation_criteria": ["Divides into 3 groups of 4", "Handles both heavier and lighter possibility", "Uses all 3 weighings efficiently", "Determines both identity and weight direction"],
            "time_limit": 300
        },
        {
            "id": "hard-2",
            "title": "Two Eggs, 100 Floors",
            "description": "You have two identical eggs and a 100-floor building. An egg breaks if dropped from a certain floor or higher. You need to determine the highest safe floor. What is the minimum number of drops needed in the worst case?",
            "difficulty": "Hard",
            "category": "Optimization",
            "solution": "14 drops. Start at floor 14, then 27 (14+13), then 39 (27+12), etc. Each time the first egg survives, go up by one less floor. If the first egg breaks, use the second egg to check floors one by one from the previous checkpoint. The formula is: n(n+1)/2 ≥ 100, so n = 14.",
            "evaluation_criteria": ["Gets 14 as the answer", "Explains the decreasing interval strategy", "Mentions n(n+1)/2 ≥ 100 formula", "Understands the two-egg constraint (linear search after first break)"],
            "time_limit": 300
        },
        {
            "id": "hard-3",
            "title": "100 Prisoners and Boxes",
            "description": "100 prisoners and 100 boxes. Each box contains one prisoner's number (randomly placed). Each prisoner may open at most 50 boxes to find their own number. They cannot communicate after the process begins. What strategy gives them the highest probability of ALL prisoners succeeding?",
            "difficulty": "Hard",
            "category": "Probability & Strategy",
            "solution": "Loop strategy: Each prisoner starts at the box with their own number, then follows the chain (opens the box whose number they just found). Since each permutation decomposes into cycles, if no cycle is longer than 50, everyone succeeds. The probability of success is approximately 1 - ln(2) ≈ 30.7%.",
            "evaluation_criteria": ["Describes the loop/cycle following strategy", "Understands permutation cycles", "Mentions ~30.7% success probability", "Explains why random guessing fails (0.5^100)"],
            "time_limit": 300
        },
        {
            "id": "hard-4",
            "title": "Three Ants on a Triangle",
            "description": "Three ants are placed randomly on the three corners of a triangle. Each ant randomly chooses one of the two directions and starts walking along the edges. What is the probability that no two ants collide?",
            "difficulty": "Hard",
            "category": "Probability",
            "solution": "1/4 or 25%. Each ant has 2 choices → 2³ = 8 total outcomes. No collision only when ALL go clockwise (1 way) or ALL go counter-clockwise (1 way). So 2/8 = 1/4 = 25%.",
            "evaluation_criteria": ["Calculates 2^3 = 8 total outcomes", "Identifies the 2 collision-free cases (all CW or all CCW)", "Gets 2/8 = 1/4 = 25%", "Clear probabilistic reasoning"],
            "time_limit": 180
        },
        {
            "id": "hard-5",
            "title": "25 Horses — Find Top 3",
            "description": "You have 25 horses and can race 5 at a time. You don't have a stopwatch — you only know the finishing order within each race. What is the minimum number of races needed to determine the three fastest horses?",
            "difficulty": "Hard",
            "category": "Tournament Logic",
            "solution": "7 races. First 5 races: race all 25 horses in groups of 5. 6th race: race the 5 group winners. This finds the fastest horse. 7th race: race the 2nd and 3rd from the fastest group, the 2nd from the runner-up group, and the winner of the third-place group. The top 2 from this race are the 2nd and 3rd fastest overall.",
            "evaluation_criteria": ["Gets 7 as the answer", "Explains the 5 initial group races", "Explains the 6th race of group winners", "Correctly identifies which horses compete in the 7th race"],
            "time_limit": 300
        }
    ],
    
    "company_style": [
        {
            "id": "comp-1",
            "title": "The 8-Litre Measurement Problem",
            "description": "You have three containers: 8 litres (full), 5 litres (empty), and 3 litres (empty). Using only these containers, measure exactly 4 litres.",
            "difficulty": "Medium",
            "category": "Constraint Logic",
            "solution": "Step 1: Pour 8→5 (8:0→3:5:0). Step 2: Pour 5→3 (3:2:3). Step 3: Pour 3→8 (6:2:0). Step 4: Pour 5→3 (6:0:2). Step 5: Pour 8→5 (1:5:2). Step 6: Pour 5→3 (1:4:3). Step 7: Pour 3→8 (4:4:0). Result: 4 litres in both 8L and 5L containers.",
            "evaluation_criteria": ["Arrives at 4 litres in some container", "Uses a step-by-step pouring sequence", "Doesn't violate container capacity constraints", "Shows systematic approach"],
            "time_limit": 300
        },
        {
            "id": "comp-2",
            "title": "The Restaurant Bill Paradox",
            "description": "Three friends pay ₹300 for a meal. The waiter returns ₹50 because the bill should have been ₹250. He gives each person ₹10 back and keeps ₹20. So each person paid ₹90: 3 × ₹90 = ₹270. The waiter has ₹20. ₹270 + ₹20 = ₹290. Where did the remaining ₹10 go?",
            "difficulty": "Easy",
            "category": "Logical Fallacy",
            "solution": "There is no missing ₹10. The question uses misleading arithmetic. The correct accounting: Each paid ₹90, total = ₹270. Of that ₹270: ₹250 went to the restaurant + ₹20 to the waiter = ₹270. You should NOT add the waiter's ₹20 to the ₹270 — it's already included in the ₹270.",
            "evaluation_criteria": ["Identifies it as a trick/misleading question", "Explains the correct accounting (270 = 250 + 20)", "Points out you shouldn't add 270 + 20", "Stays calm and explains clearly"],
            "time_limit": 180
        },
        {
            "id": "comp-3",
            "title": "Find the Lighter Coin (9 Coins)",
            "description": "You have 9 coins. One is lighter than the rest. Using a balance scale only 2 times, find the lighter coin.",
            "difficulty": "Easy",
            "category": "Logic",
            "solution": "Divide into 3 groups of 3. Weigh Group A vs Group B. If balanced, the lighter coin is in Group C. If unbalanced, take the lighter group. Then weigh any 2 coins from the suspect group. If balanced, the third is the lighter one. If unbalanced, the lighter side has it.",
            "evaluation_criteria": ["Divides into groups of 3", "Handles balanced and unbalanced cases", "Solves in exactly 2 weighings", "Uses elimination logic"],
            "time_limit": 120
        },
        {
            "id": "comp-4",
            "title": "Burning Candles — Measure 30 Minutes",
            "description": "You have two candles. Each takes exactly 1 hour to burn completely, but they burn at different (non-uniform) rates. How can you measure exactly 30 minutes?",
            "difficulty": "Easy",
            "category": "Logic",
            "solution": "Light one candle from BOTH ends. It will burn out in exactly 30 minutes (since the total burn time is halved regardless of the non-uniform rate). You don't even need the second candle for this measurement.",
            "evaluation_criteria": ["Lights one candle from both ends", "Gets 30 minutes correctly", "Understands non-uniform rate doesn't matter", "Simple and direct reasoning"],
            "time_limit": 120
        },
        {
            "id": "comp-5",
            "title": "The Hotel Derangement Problem",
            "description": "A hotel has 100 rooms and 100 guests, each assigned a room. The manager wants every guest to move to a different room such that nobody ends up in their original room. How would you design this process?",
            "difficulty": "Medium",
            "category": "Combinatorics",
            "solution": "Simplest approach: Shift everyone by one room — Guest in Room 1 → Room 2, Room 2 → Room 3, ..., Room 100 → Room 1. This is a cyclic permutation (derangement). More generally, any derangement of 100 elements works. The number of possible derangements is D(100) ≈ 100!/e.",
            "evaluation_criteria": ["Proposes a valid derangement (e.g., cyclic shift)", "Ensures no guest stays in their original room", "Mentions the concept of derangement or permutation", "Bonus: mentions D(n) formula"],
            "time_limit": 180
        }
    ]
}


def get_random_puzzle(difficulty=None):
    """
    Get a random puzzle from the bank.
    
    Args:
        difficulty: 'Easy', 'Medium', 'Hard', or None (random)
    
    Returns:
        dict: Puzzle with id, title, description, solution, evaluation_criteria
    """
    if difficulty:
        diff_key = difficulty.lower()
        if diff_key in PUZZLES:
            return random.choice(PUZZLES[diff_key])
        elif diff_key in ['easy', 'medium', 'hard']:
            return random.choice(PUZZLES[diff_key])
    
    # If no difficulty specified or not found, pick from all including company_style
    all_puzzles = []
    for category_puzzles in PUZZLES.values():
        all_puzzles.extend(category_puzzles)
    
    return random.choice(all_puzzles)


def get_puzzle_by_id(puzzle_id):
    """Get a specific puzzle by its ID."""
    for category_puzzles in PUZZLES.values():
        for puzzle in category_puzzles:
            if puzzle['id'] == puzzle_id:
                return puzzle
    return None


def get_puzzles_for_interview(difficulty='Medium', count=1):
    """
    Get puzzles appropriate for the interview difficulty.
    
    Easy interview → Easy puzzles + Company-style
    Medium interview → Medium puzzles + Company-style
    Hard interview → Hard puzzles + some Medium
    
    Args:
        difficulty: 'Easy', 'Medium', 'Hard'
        count: Number of puzzles to return
    
    Returns:
        list: List of puzzle dicts
    """
    pool = []
    
    if difficulty == 'Easy':
        pool = PUZZLES['easy'] + PUZZLES['company_style']
    elif difficulty == 'Hard':
        pool = PUZZLES['hard'] + PUZZLES['medium'][:2]
    else:  # Medium (default)
        pool = PUZZLES['medium'] + PUZZLES['company_style']
    
    count = min(count, len(pool))
    return random.sample(pool, count)


def get_all_puzzles():
    """Return all puzzles grouped by difficulty."""
    return PUZZLES


def get_puzzle_count():
    """Get total number of puzzles in the bank."""
    return sum(len(v) for v in PUZZLES.values())
