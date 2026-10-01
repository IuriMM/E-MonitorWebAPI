## 2023-10-27 - IDOR in Update Endpoints
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Missing Ownership Check in the `PUT /duvidas/{id}` endpoint. An authenticated user could update any other user's doubt because the endpoint did not check if the current user was the owner of the resource being updated.
**Learning:** Sometimes ownership checks are correctly implemented in destructive endpoints like `DELETE` but missed in `PUT` / `PATCH` endpoints. We must enforce ownership checks on all endpoints that modify a resource, retrieving the existing resource before applying the update.
**Prevention:** Always retrieve the entity from the database and verify the `current_user` matches the entity owner (or has the appropriate admin/monitor roles) *before* processing the update payload.

## 2023-10-27 - Mass Assignment and Broken Access Control in Messages
**Vulnerability:** A user could update other people's messages, as the `PUT /mensagens/{id}` endpoint allowed both the sender and recipient to alter a message. Furthermore, they could spoof the `remetente` (sender), `destinatario` (recipient), and `horario` fields because `MensagemUpdate` included them.
**Learning:** Pydantic update models must omit fields that represent system metadata or ownership information. Authorization for modifying a resource must restrict actions to the specific owner (e.g., `remetente`), not merely a participant in the interaction. However, be careful not to incorrectly apply these strict ownership checks to read operations, which often require broader participant access.
**Prevention:** 1. Ensure `Update` schemas only contain user-editable fields. 2. Verify that `current_user` is the true author of the resource before allowing modifications.
