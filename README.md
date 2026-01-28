
```markdown
# IBM Security Verify Bulk User Loader & Deleter

Python tools for bulk creating, updating, and deleting users in **IBM Security Verify** using the SCIM 2.0 API.

- `bulk_loader.py` — Bulk create/update users from CSV (with passwords, custom attributes, etc.)
- `bulk_deletion.py` — Bulk delete users listed in CSV (with safe dry-run mode)

Both scripts share the same `app.yaml` configuration.

## Requirements

- Python 3.8+ (3.10 or 3.11 recommended)
- Required packages:
  ```bash
  pip install requests pyyaml
  ```

## Installation

```bash
# Navigate to project folder
cd your-project-folder

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate          # macOS/Linux/WSL
# or on Windows: venv\Scripts\activate

# Install dependencies
pip install requests pyyaml
```

## Directory Structure

```
your-project/
├── app.yaml                  # ← main configuration file
├── bulk_loader.py            # create/update users
├── bulk_deletion.py          # delete users
└── util/
    ├── __init__.py
    ├── config_loader.py
    ├── logger.py
    ├── access_token_util.py
    ├── user_mapper.py        # CSV → SCIM payload logic
    ├── attribute_applicator.py  # applies configurable attribute rules
    └── scim_client.py
```

## Configuring app.yaml

Copy and customize the example below.

```yaml
tenant:
  base_url: "https://your-tenant.verify.ibm.com"      # ← your tenant domain
  scim_path: "/v2.0"                                  # usually fixed

auth:
  client_id: "your-client-id-here"                    # OAuth client with manageUsers scope
  client_secret: "your-client-secret-here"            # keep secret!
  token_path: "/v1.0/endpoint/default/token"          # usually correct

import:
  csv_file: "upload.csv"                              # path to your CSV
  batch_size: 200                                     # 50–1000; start small

  # Configurable attribute rules (applied to every user during creation/update)
  attribute_rules:
    - name: "active"                                  # core SCIM attribute
      value: true
      type: "static"                                  # or "from_csv"

    - name: "registrationstatus"                      # custom attribute
      value: "completed"
      type: "static"
      extension_urn: "urn:ietf:params:scim:schemas:extension:ibm:2.0:User"
      custom_container: "customAttributes"            # nested array in IBM extension
      custom_name_key: "name"                         # key for attribute name
      custom_value_key: "values"                      # key for value array

    # Example: a value from CSV
    # - name: "employeeNumber"
    #   type: "from_csv"
    #   csv_column: "employee_id"
    #   extension_urn: "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"

delete:
  dry_run: true                                       # set false to actually delete

logging:
  level: INFO                                         # DEBUG / INFO / WARNING / ERROR
  format: "%(asctime)s  %(levelname)-8s  %(message)s"
  datefmt: "%Y-%m-%d %H:%M:%S"
  to_file: false
  file_path: "bulk_operations.log"
  file_mode: "a"
```

### Where to customize what

| File                        | Purpose & when to edit                                                                 | Typical changes |
|-----------------------------|----------------------------------------------------------------------------------------|-----------------|
| `app.yaml`                  | Primary configuration file. Change values, add/remove attributes, switch tenants.     | High frequency (daily/weekly) |
| `util/user_mapper.py`       | Defines the base SCIM payload structure + any tenant-specific logic/validation.       | Medium (new tenant, new requirements) |
| `util/attribute_applicator.py` | Handles how rules from `app.yaml` are applied to the payload (nesting, merging, etc.) | Low (only if new nesting pattern or transformation needed) |
| `util/scim_client.py`       | Low-level SCIM operations (bulk, search, etc.)                                         | Very low |

**Best practice**:
- 90% of changes → only edit `app.yaml` (no code change needed)
- When logic/validation/computed fields are needed → edit `user_mapper.py`
- Only touch `attribute_applicator.py` for new complex attribute types or vendors

## CSV Format

Required columns:
- `preferred_username` (userName)
- `email`
- `externalId` (optional but recommended)
- `given_name`, `family_name` (optional)
- `password` (optional; supports `{SHA-1}...` prefix)

## Usage

```bash
# Create/update users
python bulk_loader.py

# Delete users (dry-run first!)
python bulk_deletion.py
```

**Before real deletion**:
1. Review logs
2. Set `delete.dry_run: false` in `app.yaml`
3. Re-run

## Security Notes

- Never commit `app.yaml` with real secrets
- Use least-privilege OAuth client (only `manageUsers`)
- Always test deletions with `dry_run: true`
- Consider exporting users first via SCIM or UI backup

## Troubleshooting

- **401 Unauthorized** → wrong client credentials / missing scope
- **400 Bad Request** → check logs for CSIAIxxxx codes
- **Custom attributes missing** → verify `attribute_rules` structure & URN
- **Schemas missing** → ensure required extension URNs are in payload

Happy bulk managing in IBM Verify!

Questions? Ping @chronos2g or open an issue.
```

