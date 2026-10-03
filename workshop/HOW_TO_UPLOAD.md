# Uploading FireWatch to the Steam Workshop

Whiskerwood has no in-game uploader; the upload uses Valve's SteamCMD (`E:\modding\steamcmd\steamcmd.exe`).

1. In the modkit, run **Cook & Install** on `Content/Mods/FireWatch` (close the game first).
2. Bump `"Version"` in `Mod/FireWatch/FireWatch.uplugin` (copy it into the modkit folder too) and
   write a new `"changenote"` in `workshop/FireWatch.vdf`.
3. Run `sync-from-modkit.bat`. It copies the assets into `Mod/FireWatch/` and stages
   `FireWatch.pak` + `FireWatch.uplugin` into `workshop/content/` (git-ignored; the pak is a build artifact).
4. Commit and push.
5. Run `sync-to-steam.bat`. SteamCMD asks for the password / Steam Guard code if it has no saved login.
   The item id is already in the .vdf (`3807454089`), so this updates the existing Workshop item.

The preview image is `docs/screenshot.png`.
