

## Phase 5 – Strategy Engine Deployment & Scheduling

- [x] Strategy limits seeded.
- [x] Local dry-run and execute tests performed.
- [x] Cloud Run image build & deploy scaffold in place.
- [x] Cloud Scheduler template in place.
- [ ] **IAM/Org Policy Block:** Cloud Run and Scheduler deployment was blocked by IAM permissions. The user must grant the `Secret Manager Secret Accessor` and `Service Account User` roles to the `my-run-sa` service account and rerun the deployment script.
