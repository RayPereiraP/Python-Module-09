from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    """Available crew ranks."""

    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """Represent a crew member."""

    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    """Represent a space mission and its crew."""

    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: List[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission_rules(self) -> "SpaceMission":
        """Validate safety requirements for the mission."""

        if not self.mission_id.startswith("M"):
            raise ValueError(
                'Mission ID must start with "M"'
            )

        has_leader = any(
            member.rank in {Rank.COMMANDER, Rank.CAPTAIN}
            for member in self.crew
        )

        if not has_leader:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        if self.duration_days > 365:
            experienced_crew = sum(
                member.years_experience >= 5
                for member in self.crew
            )

            if experienced_crew * 2 < len(self.crew):
                raise ValueError(
                    "Long missions (> 365 days) need 50% "
                    "experienced crew"
                )

        if not all(member.is_active for member in self.crew):
            raise ValueError(
                "All crew members must be active"
            )

        return self


def display_crew_member(member: CrewMember) -> None:
    """Display crew member information."""

    print(
        f"- {member.name} "
        f"({member.rank.value}) - {member.specialization}"
    )


def display_mission(mission: SpaceMission) -> None:
    """Display mission information and crew details."""

    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")

    for member in mission.crew:
        display_crew_member(member)


def main() -> None:
    """Demonstrate valid and invalid space missions."""

    print("Space Mission Crew Validation")
    print("=" * 41)

    valid_mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date=datetime(2024, 6, 15, 10, 30),
        duration_days=900,
        crew=[
            CrewMember(
                member_id="CM001",
                name="Sarah Connor",
                rank=Rank.COMMANDER,
                age=42,
                specialization="Mission Command",
                years_experience=15,
            ),
            CrewMember(
                member_id="CM002",
                name="John Smith",
                rank=Rank.LIEUTENANT,
                age=35,
                specialization="Navigation",
                years_experience=8,
            ),
            CrewMember(
                member_id="CM003",
                name="Alice Johnson",
                rank=Rank.OFFICER,
                age=29,
                specialization="Engineering",
                years_experience=6,
            ),
        ],
        budget_millions=2500.0,
    )

    print("\nValid mission created:")
    display_mission(valid_mission)

    print("\n" + "=" * 41)
    print("Expected validation error:")

    try:
        SpaceMission(
            mission_id="M2024_TEST",
            mission_name="Test Mission",
            destination="Moon",
            launch_date=datetime(2024, 7, 1, 10, 30),
            duration_days=100,
            crew=[
                CrewMember(
                    member_id="CM004",
                    name="Bob Carter",
                    rank=Rank.LIEUTENANT,
                    age=35,
                    specialization="Navigation",
                    years_experience=10,
                ),
                CrewMember(
                    member_id="CM005",
                    name="Jane Miller",
                    rank=Rank.OFFICER,
                    age=30,
                    specialization="Engineering",
                    years_experience=5,
                ),
            ],
            budget_millions=500.0,
        )
    except ValidationError as error:
        for validation_error in error.errors():
            print(validation_error["msg"])


if __name__ == "__main__":
    main()
