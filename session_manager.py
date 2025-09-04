import random
import time
from datetime import datetime, timedelta

class HumanSession:
    """Simulates human-like session behavior for web scraping"""
    
    def __init__(self):
        # Time-based session parameters
        self.session_start = datetime.now()
        self.max_session_length = random.randint(30, 90)  # Session lasts 30-90 minutes

        # Randomize activity levels
        self.activity_level = random.choice(['light', 'moderate', 'active'])
        
        # Set typical browsing patterns based on time of day
        current_hour = self.session_start.hour
        
        # Humans are more active during certain hours
        if 0 <= current_hour < 6:  # Late night
            self.activity_multiplier = 1.5 # Slower, longer pauses
        elif 6 <= current_hour < 9:  # Early morning
            self.activity_multiplier = 0.8  # A bit faster
        elif 9 <= current_hour < 17:  # Work hours
            self.activity_multiplier = 1.0  # Normal
        elif 17 <= current_hour < 23:  # Evening
            self.activity_multiplier = 1.2  # Slightly slower
        else:  # Late evening
            self.activity_multiplier = 1.4

        # Set session parameters based on activity level
        if self.activity_level == 'light':
            self.search_delay_range = (60, 150)
            self.break_probability = 0.25
            self.break_duration_range = (180, 600)  # 3-10 minutes
        elif self.activity_level == 'moderate':
            self.search_delay_range = (30, 100)
            self.break_probability = 0.15
            self.break_duration_range = (90, 300)  # 1.5-5 minutes
        else:  # active
            self.search_delay_range = (20, 70)
            self.break_probability = 0.10
            self.break_duration_range = (45, 180)  # 45sec-3min
        
        # Apply time-of-day multiplier to delays
        self.search_delay_range = (
            self.search_delay_range[0] * self.activity_multiplier,
            self.search_delay_range[1] * self.activity_multiplier
        )
        
        print(f"[INFO] New session started with '{self.activity_level}' activity profile.")
    
    def should_continue(self):
        """Check if the session should continue based on elapsed time."""
        elapsed_minutes = (datetime.now() - self.session_start).total_seconds() / 60
        return elapsed_minutes < self.max_session_length
    
    def get_next_delay(self):
        """Get the next delay between actions with natural variation."""
        base_delay = random.uniform(*self.search_delay_range)
        
        # 10% chance of a "distraction"
        if random.random() < 0.1:
            distraction = random.uniform(20, 70)
            print(f"[INFO] Simulating user distraction for {distraction:.1f}s...")
            return base_delay + distraction
        
        return base_delay
    
    def should_take_break(self):
        """Determine if the user should take a short break."""
        return random.random() < self.break_probability
    
    def get_break_duration(self):
        """Get duration for a break."""
        return random.uniform(*self.break_duration_range)
