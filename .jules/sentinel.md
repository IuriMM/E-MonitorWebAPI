## 2024-11-20 - Missing Authorization Check on Edit Action
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Broken Object Level Authorization (BOLA) in `update_duvida` endpoint (`routes/duvidas.py`). An authenticated user could edit or reassign ownership of any doubt they did not create.
**Learning:** While the `delete_duvida` endpoint implemented proper ownership and role checks, the `update_duvida` endpoint lacked them. This inconsistency highlights the need to systematically ensure that ownership and role validation is present on all mutative endpoints (PUT/PATCH/DELETE).
**Prevention:** Implement a consistent dependency or shared helper function for checking resource ownership across all endpoints to avoid missing checks on individual routes.
