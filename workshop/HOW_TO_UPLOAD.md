# Uploading FireWatch to the Steam Workshop

Whiskerwood has no in-game uploader; use Valve's SteamCMD.

1. In the modkit, run **Cook & Install** on `Content/Mods/FireWatch`.
2. From the repo root (Git Bash) run `./sync-from-modkit.sh --release`. It copies the assets into
   `Mod/FireWatch/` and stages `FireWatch.pak` + `FireWatch.uplugin` into `workshop/content/`
   (git-ignored; the pak is a build artifact).
3. Update `"changenote"` in `FireWatch.vdf` (and `"Version"` in the uplugin).
4. Run (SteamCMD from https://developer.valvesoftware.com/wiki/SteamCMD):
   ```
   C:\steamcmd\steamcmd.exe +login YOUR_STEAM_USERNAME +workshop_build_item "E:\modding\whiskerwood-firewatch\workshop\FireWatch.vdf" +quit
   ```
5. First upload creates the item as **private** (`visibility 2`) and writes its id into
   `"publishedfileid"` in the .vdf - commit that change. Make it public on the Workshop page.
   Later updates: same command, new changenote.

The preview image is `docs/screenshot.png`.
