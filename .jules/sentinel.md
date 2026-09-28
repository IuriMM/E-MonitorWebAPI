## 2023-10-27 - IDOR in Update Endpoints
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Missing Ownership Check in the `PUT /duvidas/{id}` endpoint. An authenticated user could update any other user's doubt because the endpoint did not check if the current user was the owner of the resource being updated.
**Learning:** Sometimes ownership checks are correctly implemented in destructive endpoints like `DELETE` but missed in `PUT` / `PATCH` endpoints. We must enforce ownership checks on all endpoints that modify a resource, retrieving the existing resource before applying the update.
**Prevention:** Always retrieve the entity from the database and verify the `current_user` matches the entity owner (or has the appropriate admin/monitor roles) *before* processing the update payload.

## 2026-09-28 - [IDOR and Mass Assignment in Mensagens]
**Vulnerability:** Found an Insecure Direct Object Reference (IDOR) and Mass Assignment vulnerability in the `/mensagens` routes. The `MensagemUpdate` model allowed updating the `remetente` (sender), `destinatario` (recipient), and `horario` fields. Additionally, the `update_mensagem` and `delete_mensagem` routes allowed anyone who was either the sender or the recipient of a message to edit or delete it, meaning a recipient could modify a message sent to them.
**Learning:** The previous implementation incorrectly conflated "participant in a conversation" with "owner of a message" when doing authorization checks for modifying resources. Also, the update schema mapped too closely to the base entity schema, enabling modification of system-managed fields.
**Prevention:**
- In update schemas (e.g., `*Update`), strictly enumerate only the fields that are allowed to be modified by the user (like `texto`), excluding read-only or system-controlled fields.
- Ensure authorization checks for edit and delete operations explicitly verify that the `current_user` is the true owner or creator of the resource, not just a participant or observer.
