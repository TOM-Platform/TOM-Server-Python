import os
import json
import pytest
from User.UserProfile import UserProfile
from User.UserProfileManager import UserProfileManager


@pytest.fixture
def sample_profile():
    return UserProfile(
        name="Sasha Rivera",
        age=31,
        occupation="Travel Writer",
        education="MA in Journalism",
        residence="Barcelona, Spain",
        citizenship="USA",
        travel_preferences={
            "interests": ["slow travel"],
            "not_interested": ["tourist traps"]
        },
        blog_writing_preferences={
            "tone": "casual",
            "format": "storytelling",
            "purpose": "inspire"
        }
    )


def test_user_profile_initialization(sample_profile):
    assert sample_profile.name == "Sasha Rivera"
    assert sample_profile.age == 31
    assert "slow travel" in sample_profile.travel_preferences["interests"]
    assert sample_profile.blog_writing_preferences["tone"] == "casual"


def test_update_travel_preferences(sample_profile):
    sample_profile.update_travel_preferences("interests", ["road trips"])
    assert "road trips" in sample_profile.travel_preferences["interests"]


def test_update_blog_writing_preferences(sample_profile):
    sample_profile.update_blog_writing_preferences({"tone": "witty"})
    assert sample_profile.blog_writing_preferences["tone"] == "witty"


def test_to_dict_and_from_dict(sample_profile):
    profile_dict = sample_profile.to_dict()
    new_profile = UserProfile.from_dict(profile_dict)
    assert new_profile.name == sample_profile.name
    assert new_profile.travel_preferences == sample_profile.travel_preferences


def test_save_and_load_profile(tmp_path, sample_profile):
    file_path = tmp_path / "test_profile.json"
    manager = UserProfileManager(str(file_path))

    manager.save_profile(sample_profile)
    assert file_path.exists()

    loaded_profile = manager.load_profile()
    assert loaded_profile.name == "Sasha Rivera"
    assert "slow travel" in loaded_profile.travel_preferences["interests"]
    assert loaded_profile.blog_writing_preferences["purpose"] == "inspire"
