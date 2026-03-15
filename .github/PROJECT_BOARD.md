# Project Board Configuration

GitHub Projects board: <https://github.com/orgs/Hexadian-Corporation/projects/1>

## Columns (Status field)

| Column        | Purpose                                            |
| ------------- | -------------------------------------------------- |
| **Backlog**       | Created issues pending prioritisation              |
| **Ready**         | Issues with all dependencies resolved, ready to start |
| **In Progress**   | Actively being developed                           |
| **In Review**     | In code review / PR open                           |
| **Done**          | Completed and merged                               |

## Additional Views

| View               | Grouping      |
| ------------------ | ------------- |
| View by Milestone  | Group by milestone  |
| View by Repository | Group by repository |

## Labels

Labels are defined in [`.github/labels.yml`](labels.yml) and synced to all
target repositories by the **Sync labels** workflow
([`.github/workflows/sync-labels.yml`](workflows/sync-labels.yml)).

Target repositories:

- `hexadian-hauling-helper`
- `hhh-contracts-service`
- `hhh-backoffice-frontend`
- `hhh-frontend`
- `hhh-maps-service`

### Triggering a manual sync

Go to **Actions → Sync labels → Run workflow** on the `main` branch.

A `LABEL_SYNC_TOKEN` organisation secret with `repo` scope is required for
cross-repository syncing.
