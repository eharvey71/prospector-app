"""Seed a profile and a watchlist for one user, to get a new install moving.

Everything below is placeholder. Put your own details in, or sign in to
the app and fill the Profile page instead — this script exists only so a
fresh project has something to crawl against before the UI is up.

    export SEED_PROJECT=your-project-id
    export SEED_UID=the-auth-uid-from-the-firebase-console
    python seed.py

Add --wipe to delete that user's applications and EVERY job posting in
the project first. That is destructive and global; it used to run
unconditionally at the bottom of this file.
"""
import argparse
import os
import sys

from google.cloud import firestore

PROJECT = os.environ.get("SEED_PROJECT", "")
UID = os.environ.get("SEED_UID", "")

profile = {
    "name": "Ada Example",
    "email": "ada@example.com",
    "location": "Richmond, VA",
    "work_auth": "US citizen",
    "salary_target": None,
    "skills": [
        "Python", "FastAPI", "PostgreSQL", "AWS", "GCP", "Firebase",
        "RESTful APIs", "technical documentation", "team leadership",
    ],
    "work_history": [
        {
            "company": "Example Corp",
            "title": "Senior Backend Developer",
            "start": "2024-01",
            "end": None,
            "bullets": [
                "Built and operated Python services behind a customer-facing product",
                "Owned release management and on-call for the platform",
            ],
        },
        {
            "company": "Another Example Inc",
            "title": "Solutions Engineer",
            "start": "2021-01",
            "end": "2024-01",
            "bullets": [
                "Ran pre-sales demonstrations and trial implementations",
                "Delivered integrations for education customers",
            ],
        },
    ],
    "writing_samples": [
        # {"title": "Sample name", "text": "a paragraph or two of your own prose"},
        #
        # Voice only. Do NOT paste a past cover letter here: the drafter
        # copies rhythm from these, and an old letter's employer leaks
        # into new ones (see functions/letter_guard.py).
    ],
    "preferences": {
        "titles": ["AI Engineer", "Solutions Architect"],
        "remote_only": False,
        "exclude_companies": [],
        "min_match_score": 70,
    },
}

watchlist = {
    "greenhouse": ["anthropic", "gitlab", "instructure"],
    "lever": [],
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wipe", action="store_true",
                    help="first delete this user's applications and ALL "
                         "job postings in the project")
    args = ap.parse_args()

    if not PROJECT or not UID:
        print("set SEED_PROJECT and SEED_UID first — see the docstring")
        return 2

    db = firestore.Client(project=PROJECT)

    if args.wipe:
        confirm = input(f"Delete {UID}'s applications and EVERY job posting "
                        f"in {PROJECT}? Type the project id to confirm: ")
        if confirm.strip() != PROJECT:
            print("not confirmed; nothing deleted")
            return 1
        n = 0
        for doc in (db.collection("users").document(UID)
                    .collection("applications").stream()):
            doc.reference.delete()
            n += 1
        print(f"deleted {n} applications")
        n = 0
        for doc in db.collection("jobPostings").stream():
            doc.reference.delete()
            n += 1
        print(f"deleted {n} postings")

    db.collection("users").document(UID).set(profile)
    (db.collection("users").document(UID)
       .collection("watchlist").document("companies").set(watchlist))
    print("seeded profile + watchlist for", UID)
    return 0


if __name__ == "__main__":
    sys.exit(main())
