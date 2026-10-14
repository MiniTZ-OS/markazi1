# MiniTZ Central Repository

This repository consolidates tracked working-tree content and recoverable Git history from the connected GitHub accounts.

- main contains unique paths from source branch, tag and pull-request trees at their original relative paths.
- Conflicting versions are preserved under __MINITZ_SOURCE_VERSIONS__/OWNER/REPOSITORY/REF/PATH.
- Original branch SHAs are retained under source-branches/OWNER/REPOSITORY/BRANCH; snapshots retain earlier branch tips.
- Source tags use source-tags/OWNER/REPOSITORY/TAG. Pull-request refs use source-pulls/OWNER/REPOSITORY/NUMBER/TYPE.
- Original source repositories are read-only inputs. Only MMLabsAI/markazi1 is written.

For private sources, add the secrets SOURCE_TOKEN_MAHDITT96, SOURCE_TOKEN_MMLABSAI and SOURCE_TOKEN_MATAGHDISI96_SOURCE with read access to the corresponding accounts' source repos, including Git LFS. See IMPORT_REPORT.md for evidence and omissions.
