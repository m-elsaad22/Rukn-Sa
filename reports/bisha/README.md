# Bisha articles (RSCA-6)

Artifacts for the Bisha cleaning / pest / electrician / electrical draft batch on `https://www.rukn-eltatawer.com/sa/`.

- `bisha_articles_audit.csv` — phase 1 decisions
- `bisha_articles_plan_summary.md` — short plan
- `bisha_articles_creation_report.csv` — draft IDs / SEO / word counts
- `bisha_articles_final_report.md` — execution summary

Canonical copies for the Project coordinator also live under the Project store `docs/` folder.

Scripts (require `WP_USER` / `WP_APP_PASSWORD`):

```bash
export WP_USER=cursor
export WP_APP_PASSWORD='…'
python3 scripts/bisha_run_audit.py
python3 scripts/bisha_create_drafts.py
```
