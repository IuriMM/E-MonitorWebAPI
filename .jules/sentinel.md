## 2023-10-27 - IDOR in Update Endpoints
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Missing Ownership Check in the `PUT /duvidas/{id}` endpoint. An authenticated user could update any other user's doubt because the endpoint did not check if the current user was the owner of the resource being updated.
**Learning:** Sometimes ownership checks are correctly implemented in destructive endpoints like `DELETE` but missed in `PUT` / `PATCH` endpoints. We must enforce ownership checks on all endpoints that modify a resource, retrieving the existing resource before applying the update.
**Prevention:** Always retrieve the entity from the database and verify the `current_user` matches the entity owner (or has the appropriate admin/monitor roles) *before* processing the update payload.

## 2026-09-15 - [Privilege Escalation / IDOR in Messages Update]
**Vulnerability:** Insecure Direct Object Reference (IDOR) and missing immutable fields protection in the `PUT /mensagens/{id}` endpoint. The endpoint checked if the user participated in the conversation but permitted the receiver to edit the message. Moreover, `remetente` and `destinatario` could be modified by the update payload.
**Learning:** Endpoints that modify resources must check exact permissions, such as allowing only the author/sender to edit their own message. Furthermore, models used for updates (e.g., `MensagemUpdate`) must exclude fields that should be immutable (like sender and receiver) to prevent data integrity compromise.
**Prevention:** Always restrict edits to the creator of the resource when applicable, and omit immutable entity fields from update schemas (Pydantic models) to prevent manipulation.
