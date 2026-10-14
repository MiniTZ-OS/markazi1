# ZombieTZ Demo 01 — RTX Delivery 2026-10-04

Source commit: `c35d3177f261b25229f5c276ededf79b9ca36976`

Engine: Unreal Engine 5.8.3

Validation:
- ZombieTZ.Integration: 12/12 PASS
- RTX soak: 120 seconds PASS
- Packaged BuildCookRun: PASS
- Packaged clean launch: PASS
- Real packaged R-key restart: PASS; restart_count=1; map/player/controller reloaded

Artifacts:
- `ZombieTZ-Demo01-Linux-20261004T145552Z.tar`
  - SHA-256: `31bc49d600a20c7699dc8e826aa3619cb4599967ab074f5c67c32c9f681376e3`
  - Contains the Linux playable package.
- `ZombieTZ-Demo01-source-c35d3177f261b25229f5c276ededf79b9ca36976.bundle`
  - SHA-256: `96a32d4c9d4e266943434a0344b6c8dd8a7a605c2dc1ae3ee158ddb7e2275bad`
  - Complete Git history; recover with `git clone <bundle> ZombieTZ`.

Packaged game binary SHA-256:
`d4dba7e27251c144f4799d092cf138a9ce27b9fa0e1afedec95683c224d821ca`
