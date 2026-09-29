## 2023-10-27 - IDOR in Update Endpoints
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Missing Ownership Check in the `PUT /duvidas/{id}` endpoint. An authenticated user could update any other user's doubt because the endpoint did not check if the current user was the owner of the resource being updated.
**Learning:** Sometimes ownership checks are correctly implemented in destructive endpoints like `DELETE` but missed in `PUT` / `PATCH` endpoints. We must enforce ownership checks on all endpoints that modify a resource, retrieving the existing resource before applying the update.
**Prevention:** Always retrieve the entity from the database and verify the `current_user` matches the entity owner (or has the appropriate admin/monitor roles) *before* processing the update payload.

## 2026-09-29 - Mass Assignment and BOLA in Messages
**Vulnerability:** Messages could be spoofed (mass assignment on sender/recipient) and recipients could edit/delete messages they received (BOLA).
**Learning:** Pydantic update models shouldn't include immutable fields. Both sender and recipient shouldn't have equal access to mutate messages.
**Prevention:** Only expose mutable fields in Update models. Verify strictly that current user is the owner/creator (remetente) of the message, not just a participant, for mutation endpoints.
