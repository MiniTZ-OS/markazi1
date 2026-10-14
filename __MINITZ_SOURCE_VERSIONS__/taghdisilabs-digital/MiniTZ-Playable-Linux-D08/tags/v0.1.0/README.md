# MiniTZ Playable Linux D08

Native x86-64 Linux packaged game build from the MiniTZ OS historical game-production lineage.

## Download
Use the GitHub Release asset: `MiniTZ-Playable-Linux-D08.tar.zst`.

## Run
```bash
mkdir -p ~/MiniTZ-Playable-D08
tar --zstd -xf MiniTZ-Playable-Linux-D08.tar.zst -C ~/MiniTZ-Playable-D08
cd ~/MiniTZ-Playable-D08/Linux
chmod +x BiellaGames.sh BiellaGames/Binaries/Linux/BiellaGames
./BiellaGames.sh -Windowed -ResX=1280 -ResY=720
```

The packaged executable is a native Linux x86-64 Unreal build and uses Vulkan.

## Integrity
SHA-256: `7ceb504983c6a5609fa4d6da77531388d1388d5f6ccf50b54d6bfd763bf451d0`
Size: 481212854 bytes

The legacy executable/package identifiers inside the archive are preserved as technical provenance; the active product identity is MiniTZ OS.
