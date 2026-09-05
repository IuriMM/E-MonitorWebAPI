## 2024-05-01 - IDOR in Doubt Updates
**Vulnerability:** Insecure Direct Object Reference (IDOR) on the `PUT /duvidas/{id}` endpoint. The endpoint permitted any authenticated user to update any doubt because it only validated the input schema but failed to retrieve the underlying record to confirm ownership.
**Learning:** This existed because authorization checks were inconsistently applied across endpoints. The `DELETE` endpoint correctly checked ownership and roles, but the `PUT` endpoint trusted the input without verifying the resource's owner.
**Prevention:** Always retrieve the target resource from the database *before* applying updates and explicitly verify that the authenticated user has the necessary permissions (e.g., owner or admin) to modify the specific object.
