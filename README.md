# OpenSpartan XUID Resolver

CLI tool that converts a gamertag to [Xbox User ID (XUID)](https://learn.microsoft.com/gaming/gdk/_content/gc/reference/live/rest/uri/presence/uri-usersxuidget).

🎥 [**Watch video**](https://www.youtube.com/watch?v=HZcG5-X_Cpw) - explains how the tool was built and how it works.

## Requirements

Install [Python](https://www.python.org/downloads/) (minimum `3.11`). The CLI should work equally well on Linux, macOS, and Windows.

## Usage

I highly recommend [creating a virtual envirnment](https://docs.python.org/3/library/venv.html) first. Once done, make sure to install the packages in `requirements.txt`:

```bash
pip install -r requirements.txt
```

You will also need to provide a **client ID registration** with Microsoft Entra ID. You can [register an application](https://learn.microsoft.com/entra/identity-platform/quickstart-register-app?tabs=certificate) for free in the Azure Portal.

If you already have a registered application, take note of the client ID and set it in your environent as `OPSP_XR_CLIENT_ID`.

**macOS/Linux**:

```bash
export OPSP_XR_CLIENT_ID=your_client_id
```

**Windows**:

```bash
$env:OPSP_XR_CLIENT_ID = "your_client_id"
```

Depending on the platform, you can also make the changes permanent (you don't need to set the client ID on every terminal launch):

**macOS/Linux**

```bash
echo 'export OPSP_XR_CLIENT_ID=your_client_id' >> ~/.bashrc
```
Change the file if you use a different shell, like `zsh`.

**Windows**

```bash
[Environment]::SetEnvironmentVariable("OPSP_XR_CLIENT_ID", "your_client_id", "User")
```

Once completed, you can call the tool from your terminal application:

```bash
python -m xr "GAMERTAG_TO_RESOLVE"
```

