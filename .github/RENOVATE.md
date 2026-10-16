# Running Renovate

The `Renovate` workflow runs daily and can be started from **Actions → Renovate →
Run workflow** on `main`. It updates only this repository, using `renovate.json`.
Existing major-update approvals and merge policies remain in effect. Update
commits use Conventional Commits.

Authentication follows [pheelee/cat](https://github.com/pheelee/cat/blob/main/.github/workflows/renovate.yml),
using the `irbe-automation` GitHub App:

1. Ensure the App is installed with access to this repository. It needs Contents,
   Pull requests, Issues and Workflows write access, plus Checks and Commit
   statuses read access. Workflows write access allows Actions dependency updates.
2. Make the App client ID available as the Actions variable
   `GHA_IRBE_AUTOMATION_APP_ID` and its private key as the Actions secret
   `GHA_IRBE_AUTOMATION_APP_PRIVATE_KEY`, using the same values as `cat`.
3. Disable the separate hosted Renovate App for this repository to avoid
   duplicate updates. Keep `irbe-automation` installed. Existing hosted-App PRs
   remain available for review; this runner uses `renovate-actions/` branches.
4. Run the workflow manually after merging it.

The token action generates a short-lived installation token restricted to this
repository and revokes it when the job finishes. A `RENOVATE_TOKEN` PAT is not
needed. App-created dependency PRs can trigger the required CI workflows. The
Renovate runner itself listens only to its schedule and manual dispatch.

Unlike `cat`, this workflow does not check out the repository or request write
permissions for the built-in token; Renovate fetches its repository through the
App token. It runs only on `main`, disables package scripts, and receives no
registry credential because the tracked images are public. The existing update
approval and merge policies remain in `renovate.json`.
