# Back-End-Development-Songs

MongoDB-backed Songs REST service, completed from the official [IBM starter](https://github.com/ibm-developer-skills-network/hvlga-Back-End-Development-Songs).
Original starter attribution and license are retained. Changes were prepared with AI assistance and should be reviewed by the learner before submission.

## Environment Setup

Tested locally with Python 3.14. Flask/Django dependency versions are pinned in requirements.txt. Run from this repository:

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The original course bin/setup.sh is preserved as supplied by IBM; it targets the course Cloud IDE. Local verification used the Python setup described above, rather than claiming that the Cloud IDE setup script ran.

## Implemented work

MongoDB connection from environment variables, health/count, GET all/by-id, create/update/delete endpoints, BSON JSON serialization and error handling. Seeding uses upserts and does not drop a database or overwrite existing records. The original template's credential-printing and drop-on-start code were removed.

Set MONGODB_URI to your MongoDB connection URI. Alternatively set MONGODB_SERVICE, MONGODB_PORT, and optional MONGODB_USERNAME/MONGODB_PASSWORD. Never commit actual credentials. Set MONGODB_SEED=1 to seed missing course data at startup.

```sh
# Example local test instance; change port to your actual database.
export MONGODB_URI=mongodb://127.0.0.1:27028
export MONGODB_SEED=1
python -m pytest -v tests
python -m flask --app backend run --host 127.0.0.1 --port 5001
```

MONGODB_MOCK=1 is available for isolated tests only. The recorded verification used a real MongoDB process, not this mode.

## Verification

3 tests passed against real local MongoDB 8.0.26, including the original health test and added CRUD/seed tests.

## Submission status

Prepared and tested locally. Not yet published to the learner GitHub account or deployed to IBM Cloud. Local screenshots and execution reports must not be described as cloud deployment evidence.
