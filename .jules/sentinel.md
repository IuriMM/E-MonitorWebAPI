## 2026-09-04 - [IDOR in Duvidas Update]
**Vulnerability:** Missing authorization check in the PUT /duvidas/{id} endpoint allows any authenticated user to update other users' questions.
**Learning:** Endpoints that modify specific resources must verify ownership before applying updates, even if the user is authenticated.
**Prevention:** Always verify if the current_user is the author of the resource or has an administrative role before permitting updates or deletions.
