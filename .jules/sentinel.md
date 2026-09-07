## 2024-09-07 - Insecure Direct Object Reference (IDOR) in Duvidas Update
**Vulnerability:** The PUT `/duvidas/{id}` endpoint allowed any authenticated user to modify any doubt (Duvida) regardless of who created it, bypassing authorization checks.
**Learning:** This occurred because the route did not verify if the `current_user` was the owner of the `duvida` object being updated, missing the authorization check before applying changes.
**Prevention:** Always verify authorization and ownership of objects before allowing modifications, ensuring only authorized users (authors, admins, monitors) can update specific resources.
