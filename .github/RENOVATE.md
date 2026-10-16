# Running Renovate

The `Renovate` workflow runs daily and can be started from **Actions → Renovate →
Run workflow** on `main`. It updates only this repository, using `renovate.json`.
Existing major-update approvals and merge policies remain in effect. Update
commits use Conventional Commits and the author `pheelee <pri@irbe.ch>`.

Before the first run:

1. Disable the hosted Renovate App for this repository to avoid duplicate update
   PRs. Existing App-created PRs remain available for manual review; this runner
   uses `renovate-actions/` branches so it does not modify the App's branches.
2. Create a fine-grained PAT for the account `pheelee`, restricted to the
   repositories this runner should maintain. Grant Contents, Pull requests,
   Issues and Workflows read/write access, plus Checks and Commit statuses read
   access. Workflows write access allows GitHub Actions dependency updates.
3. Store the PAT as the repository Actions secret `RENOVATE_TOKEN`, then run the
   workflow manually. Set an expiry and rotate it before expiry. Do not put the
   token in a config file, issue, PR or workflow input.

The default `GITHUB_TOKEN` is unsuitable here because dependency PRs it creates
would not trigger the required PR workflows. The PAT allows those CI runs. The
Renovate runner itself listens only to its schedule and manual dispatch, so those
PR events do not create a workflow loop.

The runner has no checkout step, runs only on `main`, disables package scripts,
and receives no other repository secrets. This is self-hosted Renovate in GitHub
Actions; it is an alternative to the hosted App used by the community repos.
No signing key is configured; setting the commit author does not sign commits.
