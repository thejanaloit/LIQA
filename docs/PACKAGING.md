# Packaging

- Inno: packaging/liqa-worker.iss
- Autostart: scripts/register-logon-task.ps1
- Hyper-V/VMware: dedicated VM, GPU/virtual display ≥ 1280x720, autologon, never lock.
- RDP: tscon %SESSIONNAME% 0 after connect so the console stays headed.
- Offline wheels: pip download -r apps/worker/requirements.txt -d wheels/
- Update channel: signed zip + hash in CHANGELOG (customer verifies).
- License key: POST /v1/license
- Uninstall: Inno + optional capture wipe.
