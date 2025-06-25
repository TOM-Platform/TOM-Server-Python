from typing import List, Dict, Optional


class UserProfile:
    """
    Keep a User Profile
    """

    def __init__(
            self,
            name: str,
            age: Optional[int] = None,
            occupation: Optional[str] = None,
            education: Optional[str] = None,
            residence: Optional[str] = None,
            citizenship: Optional[str] = None,
            travel_preferences: Optional[Dict[str, List[str]]] = None,  # e.g. {"interests": [], "not_interested": []}
            blog_writing_preferences: Optional[Dict[str, str]] = None
            # e.g. {"tone": "casual", "format": "narrative", "purpose": "inspire"}
    ):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.education = education
        self.residence = residence
        self.citizenship = citizenship
        self.travel_preferences = travel_preferences or {
            "interests": [],
            "not_interested": []
        }
        self.blog_writing_preferences = blog_writing_preferences or {
            "tone": "neutral",
            "format": "general",
            "purpose": "inform",
            "style": "concise"
        }

    def update_travel_preferences(self, category: str, items: List[str]):
        if category in self.travel_preferences:
            self.travel_preferences[category] = list(set(
                self.travel_preferences[category] + items
            ))
        else:
            self.travel_preferences[category] = items

    def update_blog_writing_preferences(self, updates: Dict[str, str]):
        self.blog_writing_preferences.update(updates)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "education": self.education,
            "residence": self.residence,
            "citizenship": self.citizenship,
            "travel_preferences": self.travel_preferences,
            "blog_writing_preferences": self.blog_writing_preferences
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            name=data.get("name"),
            age=data.get("age"),
            occupation=data.get("occupation"),
            education=data.get("education"),
            residence=data.get("residence"),
            citizenship=data.get("citizenship"),
            travel_preferences=data.get("travel_preferences"),
            blog_writing_preferences=data.get("blog_writing_preferences")
        )

    def __str__(self):
        return f"UserProfile({self.to_dict()})"
