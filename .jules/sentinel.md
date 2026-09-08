## 2024-05-31 - IDOR on Update Endpoints
**Vulnerability:** Broken Access Control (Insecure Direct Object Reference) on the `PUT /duvidas/{id}` endpoint. Any authenticated user could edit details of a `duvida` belonging to another user.
**Learning:** Checking permissions for reading or deleting an object is not enough. Update endpoints often take the object ID and apply the `update_one` method directly in DB, ignoring the ownership validation.
**Prevention:** Always verify `is_autor` or relevant privilege roles (`MONITOR`/`ADMIN`) BEFORE proceeding with any object modifications. Fetch the target document first and assert permissions based on `current_user` details.
