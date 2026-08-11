# my-content-repo

Content generated with Safe GitHub Publisher and GitHub Actions.

## Daily automatic posts

The `Daily automatic posts` workflow generates and commits five Chinese-first, TL8899-style responsible-play Markdown posts every day at 09:17 Asia/Shanghai. Each new post naturally connects the three related properties: [TL8899 LIVE](https://tl8899.live/) for Chinese information, [TL616](https://tl616.cc/) for the platform page, and [Myanmar Casino Guide](https://myanmarcasino.cloud/) for bilingual rules. It runs entirely on GitHub and does not require Hermes, a logged-in Windows PC, or a personal GitHub token.

The workflow is idempotent: it makes sure each date has five posts and only creates the missing number. It can also be started manually from the repository's **Actions** tab. The generator supports date-range backfills with `--start-date` and `--end-date`.
