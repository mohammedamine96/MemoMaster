import datetime
import math

def calculate_next_review(quality, last_interval, ease_factor):
    """
    Calculates the next review interval and ease factor using the SM-2 algorithm.
    
    Args:
        quality (int): The quality of the response (0-5).
            0: Complete blackout.
            1: Incorrect response; the correct one remembered.
            2: Incorrect response; where the correct one seemed easy to recall.
            3: Correct response recalled with serious difficulty.
            4: Correct response after a hesitation.
            5: Perfect recall.
        last_interval (int): The previous interval in days.
        ease_factor (float): The previous ease factor.
        
    Returns:
        tuple: (next_interval, new_ease_factor, next_due_date)
    """
    
    # 1. Update Ease Factor
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    # If EF' < 1.3, then EF' = 1.3
    new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ease_factor < 1.3:
        new_ease_factor = 1.3
        
    # 2. Calculate Next Interval
    if quality < 3:
        # If the student failed, start over
        next_interval = 1
    else:
        if last_interval == 0:
            next_interval = 1
        elif last_interval == 1:
            next_interval = 6
        else:
            next_interval = math.ceil(last_interval * new_ease_factor)
            
    # 3. Calculate Due Date
    next_due_date = datetime.datetime.now() + datetime.timedelta(days=next_interval)
    
    return next_interval, new_ease_factor, next_due_date
