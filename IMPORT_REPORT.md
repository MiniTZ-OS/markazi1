# Import Report

**Status: PARTIAL — public working-tree consolidation succeeded; full private-source/history import requires the listed Actions secrets.**

Target: `MMLabsAI/markazi1`

## Verified import

- Six public source repositories were fetched during the latest run; four have fully pushed their current source refs through the automated path.
- The consolidated `main` working tree now contains the union of unique paths plus conflicting versions under `__MINITZ_SOURCE_VERSIONS__/`.
- Latest automated run: [run 5](https://github.com/MMLabsAI/markazi1/actions/runs/38600020360), concluded success.
- Automated scan observed 7 source branch refs, 4 tag refs, 11 branch/tag trees, and 101 tree entries. Git LFS reported no failures in that run.
- Six refs that Git push rejected have been recovered through the connected GitHub API, preserving their original commit SHAs. Verified target branch heads:
  - `source-branches/MInitzrm/TaghdisiLabs/main` and `.../tree` → `68a80d406a421c6391288aa8d774387ab5346867`
  - `source-branches/MInitzrm/ZombieTZ-Releases/main` → `bd51a44a46dd1aa515cfacbe233f849ba81c6a09`
  - Matching content-addressed snapshots are also present.
  - The commit for tag `demo01-rtx-20261004-c35d317` is preserved at `source-tag-commits/MInitzrm/ZombieTZ-Releases/demo01-rtx-20261004-c35d317` and its snapshot branch. The literal Git tag ref remains pending a target write token with Workflows permission.

## Required repository Actions secrets

Add the following secrets in **Settings → Secrets and variables → Actions**. Use tokens from the corresponding account, not copied credentials in chat.

- `SOURCE_TOKEN_MAHDITT96`: read access to private repositories visible to MahdiTT96.
- `SOURCE_TOKEN_MMLABSAI`: read access to private repositories visible to MMLabsAI.
- `SOURCE_TOKEN_MATAGHDISI96_SOURCE`: read access to repositories visible to mataghdisi96-source; that connector inventory returned zero repositories, so this token also enables a full API inventory.
- `TARGET_WRITE_TOKEN`: write access to `MMLabsAI/markazi1`, including **Contents: read/write** and **Workflows: read/write**. It enables original commit refs containing workflow changes to be imported exactly. It may be the same token value as `SOURCE_TOKEN_MMLABSAI` if that token has the required target permissions; store it under both secret names.

Then run the workflow manually from [Actions](https://github.com/MMLabsAI/markazi1/actions) using **Consolidate repository history → Run workflow**. It discovers all additional repositories accessible to the configured tokens and retries the missing private history and refs.

## Private repositories currently skipped

`MiniTZOS/minitz-os-final`, `MiniTZOS/MiniTZOS`, `MInitzrm/biella`, `MInitzrm/biella-engine`, `MInitzrm/biella-games`, `MInitzrm/capability_preparation`, `MInitzrm/MiniTZ`, `MInitzrm/MiniTZCTO`, `MInitzrm/MiniTZOS-booted`, `MInitzrm/MiniTZOS-preboot`, `taghdisilabs-digital/demo-repository`, and `taghdisilabs-digital/tree`.

## Remaining limitations

- GitHub release assets are not Git refs and are not automatically copied by this workflow.
- The source repositories have not been modified.
