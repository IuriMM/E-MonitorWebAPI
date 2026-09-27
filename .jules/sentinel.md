## 2023-10-27 - IDOR in Update Endpoints
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Missing Ownership Check in the `PUT /duvidas/{id}` endpoint. An authenticated user could update any other user's doubt because the endpoint did not check if the current user was the owner of the resource being updated.
**Learning:** Sometimes ownership checks are correctly implemented in destructive endpoints like `DELETE` but missed in `PUT` / `PATCH` endpoints. We must enforce ownership checks on all endpoints that modify a resource, retrieving the existing resource before applying the update.
**Prevention:** Always retrieve the entity from the database and verify the `current_user` matches the entity owner (or has the appropriate admin/monitor roles) *before* processing the update payload.

## 2024-05-01 - [High] Broken Object Level Authorization (IDOR) and Mass Assignment in Messages
**Vulnerability:** Any participant in a conversation (including the recipient) could modify or delete messages sent by the other party. In addition, the `MensagemUpdate` model allowed the `remetente` (sender) and `destinatario` (recipient) to be updated after creation (Mass Assignment).
**Learning:** The check `if current_user["nome"] not in (mensagem["remetente"], mensagem["destinatario"])` incorrectly granted modification privileges to both parties instead of restricting them strictly to the author/sender. Further, Pydantic update models shouldn't blindly inherit or include fields that must remain immutable (like author/sender).
**Prevention:** Authorization checks for mutations (PUT/DELETE) must verify ownership, not just participation. Ensure update DTOs strictly limit fields to those that are mutable to prevent spoofing or mass assignment.
