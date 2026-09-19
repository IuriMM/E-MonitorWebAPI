## 2023-10-27 - IDOR in Update Endpoints
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Missing Ownership Check in the `PUT /duvidas/{id}` endpoint. An authenticated user could update any other user's doubt because the endpoint did not check if the current user was the owner of the resource being updated.
**Learning:** Sometimes ownership checks are correctly implemented in destructive endpoints like `DELETE` but missed in `PUT` / `PATCH` endpoints. We must enforce ownership checks on all endpoints that modify a resource, retrieving the existing resource before applying the update.
**Prevention:** Always retrieve the entity from the database and verify the `current_user` matches the entity owner (or has the appropriate admin/monitor roles) *before* processing the update payload.

## 2026-09-19 - IDOR / Mass Assignment in Messages
**Vulnerability:** The application allowed recipients to update or delete messages they received, not just the ones they sent. Furthermore, `MensagemUpdate` included `remetente` and `destinatario` fields, which allowed malicious users to modify these fields, spoofing message origins or destinations (mass assignment).
**Learning:** We must verify that `current_user` matches the *creator/sender* of the resource in `PUT`/`DELETE` endpoints, not just a participant. Also, Pydantic models for update operations must not include immutable fields like sender or recipient.
**Prevention:** Restrict updates in Pydantic to only fields that are explicitly meant to change. Always assert strict ownership checking on the specific author/sender.
