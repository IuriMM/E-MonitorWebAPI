## 2024-05-24 - Missing Authorization in Duvida Update
**Vulnerability:** Insecure Direct Object Reference (IDOR) on PUT /duvidas/{id}. Any authenticated user could update any doubt, regardless of who created it.
**Learning:** The route checked if the user was allowed to change the *status* of a doubt (requiring monitor/admin), but missed the check to see if the user was the *author* of the doubt or a monitor/admin to edit other fields.
**Prevention:** Always check both existence of the resource and ownership/authorization before performing an update operation.
