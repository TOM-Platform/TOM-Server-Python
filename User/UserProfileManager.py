import json
from .UserProfile import UserProfile


class UserProfileManager:
    """
    Manages User Profiles
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def save_profile(self, profile: UserProfile):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, indent=4)

    def load_profile(self) -> UserProfile:
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return UserProfile.from_dict(data)
