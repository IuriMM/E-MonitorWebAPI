## 2025-02-20 - IDOR in duvidas update endpoint
**Vulnerability:** Insecure Direct Object Reference (IDOR) allowed any authenticated user to update any duvida regardless of ownership.
**Learning:** The `update_duvida` endpoint did not check the existing document's owner before applying the update. Role checks were only applied to specific fields (`status`) rather than the overall object ownership.
**Prevention:** Always fetch the target resource first and explicitly verify that the `current_user` is the owner (or has administrative privileges) before processing updates.
