## 2023-10-27 - IDOR in Update Endpoints
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Missing Ownership Check in the `PUT /duvidas/{id}` endpoint. An authenticated user could update any other user's doubt because the endpoint did not check if the current user was the owner of the resource being updated.
**Learning:** Sometimes ownership checks are correctly implemented in destructive endpoints like `DELETE` but missed in `PUT` / `PATCH` endpoints. We must enforce ownership checks on all endpoints that modify a resource, retrieving the existing resource before applying the update.
**Prevention:** Always retrieve the entity from the database and verify the `current_user` matches the entity owner (or has the appropriate admin/monitor roles) *before* processing the update payload.

## 2026-09-26 - Broken Access Control & Mass Assignment in Messaging
**Vulnerability:** Broken Access Control allowed message recipients to edit or delete messages they received, not just the ones they sent. Furthermore, Mass Assignment vulnerabilities in the `MensagemUpdate` model permitted users to modify the sender (`remetente`) and recipient (`destinatario`) fields of a message.
**Learning:** Checking if a user "participates" in a conversation is sufficient for read access, but insufficient for write/delete access where strict ownership is required. Update schemas must also explicitly exclude immutable fields to prevent spoofing or ownership transfer.
**Prevention:** Always restrict mutation and deletion of resources to their specific authors. Ensure Pydantic `*Update` models explicitly omit fields that should never be altered post-creation (e.g., sender, recipient).
