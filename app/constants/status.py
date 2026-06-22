from enum import Enum

class FAQStatus(str, Enum):
    PENDING  = "pending"
    REVIEWED = "reviewed"
    ADDED_TO_FAQ = "added_to_faq"

