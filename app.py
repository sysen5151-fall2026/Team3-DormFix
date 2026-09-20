"""Run one canned UC.1 scenario through the DormFix walking skeleton."""

from resident_interface import describe_issue, provide_information, submit_issue


def main():
    # The driver represents the Student Resident in one nominal scenario.
    description = "The sink is leaking."
    intake = describe_issue(description)
    print("DormFix Walking Skeleton")
    print("------------------------")
    print(f"Resident report: {description}")
    print(f"Missing-information prompt: {intake['prompt']}")

    supplemental_information = {
        "location": "Example residence, Room 101",
        "availability": "Example access window",
    }
    reviewed_draft = provide_information(intake["draft"], supplemental_information)
    print(f"Structured draft for resident review: {reviewed_draft}")

    # This explicit third call represents review followed by submission.
    result = submit_issue(reviewed_draft)
    print(f"Ticket ID: {result['ticket']['ticket_id']}")
    print(f"Status: {result['ticket']['status']}")
    print(f"Category: {result['ticket']['request']['category']}")
    print("Missing information:", result["ticket"]["request"]["missing_fields"])


if __name__ == "__main__":
    main()
