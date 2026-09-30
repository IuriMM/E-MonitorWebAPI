## 2023-10-27 - IDOR in Update Endpoints
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Missing Ownership Check in the `PUT /duvidas/{id}` endpoint. An authenticated user could update any other user's doubt because the endpoint did not check if the current user was the owner of the resource being updated.
**Learning:** Sometimes ownership checks are correctly implemented in destructive endpoints like `DELETE` but missed in `PUT` / `PATCH` endpoints. We must enforce ownership checks on all endpoints that modify a resource, retrieving the existing resource before applying the update.
**Prevention:** Always retrieve the entity from the database and verify the `current_user` matches the entity owner (or has the appropriate admin/monitor roles) *before* processing the update payload.

## 2024-05-24 - Mass Assignment and IDOR in Mensagens
**Vulnerability:** Mass assignment in the `MensagemUpdate` Pydantic model allowed users to spoof the `remetente` (sender), `destinatario`, and `horario` fields when editing a message. Additionally, IDOR (Insecure Direct Object Reference) in `PUT` and `DELETE` endpoints for `/mensagens` permitted any participant (including the recipient) to edit or delete messages.
**Learning:** Checking if a user "participates" in a conversation is sufficient for read access (`GET`), but write/delete access requires strict ownership checks. Pydantic models for update operations must explicitly omit fields that should remain immutable after creation.
**Prevention:** Strictly differentiate read vs. write authorization logic. Ensure update Pydantic models only include mutable fields. Enforce ownership checks (`current_user` matches the original creator/sender) for modification operations.
