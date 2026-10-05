from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(str, Enum):
    """Types of alien contact."""

    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """Store and validate an alien contact report."""

    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    is_verified: bool = False

    @model_validator(mode="after")
    def validate_contact_rules(self) -> "AlienContact":
        """Validate business rules for alien contact reports."""

        if not self.contact_id.startswith("AC"):
            raise ValueError(
                'Contact ID must start with "AC"'
            )

        if (
            self.contact_type == ContactType.PHYSICAL
            and not self.is_verified
        ):
            raise ValueError(
                "Physical contact reports must be verified"
            )

        if (
            self.contact_type == ContactType.TELEPATHIC
            and self.witness_count < 3
        ):
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
            )

        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError(
                "Strong signals (> 7.0) should include received message"
            )

        return self


def display_contact(contact: AlienContact) -> None:
    """Display a valid alien contact report."""

    message = contact.message_received
    if message is None:
        message = "None"

    print(f"ID: {contact.contact_id}")
    print(f"Type: {contact.contact_type.value}")
    print(f"Location: {contact.location}")
    print(f"Signal: {contact.signal_strength}/10")
    print(f"Duration: {contact.duration_minutes} minutes")
    print(f"Witnesses: {contact.witness_count}")
    print(f"Message: '{message}'")


def main() -> None:
    """Demonstrate valid and invalid contact reports."""

    print("Alien Contact Log Validation")
    print("=" * 38)

    valid_contact = AlienContact(
        contact_id="AC_2024_001",
        timestamp=datetime(2024, 10, 5, 22, 30),
        location="Area 51, Nevada",
        contact_type=ContactType.RADIO,
        signal_strength=8.5,
        duration_minutes=45,
        witness_count=5,
        message_received="Greetings from Zeta Reticuli",
        is_verified=True,
    )

    print("\nValid contact report:")
    display_contact(valid_contact)

    print("\n" + "=" * 38)
    print("Expected validation error:")

    try:
        AlienContact(
            contact_id="AC_2024_002",
            timestamp=datetime(2024, 10, 5, 23, 15),
            location="Nevada Desert",
            contact_type=ContactType.TELEPATHIC,
            signal_strength=5.5,
            duration_minutes=20,
            witness_count=2,
            message_received="We come in peace.",
        )
    except ValidationError as error:
        for validation_error in error.errors():
            print(validation_error["msg"])


if __name__ == "__main__":
    main()
